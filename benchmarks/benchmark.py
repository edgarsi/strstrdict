import ctypes
import gc
import os
import time
from contextlib import suppress
from dataclasses import dataclass
from multiprocessing import Queue, Process
from textwrap import dedent
from typing import Any

import psutil
from gmpy2.gmpy2 import mpz_random, random_state
from tabulate import tabulate

from benchmarks.sqlitedict_wrapper import SqliteDict_Wrapper
from strstrdict import StrStrDict


# ==================== Configuration ====================

dictionary_kinds = {
    'dict': dict,
    'sqlitedict[^wrapper]': SqliteDict_Wrapper,
    'strstrdict': StrStrDict,
}


@dataclass
class BencherOptions:
    # How many elements will be written to the dictionary.
    fill_size: int = 10 ** 6
    # Pool of possible strings. Smaller pool yields more overwrites during
    # filling, and more hits when reading random keys.
    pool_size: int = 2 * fill_size
    # Both keys and values will be of this length.
    str_length_min: int = 10
    str_length_max: int = 20


def benchmark_kinds():
    for (str_length_min, str_length_max) in [(5,10), (20,30), (100,200)]:
        yield BencherOptions(
            str_length_min=str_length_min,
            str_length_max=str_length_max)


# ==================== Implementation ====================

rs = random_state()


def randomish_string(min_length, max_length, pool_size):
    # r = randint(0, pool_size)
    # s = hashlib.md5(str(r).encode()).hexdigest()
    m = mpz_random(rs, pool_size)
    length = min_length + m % (max_length - min_length + 1)
    s = mpz_random(rs, pool_size).digits(62) + ' '
    # print(length)
    # print((length // len(s)) * s + s[:length % len(s)])
    return (length // len(s)) * s + s[:length % len(s)]


def used_memory():
    process = psutil.Process(os.getpid())
    return process.memory_info().rss  # in bytes


@dataclass
class Stats:
    time_seconds: float
    memory_bytes: int


def measure(f):
    gc.collect()
    start_mem = used_memory()
    # print(f'Used memory at start: {megabytes_str(start_mem)}')
    start_time = time.monotonic()
    f()
    end_time = time.monotonic()
    gc.collect()
    end_mem = used_memory()
    # print(f'Used memory at end: {megabytes_str(end_mem)}')
    return Stats(end_time - start_time, end_mem - start_mem)


def trim_memory() -> int:
  libc = ctypes.CDLL("libc.so.6")
  return libc.malloc_trim(0)


@dataclass
class BenchResults:
    fill_time: float
    fill_memory: int
    read_time: float


class Bencher:
    def __init__(self, d, options):
        self.d = d
        self.opts = options

    def run(self):
        randomizer = measure(self.generate_rnd_strings)
        # print(f'Generated {self.opts.fill_size} random strings in {randomizer.time_seconds:.2f} seconds')
        # time.sleep(5)
        # trim_memory()
        fill_stats = measure(self.fill)
        read_stats = measure(self.read)
        del self.d
        # print(f'Used memory after cleanup: {megabytes_str(used_memory())}')
        return BenchResults(
            fill_time=fill_stats.time_seconds - randomizer.time_seconds * 2,
            fill_memory=fill_stats.memory_bytes,
            read_time=read_stats.time_seconds - randomizer.time_seconds,
        )

    def generate_rnd_strings(self):
        for i in range(self.opts.fill_size):
            self.rnd_string()

    def fill(self):
        for i in range(self.opts.fill_size):
            self.d[self.rnd_string()] = self.rnd_string()

    def read(self):
        for i in range(self.opts.fill_size):
            self.d.get(self.rnd_string())

    def rnd_string(self):
        return randomish_string(
            self.opts.str_length_min,
            self.opts.str_length_max,
            self.opts.pool_size)


@dataclass
class TableCell:
    text: str
    compare_key: Any = None


def seconds_str(t):
    return f"{t:.2f}s"


def megabytes_str(b):
    return f'{b / 1024 / 1024:.2f}'


def run_benchmark(queue, dgen, options):
    b = Bencher(dgen(), options)
    queue.put(b.run())


def benchmark_in_subprocess(deg, options):
    """ Run in subprocess, to get a clean view of used memory. Not all memory is
    always released to the OS, as allocators hope to reuse it. """
    queue = Queue()
    p = Process(target=run_benchmark, args=(queue, deg, options))
    p.start()
    p.join()
    return queue.get()


def run_with_options(options):
    headers = ['', 'Fill time (s)', 'Read time (s)', 'Memory (MB)']

    table = []
    for name, dgen in dictionary_kinds.items():
        # print('Benching ' + name)
        results = benchmark_in_subprocess(dgen, options)
        table.append([
            TableCell(name),
            TableCell(seconds_str(results.fill_time), results.fill_time),
            TableCell(seconds_str(results.read_time), results.read_time),
            TableCell(megabytes_str(results.fill_memory), results.fill_memory),
        ])

    # Make the best result bold.
    for col in range(len(headers)):
        with suppress(TypeError):
            min_at = min(range(len(table)), key=lambda i: table[i][col].compare_key)
            cell = table[min_at][col]
            cell.text = f'**{cell.text}**'

    table_texts = [[cell.text for cell in row] for row in table]

    print()
    print()
    fill_size_f = f'{options.fill_size // 10**6}m'
    pool_size_f = f'{options.pool_size // 10**6}m'
    hit_rate = options.fill_size / options.pool_size
    hit_rate_f = f'{hit_rate * 100:.0f}%'
    print(dedent(f'''\
        Filling a dictionary with {fill_size_f} items, key and value strings
        **{options.str_length_min}-{options.str_length_max} chars** long, from a
        pool of {pool_size_f} random strings. Then reading values {fill_size_f}
        times, with a {hit_rate_f} hit rate.
        '''))

    formatted_table = tabulate(table_texts, headers=headers, tablefmt='github')
    print(formatted_table)


def run_all():
    for options in benchmark_kinds():
        run_with_options(options)

    print()
    print(dedent(f'''\
        [^wrapper]: SqliteDict is used with commiting every 1000 writes.
        '''))


if __name__ == '__main__':
    m = measure(run_all)
    print(f"Benchmarking took {seconds_str(m.time_seconds)} seconds")
