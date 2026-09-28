---
name: find-mentions-exit-probe-476
description: In-process-Probe fuer scripts/sync/find-mentions.py main() ohne Netz, Kandidatenfalle, Exit-Pfade
metadata:
  type: project
---
Stand 23.09.2026.

- Probe <1 s: `sys.modules["requests"]` stubben, Modul per importlib; `fm.zotero_baseline`, `fm.SOURCES` (Tupel mit einer Funktion, `__name__` setzen), `fm.zotero_write` ersetzen; `fm.PROBLEME` zwischen Faellen leeren; SystemExit fangen; vorher `os.chdir` ins Scratch (candidates.json landet im cwd).
- Kandidatentitel brauchen fast disjunkte Wortmengen (`woerter()` streicht Kurztokens/Ziffern, `stamm()` faltet; >= 85 % Ueberlappung gilt als bekannt): `f"MHDBDB zq{i:02d}ab zq{i:02d}cd zq{i:02d}ef"`.
- Exit 1 im Schreibpfad jenseits PROBLEME: Zotero-Ablehnung, Kappung, fehlender ZOTERO_API_KEY. `basis_ok=False` kommt im echten Lauf immer mit PROBLEME. candidates.json traegt immer alle Kandidaten, Zotero bekommt nur MAX_NEU.
