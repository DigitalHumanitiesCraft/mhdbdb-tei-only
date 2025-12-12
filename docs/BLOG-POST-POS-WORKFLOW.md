---
layout: post
title: "Der Synthetische Philologe: System 1.42 in der Praxis"
author: "Christopher Pollin"
date: 2025-12-10
published: false

# Spezifische Metadaten für diesen Post
citation:
  type: "blog-post"
  container-title: "Digital Humanities Craft"
  URL: "https://dhcraft.org/excellence/blog/The-Synthetic-Philologist"
  language: "de"
  abstract: "Wie bringt man einem 'halluzinierenden Reasoner' (System 1.42) bei, sich an strenge philologische Regeln zu halten? Dieser Beitrag demonstriert einen konkreten Workflow für die PoS-Disambiguierung mittelhochdeutscher Texte mittels Gemini 3 Pro. Anstatt sich auf die 'Vibes' des Modells zu verlassen, betten wir es in ein rigides Python-Scaffolding ein, das die Rolle des 'Critical-Expert-in-the-Loop' übernimmt. Das Ergebnis ist kein Chat, sondern eine deterministische Pipeline, die stochastische Intuition in strukturierte Forschungsdaten verwandelt."
  
dublin_core:
  creator: "Christopher Pollin"
  publisher: "Digital Humanities Craft"
  subject: ["Applied Generative AI", "LLM", "Digital Humanities", "Middle High German", "Workflow Automation"]
  description: "Dieser Beitrag demonstriert einen konkreten Workflow für die PoS-Disambiguierung mittelhochdeutscher Texte mittels Gemini 3 Pro. Er zeigt, wie Frontier-LLMs durch 'Promptotyping' und strikte Validierungsskripte von stochastischen Chatbots zu zuverlässigen Komponenten in einer wissenschaftlichen Pipeline transformiert werden können."
  type: "Blogpost"
  format: "text/html"
  rights: "CC BY 4.0"
  language: "de"

schema_type: "BlogPosting"
keywords: ["LLM", "Gemini 3 Pro", "Digital Humanities", "Middle High German", "PoS Tagging", "System 1.42", "Critical Expert in the Loop"]

website_title: "Digital Humanities Craft"
website_type: "Blog"
short_title: "Der Synthetische Philologe"
abstract: "Wie bringt man einem 'halluzinierenden Reasoner' (System 1.42) bei, sich an strenge philologische Regeln zu halten? Dieser Beitrag demonstriert einen konkreten Workflow für die PoS-Disambiguierung mittelhochdeutscher Texte mittels Gemini 3 Pro."
---

![][image1]

In meinem letzten Beitrag zu **System 1.42**[^1] habe ich Frontier-LLMs als "halluzinierende Reasoner" charakterisiert: Systeme, die erstaunlich plausible Gedankengänge simulieren, ohne jedoch über eine verlässliche interne Selbstüberprüfung (System 2) zu verfügen. Für die Digital Humanities stellt dies ein fundamentales Problem dar. Unsere Arbeit basiert auf Präzision, nicht auf Plausibilität. Ein Part-of-Speech (PoS) Tag ist entweder korrekt oder falsch; "halluzinierte Korrektheit" reicht nicht aus.

Doch was passiert, wenn wir dieses "System 1.42" nicht als Orakel, sondern als **stochastische Komponente in einem deterministischen Workflow** betrachten?

In diesem Beitrag stelle ich ein konkretes Experiment vor: Die Disambiguierung von Part-of-Speech-Tags in mittelhochdeutschen (MHD) Texten mittels **Gemini 3 Pro**. Wir nutzen dabei Methoden des **Promptotyping**[^2], um dem Modell eine philologische "Verfassung" zu geben, und zwingen es durch ein Python-basiertes Validierungsgerüst in die Rolle eines disziplinierten "Junior Researchers". Das Ergebnis ist ein **Synthetischer Philologe**, der nicht mehr "vibe-codet", sondern systematisch und nachvollziehbar Entscheidungen trifft.

