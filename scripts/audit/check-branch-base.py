#!/usr/bin/env python3
"""Branch-Base-Gate: verhindert Commits auf einem Zweig, der hinter `origin/main` liegt.

    python scripts/audit/check-branch-base.py [--quiet] [--no-fetch]
    python scripts/audit/check-branch-base.py --hook          # liest Hook-JSON von stdin

Exit 0 = in Ordnung, Exit 2 = blockieren (die Ausgabe geht nach stderr und erklaert, was zu
tun ist). Gedacht als PreToolUse-Hook auf `git commit` und `git push`, laeuft aber auch von
Hand.

## `--hook`

Im Hook-Modus liest das Skript das PreToolUse-JSON von stdin und prueft **selbst**, ob der
Befehl ueberhaupt ein `git commit` oder `git push` ist. Das ist Absicht:

- kein `jq` noetig (unter Windows meist nicht vorhanden) und keine Shell-Logik, die zwischen
  bash und PowerShell unterschiedlich waere;
- `git -C <pfad> commit` wird miterkannt, was ein Muster wie `Bash(git commit*)` verpasst;
- bei allem anderen kostet der Hook nichts: er endet vor dem ersten Netzzugriff.

Fail-open ist gewollt: laesst sich stdin nicht lesen oder nicht als JSON deuten, endet das
Skript mit 0. Ein Werkzeug, das den Arbeitsfluss blockiert, weil es sich selbst nicht sicher
ist, richtet mehr Schaden an als der Fehler, den es verhindern soll.

## Warum es das gibt

Der Fehler, gegen den das Gate steht, ist **still**. `git status` sagt „nothing to commit,
working tree clean", der Zweigname sieht plausibel aus, und trotzdem sitzt der Commit auf einem
Fundament, das laengst ueberholt ist. Am 2026-07-30 wurde #248 auf `feature/236-frauenlob`
committet: 10 Commits hinter `main`, Inhalt seit PR #253 oben, Remote-Zweig geloescht. Als PR
eroeffnet haette das die schon gemergte Arbeit erneut vorgeschlagen und Nachbesserungen
ueberschrieben. Die Korrektur kostete einen kompletten Neuaufbau.

Die Regel stand an dem Tag bereits in den Projektnotizen. Sie wurde trotzdem nicht angewandt,
und genau deshalb ist ein Gate noetig statt eines Vorsatzes.

## Was geprueft wird

1. **Rueckstand:** `git rev-list --count HEAD..origin/main`. Groesser null heisst, der Zweig
   kennt Aenderungen nicht, die oben schon liegen. Blockiert.
2. **Verwaister Zweig:** Der Zweig hat ein konfiguriertes Upstream, das es auf dem Remote nicht
   mehr gibt. Typisch fuer „PR wurde gemergt, GitHub hat den Zweig geloescht, lokal lebt er
   weiter". Blockiert.
3. **Direkt auf `main`:** Hinweis, kein Block. Das regelt bereits CLAUDE.md.

Kein Netzzugang noetig, wenn `git fetch` in den letzten 10 Minuten lief; sonst wird einmal
gefetcht. `--no-fetch` unterdrueckt das (fuer Offline-Arbeit), prueft dann gegen den letzten
bekannten Stand und sagt das auch.

## Aussteigen

`SKIP_BRANCH_BASE_CHECK=1` umgeht das Gate. Bewusst vorhanden: es gibt legitime Faelle, etwa
einen Hotfix auf einem alten Stand. Wer es setzt, soll es begruenden koennen.
"""
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

FETCH_MAX_AGE_S = 600
UPSTREAM = "origin/main"

# `git ... commit` / `git ... push`, mit beliebigen Optionen dazwischen.
#
# Bewusst locker zwischen `git` und dem Verb: ein erster Versuch parste die Optionen einzeln
# und uebersah `git -C "pfad mit leerzeichen" commit`, also genau die Form, die in diesem
# Projekt staendig vorkommt (der Repo-Pfad enthaelt Leerzeichen und einen Umlaut).
#
# Zwei Einschraenkungen halten die Fehlalarme klein:
#   [^\n;&|]*?  endet an Kommando- und Pipe-Grenzen, damit `git log … | grep push` nicht zaehlt
#   (?<![-=\w]) schliesst `--grep=commit` und `--no-commit` aus
GIT_WRITE = re.compile(r"\bgit\b[^\n;&|]*?(?<![-=\w])\b(commit|push)\b")


def betrifft_uns(befehl):
    return bool(GIT_WRITE.search(befehl or ""))


