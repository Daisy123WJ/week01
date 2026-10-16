# 准备：
# pip install requests

# 为什么要有第二个api
# 第一个api(天气)证明"你能调通"
# 第二个(汇率)证明“你能稳定地调”----------也就是换一个完全不同的返回结构
# 你依然能用同一套方法(timeout/raise_for_status/.sjon()/落盘)搞定
# *******实现的功能为：调用接口，读取json串，然后将json信息分别以json数组和csv的格式保存在本地硬盘上。

# 免费，无需key的汇率接口： https://api.frankfurter.app/latest?from=USD&to=CNY

import csv
import json
import sys
import time
import requests
from datetime import datetime
from pathlib import Path

print(f"{time.time()}:{requests.__version__}")
try:
    import requests
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry
except ImportError:
    print("缺少requests库,请先执行：pip install requests")
    sys.exit(2)

BASE_DIR = Path(__file__).resolve().parent
OUT_DIR = BASE_DIR / "out"
BASE_URL = "https://api.frankfurter.app"

_result = {"pass": 0, "fail": 0, "skip": 0, "fail_names": []}


def check(name: str, cond: bool, hint: str = "") -> None:
    if cond:
        _result["pass"] += 1
        print(f"[OK]{name}")
    else:
        _result["fail"] += 1
        _result["fail_names"].append(hint)
        print(f"[FAIL]{name}<{hint}")


def skip(name: str, reason: str) -> None:
    _result["skip"] += 1
    print(f"[SKIP]{name}({reason})")


def section(title: str) -> None:
    print("\n" + "=" * 68)
    print(title)
    print("=" * 68)


section("1.Session +自动重试")


def build_session() -> requests.session:
    """带自动重启的session.生产代码的标准起手式"""
    section = requests.session()
    retry = Retry(
        total=3,
        backoff_factor=0.5,
        status_forcelist=[429, 500, 502, 503, 504],  # 当为这些状态码时才重试
        allowed_methods=["GET"],
    )
    section.mount("https://", HTTPAdapter(max_retries=retry))
    section.headers.update({"User-Agent": "learn-python-week1/1.0"})  # 统一UA 和鉴头
    return section


SESSION = build_session()
print("""
    [C#对照]
    HttpClient 天生就是“长连接+连接池”,所以C#里推荐单例复用。requests的requests.get()每次
    调用都会新建一个连接:requests.Session()才是“连接池+复用Cookie+统一Header的版本,
    对应C#里那个被复用的HttpClient实例。
    一句话:脚本里用requests.get没问题,要连续调用很多次同一个站点,就用session
    ”
""")
check("Session构造成功", isinstance(SESSION, requests.Session))

# ==================================================
# 2.一次调用：USD->CNY/EUR/JPY
# ==================================================
# 免费，无需key的汇率接口： https://api.frankfurter.app/latest?from=USD&to=CNY
section("2.汇率擦好像USD->EUR->JPY")


def get_rates(base: str = "USD", symbols: str = "CNY,EUR,JPY") -> dict:
    """
    params会自动拼成？from=USD&to=CNY,EUR,JPY---不用手拼字符串，
    也不用手动urlencode(中文，空格，特殊字符它都替你处理)。
    """
    resp = SESSION.get(
        f"{BASE_URL}/latest",
        params={"from": base, "to": symbols},
        timeout=(5, 15),
    )
    resp.raise_for_status()
    return resp.json()


rates_payload, rate_ok = None, False
try:
    t0 = time.time()
    rates_payload = get_rates()
    print(f"耗时{time.time()-t0:.2f}s")
    print(json.dumps(rates_payload, ensure_ascii=False, indent=2))
    print(f"\n基准货币:{rates_payload["base"]}")
    print(f"数据日期：{rates_payload["date"]}<-接口给的日期不是today,不要搞混淆")
    print(f"汇率:{rates_payload["rates"]}")
    rate_ok = True
    check("返回200且解析成功", True)
    check("基准时USD", rates_payload["rates"])
    check("拿到CNY汇率", "CNY" in rates_payload["rates"])
except Exception as e:
    print(f"接口不可用:{type(e).__name__:{e}}")
    for n in ["返回200且解析成功", "基准是USD", "拿到CNY汇率"]:
        skip(n, "接口不可用/无网络")
    # 离线兜底：用固定样本把后面的计算逻辑验证完
    rates_payload = {
        "amount": 10,
        "base": "USD",
        "date": "2026-10-16",
        "rates": {"CNY": 7.1200, "EUR": 0.9150, "JPY": 148.3000},
    }
    print(f"[离线演示]使用样本汇率{rates_payload['rates']}")

# =================================================
# 3.二次计算：把汇率变成"能用的东西"
# =================================================
section("3.换算与比较")


def convert(amount: float, rate: float) -> float:
    return amount * rate


data_date = rates_payload["date"]
rows = []
for cur, rate in rates_payload["rates"].items():
    rows.append(
        {
            "date": data_date,
            "base": "USD",
            "quote": cur,
            "rate": rate,
            "usd_100_to_local": round(convert(100, rate), 4),
        }
    )
