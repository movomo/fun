#! /usr/bin/env python3

# import io
import struct

from libc.stdlib cimport malloc, free
# from libc.string cimport strcpy


cpdef bytes compress(bytes data):
    """Compress data with simple rle. (same char escaping)

    >>> compress(b'aaaaabbbbbbcddefffg')
    b'\\x13\\x00\\x00\\x00aa\\x05bb\\x06cdd\\x02eff\\x03g'
    """
    # We run away if the file size exceeds 4 gigs.
    cdef unsigned long long total_length = len(data)
    if total_length > 2 ** 32:
        raise ValueError('file is too big')
    
    cdef unsigned char* data_ = <unsigned char*> data
    cdef bytearray out = bytearray()
    cdef unsigned int run_start = 0
    cdef unsigned int i = 0
    cdef unsigned char length
    cdef unsigned char run_char = 0
    cdef unsigned char c
    while i < total_length:
        c = data_[i]
        length = i - run_start
        if c != run_char:
            if length >= 2:
                out.append(run_char)
                out.append(run_char)
                out.append(length)
            elif length == 1:
                out.append(run_char)
            run_start = i
            run_char = c
        elif length == 255:
            # Next repetition will make the number out of byte boundary.
            # Reset it.
            out.append(run_char)
            out.append(run_char)
            out.append(length)
            run_start = i
        i += 1
    else:
        length = total_length - run_start
        if length >= 2:
            out.append(run_char)
            out.append(run_char)
            out.append(length)
        elif length == 1:
            out.append(run_char)

    return struct.pack('<L', total_length) + bytes(out)


cpdef bytes decompress(bytes data):
    """Decompress rle-compressed data to original.

    >>> decompress(b'\\x13\\x00\\x00\\x00aa\\x05bb\\x06cdd\\x02eff\\x03g')
    b'aaaaabbbbbbcddefffg'
    """
    cdef unsigned int original_length = struct.unpack('<L', data[:4])[0]
    cdef unsigned char* out = <unsigned char*> malloc(original_length * sizeof(char))
    if not out:
        raise MemoryError()
        
    cdef unsigned int total_length = len(data)
    cdef unsigned int i = 4
    cdef unsigned int j = 0
    cdef unsigned int k = 0
    cdef unsigned char c
    cdef unsigned char* data_ = <unsigned char*> data
    while i < total_length:
        c = data_[i]
        if i < total_length - 2 and c == data_[i + 1]:
            k = 0
            while k < data_[i + 2]:
                if j >= original_length:
                    raise ValueError('incorrect format')
                out[j] = c
                j += 1
                k += 1
            i += 3
        else:
            if j >= original_length:
                raise ValueError('incorrect format')
            out[j] = c
            i += 1
            j += 1

    cdef bytes result = out[:original_length]
    free(out)
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
    if failures == 0:
        _test()