def hook_befehl_lesen():
    """Gibt den Befehl aus dem PreToolUse-JSON zurueck, oder None wenn unlesbar."""
    try:
        roh = sys.stdin.read()
    except Exception:
        return None
    if not roh.strip():
        return None
    try:
        daten = json.loads(roh)
    except (ValueError, TypeError):
        return None
    if not isinstance(daten, dict):
        return None
    eingabe = daten.get("tool_input")
    if not isinstance(eingabe, dict):
        return None
    befehl = eingabe.get("command")
    return befehl if isinstance(befehl, str) else None


def git(*args, check=False):
    r = subprocess.run(["git", *args], capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    if check and r.returncode != 0:
        raise SystemExit(f"git {' '.join(args)} fehlgeschlagen:\n{r.stderr.strip()}")
    return r.stdout.strip(), r.returncode


def fetch_is_fresh():
    root, rc = git("rev-parse", "--git-common-dir")
    if rc != 0:
        return False
    head = Path(root) / "FETCH_HEAD"
    return head.exists() and (time.time() - head.stat().st_mtime) < FETCH_MAX_AGE_S


def main(argv):
    hook = "--hook" in argv
    quiet = "--quiet" in argv or hook
    no_fetch = "--no-fetch" in argv

    if os.environ.get("SKIP_BRANCH_BASE_CHECK"):
        return 0

    if hook:
        befehl = hook_befehl_lesen()
        if befehl is None or not betrifft_uns(befehl):
            return 0  # kein git commit/push, oder stdin unlesbar -> fail-open

    _, rc = git("rev-parse", "--git-dir")
    if rc != 0:
        return 0  # kein Repo, nichts zu pruefen

    stale_info = ""
    if not no_fetch and not fetch_is_fresh():
        _, rc = git("fetch", "--quiet", "origin")
        if rc != 0:
            stale_info = ("  (Hinweis: `git fetch` schlug fehl, geprueft wurde gegen den "
                          "letzten bekannten Stand)\n")
    elif no_fetch:
        stale_info = "  (Hinweis: --no-fetch, geprueft wurde gegen den letzten bekannten Stand)\n"

    _, rc = git("rev-parse", "--verify", "--quiet", UPSTREAM)
    if rc != 0:
        return 0  # kein origin/main bekannt, nichts zu vergleichen

    branch, _ = git("rev-parse", "--abbrev-ref", "HEAD")
    if branch == "HEAD":
        return 0  # detached, absichtlich unterwegs

    behind, _ = git("rev-list", "--count", f"HEAD..{UPSTREAM}")
    behind = int(behind or 0)

    # Upstream konfiguriert, aber auf dem Remote verschwunden?
    upstream, rc = git("rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}")
    verwaist = False
    if rc == 0 and upstream.startswith("origin/"):
        remote_branch = upstream.split("/", 1)[1]
        out, _ = git("ls-remote", "--heads", "origin", remote_branch)
        verwaist = not out.strip()

    if branch == "main" and behind == 0 and not quiet:
        print("Hinweis: du committest direkt auf main. CLAUDE.md verlangt einen Feature-Zweig.")

    if behind == 0 and not verwaist:
        if not quiet:
            print(f"Branch-Base ok: `{branch}` kennt alles aus {UPSTREAM}.")
        return 0

    lines = [f"\nBRANCH-BASE-GATE: `{branch}` ist keine gute Grundlage.\n"]
    if behind:
        lines.append(f"  * {behind} Commits aus {UPSTREAM} fehlen diesem Zweig.")
    if verwaist:
        lines.append(f"  * Das Upstream `{upstream}` existiert auf dem Remote nicht mehr. "
                     "Meist heisst das: der PR wurde gemergt und der Zweig oben geloescht.")
    if stale_info:
        lines.append(stale_info.rstrip())
    lines += [
        "",
        "  Warum das zaehlt: ein Commit hierauf schlaegt spaeter als PR vor, bereits",
        "  Gemergtes erneut zu aendern, und kann Nachbesserungen ueberschreiben.",
        "",
        "  Was zu tun ist:",
        f"    git checkout -b <neuer-zweig> {UPSTREAM}      # neu aufsetzen, empfohlen",
        f"    git merge {UPSTREAM}                          # oder den Rueckstand aufholen",
        "",
        "  Wirklich auf diesem Stand arbeiten? SKIP_BRANCH_BASE_CHECK=1 setzen.",
        "",
    ]
    print("\n".join(lines), file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
