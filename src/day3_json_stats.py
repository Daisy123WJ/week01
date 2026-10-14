import json, sys
from collections import Counter, defaultdict
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "data" / "sales_orders.json"
OUT_DIR = BASE_DIR / "out"
REPORT_FILE = OUT_DIR / "day3_report.txt"
SUMMARY_FILE = OUT_DIR / "day3_summary.json"

_result = {"pass": 0, "fail": 0, "fail_names": []}


def check(name: str, cond: bool, hint: str = "") -> None:
    if cond:
        _result["pass"] += 1
        print(f"[OK]{name}")
    else:
        _result["fail"] += 1
        _result["fail_names"].append(name)
        print(f"[FaIL]{name}<-{hint}")


def section(title: str) -> None:
    print("\n" + "=" * 68)
    print(title)
    print("=" * 68)


def summary_1():
    section("1.pathlib路劲处理")
    print(f"脚本所在目录:{BASE_DIR}")
    print(f"数据文件    :{DATA_FILE}")
    print(f"文件存在吗  :{DATA_FILE.exists()}")
    print(f"文件大小    :{DATA_FILE.stat().st_size}字节")
    print(f"文件名/后缀 :{DATA_FILE.name}/{DATA_FILE.suffix}")
    print("""
    [C#对照] System.IO.Path.Combine(
    "data","x.json")  -->Path("data")/"x.json"
    File.Exists(path) -->Path(path).exists()
    new FileInfo(path).Length-->Path(path).stat().st_size
    注意：/运算符被重载成了"拼路径",这是Python里少见的运算符重载
    """)
    check("数据文件存在", DATA_FILE.exists())
    check("斜杠拼接路径可用", (Path("a") / "b").name == "b")


