import os
import sys
import importlib.util

# Ensure the script's own directory is on sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gen import validate


def load_p(filepath):
    """Dynamically import module at filepath and return its p function."""
    spec = importlib.util.spec_from_file_location("candidate", filepath)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    if not hasattr(mod, "p"):
        raise AttributeError(f"{filepath} does not define a 'p' function")
    return mod.p


def test_all(p, data):
    """Test p against every example in data (train + test), in order."""
    failed = 0
    passed = 0

    for split in ("train", "test"):
        for i, example in enumerate(data[split]):
            inp, expected = example["input"], example["output"]
            try:
                got = p(inp)
            except Exception as e:
                print(f"[{split} {i}] ERROR: {e}")
                failed += 1
                continue

            if got == expected:
                print(f"[{split} {i}] PASS")
                passed += 1
            else:
                print(f"[{split} {i}] FAIL")
                print(f"  Input:\n{format_grid(inp)}")
                print(f"  Expected:\n{format_grid(expected)}")
                print(f"  Got:\n{format_grid(got)}")
                failed += 1

    print(f"\n---")
    print(f"Passed: {passed}, Failed: {failed}")
    return failed == 0


def format_grid(grid):
    """Pretty-print a 2D grid. All cells padded to the width of the widest value."""
    flat = [str(c) for row in grid for c in row]
    width = max(len(v) for v in flat) if flat else 1
    lines = []
    for row in grid:
        lines.append("  " + " ".join(str(c).rjust(width) for c in row))
    return "\n".join(lines)


def main():
    if len(sys.argv) > 1:
        filepath = sys.argv[1]
    else:
        filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "baseline.py")

    # Print code length
    with open(filepath, "r") as f:
        chars = len(f.read())
    print(f"Code length: {chars} chars\n")

    try:
        p = load_p(filepath)
    except Exception as e:
        print(f"Error loading {filepath}: {e}")
        sys.exit(1)

    data = validate()
    ok = test_all(p, data)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
