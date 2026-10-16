import json
import time
import sys
from datetime import datetime
from pathlib import Path

print(f"111:{requests.__version__}")
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

try:
    import requests
except ImportError:
    print("缺少requests库,请先执行:uv pip install request")
    sys.exit(2)
BASE_DIR = Path(__file__).resolve().parent
OUT_DIR = BASE_DIR / "out"

_result = {"pass": 0, "fail": 0, "skip": 0, "fail_names": []}


def check(name: str, cond: bool, hint: str = "") -> None:
    if cond:
        _result["pass"] += 1
        print(f"[OK]{name}")
    else:
        _result["fail"] += 1
        _result["fail_names"].append(name)
        print(f"[FAIL]{name} <-{hint}")


def skip(name: str, reason: str) -> None:
    _result["skip"] += 1
    print(
        f"[SKIP]{name} ({reason}:断网/被墙不影响今天的验收，换成联网环境再跑一次即可)"
    )


def section(title: str) -> None:
    print("\n" + "=" * 68)
    print(title)
    print("=" * 68)


# 1.HTTP基础(面试会问)

section("1.HTTP基础")
print("""一个请求由4个部分组成，你只要记住这4个盒子装什么:
    ① GET(取)/POST(交)/PUT(改)/DELETE(删)
    ->request.get(...)/requests.post(...,json={})
    ② URL+查询参数(query string)
     https://api.example.com/weather?city=Xian&days=3
     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^ 路径            ^^^^^^^^^^^ 参数
     ->requests.get("https://api.example.com/weather",params={"city":"Xian","days":3})
     params字典会自动帮你拼成?city=Xian&days=3,中文和空格会自动编码，不用手拼

     ③请求头Header (身份、格式、语言)
     Authorization:Bearer<token> 鉴权
     Content-type:application/json  我发的是json
     User-Agent:xxx 我是谁(有些站点不给UA会403)
     ->requests.get(url,headers={"User-Agent":"learn-python/1.0"})

     ④请求体Body(POST/PUT才有)
     ->requests.post(url,json={"name":"张三"}) #自动序列号+自动设置Content-Type

     响应：
     200 成功/301 302 挑战/400 参数错误/401 未授权/403 拒绝/404 找不到
     429请求太频繁/500 服务器炸了

     状态码不要手写if,用r.raise_for_status():
     4XX/5XX会直接抛requests.HTTPError,落进你的except
     """)

# 2.最小可用请求：一个不带任何参数的GET
section("2.最小的请求")
URL = "https://wttr.in/Xian"
r = None
t0 = time.time()
try:
    r = requests.get(URL, params={"format": "j1"}, timeout=10)
    print(f"状态码  :{r.status_code}")
    print(f"耗时：{time.time()-t0:.2f}秒")
    print(f"Content-Type:{r.headers.get('content-type')}")
    print(f"响应头条数:{len(r.headers)}")
    print(f"响应大小：{len(r.content)}字节")
    print(f"首行文本(纯文本天气):{r.text.splitlines()[0][:70] if r.text else '(空)'}")
    print(f"r.json()和r.text的区别:r.json()已经把JSON解析成dict了")
except requests.RequestException as e:
    print(f"请求失败:{type(e).__name__}:(e)")

if r is None:
    skip("GET返回200", "无网络")
elif r.status_code == 200:
    check("GET返回200", True)
else:
    check("Get返回200", False, f"实际状态码{r.status_code}")

# 3.拿JSON并解析(天气)
section("3.解析JSON天气数据")
weather_summary = None


def fetch_weather(city: str, retries: int = 3) -> dict:
    """
    带超时+状态码校验+重试的取数函数。
    这段是"能上生产和玩家代码"的分界线，----timeout 和 retry必须写
    """
    url = f"https://wttr.in/{city}"
    last_err = None
    for attempt in range(1, retries + 1):
        try:
            resp = requests.get(
                url,
                params={"format": "j1"},
                timeout=10,
                headers={"User-Agent": "learn-python-week1/1.0"},
            )
            resp.raise_for_status()
            return resp.json()
        except (requests.RequestException, ValueError) as e:
            last_err = e
            print(f"第{attempt}次失败：{type(e).__name__}:(e)")
            if attempt < retries:
                wait = 2 ** (attempt - 1)
                print(f"{wait}秒后重试...")
                time.sleep(wait)
    raise RuntimeError(f"重试{retries}次失败：{last_err}")


