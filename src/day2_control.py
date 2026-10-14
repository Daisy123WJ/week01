import sys

# 重点提醒：今天最值钱的是第2接（推导式）和第3节的"默认值参数陷阱"
##集合推到 注意点，当为{}出现的数组时，会自动去重 当为[] 出现时，【不会去重】
# -陷阱：默认值只在"定义时"求值一次，所以可以变默参数会被共享

_result = {"pass": 0, "fail": 0, "fail_names": []}


def check(name: str, cond: bool, hint: str = "") -> None:
    if cond:
        _result["pass"] += 1
        print(f"[OK]{name}" + "\n")
    else:
        _result["fail"] += 1
        _result["fail_names"].append(name)
        print(f"[FALT]{name}<{hint}" + "\n")


def section(title: str) -> None:
    print("\n" + "=" * 68)
    print(title)
    print("=" * 68)


def summary_1() -> None:
    section("1.控流程")
    score = 76
    if score >= 90:
        level = "A"
    elif score >= 75:
        level = "B"
    elif score >= 60:
        level = "C"
    else:
        level = "D"
    print(f"score={score}->level={level}")
    # 三目表达式
    result_text = "及格" if score >= 60 else "不及格"
    print(f"三元表达式：->{result_text}")

    # for=foreach (python 没有C#那种for(int i=0；i<n;i++)  用range代替)
    print("range(3) ->", list(range(3)))  # [0,1,2]左闭右开
    print("range(2,6) ->", list(range(2, 6)))
    print("range(0,10,3) ->", list(range(0, 10, 3)))  # 步长 输出结果：0，3，6，9

    # enumerate:遍历集合，要下标又要值 (C#得自己写)
    cities = ["西安", "成都", "杭州"]
    for i, city in enumerate(cities, start=1):
        print(f"{i}.{city}")

    # zip : 并行遍历两个列表(C#要用Zip)
    names = ["张三", "李四", "王五"]
    amounts = [1200, 3400, 900]
    for n, a in zip(names, amounts):
        print(f"{n}:{a}元")

    # while+break/continue
    n, total = 1, 0
    while True:
        # print(f"n1:{n},total1:{total}")
        total += n
        n += 1
        # print(f"n2:{n},total2:{total}")
        if total > 20:
            break
    print(f"while+break->累加到{total}(n={n})")

    print(f"for-else 找第一个偶数 ->{find_first_even([3,5,8,9])}")

    check("elif 分支正确", level == "B")
    check("三元表达式正确", result_text == "及格")
    # 通过enumrate()可以遍历数组，同时获得小标与集合内容
    check("enumrate下标从1开始", [i for i, _ in enumerate(cities, 1)] == [1, 2, 3])
    # 先用zip()进行打包，再使用dict()将zip转换成字典
    check("zip配对正确", dict(zip(names, amounts))["李四"] == 3400)
    check("while+break正确退出", total == 21)

    # for-else 循环


def find_first_even(numbers):
    for v in numbers:
        if v % 2 == 0:
            return v
        else:
            return None