def summary_2():
    section("2.文件读写(with语句=C#的using)")
    with open(DATA_FILE, encoding="utf-8") as f:
        raw_text = f.read()
    print(f"读入{len(raw_text)}个字符")
    print(f"前60个字符:{raw_text[:60]!r}")
    # try:
    #     with open(DATA_FILE, encoding="utf-8") as f:
    #         f.read()
    #     print(
    #         "[提示]本机默认编码恰好能读，但换台机器/换个文件就会炸-------永远显示写encoding"
    #     )
    # except UnicodeDecodeError as e:
    #     print(f"[演示到坑了]不写encoding直接炸:{e}")

    OUT_DIR.mkdir(exist_ok=True)
    (OUT_DIR / "_encoding_demo.txt").write_text("中文测试\n", encoding="utf-8")
    print(
        f"写入测试文件成功：{(OUT_DIR/'_encoding_demo.txt').read_text(encoding='utf-8')!r}"
    )

    check("成功读入JSON文本", raw_text.strip().startswith("{"))
    check("out目录已创建", OUT_DIR.exists())

    # JSON解析
    section("3.json解析(json模块=System.Text.json)")
    data = json.loads(raw_text)
    print(f"顶层键:{list(data.keys())}")
    print(f"报表日期/来源：{data["report_date"]}/{data['source']}")
    print(f"备注：{data['note']}")

    orders = data["orders"]
    print(f"订单条数：{len(orders)}")
    print(f"第一条订单：{orders[0]}")

    print("""
    [C#对照]
    jsonSerializer.Deserialize<T>(JSON)->json.loads(text) 返回dict/list,不用定义类
    jsonSerializer.Serialize(obj)-->json.dumps(obj)
    注意:python的json和C#一样,key都是字符串,类型自动推断(int/float/str/bool/null/None)
    """)
    # 用dict 直接取自动（没有请类型，所以写错字段名要到运行时才发现---这就是动态类型的代价）
    print(f"第一条金额：{orders[0]['amount']}<写错key会在运行时KeyError,不是编译器")

    check("解析出dict", isinstance(data, dict))
    check("orders是列表且20条", isinstance(orders, list) and len(orders) == 20)
    section("4.统计:分组,求和,TopN")
    total_amount = sum(o["amount"] for o in orders)
    total_qty = sum(o["qty"] for o in orders)
    avg_amount = total_amount / len(orders)
    max_order = max(orders, key=lambda o: o["amount"])
    min_order = min(orders, key=lambda o: o["amount"])
    print(f"订单总数   : {len(orders)}")

    print(f"总金额   : {total_amount:,} 元")
    print(f"总数量   : {total_qty} 件")
    print(f"单均金额 : {avg_amount:,.2f} 元")
    print(
        f"最大单     : {max_order['order_id']} {max_order['city']} {max_order['amount']:,} 元"
    )
    print(
        f"最小单     : {min_order['order_id']} {min_order['city']} {min_order['amount']:,} 元"
    )

    # ---按城市分组求和，推导式写法
    by_city = {
        c: sum(o["amount"] for o in orders if o["city"] == c)
        for c in sorted({o["city"] for o in orders})
    }
    print(f"\n按城市:{by_city}")

    # --同一个统计，用defaultdict 累加写法（第二种武器，数据大时更快）
    by_city_loop = defaultdict(int)
    for o in orders:
        by_city_loop[o["city"]] += o["amount"]
    print(f"defaultdict:{dict(by_city_loop)}")

    # ---计数：Counter(统计"哪个城市几单")
    city_count = Counter(o["city"] for o in orders)
    print(f"城市单数：{dict(city_count)}")

    # ----按品类分组
    by_category = defaultdict(int)
    for o in orders:
        by_category[o["category"]] += o["amount"]
    by_category = dict(by_category)
    print(f"按品类：{by_category}")

    # -----按销售汇总+排名（c# 的groupBy().OrderByDesending().Select())
    by_sales = defaultdict(int)
    for o in orders:
        by_sales[o["sales"]] += o["amount"]
    ranking = sorted(by_sales.items(), key=lambda kv: kv[1], reverse=True)
    print("\n销售排行")
    for i, (person, amount) in enumerate(ranking, start=1):
        print(f"{i},{person:<4}{amount:>8}元")

    # ---Top N
    top3 = sorted(orders, key=lambda o: o["amount"], reverse=True)[:3]
    print("\n Top3大单:")
    for o in top3:
        print(f"{o['order_id']}{o["city"]}{o["category"]}{o["amount"]:,}元")

    check("总金额正确", total_amount == 122600)

    check("单均金额正确", round(avg_amount, 2) == 6130.0)
    check("按城市分组正确", by_city == {"杭州": 52000, "成都": 22040, "西安": 48560})
    check("两种分组写法结果一致", dict(by_city_loop) == by_city)
    check(
        "品类分组正确", by_category == {"服务器": 98000, "显示器": 21000, "键盘": 3600}
    )
    check("销售排行第一名是李四", ranking[0][0] == "李四" and ranking[0][1] == 34920)
    check("Top3 最大单是 SO-1013", top3[0]["order_id"] == "SO-1013")

    section("5.输出报告")
    lines = [
        "=" * 46,
        f"销售统计简报(数据日期{data['report_date']})",
        "=" * 46,
        f"订单总数：{len(orders)}单",
        f"总金额：{total_amount:,}元",
        f"单价金额：{avg_amount:,.2f}元",
        "",
        "【按城市】",
    ]
    for city, amount in sorted(by_city.items(), key=lambda kv: kv[1], reverse=True):
        lines.append(f"{city:<4}{amount:>9,}元 占比{amount/total_amount:6.1%}")

    lines += ["", "[按品类]"]
    for cat, amount in sorted(by_category.items(), key=lambda kv: kv[1], reverse=True):
        lines.append(f"{cat:<4}{amount:>9,}元 占比{amount/total_amount:6.1%}")

    lines += ["", "[按销售排行]"]
    for i, (person, amount) in enumerate(ranking, start=1):
        lines.append(f"{i}.{person:<4}{amount:>9,}元")

    lines += ["", "[Top3 大单]"]
    for o in top3:
        lines.append(f"{o['order_id']}{o["city"]}{o["category"]}{o["amount"]:,}元")
    lines.append("")
    report_text = "\n".join(lines)
    REPORT_FILE.write_text(report_text, encoding="utf-8")
    print(report_text)

    summary = {
        "report_date": data["report_date"],
        "order_count": len(orders),
        "total_amount": total_amount,
        "avg_amount": round(avg_amount, 2),
        "by_city": by_city,
        "by_category": by_category,
        "ranking": [{"sales": p, "amount": a} for p, a in ranking],
    }
    SUMMARY_FILE.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )  # ensure_ascii=false 才有中文，不是\u4e2d\u6587

    print(f"报告已写入:{REPORT_FILE}")
    print(f"汇总已写入：{SUMMARY_FILE}")
    print(("""
        [关键]json.dumps 默认 ensure_ascii=True，中文会被转成 \\u897f\\u5b89这种转义。想看的中文,两个参数都要给，
        ensure_ascii=False,encoding="utf-8"
    """))

    # 会读验证
    reloaded = json.loads(SUMMARY_FILE.read_text(encoding="utf-8"))
    check("报告文件已生成", REPORT_FILE.exists() and REPORT_FILE.stat().st_size > 200)
    check("会中json已生成", SUMMARY_FILE.exists())
    check("回读json中文没有乱码", reloaded["by_city"] == by_city)
    check("回读金额与内存一致", reloaded["total_amount"] == total_amount)
    check("报告文本含【销售排行】", "销售排行" in report_text)

    # ====================================================
    section("Day3自检结果")
    total_checks = _result["pass"] + _result["fail"]
    print(f"通过{_result['pass']}/{total_checks}")
    if _result["fail"]:
        print(f"待修：{_result['fail_names']}")
    else:
        print(
            " ->全通过！打开out/day3_report.txt看一眼，（这就是明天要重构成类的那个脚本）"
        )
    sys.exit(0 if _result["fail"] == 0 else 1)


try:
    sys.stdout.reconfigure(encoding="utf-8")
    # summary_1()
    summary_2()
except Exception:
    pass
