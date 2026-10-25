import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCRIPT = HERE / "txtkit.py"


def run(*args):
    return subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True, text=True)


def make_sample() -> Path:
    path = HERE / "_sample.txt"
    path.write_text(
        "alpha\nbeta\nTODO: fix this\n中文行\n\ngamma\n",
        encoding="utf-8",
    )
    return path


def test_count():
    path = make_sample()
    result = run("count", str(path), "--json")
    assert result.returncode == 0, result.stderr
    import json
    stats = json.loads(result.stdout)
    assert stats["lines"] == 6, stats
    assert stats["blank_lines"] == 1, stats
    assert stats["cjk_characters"] == 3, stats
    path.unlink()


def test_find():
    path = make_sample()
    result = run("find", str(path), "TODO")
    assert result.returncode == 0, result
    assert "TODO" in result.stdout
    assert "匹配 1 处" in result.stdout
    path.unlink()


def test_find_no_match():
    path = make_sample()
    result = run("find", str(path), "ZZZZ")
    assert result.returncode == 1, result
    path.unlink()


def test_slice_lines():
    path = make_sample()
    result = run("slice", str(path), "--lines", "2:3")
    assert result.returncode == 0, result.stderr
    assert "beta" in result.stdout and "TODO" in result.stdout
    assert "alpha" not in result.stdout
    path.unlink()


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print(f"ok  {name}")
    print("all tests passed")
