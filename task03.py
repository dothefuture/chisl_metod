import math
import time
import numpy as np

rng = np.random.default_rng(42)
a = rng.normal(size=1_000_000)


def loop_sin_sq(arr):
    result = []
    for x in arr:
        result.append(math.sin(x) + x * x)
    return result


def numpy_sin_sq(arr):
    return np.sin(arr) + arr**2


def measure(fn, x, repeat=3):
    best = float("inf")
    result = None
    for _ in range(repeat):
        t0 = time.perf_counter()
        result = fn(x)
        t1 = time.perf_counter()
        best = min(best, t1 - t0)
    return result, best


r_loop,  t_loop  = measure(loop_sin_sq,  a)
r_numpy, t_numpy = measure(numpy_sin_sq, a)

print(f"цикл:   {t_loop*1000:10.2f} мс")
print(f"NumPy:  {t_numpy*1000:10.2f} мс")
print(f"ускорение: {t_loop / t_numpy:.1f}×")
print(f"результаты совпадают: {np.allclose(r_loop, r_numpy)}")