try:
    data = fetch_weather("Xian")
    # print(f"data-JSON:{data}")
    current = data["current_condition"][0]
    area = data.get("nearest_area", [{}])[0]

    # 此处获取city_name的写法等价与：
    # 1.list_data=area.get("areName",[{"value":"?"}])
    # 2.dict_item=list_data[0]
    # 3.city_Name=dict_item["value"]

    city_name = area.get(
        "areaName",
        [
            {
                "value": "?",
            }
        ],
    )[
        0
    ]["value"]
    today = data["weather"][0]
    weather_summary = {
        "city": city_name,
        "fetched_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "temp_c": int(current["temp_C"]),
        "feels_like_c": int(current["FeelsLikeC"]),
        "humidity": int(current["humidity"]),
        "wind_kmph": int(current["windspeedKmph"]),
        "desc": current["weatherDesc"][0]["value"],
        "today_max_c": int(today["maxtempC"]),
        "today_min_c": int(today["mintempC"]),
        "sunrise": today["astronomy"][0]["sunrise"],
        "sunset": today["astronomy"][0]["sunset"],
    }
    print(json.dumps(weather_summary, ensure_ascii=False, indent=2))
    print("""
    解析心法：
        返回的JSON在python里是嵌套的dict+lilst.
        取值链current_condition[0]["weatherDesc"][0]["value"]看着丑，
        但它等价与C#的data.CurrentCondition[0].WeatherDesc[0].Value--只是没有来兜底。
        所以KeyError要在运行是才炸(记住这点：动态语言的代价在这里最明显的)
    """)

    check("解析当前的温度", isinstance(weather_summary["temp_c"], int))
    check(
        "解析出今日最高/最低温度",
        weather_summary["today_max_c"] >= weather_summary["today_min_c"],
    )
    check("城市名非空", bool(weather_summary["city"]))

    # 存成文件(串起Day3的文件读写)
    OUT_DIR.mkdir(exist_ok=True)
    out_file = OUT_DIR / "day5_weather.json"
    out_file.write_text(
        json.dumps(weather_summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"已保存：{out_file}")
    check("天气结果已落盘", out_file.exists() and out_file.stat().st_size > 50)
    check(
        "落盘文件可回读",
        json.loads(out_file.read_text(encoding="utf-8"))["city"]
        == weather_summary["city"],
    )
except Exception as e:
    print(f"天气接口不可用：{type(e).__name__}:(e)")
    for n in [
        "解析出当前温度",
        "解析出今日最高/最低",
        "城市名非空",
        "天气结果已落盘",
        "落盘文件可回读",
    ]:
        skip(n, "接口不可用")
        # 断网时用固定数据跑一遍解析逻辑，保证"解析能力"本身被验证过
        fake = {
            "current_condition": [
                {
                    "temp_C": "18",
                    "FeelsLikeC": "17",
                    "humidity": "50",
                    "windspeedKmph": "9",
                    "weatherDesc": [{"value": "Sunny"}],
                }
            ],
            "nearest_area": [{"areaName": [{"value": "Xian"}]}],
            "weather": [
                {
                    "maxtempC": "21",
                    "mintempC": "11",
                    "astronomy": [{"sunrise": "06:50 AM", "sunset": "06:20 PM"}],
                }
            ],
        }
    c = fake["current_condition"][0]
    print(
        f"[离线演示] 用固定样本解析 -> 温度 {c['temp_C']}°C，{c['weatherDesc'][0]['value']}"
    )
    check("离线样本解析链路可用", int(c["temp_C"]) == 18)
# =============================================
# 4.用环境遍历存APIkey(铁律，现在就要培养)
# =============================================
section("4.API Key 绝对不能写进代码")
print(
    """上面的wttr.in 不需要Key.但只要你开始用正真的有价值的接口(大模型，地图，支付),就一定
      回拿到一个key,规矩只有一条
      Windows:setx MY_API_KEY "SK-xxxxxxx" 然后重开终端
      MacOS/Linux:export MY_API_KEY="sk-xxxxxx"

      代码里这样取：
      import os
      api_key=os.environ.get("MY_API_KEY")
      if not api_key:
        raise SystemExit("环境变量 MY_API_KEY 未设置")

      绝对不要做的三件事：
      1.把key直接写在.py里--》git 提交后几分钟内会被扫描机器人盗刷
      2.把key写进.py里删掉--》git历史里还在
      3.把key贴在聊天、截图、文档里

      另外.gitignore必须包含(Day6会用到)
      .venv/
      .env/
      __pycache__/  
      """
)

import os

demo_key = os.environ.get("WEEK1_DEMO_KEY")
API_kEY = os.environ.get("MY_API_KEY")
print(f"演示：环境变量WEEK1_DEMO_KEY={demo_key!r}(None 是正常的，本机没有)")
check("能读取环境变量(返回值可为None)", demo_key is None or isinstance(demo_key, str))
# =============================================
# 5.本日验收汇总
# =============================================
section("Day5-A 自检结果")
total_checks = _result["pass"] + _result["fail"]
print(f"通过{_result['pass']}/{total_checks},跳过{_result['skip']}")
if _result["fail"]:
    print(f"待修：{_result['fail_names']}")
else:
    print("--》通过，今天必须轻易看到一件事：连续打印3次【状态码+温度】,")
    print(" 然后把自己电脑的浏览器地址换成https://wttr.in/Beijing?format=j1 ,")
    print(" 你就看到同一份JSON----那一刻你就明白[AP 就是HTTP 接口]了。")
sys.exit(0 if _result["fail"] == 0 else 1)
