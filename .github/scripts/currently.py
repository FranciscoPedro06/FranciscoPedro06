"""Set the README's "currently:" line to the latest public commit message.

Looks through the user's recent public push events, skipping this profile
repo and merge commits, and writes the first line of the newest commit
message into README.md and the `facts` table in db/francisco.sql.
"""

import html
import json
import os
import re
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
README = ROOT / "README.md"
SEED = ROOT / "db" / "francisco.sql"
USER = os.environ.get("GITHUB_USER", "FranciscoPedro06")
PROFILE_REPO = f"{USER}/{USER}"
MAX_LENGTH = 72


def api(path):
    req = urllib.request.Request(f"https://api.github.com{path}")
    req.add_header("Accept", "application/vnd.github+json")
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.load(resp)


def first_line(message):
    lines = (message or "").strip().splitlines()
    line = lines[0].strip() if lines else ""
    return line if len(line) <= MAX_LENGTH else line[: MAX_LENGTH - 3].rstrip() + "..."


def latest_message(events):
    for event in events:
        if event.get("type") != "PushEvent" or event["repo"]["name"] == PROFILE_REPO:
            continue
        sha = event["payload"].get("head")
        if not sha:
            continue
        commit = api(f"/repos/{event['repo']['name']}/commits/{sha}")
        message = first_line(commit["commit"]["message"])
        if message and not message.startswith("Merge "):
            return message
    return None


def apply(message):
    readme = README.read_text()
    readme = re.sub(
        r"<!--currently-->.*?<!--/currently-->",
        lambda _: f"<!--currently-->{html.escape(message, quote=False)}<!--/currently-->",
        readme,
    )
    README.write_text(readme)

    seed = SEED.read_text()
    sql_value = message.replace("'", "''")
    seed = re.sub(
        r"\('currently',(\s*)'(?:[^']|'')*'\)",
        lambda m: f"('currently',{m.group(1)}'{sql_value}')",
        seed,
    )
    SEED.write_text(seed)


def main():
    message = latest_message(api(f"/users/{USER}/events/public?per_page=100"))
    if not message:
        print("No recent public commit found; leaving the line as is.")
        return
    print(f"currently: {message}")
    apply(message)


if __name__ == "__main__":
    main()
