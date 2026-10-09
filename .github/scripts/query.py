"""Run a visitor's SQL query (from an issue title) against db/francisco.sql.

Reads the query from the QUERY env var and prints a Markdown reply.
The database is rebuilt from scratch on every run and opened read-only.
"""

import os
import re
import sqlite3
import sys
import tempfile
import time
from pathlib import Path

SEED = Path(__file__).resolve().parents[2] / "db" / "francisco.sql"
MAX_ROWS = 50
MAX_CELL = 60
TIME_LIMIT = 1.0  # seconds
NOPE = ("DROP", "DELETE", "INSERT", "UPDATE", "ALTER", "CREATE", "ATTACH", "DETACH", "PRAGMA", "TRUNCATE", "REPLACE", "VACUUM")

ALLOWED = {sqlite3.SQLITE_SELECT, sqlite3.SQLITE_READ, sqlite3.SQLITE_FUNCTION, sqlite3.SQLITE_RECURSIVE}
BLOCKED_FUNCTIONS = {"load_extension"}

FOOTER = (
    "<sub>Tables: `projects` · `skills` · `contact` · `facts` · `things_i_built`. "
    "Open another issue to run another query.</sub>"
)


def build_db(path):
    seed = sqlite3.connect(path)
    seed.executescript(SEED.read_text())
    seed.commit()
    seed.close()


def authorizer(action, arg1, arg2, db_name, trigger):
    if action not in ALLOWED:
        return sqlite3.SQLITE_DENY
    if action == sqlite3.SQLITE_FUNCTION and (arg2 or "").lower() in BLOCKED_FUNCTIONS:
        return sqlite3.SQLITE_DENY
    return sqlite3.SQLITE_OK


def connect(path):
    conn = sqlite3.connect(":memory:", uri=True)
    conn.execute("ATTACH DATABASE ? AS francisco", (f"file:{path}?mode=ro",))
    conn.execute("PRAGMA query_only = ON")
    conn.setlimit(sqlite3.SQLITE_LIMIT_LENGTH, 100_000)
    conn.setlimit(sqlite3.SQLITE_LIMIT_SQL_LENGTH, 2_000)
    conn.set_authorizer(authorizer)
    deadline = time.monotonic() + TIME_LIMIT
    conn.set_progress_handler(lambda: time.monotonic() > deadline, 1_000)
    return conn


def cell(value):
    if value is None:
        return "NULL"
    if isinstance(value, bytes):
        return f"<{len(value)} bytes>"
    text = re.sub(r"\s+", " ", str(value))
    return text if len(text) <= MAX_CELL else text[: MAX_CELL - 3] + "..."


def ascii_table(columns, rows):
    cells = [[cell(v) for v in row] for row in rows]
    widths = [max([len(c)] + [len(r[i]) for r in cells]) for i, c in enumerate(columns)]
    border = "+" + "+".join("-" * (w + 2) for w in widths) + "+"

    numeric = [all(isinstance(r[i], (int, float)) for r in rows) for i in range(len(columns))]

    def line(values, align_numbers):
        parts = [v.rjust(w) if align_numbers and n else v.ljust(w) for v, w, n in zip(values, widths, numeric)]
        return "| " + " | ".join(parts) + " |"

    out = [border, line(columns, False), border]
    out += [line(r, True) for r in cells]
    out.append(border)
    return "\n".join(out)


def fenced(body, lang=""):
    # Use a fence longer than any backtick run in the body so it can't be escaped.
    longest = max((len(m) for m in re.findall(r"`+", body)), default=0)
    fence = "`" * max(3, longest + 1)
    return f"{fence}{lang}\n{body}\n{fence}"


def run(query):
    first_word = query.split(None, 1)[0].upper() if query else ""
    if first_word in NOPE:
        return "ERROR 1142 (42000): nice try. this database is read-only 🙂"

    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "francisco.db")
        build_db(path)
        conn = connect(path)
        start = time.perf_counter()
        try:
            cur = conn.execute(query)
            columns = [d[0] for d in cur.description or []]
            rows = cur.fetchmany(MAX_ROWS + 1) if columns else []
        except sqlite3.DatabaseError as e:
            msg = str(e)
            if "not authorized" in msg or "readonly" in msg:
                return "ERROR 1142 (42000): nice try. this database is read-only 🙂"
            if "interrupted" in msg:
                return f"ERROR 3024 (HY000): query took longer than {TIME_LIMIT:g}s. I respect the ambition."
            if "too big" in msg or "too long" in msg:
                return "ERROR 1301 (HY000): result too big. keep it under 100 KB, please."
            if "one statement at a time" in msg:
                return "ERROR 1064 (42000): one query per issue, please."
            return f"ERROR 1064 (42000): {msg}"
        finally:
            elapsed = time.perf_counter() - start
            conn.close()

    if not rows:
        return f"Empty set ({elapsed:.3f} sec)"

    truncated = len(rows) > MAX_ROWS
    rows = rows[:MAX_ROWS]
    noun = "row" if len(rows) == 1 else "rows"
    summary = f"{len(rows)} {noun} in set ({elapsed:.3f} sec)"
    if truncated:
        summary += f" -- showing the first {MAX_ROWS}"
    return ascii_table(columns, rows) + "\n" + summary


def main():
    query = os.environ.get("QUERY", "").strip()
    result = run(query)
    reply = "\n\n".join([fenced(query, "sql"), fenced(result), FOOTER])
    sys.stdout.write(reply + "\n")


if __name__ == "__main__":
    main()