def summary_2() -> None:
    section("2.推导式(替换你80%的foreach+list.add)")
    numbers = [1, 2, 3, 4, 5, 6]
    # 基础：[c#] numbers.Where(x=>x>3).ToList()
    big = [x for x in numbers if x > 3]
    print(f"1.[x for x in numbers if x>3]-->{big}" + "\n")

    # 变换+过滤：[C#]numbers.Where(...).Select(x=>x*x).ToList()
    sq = [x * x for x in numbers if x % 2 == 0]
    print(f"2.x*x for x in numbers if x%2==0--->{sq}\n")

    # 字典推到：[c#]ToDictionary(x=>x,x=>x*x)
    sq_map = {x: x * x for x in range(1, 5)}
    print(f"3.字典推导-》{sq_map}\n")

    # 集合推到 注意点，当为{}出现的数组时，会自动去重
    words = ["apple", "Avocado", "banana", "Blueberry"]
    initials1 = [w[0].lower() for w in words]
    print(f"4.1 集合推导(首字母)，List形式，不会去重->{initials1}\n")
    initials = {w[0].lower() for w in words}
    print(f"4.2 集合推导(首字母)，数组形式，会去重->{initials}\n")

    # 生成器表达式：把[]换成(),不占内存(数据量大时用它)
    gen_total = sum(x * x for x in range(1, 101))
    print(f"5.生成器表达式sum(x*x for x in range(1,101))->{gen_total}\n")

    # 嵌套推导：将二维矩阵转换成一维列表
    matrix = [[1, 2], [3, 4], [5, 6]]
    # 注意这是两个for 循环，从左向右，先循环matrix ,得出row,然后在循环Row 得出v
    flat = [v for row in matrix for v in row]
    print(f"6.嵌套推导:将二维数组转换成一维：-->{flat}\n")

    # 实战：把“分组求和” 用推导式一次写完（C# 要GroupBy+Sum）
    orders = [
        {"city": "西安", "amount": 1200},
        {"city": "成都", "amount": 800},
        {"city": "西安", "amount": 500},
    ]
    cities_u = sorted({o["city"] for o in orders})
    print(f"7.去重+排序->{cities_u}\n")
    # 阅读口诀(对付多层推导式) 推导式，从最右侧的for开始读，从右往左看循环，左边是最终要生成的内容
    # 若c的城市，在订单o中没有信息，则sum()返回0，不会报错
    group_sum = {
        c: sum(o["amount"] for o in orders if o["city"] == c) for c in cities_u
    }
    print(f"8.分组求和->{group_sum}" + "\n")

    check("带条件筛选正确", big == [4, 5, 6])
    check("变换+过滤正确", sq == [4, 16, 36])
    check("字典推导正确", sq_map == {1: 1, 2: 4, 3: 9, 4: 16})
    check("集合推导正确", initials == {"a", "b"})
    check("生成器求和正确", gen_total == 338350)
    check("嵌套推导拍平正确", flat == [1, 2, 3, 4, 5, 6])
    check("推导式分组求和正确", group_sum == {"成都": 800, "西安": 1700})


def summary_3() -> None:
    section("3.函数进阶")
    print(f"默认参数：->{greet('张三')}" + "\n")
    print(f"bad_appdend('a'):->{bad_appdend('a')}" + "\n")
    print(f"bad_appdend('b'):->{bad_appdend('b')} <- 上次的'a'还在，这就是坑 " + "\n")
    print(
        f"good_append('a'):->{good_append('a')}/good_append('b'):->{good_append('b')}"
        + "\n"
    )
    print(f"*args/**kwargs->{log(1,2)}" + "\n")
    q, r = divmod_custom(17, 5)
    print(f"多返回值(其实是tuple)->q={q},r={r}" + "\n")
    print(f"keyword-only-->{transfer('A',to_acc='B',amount=100)}")
    items = [{"n": "A", "v": 30}, {"n": "B", "v": 10}, {"n": "C", "v": 20}]
    by_v = sorted(items, key=lambda d: d["v"])
    print(f"sorted(key==lambda)-->{[d['n'] for d in by_v]}")
    check("默认参数生效", greet("张三") == "你好,张三")
    check("可变默认参数陷阱现象确认", bad_appdend("c") == ["a", "b", "c"])
    check("正确书写不共享", good_append("b") == ["b"])
    check("*args/**kwargs正常", log(1, 2) == "args=(1, 2) kwargs={}")
    check("多返回值解构正确", (q, r) == (3, 2))
    check("key排序正确", [d["n"] for d in by_v] == ["B", "C", "A"])


# --默认参数：写法像C#,但语义完全不同
def greet(name: str = "星星", prefix: str = "你好") -> str:
    return f"{prefix},{name}"


# ---陷阱：默认值只在"定义时"求值一次，所以可以变默参数会被共享
def bad_appdend(item, bucket=[]):  # 不要这样写
    bucket.append(item)
    return bucket


def good_append(item, bucket=None):  # 正确写法
    if bucket is None:
        bucket = []
    bucket.append(item)
    return bucket


