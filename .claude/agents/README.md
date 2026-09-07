# Agentendefinitionen

Zwei Subagenten, die dieses Projekt in seinen Regeln namentlich nennt:

| Datei | Agent | Wofür |
|---|---|---|
| `fable-reviewer.md` | `fable-reviewer` | Der Review-Lauf vor dem ersten Push jedes PR-Zweigs (`CLAUDE.md` → Git Rules, `docs/playbooks/BETRIEBSVERTRAG.md` Regel 11) |
| `fable-advisor.md` | `fable-advisor` | Zweitmeinung bei offenen Entwurfsfragen. **Nicht** auf einem fertigen Diff: dort erzeugt er Runden ohne Verhaltensänderung |

## Warum das eingecheckt ist

Dieselbe Begründung wie beim Gedächtnis nebenan (`../agent-memory/README.md`, Entscheidung vom 01.09.2026): sonst hängt es an der Maschine, auf der es entstanden ist.

Beim Gedächtnis war das Argument, dass Wissen verfällt. Hier ist es schärfer, weil gemessen: in der Cloud-Session vom 06.09.2026 war `fable-reviewer` **nicht aufrufbar**, und in der vom 07.09. erst, nachdem eine Session die Definitionen von Hand aus einem zweiten Repositorium geholt hatte. Der Container ist ephemer, die Repos werden beim Start frisch geklont, und alles außerhalb eines Repositoriums entsteht nicht neu. Ein eingechecktes Gedächtnis ohne eingecheckte Definition ist unbenutzbar, und Regel 11 ist dann nicht erfüllbar. Genau das ist am 06.09. passiert.

Auf einem Rechner mit eigenem Claude-Code-Setup ändert das etwas, und zwar mehr, als es zunächst aussieht. Dort liegt in `~/.claude/agents` eine Junction auf die Sammlung (`claude-code-setup/SETUP.md` Zeile 328). Die Vorrangtabelle in `code.claude.com/docs/en/sub-agents.md` gibt `.claude/agents/` den Rang 3 und `~/.claude/agents/` den Rang 4, und bei gleichem `name` überschreibt der höhere Rang den niedrigeren vollständig. **Ab diesem Check-in gewinnt also auch auf Christians Rechner die Kopie hier gegen die gepflegte Fassung**, sobald er in diesem Repositorium arbeitet. Das ist genau die Richtung, die der nächste Abschnitt teuer macht: driftet die Kopie, driftet sie unbemerkt auch dort, wo jemand glaubt, die Sammlung zu benutzen.

## Die Kopie und ihr Preis

Diese zwei Dateien sind **eine Kopie**. Sie stammen aus `chsteiner/claude-code-setup` (privat, `agents/`), Stand `9b033c8` vom 02.09.2026, kopiert am 07.09.2026, und dort werden sie gepflegt. Maßgeblich für den Abgleich ist der Quell-Commit, nicht der Kopiertag: wer später vergleicht, will wissen, welcher Stand der Sammlung hier liegt, und nicht, wann jemand `cp` getippt hat. Beide Bestände können auseinanderlaufen, und nichts prüft das: das Herkunftsrepositorium ist privat und steht der CI nicht zur Verfügung.

Das ist der Preis, der bei der Entscheidung bekannt war. Er wird bezahlt, weil die Alternative kein zweiter Bestand war, sondern gar keiner.

Wer beide Repositorien offen hat, gleicht so ab:

```bash
diff -u <setup>/agents/fable-reviewer.md .claude/agents/fable-reviewer.md
diff -u <setup>/agents/fable-advisor.md  .claude/agents/fable-advisor.md
```

Ist die Sammlung weiter, kopieren und den Stand oben mitziehen. Ist diese Kopie weiter, was vorkommen kann, wenn jemand hier etwas projektspezifisch geschärft hat, gehört die Änderung zurück in die Sammlung, sonst ist sie beim nächsten Abgleich weg.

## Was du beim Ändern wissen musst

- **`memory: project` im Vorspann des Reviewers** soll ihm laut Doku Schreibrechte auf `../agent-memory/fable-reviewer/` freischalten, obwohl seine `tools:`-Liste weder Write noch Edit nennt, und ihm zusätzlich `MEMORY.md` in den Systemprompt legen. Wer das Feld entfernt, nimmt ihm sein Gedächtnis, und die eingecheckten Dateien nebenan werden zu totem Text.

  **In der Cloud-Session vom 07.09.2026 hat beides nicht funktioniert, gemessen vom Agenten an sich selbst:** sein Werkzeugsatz war exakt die fünf aus `tools:`, ohne Write und ohne Edit, und die Einträge aus `MEMORY.md` standen nicht in seinem Systemprompt. Er konnte deshalb nichts schreiben. Die Ursache ist von innen nicht bestimmbar und hier nicht geklärt. Wer sich in einer Cloud-Session darauf verlässt, dass der Reviewer selbst mitschreibt, verlässt sich auf etwas, das dort einmal nachweislich nicht da war: dann trägt man seine Lehren von Hand nach.
- **Kein Em-Dash (U+2014)**, auch nicht in diesen Dateien. Sie sind Markdown, und `scripts/audit/check-no-em-dash.py` prüft in Markdown die Zeilen, die ein PR hinzufügt. Beim Check-in am 07.09. war der Bestand sauber (null Treffer in beiden Dateien).
- **Ein neu angelegtes `agents/`-Verzeichnis wird nicht nachgeladen.** Claude Code beobachtet die Agentenverzeichnisse zwar live, aber die erste Datei in einem frisch angelegten Verzeichnis braucht laut Doku einen Neustart der Session. Das Verzeichnis existiert jetzt, damit trifft die Ausnahme künftig nicht mehr zu.

## Was hier nicht hineingehört

Agenten, die nur zu einem Ticket gehören, und Agenten, die nichts mit diesem Korpus zu tun haben. Die zwei hier stehen in den Projektregeln; wer einen dritten hinzufügt, sollte ihn dort zuerst gebraucht haben.