rows.sort(key=lambda r: r["quote"])
# :<6 左对齐  整体占6个字符，货币占2个字符，不够6个，再补齐4个空格    :>16 表示右对齐 整体占16个字符
print(f"{'货币':<6}{'1 USD=':>4}{'100 USD=>':>16}")
for r in rows:
    # `r` 一般是接口返回的一行汇率字典（从 json 解析出来）
    #:>14.4f   右对齐，总宽度为14个字符 .4f 保留4位有效小数点
    #:>16,.2f  右对齐，总宽度位16个字符，,.2f 保留2位小数，并且千分位加分隔逗号
    print(f"{r['quote']:<6}{r['rate']:>14.4f}{r['usd_100_to_local']:>16,.2f}")
print("""
    注意这里的编程习惯差异：
    C# 里你会先建一个class RateRow{public string Quote;public decimal Rate;}
    Python第一版直接用dict就够了,等字段稳定了(第二周)再抽成@dataclass.
    **先跑通，再抽象**----------这里是python的节奏,和C#先定接口再写实现相关
    """)

check("换算结果条数正确", len(rows) == len(rates_payload["rates"]))
check("排序生效", [r["quote"] for r in rows] == sorted(rates_payload["rates"]))
check("100 USD 换算合理", 100 * rates_payload["rates"]["CNY"] > 100)

# =======================================
# 4. 落盘 CSV+JSON 串起Day3的两边武器
# =========================================================
section("4.落盘成CSV/JSON")
OUT_DIR.mkdir(exist_ok=True)
csv_file = OUT_DIR / "day5_fx_rates.csv"
json_file = OUT_DIR / "day5_fx_rates.json"

# CSV一定要newline="",否则windows 上会多出空行（C# 的streamWrite不会有这个问题）
with open(csv_file, "w", encoding="utf-8-sig", newline="") as f:
    write = csv.DictWriter(
        f, fieldnames=["date", "base", "quote", "rate", "usd_100_to_local"]
    )
    write.writeheader()
    write.writerows(rows)

json_file.write_text(
    json.dumps(rates_payload, ensure_ascii=False, indent=2), encoding="utf-8"
)
print(f"CSV:{csv_file}")
print(f"JSON:{json_file}")
print(f"CSV前3行:")
for line in csv_file.read_text(encoding="utf-8").splitlines()[:3]:
    print("  " + line)
print("""
  两个 Windows专有坑(C# 里都没有）：
  1. open(..., newline="")        -> 不写的话 CSV 每行之间会多一个空行
  2. encoding="utf-8-sig"         -> 带 BOM,Excel 双击打开中文才不乱码
     如果文件是给程序读的，用 "utf-8"；如果是给 Excel 双击看的，用 "utf-8-sig"  
""")

check("CSV已生成", csv_file.exists() and csv_file.stat().st_size > 30)
check("JSON已生成", json_file.exists())
check(
    "CSV行数=数据行+表头",
    len(csv_file.read_text(encoding="utf-8-sig").strip().splitlines()) == len(rows) + 1,
)
check(
    "CSV可被csv模块回读",
    len(list(csv.DictReader(csv_file.read_text(encoding="utf-8-sig").splitlines())))
    == len(rows),
)

# ============================
# 5.异常演练：故意打一个错的URL
# ===============================================
section("5.故意踩一次404")

try:
    resp = SESSION.get(f"{BASE_URL}/latestt", params={"from": "USD"}, timeout=10)
    print(f"错误路径的状态码->{resp.status_code}")
    resp.raise_for_status()
    check("404应该抛HTTPError", False, "竟然没抛异常")
    resp = SESSION.get()
except requests.HTTPError as e:
    print(f"正确捕获-》{type(e).__name__}:(e)")
    check("404抛出了HTTPError", True)
    print("""
    记住三种异常的分工：日常95%的情况都再这三类里：
    requests.Timeout----->超时（网络慢、目标挂了）->重试
    requests.ConnectionError->连不上（断网，域名错）-》提示用户检查网络
    requests.HttpError   ->连上了但状态码是4xx/5xx->看状态码决定
    另外JSON解析失败是ValueError(resp.json()抛),不是requests的异常
""")
except requests.RequestException as e:
    print(f"网络异常(非HTTPError):{type(e).__name__}:{e}")
    skip("404抛出了HTTPError", "无网络,跳过")

# ===================================================
# 6.本日验收汇总
# ===================================================
section("DAY5-B 自检结果")
total_checks = _result["pass"] + _result["fail"]
print(f"通过{_result['pass']}/{total_checks} 跳过{_result['skip']}")
if _result["fail"]:
    print(f"待修:{_result['fail_names']}")
else:
    print("->通过。把out/day5_fx_rates.csv用Excel双击打开")
    print(" 如果中文和列都正常，说明你已经趟过了windows上最容易踩的编码坑")
sys.exit(0 if _result["fail"] == 0 else 1)