# -----*args/**kwargs:不定参数
# 该函数意思是：接受任意数量，任意类型的参数，把位置参数和关键字参数打包，拼成字符串返回
# *args=C# `params object[] args` 可变参数数组
# **kwargs` 在 C# 没有原生对应，近似 `Dictionary<string,object>` 动态键值对
def log(*args, **kwargs):
    return f"args={args} kwargs={kwargs}"


# ----多返回值，本质是tuple(c# 用out或ValueTuple)
def divmod_custom(a: int, b: int):
    return a // b, a % b


# ---关键字参数强制传名（* 之后必须写参数名，防止调用方搞错顺序
def transfer(from_acc, *, to_acc, amount):
    return f"{from_acc}-->{to_acc}:{amount}"


def summary_4():
    section("4.异常处理")
    parse_int()
    print(f"parse_ratio('8','2')->{parse_ratio('8','2')}")
    print(f"parse_ratio('8','0')->{parse_ratio('8','0')}")
    print(f"parse_ratio('x','2')->{parse_ratio('x','2')}")
    try:
        mark_report([1])
    except NotEnoughDataError as e:
        print(
            f"自定义异常被捕获 ->{e}(类型链:{type(e).__name__}-> ReportError->Exception)"
        )
    print(f"正常情况->{mark_report([1,2,3])}")

    check("ValueError被捕获", True)
    check("多异常分发成功", parse_ratio("8", "0") == "分母不能为0")
    check("EAFP解析成功", int("12345") == 12345)
    check("自定义异常被父类捕获", issubclass(NotEnoughDataError, reportError))
    check(
        "异常信息正确", "2条" in NotEnoughDataError("至少需要2条数据，实际1条").args[0]
    )


def parse_int():
    try:
        value = int("abc")
    except ValueError as e:
        print(f"捕获ValueError->{e}")
    else:
        print("没有异常才走到这里")
    finally:
        print("finally 永远执行-----清理资源用")


def parse_ratio(a, b):
    try:
        return float(a) / float(b)
    except ValueError:
        return "参数不是数字"
    except ZeroDivisionError:
        return "分母不能为0"


def int_text():
    text = "12345"
    try:
        num = int(text)
        print(f"EAFP风格->int({text!r})成功=={num}")
    except ValueError:
        print("不是数字")


class reportError(Exception):
    "报表处理失败是跑车，业务异常统一用这个前缀"


class NotEnoughDataError(reportError):
    "数据条数不足，无法计算。"


def mark_report(rows):
    if len(rows) < 2:
        raise NotEnoughDataError(f"至少需要2条数据，实际{len(rows)}条")
    return f"报表生成成功，共{len(rows)}行"


def summary_5():
    section("5.组和练习：top_n_by_city")
    data = [
        {"name": "张三", "city": "西安", "amount": 1200},
        {"name": "李四", "city": "西安", "amount": 3400},
        {"name": "王五", "city": "西安", "amount": 900},
        {"name": "赵六", "city": "西安", "amount": 2100},
    ]
    top = top_n_by_city(data, "西安", 2)
    print(f"西安 Top2->{top}")
    print("这段5行代码在C#里大概是10行起步,这就是缩小颗粒度的意义")
    check("Top N 结果正确", top == [("李四", 3400), ("赵六", 2100)])


def top_n_by_city(records: list[dict], city: str, n: int = 2) -> list[tuple[str, int]]:
    "取某城市金额最高的前n单,返回[(姓名,金额),...]"
    rows = [r for r in records if r["city"] == city]  # 筛选
    rows.sort(key=lambda r: r["amount"], reverse=True)  # 排序
    return [(r["name"], r["amount"]) for r in rows[:n]]  # 取前N+ 边形


def summary_6():
    section("Day2 自检结果")
    total_checks = _result["pass"] + _result["fail"]
    print(f"通过{_result["pass"]}/{total_checks}")
    if _result["fail"]:
        print(f"待修：{_result['fail_names']}")
    else:
        print("->全通过，别忘了今天还要手写5个十行小脚本（day2_scripts/目录）")
    # sys.exit(0 if _result["fail"]==0 else 1)


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        summary_1()
        summary_2()
        summary_3()
        summary_4()
        summary_5()
        summary_6()
    except Exception:
        pass
