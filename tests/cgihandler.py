"""A stdlib-only stand-in for http.server.CGIHTTPRequestHandler, which Python 3.13
removed (macOS CI runners have 3.13). Runs the scripts under `cgi_directories`
(here: wrappers around `git http-backend`) with the CGI environment, passes the
request body, and sends back what they print (`Status:` and the other headers,
then the body). Enough for git's smart HTTP; not a general CGI server.
"""
import http.server
import os
import subprocess
import urllib.parse


class CGIHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    cgi_directories = ["/cgi-bin"]

    def _cgi_target(self):
        path = urllib.parse.urlsplit(self.path).path
        for directory in self.cgi_directories:
            if path.startswith(directory + "/"):
                rest = path[len(directory) + 1:]
                script, slash, info = rest.partition("/")
                return directory, script, (slash + info) if slash else ""
        return None

    def do_GET(self):
        if self._cgi_target():
            self._run_cgi()
        else:
            super().do_GET()

    def do_HEAD(self):
        if self._cgi_target():
            self._run_cgi()
        else:
            super().do_HEAD()

    def do_POST(self):
        if self._cgi_target():
            self._run_cgi()
        else:
            self.send_error(501, "Unsupported method (POST)")

    def _body(self):
        if self.headers.get("Transfer-Encoding", "").lower() == "chunked":
            data = b""
            while True:
                size = int(self.rfile.readline().split(b";")[0].strip() or b"0", 16)
                if size == 0:
                    while self.rfile.readline().strip():
                        pass
                    return data
                data += self.rfile.read(size)
                self.rfile.readline()
        length = int(self.headers.get("Content-Length") or 0)
        return self.rfile.read(length) if length else b""

    def _run_cgi(self):
        directory, script, info = self._cgi_target()
        split = urllib.parse.urlsplit(self.path)
        program = self.translate_path(directory + "/" + script)
        if not os.path.isfile(program):
            self.send_error(404, "No such CGI script")
            return
        body = self._body()
        env = dict(os.environ)
        env.update(
            SERVER_SOFTWARE="cgihandler",
            SERVER_NAME="127.0.0.1",
            GATEWAY_INTERFACE="CGI/1.1",
            SERVER_PROTOCOL=self.protocol_version,
            REQUEST_METHOD=self.command,
            SCRIPT_NAME=directory + "/" + script,
            PATH_INFO=urllib.parse.unquote(info),
            QUERY_STRING=split.query,
            REMOTE_ADDR=self.client_address[0],
            CONTENT_LENGTH=str(len(body)),
        )
        if self.headers.get("Content-Type"):
            env["CONTENT_TYPE"] = self.headers["Content-Type"]
        for name, value in self.headers.items():
            if name.lower() not in ("content-type", "content-length", "transfer-encoding"):
                env["HTTP_" + name.upper().replace("-", "_")] = value
        done = subprocess.run([program], input=body, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, env=env, cwd=os.path.dirname(program))
        head, sep, payload = done.stdout.partition(b"\r\n\r\n")
        if not sep:
            head, sep, payload = done.stdout.partition(b"\n\n")
        status = 200
        headers = []
        for line in head.decode("latin-1").splitlines():
            name, _, value = line.partition(":")
            if name.lower() == "status":
                status = int(value.strip().split()[0])
            elif name:
                headers.append((name, value.strip()))
        self.send_response(status)
        for name, value in headers:
            self.send_header(name, value)
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(payload)
