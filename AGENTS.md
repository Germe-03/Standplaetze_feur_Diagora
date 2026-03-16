

Regeln
- Nutze Deutsch für allen generierten Kontext.
- Bevorzuge es, bestehende Artefakte zu aktualisieren, statt neue zu erstellen.
- Erstelle Artefakte nur, wenn sie noch nicht existieren.
- Halte Artefakte so schlank wie möglich.
- Vermeide unnötige Kommentare im Code.
- Folge TDD (Tests vor Implementierung).
- Beachte Clean Architecture.
  - Verwende diese Abhängigkeitsrichtung: Model ← BusinessLogic ← UI
  - Für Persistenz gilt: Model ← BusinessLogic ← DataAccess ← Datenbank
  - Model enthält nur fachliche Modelle und Regeln.
  - BusinessLogic enthält Use Cases und Anwendungslogik.
  - UI enthält nur Darstellung, Eingaben und Steuerung.
  - DataAccess enthält Repository- und Persistenzlogik.
  - Datenbank ist nur das technische Speicher-Detail.
- Bevorzuge kleine vertikale Slices (ein Use Case Ende-zu-Ende).
- Wenn Anforderungen oder Architektur unklar sind, frage den Nutzer.