## **Das Problem: Wenn Statistik auf Geschichte trifft**

Klassische NLP-Tools (wie TreeTagger oder RFTagger) arbeiten stochastisch. Sie lernen Wahrscheinlichkeiten: "Wenn *der* vor einem Substantiv steht, ist es zu 99% ein Artikel." Bei standardisierten Sprachen funktioniert das hervorragend.

Mittelhochdeutsch ist jedoch, gelinde gesagt, "messy". Es gibt keine standardisierte Orthographie. Ein Wort wie *sêre* kann je nach Kontext ein Adverb ("sehr"), ein Adjektiv ("wund") oder ein Substantiv ("Schmerz") sein. Ein statistisches Modell, das auf modernem Deutsch trainiert ist (oder selbst eines, das MHD "kennt", aber nur auf Oberflächenformen schaut), scheitert hier oft grandios.

Ein klassisches Beispiel für das Versagen von LLMs im "Vibe-Modus": Das Wort *niht*. Im modernen Deutsch kennen wir *nicht* (Negation) und *nichts* (Pronomen). Im Mittelhochdeutschen ist *niht* jedoch **immer** eine Negationspartikel (Tag: `NEG`), auch wenn es an einer Stelle steht, wo wir heute ein Pronomen erwarten würden. Ein LLM, das nur "vibed", taggt es oft fälschlicherweise als `PRO`, weil es die moderne Analogie zieht.

Um dieses Problem zu lösen, reicht kein besserer Prompt. Wir brauchen eine Architektur, die das Modell zwingt, **Regeln über Wahrscheinlichkeiten** zu stellen.

## **Die Methode: Promptotyping einer Reasoning-Engine**

Anstatt mit dem LLM zu chatten, behandeln wir es als eine Funktion: `Input: XML-Chunk -> Output: Diff-Liste`.

### **1. Die Verfassung (Das Regelwerk)**
Basierend auf dem Promptotyping-Ansatz haben wir ein striktes Regelwerk (`.agent/workflows/pos-disambiguator.md`) erstellt. Dieses Dokument ist nicht nur eine Anleitung, sondern die "Konstitution" des Modells für diese Session. Es enthält explizite "Forbidden Actions" und "Known Error Patterns".

Zum Beispiel:
> **Rule:** ALL negation forms of the type *niht / ne / nit* etc. → **NEG**, NEVER PRO.

Das Modell "liest" diese Regeln und hält sie im Context Window aktiv, während es den Text analysiert. Das ist der entscheidende Unterschied zu früheren Modellen (wie GPT-3). Das Context Window von Gemini 3 Pro ist groß und stabil genug, um diese Meta-Instruktionen *gleichzeitig* mit den komplexen MHD-Satzstrukturen zu verarbeiten, ohne die Regeln zu "vergessen".

### **2. Attention Density durch Chunking**
Wir haben festgestellt, dass selbst Frontier-Modelle bei zu langen Texten "driften". Sie werden nachlässig. Daher zerlegen wir den TEI-Text per Skript in kleine Häppchen von **500 Wörtern**. 

Warum 500? Das ist eine Frage der **Attention Density**. Bei 500 Wörtern zwingen wir das Modell, jedem einzelnen Token maximale Aufmerksamkeit zu schenken. Es kann nicht "querlesen". Der Kontext ist eng genug, um präzise zu bleiben, aber weit genug (durch Overlap), um Satzgrenzen zu verstehen.

### **3. Der Output: Ein erklärbares Diff**
Wir bitten das Modell nicht, den Text neu zu schreiben (Gefahr von Halluzination!). Wir fordern eine strukturierte Liste von Änderungen:

```markdown
ABG_123 | ADV CNJ → ADV | high | adverb in comparative context
```

