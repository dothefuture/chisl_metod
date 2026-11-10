"""Домашнее задание: абсолютная и относительная погрешность.
Округление и накопление ошибки.

Каждая задача — отдельная функция; выводы печатаются вместе с результатами.
Запуск: python решение.py   (нужны numpy и matplotlib для задач 14 и 16)
"""
import math
import random
from decimal import Decimal, getcontext

import numpy as np

EPS = np.finfo(float).eps  # машинный эпсилон ≈ 2.22e-16


def header(n, title):
    print("\n" + "=" * 70)
    print(f"Задача {n}. {title}")
    print("=" * 70)


def abs_err(approx, exact):
    return abs(approx - exact)


# ---------------------------------------------------------------- Блок 1
def task1():
    header(1, "Ручной счёт")
    pairs = [
        ("3.14 ≈ π", 3.14, math.pi),
        ("2.718 ≈ e", 2.718, math.e),
        ("9.8 ≈ 9.81", 9.8, 9.81),
        ("0.333 ≈ 1/3", 0.333, 1 / 3),
    ]
    rows = []
    for name, x, xs in pairs:
        d = abs_err(x, xs)
        rel = d / abs(xs) * 100
        rows.append((name, d, rel))
        print(f"{name:14s}  Δx = {d:.6f}   δx = {rel:.4f} %")
    by_abs = [r[0] for r in sorted(rows, key=lambda r: r[1])]
    by_rel = [r[0] for r in sorted(rows, key=lambda r: r[2])]
    print("Порядок по Δx:", by_abs)
    print("Порядок по δx:", by_rel)
    print("Вывод: лучшее приближение — 2.718 ≈ e (и Δ, и δ минимальны). Порядки по Δx и δx\n"
          "совпадают не всегда: 0.333 имеет маленькую Δ (0.00033), но число само маленькое,\n"
          "поэтому δ = 0.1 % — хуже, чем у e. Δ зависит от масштаба числа, δ — нет.")


def task2():
    header(2, "Сравнение несопоставимых величин")
    for name, x, xs, unit in [("мост", 1247, 1250, "м"), ("болт", 9.7, 10.0, "мм")]:
        d = abs_err(x, xs)
        print(f"{name}: Δ = {d:g} {unit}, δ = {d / xs * 100:.2f} %")
    print("Вывод: по абсолютной ошибке «сильнее» ошибся мост (3 м против 0.3 мм), по\n"
          "относительной — болт (3 % против 0.24 %). Величины разной размерности и масштаба\n"
          "корректно сравнивать только по относительной погрешности, поэтому ошибся сильнее\n"
          "тот, кто мерил болт.")


def relative_error(approx, exact):
    """Относительная погрешность; при exact == 0 возвращает inf вместо исключения."""
    if exact == 0:
        return float("inf")
    return abs(approx - exact) / abs(exact)


def task3():
    header(3, "Функция relative_error")
    for x, xs in [(3.14, math.pi), (2.718, math.e), (9.8, 9.81), (0.333, 1 / 3)]:
        print(f"relative_error({x}, {xs:.6f}) = {relative_error(x, xs):.6e}")
    print("relative_error(1, 0) =", relative_error(1, 0), "(без ZeroDivisionError)")


def task4():
    header(4, "Обратная задача — оценка точного значения")
    x, rel = 47.3, 0.001
    # |x - x*| <= rel * |x*|  =>  x/(1+rel) <= x* <= x/(1-rel)
    lo, hi = x / (1 + rel), x / (1 - rel)
    print(f"x* ∈ [{lo:.4f}; {hi:.4f}]  ≈ [47.25; 47.35]")
    print("Пояснение: δ ≤ 0.1 % означает |x − x*| ≤ 0.001·|x*|; отсюда x/(1.001) ≤ x* ≤ x/(0.999).\n"
          "Упрощённо Δ ≈ 0.001·47.3 = 0.0473, интервал 47.3 ± 0.047.")


