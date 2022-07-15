#! /usr/bin/env python3

import io
import struct

from libc.stdlib cimport malloc
from libc.string cimport strcpy


def compress(data):
    """Compress data with simple rle. (same char escaping)

    >>> compress(b'aaaaabbbbbbcddefffg')
    b'aa\\x05bb\\x06cdd\\x02eff\\x03g'
    """
    tobyte = struct.Struct('<B')
    out = io.BytesIO()
    run_start = 0
    run_char = 0
    
    cdef unsigned int i
    cdef unsigned char c
    cdef unsigned char length
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


cpdef bytes decompress(char* data):
    """Decompress rle-compressed data to original.

    >>> decompress(b'aa\\x05bb\\x06cdd\\x02eff\\x03g')
    b'aaaaabbbbbbcddefffg'
    """
    cdef char* out = <char*> malloc(data[0] * sizeof(char))
    cdef unsigned int i = 1
    cdef unsigned int total_length = len(data) - 1
    cdef unsigned int j = 0
    cdef unsigned int k = 0
    cdef char c
    while i < total_length:
        c = data[i]
        if i < total_length - 2:
            if c == data[i + 1]:
                # out.append(c * data[i + 2])
                k = 0
                while k < data[i + 2]:
                    out[j] = c
                    j += 1
                    k += 1
            else:
                out[j] = c
                out[j + 1] = data[i + 1]
                out[j + 2] = data[i + 2]
                j += 3
            i += 3
        else:
            i += 1
            j += 1
            out[j] = c

    result = <bytes> out[:data[0]]
    return result


def _test():
    import hashlib
    import time
    from pathlib import Path

    with Path(__file__).with_name('test.bmp').open('rb') as image_r:
        data = image_r.read()

    # hash the data for verification
    input_hash = hashlib.sha256(data).hexdigest()
    input_size = len(data)

    start = time.process_time_ns()
    data = compress(data)
    ratio = len(data) / input_size
    data = decompress(data)
    end = time.process_time_ns()

    time_diff = (end - start) / 1000000000
    output_hash = hashlib.sha256(data).hexdigest()
    print(f"Done in {time_diff:.4f} seconds. (ratio: {ratio:.2f})")
    assert input_hash == output_hash


if __name__ == '__main__':
    import doctest
    failures = doctest.testmod()[0]
    if failuers == 0:
        _test()
