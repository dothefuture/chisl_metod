import math
import time
import numpy as np

rng = np.random.default_rng(42)
a = rng.normal(size=1_000_000)


def loop_mean_std(arr):
    s = 0.0
    s2 = 0.0
    for x in arr:
        s += x
        s2 += x * x
    mean = s / len(arr)
    std = math.sqrt(s2 / len(arr) - mean * mean)
    return mean, std


def numpy_mean_std(arr):
    return arr.mean(), arr.std()


def measure(fn, x, repeat=3):
    best = float("inf")
    result = None
    for _ in range(repeat):
        t0 = time.perf_counter()
        result = fn(x)
        t1 = time.perf_counter()
        best = min(best, t1 - t0)
    return result, best


r_loop,  t_loop  = measure(loop_mean_std,  a)
r_numpy, t_numpy = measure(numpy_mean_std, a)

print(f"цикл:   {t_loop*1000:10.2f} мс")
print(f"NumPy:  {t_numpy*1000:10.2f} мс")
print(f"ускорение: {t_loop / t_numpy:.1f}×")
print(f"результаты совпадают: {np.allclose(r_loop, r_numpy)}")
print(f"совпадают до 1e-12: {np.allclose(r_loop, r_numpy, rtol=0, atol=1e-12)}")
