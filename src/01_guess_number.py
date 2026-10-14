import random, sys

# 练习点：while True +break, input/int转换 异常兜底，random
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
# target = int(sys.argv[1]) if len(sys.argv) > 1 else random.randint(1, 100)
print(f"[猜数字]范围1~100，我已经想好了一个数")


# 二分法查找法
def args_demo():
    target = random.randint(1, 100)
    tries = 0
    if "--demo" in sys.argv:
        low, high = 1, 100
        while True:
            guess = (low + high) // 2
            tries += 1
            print(f"第{tries}此猜{guess}")
            if guess == target:
                print(f"[演示结束]共{tries}次猜中，答案是{target}")
                sys.exit(0)
            elif guess < target:
                low = guess + 1
                print("猜小了，上调下限")
            else:
                high = guess - 1
                print("猜大了,降低上限")


def while_demo():
    target = int(sys.argv[1]) if len(sys.argv) > 1 else random.randint(1, 100)
    tries = 0
    while True:
        raw = input("请输入1~100的整数（q退出)>").strip()
        if raw.lower() == "q":
            print(f"已退出，答案是{target}")
            break
        try:
            guess = int(raw)
        except ValueError:
            print("这不是一个整数，重来")
            continue
        tries += 1
        if guess == target:
            print(f"猜对了！一共用了{tries}次")
            break
        print(" 小了" if guess < target else "大了")


if __name__ == "__main__":
    while_demo()
# args_demo()