def task5():
    header(5, "Порог по абсолютной и относительной ошибке")
    t_lim = 0.3 / 0.005
    print(f"|T|·0.005 ≤ 0.3  ⇒  |T| ≤ {t_lim:g} °C")
    for t in (10, 60, 100, -40):
        print(f"T = {t:4d} °C: A → Δ ≤ 0.3, B → Δ ≤ {abs(t) * 0.005:.2f}")
    print("Вывод: датчик B точнее при |T| < 60 °C (на границе они равны), A — при |T| > 60 °C.\n"
          "У B ошибка растёт пропорционально измеряемой величине, у A постоянна, поэтому выбор\n"
          "датчика зависит от рабочего диапазона температур.")


# ---------------------------------------------------------------- Блок 2
def task6():
    header(6, "Подсчёт значащих цифр")
    data = [
        ("0.004520", 4, "4.520e-3"),
        ("1200", "2–4 (неоднозначно)", "1.2e3 / 1.20e3 / 1.200e3"),
        ("1.200", 4, "1.200e0"),
        ("10.03", 4, "1.003e1"),
        ("0.03050", 4, "3.050e-2"),
        ("250000", "2–6 (неоднозначно)", "2.5e5 … 2.50000e5"),
    ]
    for num, n, sci in data:
        print(f"{num:>9s}: значащих = {n}, экспоненциально: {sci}")
    print("Вывод: неоднозначны целые числа с нулями на конце (1200, 250000): по записи\n"
          "нельзя понять, измерены эти нули или просто держат разряд. Экспоненциальная\n"
          "форма явно показывает, сколько цифр значимо. Ведущие нули (0.004520) значащими\n"
          "не являются никогда.")


def task7():
    header(7, "Честная запись результата")
    print("x = 4.74 ± 0.02  (3 значащие цифры)")
    print("Погрешность 0.02 — в разряде сотых, значит последняя верная цифра тоже в сотых.\n"
          "Запись 4.738291 ± 0.02 неверна: цифры 8291 лежат далеко за пределами точности и\n"
          "создают ложное впечатление точности до миллионных.")


def task8():
    header(8, "Округление и banker's rounding")
    vals = [0.5, 1.5, 2.5, 3.5, -0.5, -1.5, -2.5]
    print("round:", [round(v) for v in vals])
    print("Python округляет .5 к ближайшему ЧЁТНОМУ (banker's rounding, IEEE 754),\n"
          "чтобы половины уходили вверх и вниз поровну и не копили смещение.")
    rng = random.Random(42)
    n = 10 ** 6
    nums = [rng.randrange(10) + 0.5 for _ in range(n)]
    exact = math.fsum(nums)
    up = sum(math.floor(v + 0.5) for v in nums)
    bank = sum(round(v) for v in nums)
    print(f"точная сумма   = {exact:.1f}")
    print(f"«вверх»        = {up}   сдвиг = {up - exact:+.1f}  (≈ +0.5 на каждое число)")
    print(f"banker's       = {bank}   сдвиг = {bank - exact:+.1f}")
    print("Вывод: «всегда вверх» даёт систематический сдвиг +0.5·N = +500 000 на 10⁶ чисел,\n"
          "banker's — сдвиг около нуля. В финансах миллионы операций округления, и такой\n"
          "систематический сдвиг превращается в реальные деньги.")


def task9():
    header(9, "Промежуточное округление — зло")
    ref = math.fsum(1 / k for k in range(1, 101))
    s_a = 0.0
    for k in range(1, 101):
        s_a += 1 / k
    s_b = sum(round(1 / k, 3) for k in range(1, 101))
    da, db = abs(s_a - ref), abs(s_b - ref)
    print(f"эталон fsum = {ref!r}")
    print(f"(а) float       = {s_a!r}  ΔS = {da:.3e}  δS = {da / ref:.3e}")
    print(f"(б) round(·,3)  = {s_b!r}  ΔS = {db:.3e}  δS = {db / ref:.3e}")
    if da == 0:
        print(f"сумма (а) совпала с эталоном до последнего бита; ошибка (б) больше\n"
              f"даже половины шага сетки float (ε·S/2 = {EPS * ref / 2:.1e}) в "
              f"{db / (EPS * ref / 2):.1e} раз")
    else:
        print(f"ошибка (б) больше в {db / da:.2e} раз")
    print("Правило: округлять нужно только окончательный результат; промежуточные значения\n"
          "держим с полной точностью, иначе ошибки округления каждого слагаемого копятся.")


