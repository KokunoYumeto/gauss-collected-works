# Carl Friedrich Gauss: Werke, Band VIII

## Nachträge zu den Bänden I, II, III

Diese Ausgabe enthält den achten Band in den ursprünglichen deutschen, lateinischen und französischen Texten. Sie umfasst die historischen Titelblätter und das Porträt, alle neun Abteilungen sowie die allgemeinen Bemerkungen, Berichtigungen, das Inhaltsverzeichnis und die Verlagsanzeige.

Die Abteilungen sind Arithmetik und Algebra; Analysis; Numerisches Rechnen; Wahrscheinlichkeitsrechnung; Grundlagen der Geometrie; Geometria Situs; Aufgaben und Lehrsätze der elementaren Geometrie angehörig; Verwendung complexer Grössen für die Geometrie; Theorie der krummen Flächen. Die gedruckten historischen Bemerkungen, Briefe, Fußnoten, Tabellen und mathematischen Zeichnungen gehören zum Text. Historische Berichtigungen stehen als eigener Bestandteil neben den unverändert wiedergegebenen mathematischen Aussagen.

Der Lesetext umfasst 440 PDF-Seiten. Lesezeichen erschließen die Abteilungen und die einzelnen Abhandlungen der Analysis. Die im Text genannten Seitenzahlen beziehen sich auf die historische Ausgabe. Die gedruckte Seitenzählung des Lesetextes beginnt in den einzelnen Teilbänden erneut; die Seitenanzeige des PDF-Programms zählt den gesamten Band fortlaufend. Die Schlussblätter haben ein größeres Seitenformat, damit das historische Inhaltsverzeichnis und die Verlagsanzeige lesbar bleiben. Leere historische Blätter und der moderne Bibliotheksumschlag enthalten keinen ergänzten Lesetext.

Das LaTeX-Paket enthält sämtliche bearbeitbaren Texte, Formeln, Tabellen und Zeichnungen. Das Porträt ist die einzige Rasterabbildung. Die Verzeichnisse unter `parts/` enthalten die vollständigen Satzquellen der aufeinanderfolgenden Teile. Die mathematischen Zeichnungen bestehen aus bearbeitbaren Pfaden und Beschriftungen; ihre Konturen geben auch Unregelmäßigkeiten der Vorlage wieder.

Der Text ist KI-transkribiert; auch der Vergleich mit den Druckvorlagen und der moderne Satz wurden von KI ausgeführt. Eine menschliche oder unabhängige Begutachtung wird nicht behauptet. Moderne Schriftzeichen, Satzabstände und die Annäherung der Zeichnungskonturen sind keine Identität mit historischen Drucktypen oder Kupferstichen. Beschädigte oder abgeschnittene Stellen wurden, soweit vorhanden, mit weiteren Fotografien der gedruckten Ausgabe verglichen. Insbesondere liefert eine vollständige alternative Fotografie den rechten, im Hauptscan abgeschnittenen Teil der historischen Seite 95. Mehrdeutige Zeichen behalten die bei ihrer Lesung festgehaltenen Einschränkungen; mathematische Unregelmäßigkeiten werden nicht stillschweigend berichtigt. Ein älterer Erweiterungsfont bei den Knotentabellen besitzt keine vollständige Unicode-Zuordnung, obwohl seine Zeichen im PDF sichtbar und im LaTeX bearbeitbar sind.

## Satz aus den Quellen

Erforderlich sind XeLaTeX, die in den Teilquellen geladenen Standardpakete, Latin Modern und die dort angegebene Schrift für kyrillische Zeichen sowie Python mit PyMuPDF. Unter Windows führt `build_volume.ps1` je zwei XeLaTeX-Durchläufe pro Teil aus und erstellt anschließend den zusammenhängenden Lesetext. Optional können die Programme mit `-Python` und `-XeLaTeX` angegeben werden. Das Skript beansprucht den gemeinsamen TeX-Slot ohne Wartezeit; ist er belegt, startet kein Compiler.

Alternativ wird in jedem Verzeichnis `parts/<Teil>/` zweimal `xelatex -output-directory=build -jobname=source source.tex` ausgeführt; das Unterverzeichnis `build` muss zuvor angelegt werden. Danach erzeugt `python assemble_reader.py --output Gauss_Werke_VIII.pdf` den Lesetext mit Lesezeichen und Verweisen. Die Zusammensetzung erfolgt aus neu gesetzten LaTeX-Seiten; eingescannte Seiten sind kein Bestandteil des Satzes. `volume.json` legt die Reihenfolge der Teile fest.


This is an AI-transcribed original-language edition with AI-produced typesetting. Historical authorship and inherited editorial contributions retain their printed credits. Authorship, source identity and rights notices appear in RIGHTS_AND_CREDITS.md.
