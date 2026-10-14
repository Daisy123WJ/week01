import sys

limit = int(sys.argv[1]) if len(sys.argv) > 1 else 20
print(f"limit->{limit}")


def fizbuzz(n: int) -> str:
    if n % 15 == 0:
        return "FizzBuzz"
    if n % 3 == 0:
        return "fizz"
    if n % 5 == 0:
        return "Buzz"
    return str(n)


if __name__ == "__main__":
    result = [fizbuzz(i) for i in range(1, limit + 1)]
    print(" ".join(result))
    alternative = [
        (
            (
                "fizzBuzz"
                if i % 15 == 0
                else "Fizz" if i % 3 == 0 else "Buzz" if i % 5 == 0 else str(i)
            )
            for i in range(1, limit + 1)
        )
    ]
    assert result == alternative, "两种洗发结果不一致，检查if顺序"
    print(f"[自检] 1~{limit} 两种写法结果一致 √")