# ---------------------------------------------------------------- Блок 3
def task10():
    header(10, "Классика 0.1 + 0.2")
    s = 0.1 + 0.2
    print(f"0.1 + 0.2 = {s!r}")
    print("== 0.3 :", s == 0.3, "| isclose:", math.isclose(s, 0.3))
    d = abs(s - 0.3)
    print(f"Δ = {d:.3e}, δ = {d / 0.3:.3e}")
    print("На пальцах: компьютер хранит числа в двоичной системе. 1/10 в двоичной системе —\n"
          "бесконечная периодическая дробь (как 1/3 = 0.333… в десятичной), и её приходится\n"
          "обрезать. Поэтому 0.1 и 0.2 хранятся чуть неточно, и эти крошки дают 0.30000000000000004.")


def task11():
    header(11, "Катастрофическая потеря точности")
    a, b = 1 + 1e-15, 1.0
    r = a - b
    print(f"a − b = {r!r}, ожидали 1e-15, δ = {relative_error(r, 1e-15):.3%}")
    qa, qb, qc = 1.0, 1e8, 1.0
    disc = math.sqrt(qb * qb - 4 * qa * qc)
    bad = (-qb + disc) / (2 * qa)
    good = (2 * qc) / (-qb - disc)
    import mpmath
    mpmath.mp.dps = 50
    ref = float((-mpmath.mpf(qb) + mpmath.sqrt(mpmath.mpf(qb) ** 2 - 4)) / 2)
    print(f"меньший корень «в лоб»   = {bad!r}   δ = {abs((bad - ref) / ref):.2e}")
    print(f"меньший корень устойчиво = {good!r}  δ = {abs((good - ref) / ref):.2e}")
    print(f"эталон mpmath            = {ref!r}")
    print("Вывод: вычитание близких чисел (−b + √D при b ≫ c) уничтожает значащие цифры.\n"
          "Формула x₂ = 2c / (−b − √D) складывает числа одного знака и даёт точный ответ.")


def task12():
    header(12, "Накопление в цикле — сравнение стратегий")
    arr = [0.1] * 1_000_000
    ref = 1e5
    total = 0.0
    for x in arr:
        total += x
    res = {"цикл": total, "sum()": sum(arr), "math.fsum": math.fsum(arr)}
    print(f"{'способ':10s} {'результат':>22s} {'Δ':>11s} {'δ':>11s}")
    for k, v in res.items():
        d = abs(v - ref)
        print(f"{k:10s} {v!r:>22s} {d:11.3e} {d / ref:11.3e}")
    print("Вывод: наивный цикл копит ошибку (~1e-6). sum() в Python ≥ 3.12 использует\n"
          "компенсированное суммирование и почти точен, а fsum возвращает правильно\n"
          "округлённую сумму. fsum точнее цикла на много порядков.")


def task13():
    header(13, "Суммирование в правильном порядке")
    small = [1e-10] * 500_000
    big = [1e6] * 500_000
    ref = math.fsum(small + big)

    def naive(seq):
        t = 0.0
        for x in seq:
            t += x
        return t

    a = naive(small + big)
    b = naive(big + small)
    print(f"эталон fsum          = {ref!r}")
    print(f"(а) малые → большие  = {a!r}  Δ = {abs(a - ref):.3e}")
    print(f"(б) большие → малые  = {b!r}  Δ = {abs(b - ref):.3e}")
    print("Вывод: когда к сумме ~5e11 прибавляют 1e-10, слагаемое меньше половины шага сетки\n"
          "float и просто теряется. Если сначала сложить маленькие, они успевают накопиться\n"
          "(5e-5) и не теряются. Правило: суммировать от малых к большим, а лучше fsum.")


