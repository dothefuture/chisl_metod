"""Домашнее задание: NumPy — массивы, формы, типы данных и базовые операции.

Каждая задача — отдельная функция с print. Данные генерируются в коде.
Запуск: python решение.py
"""
import numpy as np

np.set_printoptions(precision=4, suppress=True, linewidth=110)


def header(n, title):
    print("\n" + "=" * 72)
    print(f"Задача {n}. {title}")
    print("=" * 72)


# ---------------------------------------------------- Блок 1: ndarray, shape, dtype
def task1():
    header(1, "Инвентаризация массива")
    a = np.arange(60).reshape(3, 4, 5)
    print("shape:", a.shape, "ndim:", a.ndim, "size:", a.size, "dtype:", a.dtype)
    print("strides:", a.strides, "C_CONTIGUOUS:", a.flags["C_CONTIGUOUS"])
    item = a.itemsize
    print(f"Объяснение: элемент занимает {item} байт. strides = ({a.strides[0]}, {a.strides[1]}, "
          f"{a.strides[2]}) — на сколько байт сдвинуться в памяти, чтобы перейти\n"
          f"к следующему элементу по оси 0 (целый блок 4×5={20} элементов × {item} байт), по оси 1\n"
          f"(строка из 5 элементов) и по оси 2 (один элемент). size = 3·4·5 = 60 — произведение\n"
          "длин всех осей, то есть общее число элементов.")


