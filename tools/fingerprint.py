"""Fingerprint of a JPEG page image that ignores metadata.

Some programs (photo apps, file transfer tools) add metadata blocks such as EXIF, XMP or
C2PA "content credentials" to a JPEG without changing a single pixel. Those blocks live in
APPn/COM segments. This fingerprint hashes everything EXCEPT those segments — i.e. the actual
image data — so it changes if any pixel data changes, but not when harmless metadata is added.
Standard library only (no Pillow needed)."""
import hashlib

def jpeg_fingerprint(data: bytes) -> str:
    if data[:2] != b"\xff\xd8":
        raise ValueError("not a JPEG file")
    h = hashlib.sha256(b"\xff\xd8")
    pos = 2
    while pos < len(data):
        if data[pos] != 0xFF:
            raise ValueError("corrupt JPEG structure")
        marker = data[pos + 1]
        if marker == 0xDA:                      # start of scan: the compressed pixels, to end of file
            h.update(data[pos:])
            break
        length = int.from_bytes(data[pos + 2:pos + 4], "big")
        segment = data[pos:pos + 2 + length]
        if not (0xE0 <= marker <= 0xEF or marker == 0xFE):   # skip APP0-APP15 and comments
            h.update(segment)
        pos += 2 + length
    return h.hexdigest()
