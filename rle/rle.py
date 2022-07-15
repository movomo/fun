#! /usr/bin/env python3

import io
import struct


def compress(data):
    """Compress data with simple rle. (same char escaping)

    >>> compress(b'aaaaabbbbbbcddefffg')
    b'aa\\x05bb\\x06cdd\\x02eff\\x03g'
    """
    tobyte = struct.Struct('<B')
    out = io.BytesIO()
    run_start = 0
    run_char = 0
    for i, c in enumerate(data):
        length = i - run_start
        if c != run_char:
            if length >= 2:
                out.write(tobyte.pack(run_char)*2 + tobyte.pack(length))
            else:
                out.write(tobyte.pack(run_char) * length)
            run_start = i
            run_char = c
        elif length == 255:
            # Next repetition will make the number out of byte boundary.
            # Reset it.
            out.write(tobyte.pack(run_char)*2 + tobyte.pack(length))
            run_start = i
    else:
        length = len(data) - run_start
        if length >= 2:
            out.write(tobyte.pack(run_char)*2 + tobyte.pack(length))
        else:
            out.write(tobyte.pack(run_char) * length)

    out.seek(0)
    return out.read()


def decompress(data):
    """Decompress rle-compressed data to original.

    >>> decompress(b'aa\\x05bb\\x06cdd\\x02eff\\x03g')
    b'aaaaabbbbbbcddefffg'
    """
    tobyte = struct.Struct('<B')
    out = io.BytesIO()
    total_length = len(data)
    i = 0
    while i < total_length:
        c = data[i]
        if i < total_length - 2 and c == data[i + 1]:
            out.write(tobyte.pack(c) * data[i + 2])
            i += 3
        else:
            out.write(tobyte.pack(c))
            i += 1

    out.seek(0)
    return out.read()


if __name__ == '__main__':
    import doctest
    doctest.testmod()
