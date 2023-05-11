class SequenceCounter:
    def __init__(self, base) -> None:
        if not base >= 1:
            raise "Base must be 1 or above"
        self.digits = [0]
        self.base = base

    def increment(self):
        n = 0
        while True:
            if len(self.digits) < (n + 1):
                self.digits.append(0)
                break
            self.digits[n] += 1
            if self.digits[n] == self.base:
                self.digits[n] = 0
                n += 1
            else:
                break
        return self.digits

    def __repr__(self) -> str:
        return str(self.digits)

    def __eq__(self, __value: object) -> bool:
        return self.digits == object

    def __iter__(self):
        return self.digits.__iter__()


def main():
    counter = SequenceCounter(3)
    for _ in range(100):
        print(counter)
        counter.increment()


if __name__ == "__main__":
    main()
