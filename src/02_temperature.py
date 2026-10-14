import sys


def c_to_f(c: float) -> float:
    return c * 9 / 5 + 32


def f_to_c(f: float) -> float:
    return (f - 32) * 5 / 9


def change_demo():
    if len(sys.argv) > 3:
        value, unit = float(sys.argv[1]), sys.argv[2].upper()
        if unit == "C":
            print(f"{value:.1f}℃={c_to_f(value):.1f}℉")
        elif unit == "F":
            print(f"{value:.f}℉={f_to_c(value):.1f}℃")
        else:
            print("单位只能是C 或 F")
    else:
        assert c_to_f(100) == 212.0
        assert abs(f_to_c(32) - 0.0) < 1e-9
        assert abs(f_to_c(212) - 100) < 1e-9
        print("[自检]100C=212F √ 32F=0C √ 212F=100C √")


if __name__ == "__main__":
    change_demo()
