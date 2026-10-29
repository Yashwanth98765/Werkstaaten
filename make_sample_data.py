"""Creates SYNTHETIC sample Excel files in sample_data/ (same columns as the real exports)."""
import pandas as pd

DOKU_COLS = ["Bereich", "Stufe", "DOKU-Element", "Binnendifferenzierung", "Beispiel/Ziel", "Reflexion",
             "Erreicht/Nicht erreicht", "DOKU-Bogen Start", "DOKU-Bogen Ende", "Klient ID"]
a = "I 3a  Gefährdung von Sicherheit und Gesundheit am Arbeitsplatz feststellen und Maßnahmen zu ihrer Vermeidung ergreifen"
b = "I 3b  Berufsbezogene Arbeitsschutz- und Unfallverhütungsvorschriften anwenden"
c = "I 3c  Verhaltensweisen bei Unfällen beschreiben sowie erste Maßnahmen einleiten"
d = "I 3d  Vorschriften des vorbeugenden Brandschutzes anwenden. Verhaltensweisen bei Bränden beschreiben"
e = "I 4a  Zur Vermeidung betriebsbedingter Umweltbelastungen im beruflichen Einwirkungsbereich beitragen"
doku = [
    ["BBB 2. Jahr", "-3", a, "Beherrscht eine erlernte Grundlage der Arbeitssicherheit", "Nennt ein Gefahrensymbol",
     "Kennt die Gefahrensymbole, aber kann sie nicht immer richtig wiedergeben.", "erreicht", "", "", "27236"],
    ["BBB 2. Jahr", "-3", b, "Beherrscht eine erlernte berufsbezogene Arbeitsschutz- und Unfallverhütungsvorschrift", "Trägt Sicherheitsschuhe", "", "", "", "", "27236"],
    ["BBB 2. Jahr", "-3", c, "Kann eine erlernte Verhaltensweise bei Unfällen wiedergeben und beherrscht eine erlernte Maßnahme", "Holt bei Unfall Hilfe",
     "Im Bereich der Ersten Hilfe verfügt der Teilnehmer über punktuelles theoretisches Vorwissen, zeigt jedoch erhebliche Schwierigkeiten bei der praktischen Umsetzung. Aufgrund von Einschränkungen im Transfer- und Handlungsverständnis kann er das theoretische Wissen in konkreten Situationen nicht selbstständig anwenden.", "erreicht", "", "", "27236"],
    ["BBB 2. Jahr", "-3", d, "Beherrscht eine erlernte Vorschrift des vorbeugenden Brandschutzes", "Nennt die Vorschrift, dass kein Feuer gemacht werden darf", "", "", "", "", "27236"],
    ["BBB 2. Jahr", "-3", e, "Kann eine erlernte Umweltbelastung wiedergeben", "Benennt, dass Folie als Verpackungsmaterial nicht gut für die Umwelt ist", "", "", "", "", "27236"],
    # synthetic additions
    ["BBB 1. Jahr", "-2", a, "Erkennt mehrere Gefahrensymbole", "Ordnet Gefahrensymbole zu",
     "Konzentration lässt nach ca. 30 Minuten nach; mit ruhigem Arbeitsplatz und Pausenplan gelingt die Aufgabe deutlich besser.", "nicht erreicht", "", "", "28055"],
    ["BBB 1. Jahr", "-2", b, "Wendet eine Vorschrift an", "Trägt Gehörschutz an der Maschine",
     "Trägt den Gehörschutz zuverlässig, wenn er erinnert wird. Visuelle Erinnerungskarte am Arbeitsplatz hat geholfen.", "erreicht", "", "", "28055"],
    ["BBB 1. Jahr", "-1", c, "Beschreibt Verhalten bei Unfällen", "Holt bei Unfall Hilfe",
     "Handelt in Rollenspielen sicher, braucht aber Hilfe bei der Reihenfolge der Schritte. Bildkarten mit Schrittfolge unterstützen.", "erreicht", "", "", "28055"],
    ["BBB 1. Jahr", "0", e, "Erklärt einen Beitrag zum Umweltschutz", "Trennt Abfall richtig",
     "Arbeitet selbstständig und sorgfältig bei der Mülltrennung.", "erreicht", "", "", "28047"],
]
att = [[28057, f"{d} {w}", "", f"{d.upper()}_{w.upper()}", "111, H1"]
       for d in ("Montag", "Dienstag", "Mittwoch") for w in ("Kommen", "Gehen")]
clients = [
    ["Mainfränk. Werkst. Würzburg", "28057", "14.02.2004", "01.09.2026", "", "EV", "Bundesagentur für Arbeit", "Selbstfahrer"],
    ["Mainfränk. Werkst. Würzburg", "28047", "05.08.2006", "01.09.2026", "", "EV", "Bundesagentur für Arbeit", "Tour D1110 Würzburg"],
    ["Mainfränk. Werkst. Würzburg", "28059", "03.12.2005", "01.09.2026", "", "EV", "Bundesagentur für Arbeit", "Tour D1110 Würzburg"],
    ["Mainfränk. Werkst. Würzburg", "28055", "24.08.2006", "01.09.2026", "", "BBB1", "Bundesagentur für Arbeit", "Tour D1110 Würzburg"],
    ["Mainfränk. Werkst. Würzburg", "27236", "11.03.2004", "01.09.2024", "", "BBB2", "Bezirk Unterfranken", "Selbstfahrer"],  # synthetic
]
pd.DataFrame(doku, columns=DOKU_COLS).to_excel("sample_data/doku_bogen.xlsx", index=False)
pd.DataFrame(att, columns=["Klient ID", "DOKU-Element", "Angaben/Auswahl", "DOKU-Element Id", "Gruppe WfbM"]).to_excel("sample_data/anwesenheit.xlsx", index=False)
pd.DataFrame(clients, columns=["Einrichtung WfbM", "Klient ID", "Geburtsdatum", "Eintritt WfbM", "Austritt WfbM",
                               "Klientenstatus WfbM", "Kostenträger WfbM", "Fahrdienst"]).to_excel("sample_data/klienten.xlsx", index=False)
print("sample_data written")
