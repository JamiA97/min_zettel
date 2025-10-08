#!/usr/bin/env python3
import os
import sys
import tempfile
import subprocess
from pathlib import Path
from time import perf_counter
from datetime import datetime, timedelta


ROOT = Path(__file__).resolve().parents[1]
ZK = str(ROOT / "zk")


def run(cmd, env=None, input=None):
    e = os.environ.copy()
    if env:
        e.update(env)
    proc = subprocess.run([sys.executable, ZK] + cmd, input=input, text=True, capture_output=True, env=e)
    return proc.returncode, proc.stdout.strip(), proc.stderr.strip()


def write(path: Path, text: str):
    path.write_text(text, encoding="utf-8")


def header(id, title):
    now = datetime.utcnow().isoformat(timespec="seconds")
    return (
        f"id: {id}\n"
        f"title: {title}\n"
        f"created: {now}\n"
        f"updated: {now}\n"
        f"aliases: \n\n"
    )


def main():
    tmp = Path(tempfile.mkdtemp(prefix="zk_test_"))
    env = {
        "ZK_DIR": str(tmp),
        "ZK_TIMEZONE": "UTC",
        "ZK_EXT": ".md",
        # avoid opening editors during tests
        "EDITOR": "true" if os.name != "nt" else "notepad",
    }

    print(f"Using temp dir: {tmp}")

    # doctor should report environment
    rc, out, err = run(["doctor"], env)
    assert rc == 0, (rc, err)
    assert "ZK_DIR:" in out

    # new (no open)
    rc, out, err = run(["new", "Alpha Note", "--no-open"], env)
    assert rc == 0, (rc, err)
    id1 = out.strip().splitlines()[-1]
    p1 = next(tmp.glob(f"{id1}_*.md"))
    print("Created:", id1, p1.name)

    rc, out, err = run(["new", "Beta Note", "--no-open"], env)
    assert rc == 0, (rc, err)
    id2 = out.strip().splitlines()[-1]
    p2 = next(tmp.glob(f"{id2}_*.md"))

    # add links: p2 links to p1, titled and untitled
    t1 = p1.read_text(encoding="utf-8")
    t2 = p2.read_text(encoding="utf-8")
    title1 = "Alpha Note"
    t2 += f"See [[{id1} {title1}]] and [[{id1}]].\n"
    write(p2, t2)

    # links
    rc, out, err = run(["links", id2], env)
    assert rc == 0
    assert id1 in out.splitlines()

    # backlinks
    rc, out, err = run(["backlinks", id1], env)
    assert rc == 0
    assert id2 in out

    # alias and find
    rc, out, err = run(["alias", id1, "ALPHA"], env)
    assert rc == 0
    rc, out, err = run(["find", "alpha"], env)
    assert id1 in out

    # grep header and body
    rc, out, err = run(["grep", id1], env)
    assert id1 in out
    rc, out, err = run(["grep", title1], env)
    assert id1 in out
    rc, out, err = run(["grep", id1, "--body"], env)
    assert id2 in out

    # rename should update inbound link titles [[ID Old Title]] -> [[ID New Title]]
    new_title = "Alpha Renamed"
    rc, out, err = run(["rename", id1, new_title], env)
    assert rc == 0, (rc, err)
    t2b = p2.read_text(encoding="utf-8")
    assert f"[[{id1} {new_title}]]" in t2b
    assert f"[[{id1} {title1}]]" not in t2b

    # audit
    rc, out, err = run(["audit", "--dead", "--orphans", "--dups"], env)
    assert rc == 0
    print("Audit:\n" + out)

    # graph
    rc, out, err = run(["graph", "--center", id2, "--depth", "2"], env)
    assert rc == 0
    assert f"{id2} ->" in out

    # performance: generate 10k stubs
    print("Generating 10k stub notes (headers only)…")
    base_dt = datetime(2030, 1, 1, 0, 0)
    for i in range(10_000):
        dt = base_dt + timedelta(minutes=i)
        nid = dt.strftime("%Y_%m%d_%H%M")
        fname = f"{nid}_stub.md"
        write(tmp / fname, header(nid, f"Stub {i}"))

    # time ls/find/backlinks
    def timed(cmd):
        t0 = perf_counter()
        rc, out, err = run(cmd, env)
        dt = (perf_counter() - t0) * 1000.0
        return dt, rc, out, err

    dt_ms, rc, out, err = timed(["ls", "--limit", "5"])  # typical fast path
    print(f"ls --limit 5: {dt_ms:.1f} ms, rc={rc}")
    dt_ms, rc, out, err = timed(["find", "stub 9999"])  # header scan
    print(f"find stub: {dt_ms:.1f} ms, rc={rc}")
    dt_ms, rc, out, err = timed(["backlinks", id1])  # scan all for ID
    print(f"backlinks: {dt_ms:.1f} ms, rc={rc}")

    # Windows-specific: default editor fallback should be notepad
    if os.name == "nt":
        env_no_editor = env.copy()
        env_no_editor.pop("EDITOR", None)
        rc, out, err = run(["doctor"], env_no_editor)
        assert "EDITOR: notepad" in out

    print("All tests passed.")


if __name__ == "__main__":
    main()

