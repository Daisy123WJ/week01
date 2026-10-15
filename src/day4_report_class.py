import sys, json
from collections import defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path

# 今天不是重新写一遍，而是“重构” 你亲手体会一件事
# Day3 那种从头到尾写的脚本，第二人接手就会改坏
# Day4 把它包成类，才敢交“代码”
# 对照关系（这是你今天唯一需要记住的）：
# C# Class/new/this/ToString()/Equals()/static/recode
# python class/直接调用类名/self/_str_/_eq_/@staticmethod/@dataclass

try:
    sys.stdout.reconfigur(encoding="utf-8")
except Exception:
    pass

BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "data" / "sales_orders.json"
OUT_DIR = BASE_DIR / "out"
_result = {"pass": 0, "fail": 0, "fail_names": []}


def check(name: str, cond: bool, hint: str = "") -> None:
    if cond:
        _result["pass"] += 1
        print(f"[OK]{name}")
    else:
        _result["fail"] += 1
        _result["fail_names"].append(name)
        print(f"[FAIL]{name}<-{hint}")


def section(title: str) -> None:
    print("\n" + "=" * 68)
    print(title)
    print("=" * 68)


##====================================================
# 1.@dataclass:最像C#的地方
# ====================================================

section("1.dataclass----------------Python的record/POCO")


# 一行订单。@dataclass 自动生成 __init__/__repr__/__eq__,等于C#的recod.
@dataclass
class Order:
    order_id: str
    city: str
    category: str
    sales: str
    amount: int
    qty: int

    # 从json的dict构造对象，写法要显示，别用cls(**d) -----数据多一个字典就崩
    @classmethod
    def from_dict(cls, d: dict) -> "Order":
        return cls(
            order_id=d["order_id"],
            city=d["city"],
            category=d["category"],
            sales=d["sales"],
            amount=d["amount"],
            qty=d["qty"],
        )

    # dataclass 自带的"转字典"(省掉手写6行)-->将对象转换成字典
    def to_dict(self) -> dict:
        return asdict(self)

    # 实例方法：self一定要在第一个参数(C#里是隐藏的this)
    def is_big(self, threshold: int = 10000) -> bool:
        return self.amount >= threshold

    # C# public override string ToString()
    def __str__(self) -> str:
        return f"{self.order_id}|{self.city}|{self.category}|{self.sales}|{self.amount:,}元"

    # 定义<号>以后可以直接sort()对象列表
    def __lt__(self, other: "Order") -> bool:
        return self.amount < other.amount


o1 = Order("SO-X", "西安", "键盘", "张三", 999, 1)
o2 = Order("SO-X", "西安", "键盘", "张三", 999, 1)
print(f"str(order)->{o1}")
print(f"自动相等比较 ->o1==o2 得到{o1==o2}<- dataclass帮你写了__eq__")
print(f"将对象转换成字典:to_dict() ->{o1.to_dict()}")
print(f"类型注释->{Order.__dataclass_fields__['amount'].type}")

print("""
    [C#对照]
    public recodrd Order(int Amount); ->@dataclass class Order:amount:int
    public override string ToString() ->def__str__(self)
    public static Order FromDict(...) ->@classmethod def from_dict(cls,...)
""")
check("dataclass自动__eq__", o1 == o2)
check("__str__生效", "SO-X" in str(o1))
check("to_dict可用", o1.to_dict()["amount"] == 999)
check("实例方法可用", o1.is_big(100) is True and o1.is_big(1000) is False)

# =================================
# 2.类：把Day3的散装函数受尽一个盒子
# ==================================
section("2.SalesReport类")


