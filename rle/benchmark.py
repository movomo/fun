#! /usr/bin/env python3

import hashlib
import time

from pathlib import Path

import rle
import crle


def benchmark(module):
    with Path(__file__).with_name('test.bmp').open('rb') as image_r:
        data = image_r.read()

    # hash the data for verification
    input_hash = hashlib.sha256(data).hexdigest()
    input_size = len(data)

    start = time.process_time_ns()
    data = module.compress(data)
    ratio = len(data) / input_size
    data = module.decompress(data)
    end = time.process_time_ns()

    time_diff = (end - start) / 1000000000
    output_hash = hashlib.sha256(data).hexdigest()
    print(f"Done in {time_diff:.4f} seconds. (ratio: {ratio:.2f})")
    return input_hash == output_hash


def main():
    # print(f"cpython: {benchmark(rle)}")
    print(f"cython unmodified: {benchmark(crle)}")


if __name__ == '__main__':
    main()
