# Agent-Memory

Was hier liegt, hat kein Mensch geschrieben.

`fable-reviewer` ist der Review-Subagent, den dieses Projekt vor dem ersten Push jedes PR-Zweigs laufen lässt (`CLAUDE.md` → Git Rules, `docs/playbooks/BETRIEBSVERTRAG.md` Regel 11). Prüft er einen Diff und lernt dabei etwas, das beim nächsten Mal wieder gilt, schreibt er es hierher: eine Datei je Lehre, dazu `MEMORY.md` als Index. Beim nächsten Lauf bekommt er den Index wieder in seinen Systemprompt und liest die Einzeldateien über dessen Verweise bei Bedarf.

Er tut das selbst und ungefragt. Das Feld `memory: project` in seiner Definition schaltet ihm Schreibrechte für genau dieses Verzeichnis frei, auch wenn seine Werkzeugliste sie nicht nennt.

## Warum das eingecheckt ist

Sonst verfällt es mit der Session und bleibt auf der Maschine, auf der es entstanden ist. Eingecheckt gilt es für alle fünf Autoren dieses Repositoriums und ist nachlesbar und korrigierbar wie jeder andere Text. Die Entscheidung ist am 01.09.2026 gefallen, gegen den naheliegenden Weg, das Verzeichnis zu ignorieren: Wissen wegzuwerfen ist teurer als ein paar Dateien mitzuführen.

## Der Haken, den dieses Projekt hat

**Jede autonome Session arbeitet in ihrem eigenen Worktree** (`BETRIEBSVERTRAG.md` Regel 6, `MASTERPLAN-AUTONOME-ISSUE-SESSION.md` §2.1 Regel 29). Der Reviewer schreibt deshalb in das `.claude/agent-memory/` **des Worktrees**, nicht in dieses hier, und der Worktree wird nach dem Merge abgeräumt. Wer ihn abräumt, ohne vorher nachzusehen, wirft genau das weg, wofür dieses Verzeichnis existiert.

Also: **vor `git worktree remove` einmal in `<worktree>/.claude/agent-memory/` nachsehen** und Neues von Hand hierher übernehmen. Und nicht erst am Ende, sondern nach jeder Review-Runde. Der Anlass ist eine Beobachtung aus dem Schwesterprojekt `corema`, hier **nicht nachgemessen** und über zwei Stationen weitergereicht: dort soll der Reviewer bei einem PR mit vier Runden nur in Runde 3 geschrieben haben. Ob die Zahl stimmt, ändert am Schluss nichts: er schreibt, wann er will, und wer nur einmal nachsieht, findet es nach Rundenglück.

## Was du damit tun kannst

Lesen. Es sind Fehler, die hier schon passiert sind, meist mitsamt dem Kommando, mit dem man sie nachmisst. Ist ein Eintrag falsch, korrigiere oder lösche ihn wie jede andere Datei. Er ist eine Behauptung wie jede andere, und Regel 12 des Betriebsvertrags gilt auch für ihn.

## Was du nicht tun musst

Wer ohne Claude Code arbeitet, braucht hier nichts. Diese Dateien sind kein Vertrag, keine Konvention und keine Anleitung für Menschen, und sie gehören nicht zu den 15 promptotyping-Dokumenten. Verbindlich bleibt, was in `CLAUDE.md`, `docs/` und den Playbooks steht.

## Bei einem Merge-Konflikt in `MEMORY.md`

Beide Seiten stehen lassen. Das ist eine Wissensdatei und kein Zustand.