# """Day3里那些全局遍历(orders/total/amount/by city...) 现在全部变成实例状态。
# 好处：同一个进程里可用同时开多方报表，互不干扰；测试时可用直接构造对象。
# [C#对照]这里是一个普通类，区别只有两点：
#   1.构造函数叫__init__,第一个参数是self
#    2.没有privat/public,靠的是划线约定(_Orders表示"别从外面碰")
# """
class SalesReport:

    def __init__(self, orders: list[Order], report_date: str = ""):
        self._Orders = list(orders)  # 拷贝一份，防止外部改了影响内部
        self.report_date = report_date

    # 构造：从文件读进来
    @classmethod
    def from_json_file(cls, path: str | Path) -> "SalesReport":
        path = Path(path)
        raw = json.loads(path.read_text(encoding="utf-8"))
        orders = [Order.from_dict(d) for d in raw["orders"]]
        return cls(orders, raw.get("report_date", ""))

    # --魔术方法：让对象像内置类型一样被使用
    def __len__(self) -> int:
        return len(self._Orders)

    def __iter__(self):
        return iter(self._Orders)

    # 调试时看到有意义的信息
    def __repr__(self) -> str:
        return f"SalesReport({len(self)}单，合计{self.total_amount:,}元)"

    # --属性：像字段一样访问，实际是算出来的(C#的只读属性)
    @property
    def total_amount(self) -> int:
        return sum(o.amount for o in self._Orders)

    @property
    def avg_amount(self) -> float:
        return self.total_amount / len(self._Orders) if self._Orders else 0.0

    @property
    def big_Orders(self) -> list[Order]:
        return [o for o in self._Orders if o.is_big()]

    # ------业务方法----------------------------------
    # 按任意字段分组求和：sum_by('city')/sum_by('catagory')/sum_by('sales')
    # 这里用了getattr------------动态语言才能这么干（C#要反射或表达式树）。
    def sum_by(self, field_name: str) -> dict[str, int]:
        result = defaultdict(int)
        for o in self._Orders:
            result[getattr(o, field_name)] += o.amount
        return dict(result)

    # 靠Order.__lt__直接排对象
    def ranking(self, field_name: str = "sales") -> list[tuple[str, int]]:
        return sorted(
            self.sum_by(field_name).items(), key=lambda kv: kv[1], reverse=True
        )

    # Order.__lt__直接排对象
    def top_n(self, n: int = 3) -> list[Order]:
        return sorted(self._Orders, reverse=True)[:n]

    def count_by(self, field_name: str) -> dict[str, int]:
        counter = defaultdict(int)
        for o in self._Orders:
            counter[getattr(o, field_name)] += 1
        return dict(counter)

    # ----输出----------------------------------
    # [C# static方法。和实例无关的工具函数就放这里，不需要self.]
    def format_money(self, value: float) -> str:
        return f"{value:,.0f}元"

    # 生成文本简报（纯函数：不写文件，不打印，方便单测）
    def render(self) -> str:
        lines = [
            "=" * 50,
            f"销售统计简报(数据日期{self.report_date or '未标注'})",
            "=" * 50,
            f"订单总数:{len(self)}单",
            f"总金额:{self.format_money(self.total_amount)}",
            f"单价金额:{self.avg_amount:,.2f}元"
            f"大单(>=1万):{len(self.big_Orders)}单",
            "",
        ]
        for title, field in [("按城市", "city"), ("按品类", "category")]:
            lines.append(f"{title}")
            for name, amount in sorted(
                self.sum_by(field).items(), key=lambda kv: -kv[1]
            ):
                pct = amount / self.total_amount
                lines.append(f"{name:<4}{amount:>9,}元 占比{pct:6.1%}")
            lines.append("")
        lines.append("销售排行")
        for i, (person, amount) in enumerate(self.ranking(), start=1):
            lines.append(f"{i}.{person:<4}{self.format_money(amount):>12}")
        lines.append("")
        lines.append("[Top3大单]")
        for o in self.top_n(3):
            lines.append(f"{o}")
        return "\n".join(lines)

    def save(self, path: str | Path) -> Path:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self.render(), encoding="utf-8")
        return path

    def save_json(self, path: str | Path) -> Path:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "report_date": self.report_date,
            "order_count": len(self),
            "total_amount": self.total_amount,
            "avg_amount": round(self.avg_amount, 2),
            "by_city": self.sum_by("city"),
            "by_category": self.sum_by("category"),
            "ranking": [{"sales": p, "amount": a} for p, a in self.ranking()],
        }
        path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        return path


# 3.用起来（这一段就是 重构之后的开销） 将json 文件转换成集合数组，然后进行各类汇总
section("3.使用这个类")
report = SalesReport.from_json_file(DATA_FILE)
print(f"len(report)     ->{len(report)}")
print(f"repr(report)    ->{report!r}")
print(f"report.total_amount    ->{report.total_amount:,}")
print(f"report.avg_amount      ->{report.avg_amount:,.2f}")
print(f"report.sum_by('city')  ->{report.sum_by('city')}")
print(f"report.count_by('city') ->{report.count_by('city')}")
print(f"report.ranking()[0]     ->{report.ranking()[0]}")
print(f"report.top_n(1)[0]      ->{report.top_n(1)[0]!r}")
print(f"大单列表长度             ->{len(report.big_Orders)}")

# 类的真正好处：可用同时存在多个互相独立的实例
report_west = SalesReport([o for o in report if o.city == "西安"], "西安分部")
print(f"\n第二个实例(只含西安)->{report_west!r}")

report.save(OUT_DIR / "day4_report.txt")
report.save_json(OUT_DIR / "day4_summary.json")
print(f"已写出:{OUT_DIR/'day4_report.txt'}")
print(f"已写出:{OUT_DIR/'day4_summary.json'}")


check("len()生效", len(report) == 20)
check("property求和正确", report.total_amount == 122600)
check("sum_by动态字段可用", report.sum_by("city")["西安"] == 48560)
check("ranking第一名是李四", report.ranking()[0] == ("李四", 34920))
check("top_n用到了__lt__", report.top_n(1)[0].order_id == "SO-1013")
check("大单数量正确", len(report.big_Orders) == 5)
check(
    "第二个实体独立",
    report_west.total_amount == 48560 and report.total_amount == 122600,
)
check("static 方法格式正确", report.format_money(122600) == "122,600元")
check("报告文件已生成", (OUT_DIR / "day4_report.txt").exists())
check(
    "JSON已生成且中文正常",
    json.loads((OUT_DIR / "day4_summary.json").read_text(encoding="utf-8"))["by_city"][
        "杭州"
    ]
    == 52000,
)

# 5.本日验收汇总
section("Day4 自检结果")
total_checks = _result["pass"] + _result["fail"]
print(f"通过{_result['pass']}/{total_checks}")
if _result["fail"]:
    print(f"待修：{_result['fail_names']}")
else:
    print("->全通过!今天最重要的不是这些OK,而是你自己动手的那一步")
    print("  打开day3_json_stats.py,把它的第4节(做统计)改写成调用SalesReport,")
    print("  让它从200行缩到60行。做不到这一段,Day4不算过。")
sys.exit(0 if _result["fail"] == 0 else 1)

# 上证指数： 3741.11   924行情：2635.09
# 第一类：长电 南大  彤程，中科，雅克 软通
# 第二类： 18.95
# 第三类：
