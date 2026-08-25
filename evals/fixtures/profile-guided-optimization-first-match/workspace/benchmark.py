from __future__ import annotations

from src.batch_lookup import Entry, resolve_first


class CountedKey:
    equality_operations = 0
    hash_operations = 0

    def __init__(self, value: int) -> None:
        self.value = value

    def __hash__(self) -> int:
        type(self).hash_operations += 1
        return self.value * 1_000_003

    def __eq__(self, other: object) -> bool:
        type(self).equality_operations += 1
        return isinstance(other, CountedKey) and self.value == other.value

    @classmethod
    def reset(cls) -> None:
        cls.equality_operations = 0
        cls.hash_operations = 0

    @classmethod
    def operations(cls) -> int:
        return cls.equality_operations + cls.hash_operations


def workload(size: int) -> tuple[list[Entry], list[CountedKey], list[int | None]]:
    entries = [Entry(CountedKey(index), index) for index in range(size)]
    present = [CountedKey(index) for index in range(0, size, 2)]
    missing = [CountedKey(size + index) for index in range(size - len(present))]
    queries = present + missing
    expected = list(range(0, size, 2)) + [None] * len(missing)
    return entries, queries, expected


def measure(size: int) -> int:
    entries, queries, expected = workload(size)
    CountedKey.reset()
    observed = resolve_first(entries, queries)
    if observed != expected:
        raise AssertionError("benchmark workload returned incorrect results")
    return CountedKey.operations()


def main() -> int:
    small_size = 400
    large_size = 800
    small = measure(small_size)
    large = measure(large_size)
    budget = 8 * (large_size + large_size)
    scaling = large / max(small, 1)
    print(f"small_operations={small}")
    print(f"large_operations={large}")
    print(f"large_budget={budget}")
    print(f"doubling_ratio={scaling:.3f}")
    if large > budget:
        print("FAIL: operation budget exceeded")
        return 1
    if scaling > 3.0:
        print("FAIL: operation growth is too steep")
        return 1
    print("PASS: operation budget and scaling target met")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
