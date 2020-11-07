# DSCS Gruppenprojekt
## Proposal
Leonard Kehl, Dominik Buchegger

### Background
Wird in der Schweiz eine AG, GmbH oder Genossenschaft geschlossen, muss das noch vorhandene Vermögen liquidiert werden. Dazu müssen im Schweizerischen Handelsamtsblatt (SHAB) drei Schuldenrufe veröffentlicht werden. Melden Gläubiger dieser Gesellschaft ihre Ansprüche nicht innerhalb der Frist von 1 Monat nach dem letzten Schuldenruf an, gehen ihre Ansprüche verloren.

Es ist klar, dass es für Unternehmen und allenfalls sogar Privatpersonen notwendig ist, dieses Amtsblatt im Blick zu behalten, um bei Liquidationen anderer Gesellschaften nicht alle Ansprüche zu verlieren. Auf der Webseite shab.ch lassen sich aber nur einzelne Unternehmen suchen, was eher unpraktikabel ist.

### Grund App
Unsere App-Idee besteht aus 2 Teilen:

1.	Wir laden täglich (Wochentage) die neue Version des Amtsblatt als PDF herunter, lesen dieses in Python ein, extrahieren die Informationen daraus und speichern diese in einer Datenbank.

2.	Zusätzlich haben wir eine App auf einem Server, welche die Informationen aus dieser Datenbank abruft und es den Personen ermöglicht eine Liste von Unternehmensnamen einzugeben und daraus die Frist und die Kontaktadresse von allfälligen Unternehmen in Liquidation zu erhalten.

### Mögliche Erweiterungen
•	Fuzzy-matching für die Namen könnte sinnvoll sein. Im Moment keine Ahnung wie einbaubar.
•	Es können Accounts auf unserer Webseite erstellt werden und Namenslisten gespeichert werden. Sobald ein Eintrag in die Datenbank geladen wird, welcher mit der Namensliste übereinstimmt, werden die Nutzer benachrichtigt (Mail, SMS, …).
•	Es gibt auch noch sog. Erbenrufe, bei denen Gläubiger auch den Anspruch verlieren, wenn sie sich nicht melden. Diese werden jedoch i.d.R. nur kantonal (einige Kantone veröffentlichen diese auch im SHAB) veröffentlicht. Somit müssten Gläubiger jedes kantonale Amtsblatt prüfen. Die meisten Kantone veröffentlichen diese Amtsblätter zwar digital, jedoch sind einige Zugänge davon kostenpflichtig. Daher wäre dies sicherlich ein cooles Feature, aufgrund der unterschiedlichsten Formatierung jedes Amtsblatt und den verschiedenen Veröffentlichungen ist dies vielleicht eher zu aufwändig und bringt ggf. auch nicht so viel Mehrwert, da dies nur bei Erbschaften eine Rolle spielt, wenn ein sogenanntes öffentliches Inventar (also Auflistung Vermögen & Schulden des Erblassers) verlangt wird.
•	Allenfalls könnten auch bereits Templates für die Anmeldung der Forderung generiert werden.

### Schwierigkeiten in der Umsetzung
Das SHAB kann nur als PDF heruntergeladen werden. Daher braucht es eine automatisierte Umwandlung von PDF zu Text beim Einlesen in Python. Danach muss dieser existierende String so sliced werden, dass es einzelne Blöcke gibt und dann erneut so, dass die einzelnen Informationen für die Datenbank extrahiert werden können. Auch können diese Meldungen in unterschiedlichen Sprachen veröffentlicht werden, wodurch slicing basierend auf Wörtern erschwert wird.
