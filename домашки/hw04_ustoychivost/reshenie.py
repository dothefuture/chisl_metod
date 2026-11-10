"""Домашнее задание: устойчивость алгоритма и корректная постановка эксперимента.

Каждая задача — отдельная функция. Таблицы печатаются, графики сохраняются в PNG
рядом со скриптом. Эталон везде — mpmath с 50 знаками.
Запуск: python решение.py   (нужны numpy, matplotlib, mpmath)
"""
import math
import platform
import random

import matplotlib
import mpmath
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

mpmath.mp.dps = 50
EPS = np.finfo(float).eps


def header(n, title):
    print("\n" + "=" * 72)
    print(f"Задача {n}. {title}")
    print("=" * 72)


def rel(x, ref):
    ref = mpmath.mpf(ref)
    if ref == 0:
        return float("inf") if x != 0 else 0.0
    return float(abs((mpmath.mpf(x) - ref) / ref))


def save_loglog(xs, series, xlabel, title, fname):
    plt.figure(figsize=(7, 4.5))
    for label, ys in series.items():
        plt.loglog(xs, [max(y, 1e-18) for y in ys], "o-", label=label)
    plt.xlabel(xlabel)
    plt.ylabel("относительная ошибка")
    plt.title(title)
    plt.grid(True, which="both", alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(fname, dpi=120)
    plt.close()
    print(f"график: {fname}")


# ------------------------------------------------------- Блок 1: обусловленность
def task1():
    header(1, "Число обусловленности вручную")
    cases = [
        ("√x, x=1e-8", "1/2 (для любого x>0)", 0.5),
        ("ln x, x=1.001", "1/ln x ≈ 1000.5", 1 / math.log(1.001)),
        ("x−1, x=1.000001", "x/(x−1) ≈ 1e6", 1.000001 / 1e-6),
        ("sin x, x=π/2", "x·cos x / sin x = 0", 0.0),
    ]
    for name, formula, val in cases:
        print(f"{name:18s} cond = {formula:22s} ≈ {val:.4g}")
    print("По возрастанию: sin x (0) < √x (0.5) < ln x (~1e3) < x−1 (~1e6).\n"
          "Хорошо обусловлены sin x и √x, плохо — ln x возле 1 и x−1 возле 1.\n"
          "Самая опасная x−1 при x≈1: относительная ошибка входа усиливается в миллион раз\n"
          "(это и есть вычитание близких чисел).")


def task2():
    header(2, "Вычитание близких чисел")
    print("f(a,b)=a−b: cond_a = |a/(a−b)|, cond_b = |b/(a−b)| → ∞ при a→b.")
    a, b, da = 1 + 1e-8, 1.0, 1e-9
    cond_a = abs(a / (a - b))
    f0, f1 = a - b, (a + da) - b
    rel_in = da / a
    rel_out = abs(f1 - f0) / abs(f0)
    print(f"cond_a = {cond_a:.4g}")
    print(f"δ входа = {rel_in:.3e}, δ выхода = {rel_out:.3e}, отношение = {rel_out / rel_in:.4g}")
    print("Вывод: фактическое усиление ≈ 1e8, как и предсказывает cond. Малое изменение a\n"
          "даёт относительно огромное изменение разности: задача плохо обусловлена сама по\n"
          "себе, ни один алгоритм это не исправит.")


def task3():
    header(3, "Кратные корни — плохая обусловленность")
    print(f"{'ε':>8s} {'корень':>22s} {'сдвиг':>12s} {'отн. сдвигов':>14s}")
    prev = None
    for eps in (1e-2, 1e-4, 1e-6):
        # x² − 2x + (1 − ε) = 0  ⇒  x = 1 ± √ε
        disc = 4 - 4 * (1 - eps)
        root = (2 + math.sqrt(disc)) / 2
        shift = root - 1
        ratio = "" if prev is None else f"{prev / shift:.1f}"
        print(f"{eps:8.0e} {root!r:>22s} {shift:12.3e} {ratio:>14s}")
        prev = shift
    print("Вывод: возмущение ε сдвигает корень на √ε: при ε=1e-6 сдвиг 1e-3, в тысячу раз\n"
          "больше возмущения. Уменьшение ε в 100 раз уменьшает сдвиг только в 10 раз.\n"
          "Кратный корень плохо обусловлен: cond → ∞ (сдвиг ~ ε^(1/k) для кратности k).")


def task4():
    header(4, "Обусловленность vs устойчивость")
    print("Пример: f(x) = (e^x − 1)/x при малых x. Задача хорошо обусловлена\n"
          "(cond = |x·f'/f| ≈ x/2 → 0), f ≈ 1 + x/2. Неустойчивый алгоритм: (exp(x)−1)/x\n"
          "(вычитание близких). Устойчивый: expm1(x)/x.")
    print(f"{'x':>8s} {'неуст.':>22s} {'уст.':>22s} {'δ неуст.':>10s} {'δ уст.':>10s}")
    for p in range(2, 17, 2):
        x = 10.0 ** -p
        ref = mpmath.expm1(mpmath.mpf(x)) / mpmath.mpf(x)
        bad = (math.exp(x) - 1) / x
        good = math.expm1(x) / x
        print(f"{x:8.0e} {bad!r:>22s} {good!r:>22s} {rel(bad, ref):10.2e} {rel(good, ref):10.2e}")
    print("Проблема задачи: её нет, f хорошо обусловлена.\n"
          "Проблема алгоритма: exp(x)−1 вычитает близкие числа и теряет цифры; при x=1e-16\n"
          "получается 0 (ошибка 100 %). expm1 вычисляет e^x−1 напрямую и устойчив.")


# ------------------------------------------------------- Блок 2: устойчивость
def small_root_bad(b, c=1.0):
    return (-b + math.sqrt(b * b - 4 * c)) / 2


def small_root_good(b, c=1.0):
    return 2 * c / (-b - math.sqrt(b * b - 4 * c))


def small_root_ref(b, c=1):
    b = mpmath.mpf(b)
    return (-b + mpmath.sqrt(b * b - 4 * c)) / 2


def task5():
    header(5, "Квадратное уравнение — классика")
    print(f"{'b':>8s} {'ошибка плохого':>16s} {'ошибка хорошего':>16s}")
    for b in (1e4, 1e8, 1e12):
        ref = small_root_ref(b)
        print(f"{b:8.0e} {rel(small_root_bad(b), ref):16.3e} {rel(small_root_good(b), ref):16.3e}")
    print("Вывод: при b=1e4 «плохой» способ теряет ~7 цифр (δ ≈ 1e-9), при b=1e8 ошибка\n"
          "уже 25 %, при b=1e12 результат 0 (ошибка 100 %). Ошибка растёт как ε·b², то есть\n"
          "катастрофической (> 1 %) она становится примерно с b ≈ 1e7. «Хороший» способ\n"
          "точен до машинного ε при любом b.")


def task6():
    header(6, "(1 − cos x)/x² при малых x")
    xs = [1e-2, 1e-4, 1e-6, 1e-8, 1e-10]
    bad_err, good_err = [], []
    print(f"{'x':>8s} {'плохо':>14s} {'хорошо':>14s} {'δ плохо':>10s} {'δ хорошо':>10s}")
    first_over = None
    for x in xs:
        ref = (1 - mpmath.cos(mpmath.mpf(x))) / mpmath.mpf(x) ** 2
        bad = (1 - math.cos(x)) / x ** 2
        good = 2 * math.sin(x / 2) ** 2 / x ** 2
        eb, eg = rel(bad, ref), rel(good, ref)
        bad_err.append(eb)
        good_err.append(eg)
        if first_over is None and eb > 0.01:
            first_over = x
        print(f"{x:8.0e} {bad:14.8g} {good:14.8g} {eb:10.2e} {eg:10.2e}")
    print(f"Ошибка «плохого» способа впервые > 1 % при x = {first_over:g}")
    save_loglog(xs, {"1−cos x": bad_err, "2sin²(x/2)": good_err}, "x",
                "Задача 6: (1−cos x)/x²", "task6_cos.png")
    print("Правило: если формула вычитает почти равные величины (1−cos x, √(x+1)−√x,\n"
          "e^x−1), ищем тождество, которое превращает разность в произведение или сумму.")


def task7():
    header(7, "√(x+1) − √x при больших x")
    xs = [1e4, 1e8, 1e12, 1e14, 1e16]
    eb_list = []
    print(f"{'x':>8s} {'δ плохо':>10s} {'δ хорошо':>10s}")
    for x in xs:
        ref = mpmath.sqrt(mpmath.mpf(x) + 1) - mpmath.sqrt(mpmath.mpf(x))
        bad = math.sqrt(x + 1) - math.sqrt(x)
        good = 1 / (math.sqrt(x + 1) + math.sqrt(x))
        eb = rel(bad, ref)
        eb_list.append(max(eb, 1e-18))
        print(f"{x:8.0e} {eb:10.2e} {rel(good, ref):10.2e}")
    slope = np.polyfit(np.log10(xs[:4]), np.log10(eb_list[:4]), 1)[0]
    print(f"Оценка наклона log(ошибки) от log(x) по первым точкам: ≈ {slope:.2f}")
    print("Вывод: ошибка «плохого» способа растёт примерно линейно (показатель ≈ 1, δ ~ ε·x),\n"
          "а при x=1e16 результат 0 (ошибка 100 %), потому что x+1 == x в float. Домножение\n"
          "на сопряжённое убирает вычитание и даёт точность ~ε при всех x.")


def task8():
    header(8, "log(1+x) против log1p(x)")
    print(f"{'x':>8s} {'δ log(1+x)':>12s} {'δ log1p':>12s}")
    for x in (1e-2, 1e-8, 1e-12, 1e-16):
        ref = mpmath.log(1 + mpmath.mpf(x))
        print(f"{x:8.0e} {rel(math.log(1 + x), ref):12.2e} {rel(math.log1p(x), ref):12.2e}")
    print("log1p(x) вычисляет ln(1+x), не формируя сумму 1+x (в документации Python:\n"
          "«accurate for x near zero»). Сумма 1+x при малых x теряет младшие цифры x, а при\n"
          "x<ε/2 вообще становится 1, и log даёт 0. Функции log1p, expm1, hypot существуют\n"
          "именно затем, чтобы избежать сокращения и переполнения в типовых формулах.")


def task9():
    header(9, "Неустойчивость накопления в сумме")
    ns = [10 ** 5, 10 ** 6, 10 ** 7]
    errs = {"цикл": [], "sum": [], "fsum": []}
    print(f"{'n':>9s} {'δ цикл':>10s} {'δ sum':>10s} {'δ fsum':>10s}")
    for n in ns:
        ref = mpmath.harmonic(n)
        arr = [1.0 / k for k in range(1, n + 1)]
        t = 0.0
        for v in arr:
            t += v
        e = (rel(t, ref), rel(sum(arr), ref), rel(math.fsum(arr), ref))
        for k, v in zip(errs, e):
            errs[k].append(v)
        print(f"{n:9d} {e[0]:10.2e} {e[1]:10.2e} {e[2]:10.2e}")
    save_loglog(ns, errs, "n", "Задача 9: гармонический ряд", "task9_harmonic.png")
    print("Вывод: ошибка наивного цикла растёт с n (примерно ∝ n·ε в худшем случае), но\n"
          "для n ≤ 1e7 остаётся ~1e-14…1e-13 — порог 1e-10 не достигается; он будет\n"
          "превышен ориентировочно при n ~ 1e10 и больше. fsum точен при любом n.")


# ------------------------------------------- Блок 3: корректный эксперимент
def task10():
    header(10, "Разделение источников ошибки (функция из задачи 6)")

    def bad64(x):
        return (1 - math.cos(x)) / x ** 2

    def bad32(x):
        x = np.float32(x)
        return float((np.float32(1) - np.cos(x)) / (x * x))

    def good64(x):
        return 2 * math.sin(x / 2) ** 2 / x ** 2

    def ref(x):
        return (1 - mpmath.cos(mpmath.mpf(x))) / mpmath.mpf(x) ** 2

    print("(а) плохой алгоритм, меняем x:")
    for x in (1e-2, 1e-4, 1e-6):
        print(f"   x={x:g}: δ = {rel(bad64(x), ref(x)):.2e}")
    x = 1e-3
    print(f"(б) x={x:g}, float64 vs float32 (плохой алгоритм):")
    e64, e32 = rel(bad64(x), ref(x)), rel(bad32(x), ref(x))
    print(f"   float64: δ = {e64:.2e};  float32: δ = {e32:.2e}")
    print(f"(в) x={x:g}, плохой vs хороший (float64):")
    eg = rel(good64(x), ref(x))
    print(f"   плохой: δ = {e64:.2e};  хороший: δ = {eg:.2e}")
    print("Таблица влияния факторов (порядки величины):")
    print(f"   x: 1e-2 → 1e-6                  ≈ +{math.log10(rel(bad64(1e-6), ref(1e-6)) / rel(bad64(1e-2), ref(1e-2))):.0f} порядков")
    print(f"   float64 → float32 (x=1e-3)      ≈ +{math.log10(max(e32, 1e-18) / max(e64, 1e-18)):.0f} порядков")
    print(f"   плохой → хороший (x=1e-3)       ≈ −{math.log10(max(e64, 1e-18) / max(eg, 1e-18)):.0f} порядков")
    print("Вывод: в (а) доминирует сокращение при вычитании (растёт при x→0); в (б) —\n"
          "машинная точность (у float32 ε в 5e8 раз больше); в (в) смена алгоритма убирает\n"
          "сокращение и возвращает точность к уровню ε.")


def task11():
    header(11, "Эталон — обязателен")
    x = 1e-16
    a1 = math.log(1 + x)
    a2 = math.log((1 + x) * 1.0)  # другая запись того же неустойчивого вычисления
    ref = mpmath.log1p(mpmath.mpf(x))
    print(f"алгоритм 1 = {a1!r}, алгоритм 2 = {a2!r}, a1 == a2: {a1 == a2}")
    print(f"эталон mpmath = {mpmath.nstr(ref, 17)}")
    print(f"δ1 = {rel(a1, ref):.2e}, δ2 = {rel(a2, ref):.2e}")
    print("Вывод: два float-результата совпали, но оба равны 0 при точном ответе ~1e-16\n"
          "(ошибка 100 %). Совпадение двух алгоритмов с одной и той же слабостью ничего\n"
          "не доказывает, поэтому без независимого эталона сравнение float с float — ошибка.")


def task12():
    header(12, "Диапазон, а не одна точка (функция из задачи 7)")
    xs = np.logspace(2, 16, 15)
    errs = []
    for x in xs:
        ref = mpmath.sqrt(mpmath.mpf(x) + 1) - mpmath.sqrt(mpmath.mpf(x))
        errs.append(max(rel(math.sqrt(x + 1) - math.sqrt(x), ref), 1e-18))
    good = [i for i, e in enumerate(errs) if 1e-17 < e < 0.5]
    slope = np.polyfit(np.log10(xs[good]), np.log10(np.array(errs)[good]), 1)[0]
    for x, e in zip(xs, errs):
        print(f"   x={x:8.1e}  δ = {e:.2e}   (теория ε·x = {EPS * x:.1e})")
    print(f"Наклон в log-log (без точек, где δ=0 или 100 %): ≈ {slope:.2f}")
    save_loglog(xs, {"√(x+1)−√x": errs, "ε·x (теория)": list(EPS * xs)}, "x",
                "Задача 12: рост ошибки", "task12_range.png")
    print("Вывод: наклон ≈ 1, как и предсказывает оценка ε·x; сами точки лежат ниже этой\n"
          "прямой и прыгают (случайные округления), то есть ε·x — верхняя граница. По одной\n"
          "точке (например, x=1e12) можно получить и «неплохие» 7.6e-6, и не увидеть ни скорость\n"
          "роста ошибки, ни где алгоритм ломается, поэтому нужен диапазон.")


def task13():
    header(13, "Воспроизводимость эксперимента")
    print(f"Python {platform.python_version()}, numpy {np.__version__}")

    def run(seed):
        random.seed(seed)
        data_py = [random.random() for _ in range(10 ** 5)]
        rng = np.random.default_rng(seed)
        data_np = rng.random(10 ** 5)
        return (sum(data_py), math.fsum(data_py), float(np.sum(data_np)),
                math.fsum(data_np.tolist()))

    r1, r2, r3 = run(42), run(42), run(43)
    print(f"seed=42, запуск 1: sum={r1[0]!r} fsum={r1[1]!r} np.sum={r1[2]!r}")
    print(f"seed=42, запуск 2: совпадает с запуском 1: {r1 == r2}")
    print(f"seed=43: sum={r3[0]!r} fsum={r3[1]!r} np.sum={r3[2]!r}")
    for name, r in (("seed=42", r1), ("seed=43", r3)):
        print(f"   {name}: |sum−fsum| = {abs(r[0] - r[1]):.1e}, |np.sum−fsum(np)| = {abs(r[2] - r[3]):.1e}")
    print("Вывод: при одинаковом seed результаты совпадают бит в бит, при другом seed —\n"
          "другие данные и другие суммы. В этих версиях sum() (Python ≥ 3.12 суммирует с\n"
          "компенсацией) и np.sum (попарное суммирование) совпали с fsum для обоих seed:\n"
          "это систематическое свойство алгоритмов, а не случайность данных. В старых версиях\n"
          "Python sum() был наивным и давал расхождение ~1e-11, поэтому без фиксации seed и\n"
          "версий Python/numpy эксперимент нельзя повторить.")


def task14():
    header(14, "Границы представимости")
    cases = {
        "большие 1e300": [1e300, 1e300, -1e300],
        "малые 1e-300": [1e-300] * 3,
        "с нулём": [0.0, 1.0, -0.0],
        "денормализованные 1e-320": [1e-320] * 3,
        "с inf": [1.0, float("inf"), 2.0],
        "inf и −inf": [float("inf"), -float("inf")],
        "с nan": [1.0, float("nan"), 2.0],
        "переполнение 1e308+1e308": [1e308, 1e308, -1e308],
    }

    def naive(seq):
        t = 0.0
        for v in seq:
            t += v
        return t

    def safe_fsum(seq):
        try:
            return repr(math.fsum(seq))
        except (OverflowError, ValueError) as exc:
            return f"{type(exc).__name__}: {exc}"

    print(f"{'массив':28s} {'наивно':>14s}   fsum")
    for name, arr in cases.items():
        print(f"{name:28s} {naive(arr)!r:>14s}   {safe_fsum(arr)}")
    print("Выводы: nan «отравляет» оба способа (результат nan). С одним inf оба дают inf.\n"
          "inf + (−inf): наивный цикл тихо даёт nan, а fsum бросает ValueError. При\n"
          "промежуточном переполнении (1e308+1e308−1e308) наивный цикл тихо получает inf\n"
          "(верный ответ 1e308), а fsum бросает OverflowError — громко сообщает о проблеме.\n"
          "Денормализованные числа складываются, но хранятся с меньшим числом значащих бит.\n"
          "В реальном коде граничные значения проверяют заранее (math.isfinite, np.isnan)\n"
          "и обрабатывают исключения, а не надеются, что сумма «как-нибудь» посчитается.")


def task15():
    header(15, "Полный корректный эксперимент: ln(1+x), функция из задачи 8")
    print("Цель: показать, где наивный ln(1+x) неустойчив, и оценить достижимую точность.")
    print("Постановка: плохо = math.log(1+x), хорошо = math.log1p(x); эталон — mpmath.log1p\n"
          "с 50 знаками; вход x на лог-сетке 1e-1 … 1e-16 (16 точек).")
    xs = np.logspace(-1, -16, 16)
    bad_e, good_e = [], []
    print(f"{'x':>8s} {'плохой':>22s} {'хороший':>22s} {'эталон':>22s} {'δ плох':>9s} {'δ хор':>9s}")
    for x in xs:
        ref = mpmath.log1p(mpmath.mpf(float(x)))
        b, g = math.log(1 + x), math.log1p(x)
        eb, eg = rel(b, ref), rel(g, ref)
        bad_e.append(max(eb, 1e-18))
        good_e.append(max(eg, 1e-18))
        print(f"{x:8.0e} {b!r:>22s} {g!r:>22s} {mpmath.nstr(ref, 16):>22s} {eb:9.1e} {eg:9.1e}")
    save_loglog(xs, {"log(1+x)": bad_e, "log1p(x)": good_e}, "x",
                "Задача 15: ln(1+x)", "task15_log1p.png")
    print("Результаты и вывод: ошибка наивного способа ≈ ε/x — она растёт при уменьшении x;\n"
          "до x ≈ 1e-6 он даёт ~1e-10 (пригоден для грубых расчётов), при x ≈ 1e-12 — около\n"
          "1e-4, при x < 1e-16 — 100 %. Причина — округление суммы 1+x (потеря младших цифр\n"
          "x). log1p держит ошибку на уровне ε (~1e-16) во всём диапазоне: это достижимая\n"
          "точность для float64.")


if __name__ == "__main__":
    for fn in (task1, task2, task3, task4, task5, task6, task7, task8, task9,
               task10, task11, task12, task13, task14, task15):
        fn()
    print("\nБонус (задача 16) не выполнялся — он необязательный и требует найти чужой код.")