def task14(show_plot=True):
    header(14, "Детектор накопления погрешности")
    ref_final = math.exp(10000 * math.log(1.0001))
    x = 1.0
    thresholds = {1e-9: None, 1e-6: None, 1e-3: None}
    rels = []
    for i in range(1, 10_001):
        x *= 1.0001
        exact_i = math.exp(i * math.log1p(0.0001))
        rel = abs(x - exact_i) / exact_i
        rels.append(rel)
        for th in thresholds:
            if thresholds[th] is None and rel > th:
                thresholds[th] = i
    print(f"итерационно: {x!r}, эталон: {ref_final!r}, δ = {abs(x - ref_final) / ref_final:.3e}")
    for th, step in thresholds.items():
        print(f"δ > {th:g}: {'не превышена за 10 000 шагов' if step is None else f'на шаге {step}'}")
    print("Вывод: при умножении относительная ошибка каждого шага (~ε/2) складывается, и\n"
          "δ растёт с числом шагов (в худшем случае ~n·ε, в среднем медленнее, ~√n·ε).\n"
          "За 10⁴ шагов она доходит лишь до ~1e-14, поэтому пороги 1e-9 и выше не\n"
          "достигаются. Но в процессах с миллиардами шагов (симуляции, сложные проценты)\n"
          "ошибка становится заметной.")
    if show_plot:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        plt.figure(figsize=(7, 4))
        plt.semilogy(range(1, 10_001), [max(r, 1e-18) for r in rels])
        plt.xlabel("номер шага")
        plt.ylabel("δx")
        plt.title("Рост относительной погрешности x *= 1.0001")
        plt.grid(True, which="both", alpha=0.3)
        plt.tight_layout()
        plt.savefig("task14_delta.png", dpi=120)
        print("график сохранён: task14_delta.png")


def task15():
    header(15, "Финансы: float vs Decimal")
    n = 10 ** 6
    f = 0.0
    for _ in range(n):
        f += 0.01
    getcontext().prec = 28
    d = Decimal("0")
    step = Decimal("0.01")
    for _ in range(n):
        d += step
    kop = 0
    for _ in range(n):
        kop += 1
    exact = Decimal(10000)
    print(f"float   = {f!r}   расхождение = {abs(Decimal(repr(f)) - exact)} руб "
          f"({abs(f - 10000) / 10000 * 100:.2e} %)")
    print(f"Decimal = {d}   расхождение = {abs(d - exact)} руб")
    print(f"int коп = {kop} коп = {kop // 100}.{kop % 100:02d} руб, расхождение 0")
    print("Вывод: «правильный» результат с точки зрения бухгалтерии — ровно 10 000.00 руб,\n"
          "его дают Decimal и учёт в целых копейках. float не может точно хранить 0.01,\n"
          "поэтому сумма уже не равна 10000 ровно: проверка == 10000 не пройдёт, а при\n"
          "миллиардах операций и больших суммах расхождение дорастает до копеек.\n"
          "Поэтому деньги хранят в Decimal или в целых копейках (int).")


def task16():
    header(16, "Бонус: мини-исследование среднего")
    rng = np.random.default_rng(42)
    data = rng.random(10 ** 5)
    lst = data.tolist()
    t = 0.0
    for v in lst:
        t += v
    n = len(lst)
    means = {
        "цикл": t / n,
        "sum": sum(lst) / n,
        "fsum": math.fsum(lst) / n,
        "numpy.mean": float(np.mean(data)),
    }
    ref = means["fsum"]
    for k, v in means.items():
        print(f"{k:10s} = {v!r:22s} отличие от fsum = {(v - ref) / EPS:+.1f} ε")
    print("Вывод: fsum даёт правильно округлённую сумму и служит эталоном. numpy.mean\n"
          "использует попарное (pairwise) суммирование: ошибка растёт как log n, поэтому\n"
          "отличие в пределах нескольких ε, но в общем случае равенство с fsum не гарантировано.")


if __name__ == "__main__":
    for fn in (task1, task2, task3, task4, task5, task6, task7, task8, task9,
               task10, task11, task12, task13, task14, task15, task16):
        fn()