def task2():
    header(2, "int vs float — тихая ловушка")
    a = np.array([1, 2, 3, 4])
    print("a / 2   =", a / 2, (a / 2).dtype)
    print("a // 2  =", a // 2, (a // 2).dtype)
    print("a / 2.0 =", a / 2.0)
    print("a.dtype =", a.dtype, "| a после операций:", a)
    b = np.array([1, 2, 3], dtype=np.int8)
    with np.errstate(over="ignore"):
        c = b + np.int8(127)
    print("b + 127 =", c, c.dtype)
    print("Объяснение: a / 2 создаёт НОВЫЙ массив float64, исходный a не меняется. int8 хранит\n"
          "только −128…127, поэтому 1+127=128 «переворачивается» в −128 (переполнение по\n"
          "модулю 2⁸). NumPy не проверяет переполнение для скорости — поэлементные операции\n"
          "выполняются как в C, без проверок, и ошибку не бросает.")


def task3():
    header(3, "float32 vs float64 — реальная точность")
    e32 = float(np.float32(0.1)) - 0.1
    e64 = float(np.float64(0.1)) - 0.1
    print("float32:", repr(e32), f"{e32:.20e}")
    print("float64:", repr(e64), f"{e64:.20e}")
    ratio = abs(e32) / max(abs(e64), np.finfo(float).tiny)
    print("ошибка float64 = 0, потому что np.float64(0.1) и 0.1 — одно и то же число." if e64 == 0
          else f"float32 хуже в {ratio:.2e} раз")
    print(f"Сравним с машинным ε: float32 ε = {np.finfo(np.float32).eps:.2e}, "
          f"float64 ε = {np.finfo(np.float64).eps:.2e} (разница ≈ 5.4e8 раз).")
    print("Вывод: float32 допустим, где хватает ~7 значащих цифр (графика, нейросети, данные\n"
          "датчиков). Нельзя использовать его там, где ошибка копится или есть вычитание\n"
          "близких чисел: суммы больших массивов, итерационные методы, плохо обусловленные\n"
          "системы, финансы.")


def task4():
    header(4, "Явный dtype при создании")
    arrays = {
        "zeros float64": np.zeros((2, 3), dtype=np.float64),
        "zeros float32": np.zeros((2, 3), dtype=np.float32),
        "ones int16": np.ones((2, 3), dtype=np.int16),
        "full 7 uint8": np.full((2, 3), 7, dtype=np.uint8),
    }
    for k, v in arrays.items():
        print(f"{k:14s} dtype={v.dtype}, nbytes={v.nbytes}")
    big64 = np.zeros((1000, 1000), np.float64).nbytes
    big32 = np.zeros((1000, 1000), np.float32).nbytes
    print(f"(1000,1000): float64 = {big64:,} Б, float32 = {big32:,} Б, экономия = {big64 - big32:,} Б (~3.8 МБ)")
    print("Вывод: float32 вдвое экономнее по памяти и быстрее, но точность ~7 цифр вместо ~16.\n"
          "Выбор dtype — это компромисс «память/скорость vs точность».")


# ------------------------------------------- Блок 2: reshape, ravel, flatten, .T
def task5():
    header(5, "Цепочка reshape")
    a = np.arange(24)
    cur = a
    for shape in [(4, 6), (2, 3, 4), (2, 2, 6), (24,)]:
        cur = cur.reshape(shape)
        print(f"{str(shape):10s} shape={cur.shape}, данные целы: {np.array_equal(a, cur.ravel())}, "
              f"view: {np.shares_memory(a, cur)}")
    print("Объяснение: reshape меняет только «вид» (shape и strides), а данные в памяти остаются\n"
          "те же — поэтому это view без копирования. Копировать приходится, когда новые формы\n"
          "нельзя описать strides над старым буфером, например reshape после транспонирования\n"
          "(a.T.reshape(-1)) — данные уже не лежат подряд в нужном порядке.")
    src = np.arange(6).reshape(2, 3)
    t = src.T.reshape(-1)
    print("пример копии: src.T.reshape(-1) делит память с src?", np.shares_memory(src, t),
          "→ это копия:", t)


def task6():
    header(6, "flatten vs ravel — копия или view")
    m = np.arange(12).reshape(3, 4)
    f = m.flatten()
    r = m.ravel()
    print("f.base is None:", f.base is None, "| r.base is not None:", r.base is not None)
    f[0] = 999
    print("после f[0]=999, M[0,0] =", m[0, 0], "(не изменился)")
    r[1] = 888
    print("после r[1]=888, M[0,1] =", m[0, 1], "(изменился!)")
    print("Вывод: flatten всегда делает копию — её безопасно менять. ravel возвращает view,\n"
          "когда может (быстро, без памяти), но изменения попадают в исходник. ravel — для\n"
          "чтения, flatten — когда нужна независимая копия.")


def task7():
    header(7, "newaxis, squeeze, транспонирование")
    v = np.arange(5)
    print("v[:, None].shape =", v[:, None].shape, "— добавили ось: столбец 5×1")
    print("v[None, :].shape =", v[None, :].shape, "— добавили ось спереди: строка 1×5")
    print("squeeze(v[:, None]).shape =", np.squeeze(v[:, None]).shape, "— убрали оси длины 1")
    t = np.arange(6).reshape(2, 3).T
    print("arange(6).reshape(2,3).T, shape =", t.shape, "— строки стали столбцами:\n", t)
    s = v[:, None] + v[None, :]
    print("v[:, None] + v[None, :], shape =", s.shape, "— таблица сложения (i+j):\n", s)
    print("v[:, None] * v[None, :] — таблица умножения:\n", v[:, None] * v[None, :])


def task8():
    header(8, "Транспонирование без копии")
    a = np.arange(6).reshape(2, 3)
    b = a.T
    print("B.base is A:", b.base is a, "(base у обоих — исходный arange) | B.base is not None:",
          b.base is not None, "| общая память:", np.shares_memory(a, b))
    b[0, 1] = 999
    print("после B[0,1]=999 A =\n", a)
    print("A.strides =", a.strides, " B.strides =", b.strides)
    print("Вывод: .T не копирует данные, а меняет местами strides — тот же буфер читается\n"
          "«по столбцам». Поэтому изменение B меняет A (элемент A[1,0]).")


# ------------------------------------------------- Блок 3: операции, axis
def task9():
    header(9, "Поэлементно vs матричное")
    a = np.arange(6).reshape(2, 3)
    b = np.arange(6).reshape(3, 2)
    print("A @ B, shape", (a @ b).shape, "\n", a @ b)
    print("A.T @ B.T, shape", (a.T @ b.T).shape, "\n", a.T @ b.T)
    print("A * A, shape", (a * a).shape, "\n", a * a)
    try:
        a * b
    except ValueError as exc:
        print("A * B → ValueError:", exc)
    d = np.diag([2, 3])
    print("Для диагональных D: D*D == D@D:", np.array_equal(d * d, d @ d))
    print("Разница: * — поэлементное умножение (формы должны совпадать или транслироваться),\n"
          "@ — матричное (строка на столбец, внутренние размеры должны совпадать). A(2×3)*B(3×2)\n"
          "не транслируются, поэтому ошибка. Для диагональных матриц оба дают одно и то же.")


def task10():
    header(10, "axis=0 vs axis=1")
    m = np.arange(12).reshape(3, 4)
    print("M =\n", m)
    print("sum(axis=0) =", m.sum(axis=0), "— свернули ось строк: сумма каждого столбца")
    print("sum(axis=1) =", m.sum(axis=1), "— свернули ось столбцов: сумма каждой строки")
    print("mean(axis=0) =", m.mean(axis=0), "— среднее по столбцам")
    print("mean(axis=1) =", m.mean(axis=1), "— среднее по строкам")
    print("argmax(axis=0) =", m.argmax(axis=0), "— номер строки с максимумом в каждом столбце")
    print("argmax(axis=1) =", m.argmax(axis=1), "— номер столбца с максимумом в каждой строке")
    small = np.array([[1, 2], [10, 20]])
    print("Проверка на [[1,2],[10,20]]: sum(axis=0) =", small.sum(axis=0),
          "= [1+10, 2+20] → это суммы столбцов.")


def task11():
    header(11, "keepdims и broadcasting")
    x = np.random.default_rng(42).normal(size=(5, 3))
    m0, m0k = x.mean(axis=0), x.mean(axis=0, keepdims=True)
    print("mean(axis=0).shape =", m0.shape, "| keepdims:", m0k.shape)
    print("(X - m0).shape =", (x - m0).shape, "| (X - m0k).shape =", (x - m0k).shape)
    print("std(axis=1).shape =", x.std(axis=1).shape, "| keepdims:", x.std(axis=1, keepdims=True).shape)
    try:
        x - x.mean(axis=1)
    except ValueError as exc:
        print("X - X.mean(axis=1) без keepdims → ValueError:", exc)
    z = (x - x.mean(axis=1, keepdims=True)) / x.std(axis=1, keepdims=True)
    print("средние по строкам ≈ 0:", np.allclose(z.mean(axis=1), 0))
    print("std по строкам ≈ 1:", np.allclose(z.std(axis=1), 1))
    print("Зачем keepdims: результат (5,1) правильно транслируется вдоль строк. Без него\n"
          "получается (5,), что выравнивается по последней оси (3) — формы не совпадают\n"
          "(ошибка) или, хуже, совпадают случайно и дают неверный результат.")


# --------------------------------------------- Блок 4: индексация, broadcasting
def task12():
    header(12, "Срез — view, не копия")
    a = np.arange(10)
    b = a[2:5]
    b[0] = 999
    print("после b[0]=999 через срез: a =", a)
    a = np.arange(10)
    c = a[2:5].copy()
    c[0] = 999
    print("после c[0]=999 через copy: a =", a)
    print("Почему важно: если «вырезать» кусок данных для анализа и, например, нормировать\n"
          "его на месте, испортится исходный массив, и следующий эксперимент пойдёт на\n"
          "искажённых данных. View — преимущество при работе с огромными массивами (окна,\n"
          "строки матрицы без копирования памяти) и баг, когда кусок меняют, думая, что это копия.")


def task13():
    header(13, "Булева маска и fancy indexing")
    a = np.random.default_rng(0).normal(size=20)
    print("a > 0:", a[a > 0].size, "элементов")
    print("(-1 < a < 1):", a[(a > -1) & (a < 1)].size, "элементов")
    print("a[[0,5,10,15]] =", a[[0, 5, 10, 15]], "— выборка по списку индексов (каждый 5-й)")
    print("|a| > 2 (выбросы):", a[np.abs(a) > 2])
    a[a < 0] = 0
    print("после a[a<0]=0:", a)
    print("Объяснение: & связывает сильнее, чем > и <, поэтому a > 0 & (a < 1) читается как\n"
          "a > (0 & (a < 1)) — побитовое И числа с массивом bool, получается бессмыслица или\n"
          "ошибка. Скобки (a > 0) & (a < 1) сначала строят две маски, затем объединяют их.")


def task14():
    header(14, "Broadcasting в реальной задаче")
    x = np.random.default_rng(1).normal(size=(100, 3))
    xn = (x - x.mean(axis=0)) / x.std(axis=0)
    print("mean ≈ 0:", np.allclose(xn.mean(axis=0), 0), "| std ≈ 1:", np.allclose(xn.std(axis=0), 1))
    d = np.sqrt(((xn[:, None, :] - xn[None, :, :]) ** 2).sum(axis=-1))
    print("D.shape =", d.shape, "| диагональ ≈ 0:", np.allclose(np.diag(d), 0),
          "| симметрична:", np.allclose(d, d.T))
    print("Трюк: xn[:, None, :] (100,1,3) − xn[None, :, :] (1,100,3) → (100,100,3) — все пары\n"
          "строк сразу, затем сумма квадратов по оси признаков и корень.")


def task15():
    header(15, "Полный кейс: данные → выборка → reshape → агрегация → нормировка")
    rng = np.random.default_rng(42)
    raw = rng.normal(loc=20, scale=2, size=(30, 4))
    raw[7, 2] = 100
    print("1) shape:", raw.shape, "dtype:", raw.dtype, "size:", raw.size)
    mask = np.abs(raw - raw.mean(axis=0)) > 3 * raw.std(axis=0)
    print("2) выбросов:", mask.sum(), "на позициях", np.argwhere(mask).tolist())
    clean = raw.copy()
    clean[mask] = np.nan
    col_mean = np.nanmean(clean, axis=0)
    clean = np.where(np.isnan(clean), col_mean, clean)
    print("3) значение [7,2] после замены:", round(clean[7, 2], 4), "(среднее столбца без выброса)")
    print("4) .T → .T без изменений:", np.array_equal(clean, clean.T.T))
    flat = clean.ravel()
    print("5) ravel →", flat.shape, "→ reshape(30,4), равны:", np.array_equal(clean, flat.reshape(30, 4)))
    mu, sd = clean.mean(axis=0), clean.std(axis=0)
    print("6) средние по датчикам:", mu, "\n   std по датчикам:", sd)
    norm = (clean - mu) / sd
    print("7) после нормировки: средние ≈ 0:", np.allclose(norm.mean(axis=0), 0),
          "| std ≈ 1:", np.allclose(norm.std(axis=0), 1))
    print("Вывод: copy() понадобился перед заменой выбросов, чтобы не портить исходный raw\n"
          "(присваивание по маске меняет массив на месте). Broadcasting сработал при сравнении\n"
          "(30,4) с (4,) в поиске выбросов, в np.where со средними столбцов и при нормировке.\n"
          "Ошибка формы могла возникнуть, если взять mean(axis=1) — форма (30,) не\n"
          "транслируется к (30,4) без keepdims. .T и ravel/reshape данных не меняют.")


if __name__ == "__main__":
    for fn in (task1, task2, task3, task4, task5, task6, task7, task8, task9, task10,
               task11, task12, task13, task14, task15):
        fn()
    print("\nБонус (задача 16) не выполнялся — он необязательный и требует найти чужой код.")