Besonders wichtig ist das Feld `reason`. Hier muss das Modell seine Entscheidung begründen. Das ist der externalisierte "Chain of Thought". Es macht die Entscheidung des Modells **explicable** (nachvollziehbar).

## **Der Critical-Expert-in-the-Code: Die Validierungsschleife**

Bis hierher ist es nur gutes Prompt Engineering. Der eigentliche Durchbruch ("System 2") passiert **außerhalb** des Modells. Wir haben ein Python-Gerüst gebaut, das als strenger Professor fungiert.

### **Der Refinement-Loop**
Das LLM ist faul (System 1). Wenn es ein Wort nicht versteht oder unsicher ist, neigt es dazu, es einfach zu überspringen. In einem Chat würde das niemand merken. In unserem Workflow fällt das sofort auf.

1.  **Detection:** Ein Skript (`find-missing-decisions.py`) vergleicht den Input-Chunk mit dem Output des Modells.
2.  **Rejection:** Fehlen Entscheidungen? Hat das Modell ein Wort ausgelassen?
3.  **Refinement:** Wenn ja, generiert das System automatisch einen `_FIX`-Task: *"Du hast folgende 4 Wörter im Chunk 013 vergessen. Analysiere sie jetzt."*

Das zwingt das Modell, seinen "System 1"-Impuls (Überspringen) zu unterdrücken und in den "System 2"-Modus zu wechseln. Wir haben beobachtet, wie das Modell beim zweiten Durchlauf oft korrekte, tiefgründige Analysen für Wörter lieferte, die es beim ersten Mal "übersehen" wollte.

**Das Paradoxon der Ambiguität:**
Interessanterweise stießen wir hier auf ein "System 1.42"-Problem. Unsere ursprüngliche Anweisung lautete: "Wenn du dir absolut unsicher bist, überspringe das Wort." Das Modell, sehr gehorsam, übersprang daraufhin wirklich schwierige, ambige Stellen. Unser Validierungsskript interpretierte dies jedoch als Fehler ("Missing Decision") und schickte das Modell in eine Endlosschleife.
Die Lösung? Wir mussten die Anweisung ändern: **"Make a Best Guess."** Wir zwingen das Modell zur Entscheidung, markieren diese aber mit `confidence='low'`. Das ist wissenschaftlich ehrlicher: Eine markierte Unsicherheit ist besser als eine Datenlücke.

## **Fazit: Vom Vibe zur Philologie**

Dieses Experiment zeigt, dass LLMs in den Digital Humanities weit mehr sein können als "Stochastic Parrots". Wenn wir sie in eine rigide Architektur einbetten, die ihre stochastische Natur durch deterministische Validierung einhegt, erhalten wir ein mächtiges Werkzeug.

Der "Synthetische Philologe" ersetzt den Menschen nicht. Er skaliert dessen Intuition. Das Modell übernimmt die Kärrnerarbeit der Disambiguierung, liefert aber zu jeder Entscheidung eine Begründung mit. Der menschliche *Critical Expert* muss nicht mehr 50.000 Wörter taggen, sondern nur noch die 500 Entscheidungen prüfen, bei denen das Modell selbst unsicher war oder die Validierungsskripte Alarm geschlagen haben.

Wir haben System 1.42 nicht repariert – es halluziniert immer noch. Aber wir haben gelernt, seine Halluzinationen so eng zu führen, dass sie als **produktive Hypothesen** in einem wissenschaftlichen Prozess nutzbar werden.

[^1]:  Christopher Pollin. System 1.42: Wie (Frontier-)LLMs “tatsächlich” funktionieren. [https://dhcraft.org/excellence/blog/System1-42](https://dhcraft.org/excellence/blog/System1-42)

[^2]:  Christopher Pollin. Promptotyping: Von der Idee zur Anwendung. [https://dhcraft.org/excellence/blog/Promptotyping](https://dhcraft.org/excellence/blog/Promptotyping)

[image1]: img/synthetic-philologist.png
