#! /usr/bin/env python3

import io
import struct


def compress(data):
    """Compress data with simple rle. (same char escaping)

    >>> compress(b'aaaaabbbbbbcddefff')
    b'aa5bb6cdd2eff3'
    """
    tobyte = struct.Struct('@B')
    out = io.BytesIO()
    run_start = 0
    run_char = b''
    for i, c in enumerate(data):
        length = i - run_start
        if c != run_char:
            if length >= 2:
                out.write(run_char*2 + tobyte.pack(length))
            else:
                out.write(run_char * length)
            run_start = i
            run_char = c
        elif length == 255:
            # Next repetition will make the number out of byte boundary.
            # Reset it.
            out.write(run_char*2 + tobyte.pack(length))
            run_start = i


def decompress(data):
    """Decompress rle-compressed data to original.

    >>> decompress(b'aa5bb6cdd2eff3')
    b'aaaaabbbbbbcddefff'
    """
    frombyte = struct.Struct('@B')
    out = io.BytesIO()
    total_length = len(data)
    while i < total_length:
        c = data[i]
        if i < total_length - 2 and c == data[i + 1]:
            repeat = frombyte.unpack(data[i + 2])[0]
            out.write(c * repeat)
            i += 2
        else:
            out.write(c)
            i += 1


if __name__ == '__main__':
    import doctest
    doctest.testmod()
