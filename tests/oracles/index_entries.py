#!/usr/bin/env python3
"""What an index file holds, without the checksum or any extension's bytes: the
version and entry count, each entry's raw bytes in hex, then each extension's
signature and size. Two index files that print the same entry lines hold the
same entries byte for byte (stat fields, flags, extended flags and padding
included), whichever program wrote them.

    python3 tests/oracles/index_entries.py <index-file> [raw]     raw: 20 (default) or 32
"""
import struct
import sys

data = open(sys.argv[1], "rb").read()
raw = int(sys.argv[2]) if len(sys.argv) > 2 else 20
end = len(data) - raw
version, count = struct.unpack(">II", data[4:12])
print("version %d count %d" % (version, count))
offset = 12
for _ in range(count):
    start = offset
    flags = struct.unpack(">H", data[offset + 40 + raw : offset + 42 + raw])[0]
    name = offset + 42 + raw + (2 if flags & 0x4000 else 0)
    nul = data.index(b"\0", name)
    length = nul + 1 - start
    length += (-length) % 8
    offset = start + length
    print("entry " + data[start:offset].hex())
while end - offset >= 8:
    signature = data[offset : offset + 4].decode("latin-1")
    size = struct.unpack(">I", data[offset + 4 : offset + 8])[0]
    print("extension %s %d" % (signature, size))
    offset += 8 + size
