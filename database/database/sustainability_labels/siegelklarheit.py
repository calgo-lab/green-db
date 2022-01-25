from datetime import datetime
from typing import Dict, Union

from core.domain import LabelIDType, SustainabilityLabel

information_from = datetime(2022, 1, 25, 12)

# flake8: noqa
__label_information: Dict[str, Dict[str, Union[str, int]]] = {
    LabelIDType.BE_L_CO.name: {
        "name": "Blauer Engel - Laptops & Co.",
        "description": "Ziel dieses Blauen Engel für Computer (DE-UZ 78,) ist es, Geräte auszuzeichnen, die einen geringen Energieverbrauch haben, langlebige und recyclinggerechte Konstruktion aufweisen und umweltbelastende Materien vermeiden.",
        "credibility_evaluation": 73,
        "ecological_evaluation": 61,
        "social_evaluation": 0,
    },
    LabelIDType.BE_P.name: {
        "name": "Blauer Engel - Papier",
        "description": "Das Siegel kennzeichnet Papier, welches zu 100% aus Altpapier hergestellt ist (DE-UZ 14a). Beim ökologischen Systemvergleich schneiden Papierprodukte aus Altpapier gegenüber Papierprodukten aus Primärfasern, die Holz als Faserrohstoffquelle nutzen, im Hinblick auf Ressourcenverbrauch, Abwasserbelastung, Wasser- und Energieverbrauch wesentlich besser ab – bei vergleichbaren Gebrauchseigenschaften der Produkte. Zusätzlich werden Anforderungen an den Chemikalieneinsatz gestellt, so sind beispielsweise bei der Herstellung der Einsatz von Chlor, halogenierten Bleichmitteln und biologisch schwer abbaubaren Komplexbildnern verboten.",
        "credibility_evaluation": 79,
        "ecological_evaluation": 60,
        "social_evaluation": 0,
    },
    LabelIDType.BE_T.name: {
        "name": "Blauer Engel - Textilien",
        "description": "Das Siegel kennzeichnet Textilien, die ohne gesundheitsgefährdende Chemikalien und unter Einhaltung hoher Umweltstandards hergestellt wurden. Die Produkte müssen außerdem gute Gebrauchseigenschaften aufweisen. Das Siegel für Textilien basiert auf der Vergabekriterien DE-UZ 154.",
        "credibility_evaluation": 93,
        "ecological_evaluation": 78,
        "social_evaluation": 39,
    },
    LabelIDType.BE_WR.name: {
        "name": "Blauer Engel - Wasch- & Reinigungsmittel",
        "description": "Das Siegel kennzeichnet Wasch- und Reinigungsmittel, die so hergestellt wurden, dass sie in ihrer Erzeugung, Verwendung und Entsorgung möglichst umwelt- und gesundheitsverträglich sind ohne Sie sollen dazu beitragen, Risiken für die Umwelt und die menschliche Gesundheit bei der Verwendung gefährlicher Stoffe zu verringern und zu verhüten, sowie den Verpackungsabfall zu minimieren. Die Schonung natürlicher Ressourcen ist ebenfalls ein wichtiges Anliegen des Umweltzeichens. Reinigungsmittel mit dem Blauen Engel sollen dadurch einen Beitrag leisten, indem bei ihrer Herstellung nachwachsende Rohstoffe eingesetzt werden, die unter nachhaltigen Bedingungen angebaut wurden bzw. die den nachhaltigen Anbau fördern.",
        "credibility_evaluation": 73,
        "ecological_evaluation": 72,
        "social_evaluation": 0,
    },
    LabelIDType.ECOCERT.name: {
        "name": "ECOCERT",
        "description": "Der Standard hat zum Ziel, ein Set anspruchsvoller Kriterien zu definieren, die Umwelt- und Nachhaltigkeitsanforderungen an den Herstellungsprozess und das gesamte Produkt beinhalten, insbesondere im Hinblick auf Rohstoffe natürlichen Ursprungs und recycelbare Verpackungen.",
        "credibility_evaluation": 64,
        "ecological_evaluation": 84,
        "social_evaluation": 0,
    },
    LabelIDType.EU_ECO_T.name: {
        "name": "EU Ecolabel - Textilien",
        "description": "Ziel des EU Ecolabels ist, Verbraucher:innen einen Hinweis auf umweltfreundlichere Produkte und Dienstleistungen zu geben. Das Siegel kennzeichnet sowohl Natur- als auch Kunstfasertextilien. Alle Anforderungen müssen unmittelbar erfüllt werden. Das Siegel definiert Anforderungen an umweltfreundliche Prozesse entlang des gesamten Produktionsweges.",
        "credibility_evaluation": 92,
        "ecological_evaluation": 73,
        "social_evaluation": 32,
    },
    LabelIDType.FS.name: {
        "name": "Fair Stone",
        "description": "Schwerpunkt ist die Verbesserung der Arbeitsbedingungen in Steinbrüchen und steinverarbeitenden Betrieben in Entwicklungs- und Schwellenländern.",
        "credibility_evaluation": 61,
        "ecological_evaluation": 52,
        "social_evaluation": 71,
    },
    LabelIDType.FWF.name: {
        "name": "Fair Wear Foundation",
        "description": "Ziel ist, die Arbeitsbedingungen in Unternehmen der Textilindustrie weltweit zu verbessern. Der Schwerpunkt liegt dabei auf Betrieben, in denen Textilien genäht werden.",
        "credibility_evaluation": 95,
        "ecological_evaluation": 0,
        "social_evaluation": 79,
    },
    LabelIDType.FT_B.name: {
        "name": "Fairtrade - Baumwolle",
        "description": "Das Siegel „Fairtrade Baumwolle“ steht für sozialverträgliche Lebens- und Arbeitsbedingungen in der Baumwollproduktion. Es richtet sich insbesondere an Kleinbauern. Die Lizenzgebühren und ein Anteil des Fairtrade-Aufpreises werden für Projekte in den Produktionsländern genutzt. Das Siegel stellt außerdem Anforderungen an einen umweltverträglichen Baumwollanbau.",
        "credibility_evaluation": 91,
        "ecological_evaluation": 56,
        "social_evaluation": 72,
    },
    LabelIDType.FT_TP.name: {
        "name": "Fairtrade Textile Production",
        "description": "Das Siegel „Fairtrade - Textilien“ zielt darauf ab, die Lebens- und Arbeitsbedingungen der Arbeiterinnen und Arbeiter in der Textilindustrie zu verbessern. Außerdem unterstützt es eine umweltverträgliche Produktion. Das Siegel beinhaltet auch, Händler von Textilien mit Hilfe von Lizenzverträgen zu fairen Handelsbedingungen zu verpflichten.",
        "credibility_evaluation": 93,
        "ecological_evaluation": 35,
        "social_evaluation": 70,
    },
    LabelIDType.GOTS.name: {
        "name": "Global Organic Textile Standard",
        "description": "Ziel des Standards ist es, entlang der gesamten textilen Lieferkette strenge Anforderungen an die ökologischen und sozialen Bedingungen bei der Textil- und Bekleidungsherstellung mit ökologisch erzeugten Rohstoffen festzulegen.",
        "credibility_evaluation": 89,
        "ecological_evaluation": 75,
        "social_evaluation": 66,
    },
    LabelIDType.IVN_NL.name: {
        "name": "IVN Naturleder",
        "description": "Ziel des IVN Naturleder Siegels ist es, die Herstellung von Lederwaren ökologischer, sozialverträglicher und gesünder zu gestalten. Anforderungen stellt das Siegel deshalb vor allem in den Bereichen Umweltbelastung, Gefahrenstoffe, Entsorgung und Recyclingfähigkeit des Leders, Gesundheit sowie gerechten Arbeitsbedingungen. Das Siegel deckt alle Herstellungsstufen von der Rohware bis zum Verkauf und Gebrauch des fertigen Leders (jedoch nicht des verarbeiteten Lederprodukts) ab.",
        "credibility_evaluation": 82,
        "ecological_evaluation": 87,
        "social_evaluation": 73,
    },
    LabelIDType.NCP.name: {
        "name": "Nature Care Products Standard ",
        "description": "NCP (Nature-Care-Product-Standard) bietet eine einfache Umwelt-Kennzeichnung für Gegenstände des täglichen Bedarfs. Das Siegel ist für alle Non-Food-Produkte aus nachwachsenden Rohstoffen, wie Wasch- und Reinigungsmittel, Hygieneartikel, Pflegemittel für Gegenstände, Spielzeug, Kerzen oder Düngemittel, die aus natürlichen Inhaltstoffen bestehen und die Umwelt nicht unnötig belasten, konzipiert. Diese Zertifizierung schließt die Regelungslücke im ökologischen Non-Food-Bereich und definiert so notwendige Maßstäbe für echte nachhaltige Naturprodukte.",
        "credibility_evaluation": 73,
        "ecological_evaluation": 72,
        "social_evaluation": 8,
    },
    LabelIDType.NL_T.name: {
        "name": "Naturland - Textilien",
        "description": "Naturland verbindet Ökologischen Landbau mit Sozialer Verantwortung und Fairem Handel - regional und weltweit. Das Ziel ist der Erhalt einer gemeinsamen Lebensgrundlage durch umfassende Nachhaltigkeit entlang der gesamten Wertschöpfungskette - ganz im Sinne der globalen Nachhaltigkeitsziele der UN (SDGs). Im Textil-Bereich kennzeichnet das Naturland-Siegel Produkte aus Bio-Baumwolle, bei deren Produktion und Verarbeitung ökologische, aber auch soziale Anforderungen erfüllt werden. Textilien, die mit dem Naturland Siegel zertifiziert sind, müssen zu mindestens 95% aus ökologisch erzeugten Naturfasern bestehen.",
        "credibility_evaluation": 83,
        "ecological_evaluation": 88,
        "social_evaluation": 61,
    },
    LabelIDType.IVN_NT_BEST.name: {
        "name": "Naturtextil IVN zertifiziert BEST",
        "description": "Der Standard spiegelt seit 2000 die IVN entworfenen Richtlinien für Naturtextilien wider und bildet die gesamte textile Produktionskette ab, in ökologischer und sozialverantwortlicher Hinsicht. Schwerpunkt ist der Einsatz von 100% natürlichen Bio-Fasern.",
        "credibility_evaluation": 82,
        "ecological_evaluation": 96,
        "social_evaluation": 72,
    },
    LabelIDType.NE_WR.name: {
        "name": "Nordic Ecolabel - Wasch- & Reinigungsmittel",
        "description": "Das Nordic Swan Ecolabel verfolgt das Ziel, die Umweltbelastung durch die Produktion und den Konsum von Waren und Dienstleistungen zu reduzieren - und es Verbrauchern und professionellen Einkäufern leicht zu machen, die umweltfreundlichsten Waren und Dienstleistungen auszuwählen. Das Nordic Ecolabel zeichnet auch umweltfreundliche Wasch- und Reinigungsmittel aus. Die ausgezeichneten Produkte haben beispielsweise eine hohe Abbaubarkeit im Wasser und beinhalten wenige gefährliche Materialien.",
        "credibility_evaluation": 75,
        "ecological_evaluation": 80,
        "social_evaluation": 8,
    },
    LabelIDType.MIG_OEKO_TEX.name: {
        "name": "OEKO-TEX Made in Green",
        "description": "MADE IN GREEN by OEKO-TEX® ist ein nachverfolgbares Produktsiegel für alle Arten von Textilien und Lederartikel, die in umweltfreundlichen Betrieben und an sicheren und sozialverträglichen Arbeitsplätzen produziert wurden. Zudem gibt das MADE IN GREEN Siegel Konsument:innen die Gewissheit, dass das das Textil- oder Lederprodukt aus schadstoffgeprüften Materialien besteht.",
        "credibility_evaluation": 76,
        "ecological_evaluation": 80,
        "social_evaluation": 80,
    },
    LabelIDType.SA8000.name: {
        "name": "SA8000",
        "description": "Die Norm SA8000 und das Zertifizierungssystem bieten einen Rahmen für Organisationen aller Art, in jeder Branche und in jedem Land, um ihre Geschäfte in einer Weise zu führen, die fair und menschenwürdig für die Arbeitnehmer:innen ist, und um ihre Einhaltung höchster Sozialstandards zu demonstrieren. Die SA8000-Norm basiert auf international anerkannten Standards für menschenwürdige Arbeit, einschließlich der Allgemeinen Erklärung der Menschenrechte, der IAO-Konventionen und der nationalen Gesetze. SA8000 wendet einen Managementsystem-Ansatz auf die soziale Leistung an und legt den Schwerpunkt auf kontinuierliche Verbesserung, nicht auf eine Prüfung nach Checklisten.",
        "credibility_evaluation": 90,
        "ecological_evaluation": 2,
        "social_evaluation": 74,
    },
    LabelIDType.TCO_N.name: {
        "name": "TCO Certified Notebooks 8.0",
        "description": "Ziel von TCO ist es, den Fortschritt hin zu nachhaltigen IT-Produkten voranzutreiben. Zertifizierte Produkte müssen während des gesamten Lebenszyklus umfassende ökologische und soziale Kriterien erfüllen. So müssen die Fabriken, in denen zertifizierte Produkte hergestellt werden, Kriterien zu Arbeitszeiten, Arbeitsumgebung und Löhnen einhalten. Die Produkte müssen Kriterien für Energieeffizienz, ergonomisches Design und einen begrenzten Gehalt an gefährlichen Stoffen erfüllen. Unabhängige, akkreditierte Organisationen verifizieren, dass Fabriken und Produkte alle Kriterien in TCO Certified erfüllen. Die Verifizierung erfolgt sowohl vor als auch nach der Ausstellung des Zertifikats und deckt den gesamten Gültigkeitszeitraum ab.",
        "credibility_evaluation": 80,
        "ecological_evaluation": 68,
        "social_evaluation": 45,
    },
    LabelIDType.TCO_S.name: {
        "name": "TCO Certified Smartphones 8.0",
        "description": "Ziel von TCO ist es, den Fortschritt hin zu nachhaltigen IT-Produkten voranzutreiben. Zertifizierte Produkte müssen während des gesamten Lebenszyklus umfassende ökologische und soziale Kriterien erfüllen. So müssen die Fabriken, in denen zertifizierte Produkte hergestellt werden, Kriterien zu Arbeitszeiten, Arbeitsumgebung und Löhnen einhalten. Die Produkte müssen Kriterien für Energieeffizienz, ergonomisches Design und einen begrenzten Gehalt an gefährlichen Stoffen erfüllen. Unabhängige, akkreditierte Organisationen verifizieren, dass Fabriken und Produkte alle Kriterien in TCO Certified erfüllen. Die Verifizierung erfolgt sowohl vor als auch nach der Ausstellung des Zertifikats und deckt den gesamten Gültigkeitszeitraum ab.",
        "credibility_evaluation": 80,
        "ecological_evaluation": 62,
        "social_evaluation": 52,
    },
    LabelIDType.XX_PLUS.name: {
        "name": "Xertifix PLUS",
        "description": "XertifiX überprüft regelmäßig Fabriken und Steinbrüche in Indien, China und Vietnam, um sicherzustellen, dass die Standardkriterien erfüllt werden: Der Standard umfasst die IAO-Kernarbeitsabkommen, darunter das Verbot von Kinderarbeit und Sklaverei, einen besseren Schutz der Gesundheit und Sicherheit von erwachsenen Arbeitnehmer:innen, gerechte Löhne und Arbeitszeiten, Umweltschutz und Rechtmäßigkeit. Wenn die Anforderungen erfüllt sind, stellt XertifiX Zertifikate für die Steine aus.",
        "credibility_evaluation": 64,
        "ecological_evaluation": 80,
        "social_evaluation": 60,
    },
    LabelIDType.BLUES_P.name: {
        "name": "bluesign® product",
        "description": "Ziel des Siegels ist, die Umwelteinflüsse der Textilindustrie zu verringern. Es steht außerdem für die sichere Herstellung und Verarbeitung von Kunst- und Naturfasern.",
        "credibility_evaluation": 79,
        "ecological_evaluation": 75,
        "social_evaluation": 52,
    },
    LabelIDType.OE_UZ.name: {
        "name": "Austrian Ecolabel (ÖUZ)",
        "description": "Die Auszeichnung erhalten nur jene Produkte und Dienstleistungen, die neben einer Vielzahl an Umweltkriterien auch Anforderungen an Qualität und Langlebigkeit erfüllen. Papier für Bürokommunikation, Zeitungen und Magazine muss hohe Qualitätsanforderungen erfüllen - mit dem Umweltzeichen erfüllt es auch den besten Stand der Umwelttechnik. Es besteht zu 100 Prozent aus Recycling- oder gänzlich chlorfrei gebleichtem Papier und bei der Herstellung wird auf optimale und umweltgerechte Nutzung der Rohstoffe geachtet: - Der Faserstoff von Schreib-, Kopier, EDV- und Druckpapier besteht zur Gänze aus Altpapier, 60 Prozent davon aus unteren und mittleren Sorten was dazu beiträgt, dass auch mindere Papierqualitäten wiederverwertet werden - Hochqualitatives Papier für Tintenstrahl- und Hochleistungslaserdrucker sowie Papier für Zeitungen, Zeitschriften und Magazine wird nur aus Holz hergestellt, das zu 50 Prozent aus nachhaltiger Forstwirtschaft stammt - Bei der Herstellung aller Papiersorten gibt es strikte Beschränkungen für den Einsatz von gesundheits- oder umweltgefährdenden Chemikalien sowie strenge Grenzwerte für die Schadstoff-Belastung von Luft und Wasser. - Für Produkte aus Recyclingpapier muss der Faserstoff zu 100 % aus Altpapier bestehen. Je nach Produktgruppe wird der Einsatz von mindestens 50 % Unteren und Mittleren Sorten gefordert. Dies trägt dazu bei, dass auch haushaltsübliche Papierqualitäten einem Recyclingprozess zugeführt werden.",
        "credibility_evaluation": 30,
        "ecological_evaluation": 53,
        "social_evaluation": 5,
    },
    LabelIDType.BE_LE.name: {
        "name": "Blauer Engel - Leder",
        "description": "Das Siegel für Leder basiert auf den Vergabekriterien DE-UZ 148. Leder können aufgrund ihrer großen Oberfläche und ihrer langen Lebensdauer eine wesentliche Quelle für Schadstoffe in Innenräumen sein. Schadstoffe, die die Gesundheit und Umwelt belasten können, stammen in der Regel vom Gerbprozess und von der Konservierung des Leders. Der Blaue Engel für emissionsarme Leder signalisiert, dass bei den ausgezeichneten Ledern die Umwelt- und Gesundheitsbelastungen von der Produktion über die gesamte Nutzungsdauer, bis hin zur Verwertung und Entsorgung minimiert sind. Das Umweltzeichen eröffnet z. B. die Möglichkeit, dass Polstermöbelhersteller und auch der handwerkliche Polsterer für ihre Produkte gezielt emissionsarmen Polsterleder mit dem Blauen Engel auswählen und damit dem Verbraucher ein gesundheitlich unbedenkliches Polstermöbel anbieten können.",
        "credibility_evaluation": 73,
        "ecological_evaluation": 50,
        "social_evaluation": 16,
    },
    LabelIDType.CTC_T_PLATIN.name: {
        "name": "Cradle to Cradle - Textilien - Platin Level",
        "description": "Materialien und Produkte, die die Anforderungen des Cradle to Cradle Certified Product Standard erfüllen, können die Cradle to Cradle-Zertifizierung erhalten. Der Cradle to Cradle Certified Product Standard bewertet die Sicherheit, Kreislauffähigkeit und Verantwortung von Materialien und Produkten in fünf Kategorien der Nachhaltigkeitsleistung: Materialgesundheit, Kreislauffähigkeit des Produkts, saubere Luft und Klimaschutz, Wasser- und Bodenverantwortung sowie soziale Fairness. Um eine Produktzertifizierung zu erhalten, müssen die Unternehmen mit einem unabhängigen Prüfer zusammenarbeiten, um den Leistungsgrad eines Produkts in den fünf Nachhaltigkeitskategorien zu ermitteln. Dem Produkt wird dann für jede Kategorie eine Leistungsstufe zugewiesen (Bronze, Silber, Gold, Platin).",
        "credibility_evaluation": 85,
        "ecological_evaluation": 59,
        "social_evaluation": 1,
    },
    LabelIDType.EU_ECO_P.name: {
        "name": "EU Ecolabel - Papier",
        "description": "Das Siegel stellt Anforderungen an den gesamten Herstellungsprozess des Papiers. Um Wasser und Luft zu schonen, wird der Chemikalieneinsatz beschränkt. Das verwendete Material muss außerdem zu mindestens 70% recycelt sein und/oder von externen Zertifizierungssystemen, wie beispielsweise FSC und PEFC, zertifiziert sein.",
        "credibility_evaluation": 61,
        "ecological_evaluation": 51,
        "social_evaluation": 0,
    },
    LabelIDType.ECO_GARANTIE.name: {
        "name": "Ecogarantie ®",
        "description": "Das Siegel kennzeichnet Wasch- und Reinigungsmittel, die überwiegend aus ökologisch angebauten Inhaltsstoffen bestehen. Zudem werden weitere umweltschonende Anforderungen gestellt. Diese beziehen sich zum Beispiel auf die Abbaubarkeit und die Toxizität des Produkts.",
        "credibility_evaluation": 64,
        "ecological_evaluation": 74,
        "social_evaluation": 2,
    },
    LabelIDType.FLA.name: {
        "name": "Fair Labor Association",
        "description": "Der FLA-Verhaltenskodex für Arbeitsplätze legt Arbeitsstandards fest, die darauf abzielen, menschenwürdige Arbeitsbedingungen in Fabriken und auf Farmen zu erreichen. Die FLA-Prinzipien für faire Arbeitsbedingungen und verantwortungsvolle Beschaffung und Produktion definieren wesentliche Praktiken auf Unternehmensebene zur Gewährleistung sicherer und nachhaltiger Lieferketten. Alle FLA-Standards basieren auf den Normen der Internationalen Arbeitsorganisation (ILO-Kernkonventionen) und international anerkannten guten Arbeitspraktiken. Jedes Mitgliedsunternehmen verpflichtet sich zur Umsetzung der FLA-Grundsätze in seinen eigenen Geschäftspraktiken und zur Einhaltung des FLA-Verhaltenskodexes in seiner Lieferkette. Die FLA bewertet ihre Mitgliedsunternehmen fortlaufend und verleiht die Akkreditierung an Unternehmen, die nachweislich die FLA-Standards einhalten.",
        "credibility_evaluation": 85,
        "ecological_evaluation": 11,
        "social_evaluation": 62,
    },
    LabelIDType.IGEP.name: {
        "name": "IGEP",
        "description": "Ziel des Siegels ist es, Kinderarbeit in der Natursteinindustrie in Indien und China zu verhindern und die Eignung für den europäischen Markt sicherzustellen. Dies geschieht durch den ISES 2020-Standard, der zusätzlich zu Kinderarbeit Managementsysteme, Zwangsarbeit, Gesundheit und Sicherheit an Arbeitsplatz, Vereinigungsfreiheit und Recht auf Kollektivverhandlungen, Diskriminierung, Disziplinarpraktiken, Arbeitszeiten, Vergütung, Zulieferer und Umweltaspekte umfasst. IGEP führt diese Audits und Zertifizierungen auch in vielen anderen Industrien jeweils für die gesamte Lieferkette durch.",
        "credibility_evaluation": 37,
        "ecological_evaluation": 64,
        "social_evaluation": 56,
    },
    LabelIDType.AISE_G.name: {
        "name": "Nachhaltigkeitsinitiative der A.I.S.E. - Logo mit grünem Siegel",
        "description": "Ziel ist es, den gesamten Industriesektor zu bestärken, kontinuierliche Verbesserungen im Hinblick auf Nachhaltigkeit anzustrengen. Zudem sollen Endverbraucher:innen dazu ermuntert werden, nachhaltiger zu waschen und zu reinigen. Die A.I.S.E.-Charter ist ein wissenschaftlich fundiertes Rahmenwerk, welches zudem auf Lebenszyklus-Analysen basiert. Es erleichtert einen gemeinschaftlichen Industrie-Ansatz hinsichtlich nachhaltiger Praktiken und Berichterstattung. Dieser beinhaltet u.a. Produktsicherheit, soziale Unternehmensverantwortung, Gesundheit und Sicherheit am Arbeitsplatz, effiziente Ressourcen-Nutzung sowie Endverbraucher:innen-Informationen.",
        "credibility_evaluation": 59,
        "ecological_evaluation": 64,
        "social_evaluation": 31,
    },
    LabelIDType.TUEV_GP_L.name: {
        "name": "TÜV Rheinland Green Product Mark (Laptops)",
        "description": "Ziel des TÜV Rheinland Green Product Mark Siegels ist es, zur Reduktion negativer Umwelteinflüsse, die bei der Herstellung und dem Gebrauch von Laptops entstehen können, beizutragen. Dazu stellt der Standard Anforderungen an den Umgang mit chemischen Inhaltsstoffen, die Wiederverwendbarkeit und Wiederverwendung recycelter Materialien, den Carbon Footprint/die CO2-Bilanz, und den Energieverbrauch/die Energieeffizienz.",
        "credibility_evaluation": 72,
        "ecological_evaluation": 50,
        "social_evaluation": 18,
    },
    LabelIDType.TUEV_GP_S.name: {
        "name": "TÜV Rheinland Green Product Mark (Smartphones)",
        "description": "Ziel des TÜV Rheinland Green Product Mark Siegels ist es, zur Reduktion negativer Umwelteinflüsse, die bei der Herstellung und dem Gebrauch von Mobiltelefonen entstehen können, beizutragen. Dazu stellt der Standard Anforderungen an den Umgang mit chemischen Inhaltsstoffen, die Wiederverwendbarkeit und Wiederverwendung recycelter Materialien, den Carbon Footprint/die CO2-Bilanz, und den Energieverbrauch/die Energieeffizienz.",
        "credibility_evaluation": 72,
        "ecological_evaluation": 43,
        "social_evaluation": 19,
    },
    LabelIDType.WFTO.name: {
        "name": "World Fair Trade Organization ",
        "description": "Die WFTO zeichnet Unternehmen aus, die sich für eine Verbesserung der Lebens- und Arbeitsbedingungen von Produzent:innen in Entwicklungsländern einsetzen. Die WFTO verifiziert, dass Mitgliedsunternehmen sich an den zehn Prinzipien des fairen Handels ausrichten.",
        "credibility_evaluation": 54,
        "ecological_evaluation": 5,
        "social_evaluation": 64,
    },
    LabelIDType.XX.name: {
        "name": "XertifiX",
        "description": "XertifiX überprüft regelmäßig Fabriken und Steinbrüche in Indien, China und Vietnam, um sicherzustellen, dass die Standardkriterien erfüllt werden: Der Standard umfasst die IAO-Kernarbeitsabkommen, darunter das Verbot von Kinderarbeit und Sklaverei, einen besseren Schutz der Gesundheit und Sicherheit von erwachsenen Arbeitnehmer:innen, gerechte Löhne und Arbeitszeiten, Umweltschutz und Rechtmäßigkeit. Wenn die Anforderungen erfüllt sind, stellt XertifiX Zertifikate für die Steine aus.",
        "credibility_evaluation": 66,
        "ecological_evaluation": 20,
        "social_evaluation": 47,
    },
    LabelIDType.CCCC.name: {
        "name": "4C - Common Code for the Coffee Community",
        "description": "Als unabhängiger und Stakeholder:innen getragener Standard für den gesamten Kaffeesektor zielt 4C auf die weltweite Stärkung der Produktion von umweltfreundlichem, sozial gerechtem und wirtschaftlich tragfähigem Kaffee ab.",
    },
    LabelIDType.ASC.name: {
        "name": "Aquaculture Stewardship Council ",
        "description": "Ziel ist es die konventionelle Aquakultur auf globaler Ebene nachhaltiger zu machen. Das ASC-Zertifizierungsprogramm zeichnet dabei verantwortungsvolle Fischzuchten und Futtermittelproduzenten aus die, die ASC Standards einhalten. Die Standards umfassen sowohl umweltbezogene als auch soziale Auswirkungen der Zucht und Produktion. Für die Rückverfolgbarkeit des zertifizierten Aquakulturprodukte müssen sich die Unternehmen der Lieferkette einem Produktkettenaudit (Chain of Custody) unterziehen",
    },
    LabelIDType.BCI.name: {
        "name": "Better Cotton Initiative",
        "description": "Ziel ist die Verbesserung der Umwelt- und Arbeitsbedingungen im Baumwollanbau. Die Anbaubetriebe müssen Einstiegskriterien erfüllen und dann Verbesserungen nachweisen. Rund 12 Prozent der weltweiten Baumwollproduktion waren 2016 BCI zertifiziert.",
    },
    LabelIDType.BIO.name: {
        "name": "Bio-Siegel (deutsch)",
        "description": "Das Bio-Siegel kennzeichnet Produkte aus kontrolliert biologischem Anbau (kbA). Ziel ist die Förderung der biologischen Landwirtschaft über klar definierte gesetzliche Regelungen. Für das Bio-Siegel gelten auf Grundlage der EU-Ökoverordnung dieselben Kriterien wie für das EU-Bio-Siegel. Das Bio-Siegel kann zusätzlich zum (verpflichtenden) EU-Bio-Siegel auf Produkten abgebildet werden. Die EU-Ökoverordnung umfasst keine gesonderten sozialrechtlichen Regelungen.",
    },
    LabelIDType.BK_RF.name: {
        "name": "Biokreis - regional & fair",
        "description": "Kurze Wege, Marktpartnerschaften, die auf Vertrauen statt auf anonymen Marktmechanismen beruhen, eine ehrliche Entlohnung der Bäuer:innen, gute Rohstoffe und die Förderung der regionalen Kulturlandschaften.",
    },
    LabelIDType.BK.name: {
        "name": "Biokreis-Siegel",
        "description": "Biokreis steht seit 1979 für regionale, vertrauensvolle Netzwerke, für Tierwohl und handwerkliche Lebensmittelverarbeitung im Einklang mit der Natur. Biokreis gestaltet kreativ und konsequent den ökologischen Landbau.",
    },
    LabelIDType.BIOLAND.name: {
        "name": "Bioland",
        "description": "Das Bioland-Markenzeichen steht für Tierwohl, Artenvielfalt und klimafreundliche Landwirtschaft mit Herkunft Deutschland oder Südtirol. Das Ziel des Verbandes ist es die natürlichen Lebensgrundlagen auf der Erde zu schützen und die Umgestaltung der Land- und Lebensmittelwirtschaft auf ökologische Kriterien voranzutreiben. Bioland hat strenge Richtlinien, beispielsweise zur Förderung der Biodiversität und zur Aufzucht der männlichen Küken in der Legehennenhaltung.",
    },
    LabelIDType.BIOPARK.name: {
        "name": "Biopark",
        "description": "Ziel des seit 1991 vergebenen Biopark-Siegels ist, den ökologischen Landbau zu fördern. Angestrebt wird ein möglichst in sich geschlossener Betriebskreislauf. Dabei geht es um den Schutz der Umwelt, Landschaftspflege und artgerechte Tierhaltung.",
    },
    LabelIDType.BVA.name: {
        "name": "Biozyklisch-Veganer Anbau",
        "description": "Das Siegel kennzeichnet Produkte aus biozyklisch-veganem Anbau, einer ökologischen Landwirtschaft auf rein pflanzlicher Grundlage. Diese Anbauform schließt jegliche kommerzielle Nutz- und Schlachttierhaltung aus und verwendet keinerlei Betriebsmittel tierischen Ursprungs. Besonderer Wert wird dabei auf die Förderung der Artenvielfalt und eines gesunden Bodenlebens, auf die Schließung von Stoffkreisläufen sowie auf einen gezielten Humusaufbau gelegt. Verbraucher:innen erhalten die Gewährleistung, dass mit diesem Siegel ausgezeichnete Produkte nach ökologischen und veganen Prinzipien erzeugt und verarbeitet wurden.",
    },
    LabelIDType.BONSUCRO.name: {
        "name": "Bonsucro",
        "description": "Bonsucros Vision ist ein Zuckersektor mit nachhaltigen Erzeuger:innengemeinschaften und widerstandsfähigen und gesicherten Lieferketten für die Erzeuger:innen. Bonsucro arbeitet mit weltweit anerkannten Standards für die soziale, ökologische und wirtschaftliche Nachhaltigkeit der Zuckerrohrproduktion und -verarbeitung. Damit soll sichergestellt werden, dass die aus Zuckerrohr hergestellten Produkte einen Mehrwert für die Landwirte und Gemeinschaften in den Zuckerrohranbauländern schaffen, die Umwelt schützen und die Menschen- und Arbeitsrechte wahren.",
    },
    LabelIDType.BSCI.name: {
        "name": "Business Social Compliance Initiative",
        "description": "Ziel des amfori BSCI-Systems ist die schrittweise Verbesserung der Arbeitsbedingungen und der Schutz der Menschenrechte in der globalen Lieferkette der amfori-Mitglieder, die amfori BSCI nutzen. Unabhängige amfori-BSCI-Sozialaudits sind ein Instrument zur Risikoanalyse und Messung der Situation in Produktionsstätten. Ein breites Schulungsangebot für amfori-Mitglieder und insbesondere Produktionsstätten bietet eine gute Möglichkeit, mit der Unternehmen ihre Kenntnisse und die Praxis verbessern können, damit die Kriterien des amfori BSCI-Verhaltenskodizes eingehalten werden.",
    },
    LabelIDType.CA_BC.name: {
        "name": "C&A Biocotton",
        "description": "C&A nutzt das unternehmenseigene Siegel “C&A BIO COTTON” für C&A-Produkte, die mit Baumwolle aus zertifiziertem Anbau hergestellt werden. Für jedes C&A-Produkt mit dem BIO COTTON-Siegel gilt, dass es nach OCS (Organic Content Standard) oder GOTS (Global Organic Textiles Standard) zertifiziert ist und dass die Lieferkette der Baumwolle von der Quelle bis zum Endprodukt gründlich überwacht wurde.",
    },
    LabelIDType.CTFL.name: {
        "name": "Carbon Trust Footprint Label",
        "description": "Das Carbon Trust Footprint Label wird an Produkte verliehen, deren CO2-Fußabdruck von Carbon Trust im Einklang mit international anerkannten Standards (PAS2050, GHG Product Standard und ISO14067) zertifiziert wurde. Das Siegel belegt die Messung, Reduzierung oder Klimaneutralität des Produktfußabdrucks von Produkten aus allen Branchen. Es steht für das Engagement für ökologische Nachhaltigkeit.",
    },
    LabelIDType.CSE.name: {
        "name": "Certified Sustainable Economics (CSE)",
        "description": "Die CSE-Zertifizierung ist eine branchenübergreifende Nachhaltigkeitszertifizierung für Unternehmen und nachhaltig orientierte Organisationen. Das CSE-Siegel ist ein Qualitätssiegel für Produkte aus einem geprüft nachhaltig wirtschaftenden Unternehmen. Der CSE-Standard wird regelmäßig überprüft und entwickelt sich fortlaufend weiter. Aktuell gibt es den CSE-Standard für diese Branchen: Bio-Lebensmittel, Naturkosmetik, ökologische Wasch- und Reinigungsmittel, Naturprodukte, Produkte aus einer Kreislaufwirtschaft (z.B. Recyclingplastik), Handel, Dienstleister:innen, Banken. CSE möchte Verbraucher:innen ein Unterscheidungsmerkmal geben, damit Produkte aus einem ganzheitlich nachhaltig wirtschaftenden Unternehmen erkannt werden können. CSE umfasst die Einhaltung der Menschenrechte, Förderung des Öko-Landbaus, klimaneutrale Produktion, ethisches Finanzwesen und weitere Mindestanforderungen.",
    },
    LabelIDType.CNI.name: {
        "name": "Climate Neutral Standard",
        "description": "Das Ziel des Standards ist es, Unternehmen, Regierungsorganisationen und Organisationen in die Lage zu versetzen, sich dem Ziel des Pariser Abkommens anzunähern, indem sie ihre Scope-1-, -2- und -3-THG-Emissionen schrittweise auf ein absolutes Null reduzieren und die verbleibenden Emissionen durch glaubwürdige und zertifizierte Ausgleichsprojekte kompensieren. Unternehmen können sich für ihre Organisation, Produkte, Verpackungen und Dienstleistungen klimaneutral zertifizieren lassen.",
    },
    LabelIDType.CP.name: {
        "name": "ClimatePartner",
        "description": "Das ClimatePartner-Siegel kennzeichnet klimaneutrale Produkte oder dessen Verpackungen, Dienstleistungen oder Unternehmen. Hierfür werden die CO2 -Emissionen berechnet und die Emissionen durch die Unterstützung eines Klimaschutzprojektes ausgeglichen. So sollen Unternehmen für den Klimaschutz sensibilisiert werden und Verbraucher:innen die Möglichkeit erhalten, klimaneutral zu konsumieren.",
    },
    LabelIDType.CCS.name: {
        "name": "Content Claim Standard",
        "description": "Im Mittelpunkt stehen Rückverfolgbarkeit und Transparenz in der Produktionskette. Mit dem Content Claim Standard können Unternehmen nachweisen, wie hoch der Anteil eines bestimmten Materials im Endprodukt ist.",
    },
    LabelIDType.CMIA.name: {
        "name": "Cotton made in Africa",
        "description": "CmiA bietet mit CmiA und CmiA-Organic zwei international anerkannte Standards für nachhaltige Baumwolle aus Afrika. Ziel von CmiA ist es durch die Aktivierung von Marktkräften Lizenzeinnahmen zu generieren, die Textilunternehmen und Brands für den Einsatz des Cotton made in Africa Labels bezahlen. Ausschließlich Unternehmen mit Lizenzvertrag dürfen CmiA ausgezeichnete Produkte vertreiben. Die Einnahmen werden in Afrika reinvestiert und ermöglichen Baumwollbäuer:innen in Afrika bessere Lebens- und Arbeitsbedingungen und fördern den Schutz unserer Umwelt. Um die Umsetzung dieser Ziele und die weltweite Verarbeitung des Rohstoffs sicherzustellen, arbeitet die Initiative mit einem weitreichenden Netzwerk in den afrikanischen Anbauländern der Baumwolle, zahlreichen Partner:innen weltweit entlang der textilen Lieferkette sowie Regierungs- und Nichtregierungsorganisationen zusammen.",
    },
    LabelIDType.CTC_WR.name: {
        "name": "Cradle to Cradle - Wasch- & Reinigungsmittel",
        "description": "Ziel ist die Förderung eines Wirtschaftssystems ohne Abfall. Das heißt, dass alle Materialien, die in einem Produkt eingesetzt werden, wiederverwertet oder biologisch abgebaut werden können. Das Siegel zeichnet Produkte aus, die umweltsichere, gesundheitlich unbedenkliche und kreislauffähige Materialien verwenden.",
    },
    LabelIDType.DEMETER.name: {
        "name": "Demeter",
        "description": "Das Demeter Siegel zielt darauf ab, die biologisch-dynamische Wirtschaftsweise in landwirtschaftlichen Betrieben zu fördern und zu verbreiten. Diese geht zurück auf Rudolf Steiner, den Begründer der Anthroposophie. Sie sieht einen landwirtschaftlichen Betrieb als Organismus, der seine eigene Charakteristik hat.",
    },
    LabelIDType.ECO_PP_OEKO_TEX.name: {
        "name": "ECO PASSPORT by OEKO-TEX",
        "description": "ECO PASSPORT by OEKO-TEX ist eine unabhängige Zertifizierung für Chemikalien, Farbmittel und Hilfsstoffe, die in der Herstellung von Textilien und Lederartikeln eingesetzt werden. Dabei wird überprüft, ob jeder einzelne Inhaltsstoff der chemischen Produkte die gesetzlichen Anforderungen erfüllt und unschädlich für die menschliche Gesundheit ist. Der Nachweis dafür erfolgt über die Untersuchung der Endprodukte auf schädliche Chemikalien.",
    },
    LabelIDType.ECOVIN.name: {
        "name": "ECOVIN",
        "description": "Das ECOVIN Siegel kennzeichnet Weine und andere Traubenerzeugnisse aus kontrolliert ökologischem Anbau. ECOVIN Weingüter fördern die biologische Vielfalt, lebendige Böden und das ökologische Gleichgewicht auf ihren Flächen. Der Standard umfasst auch soziale und wirtschaftliche Kriterien.",
    },
    LabelIDType.EPEAT_MP.name: {
        "name": "EPEAT - Mobile Phones",
        "description": "Das EPEAT-Siegel zeichnet Mobiltelefone aus, die weniger Umweltbelastung verursachen als herkömmliche Produkte. Beispielsweise verbrauchen die Geräte weniger Strom während der Nutzung und haben eine längere Lebensdauer. EPEAT führt drei verschiede Siegel: EPEAT Bronze, EPEAT Silber und EPEAT Gold.",
    },
    LabelIDType.EPEAT_L_CO.name: {
        "name": "EPEAT Laptops & Co.",
        "description": "Das EPEAT-Siegel zeichnet Computer aus, die weniger Umweltbelastung verursachen als herkömmliche Produkte. Beispielsweise verbrauchen die Geräte weniger Strom während der Nutzung und haben eine längere Lebensdauer. EPEAT führt drei verschiede Siegel: EPEAT Bronze, EPEAT Silber und EPEAT Gold.",
    },
    LabelIDType.EU_ECO_H.name: {
        "name": "EU Ecolabel - Hartbeläge",
        "description": "Die Produktgruppe Hartbeläge umfasst unter anderem Waschtischplatten und Küchenarbeitsplatten aus Naturstein sowie Zwischenprodukte, insbesondere Blöcke und Platten aus Naturstein. Das Siegel stellt Anforderungen an den gesamten Lebenszyklus der Produkte und stellt sicher, dass die mit dem EU Ecolabel ausgezeichneten Hartbelagsprodukte in Bezug auf ihre Umweltvertäglichkeit zu den besten auf dem Markt gehören. Konkret führen die EU Ecolabel Kriterien zu: einer Verringerung der Landnutzungsauswirkungen des Rohstoffabbaus; einer Beschränkung der Verwendung von gefährlichen Substanzen; effizienten Produktionsprozessen; einem verstärkten Einsatz erneuerbarer Energien; einer hohen Materialeffizienz, einschließlich der Wiederverwendung/Recycling von Prozessabfällen; einer Begrenzung der Emissionen von Schadstoffen, die zur globalen Erwärmung, Versauerung und Eutrophierung beitragen und die für die menschliche Gesundheit schädlich sind.",
    },
    LabelIDType.EU_ECO_L_CO.name: {
        "name": "EU Ecolabel - Laptops & Co.",
        "description": "Die EU Ecolabel Produktgruppe Elektronische Displays umfasst Fernsehgeräte, Computermonitore und digitale Anzeigesysteme. Strenge Kriterien, die sich auf die wichtigsten Umweltauswirkungen während des gesamten Lebenszyklus der Produkte konzentrieren, stellen sicher, dass die mit dem EU Ecolabel ausgezeichneten elektronischen Displays energieeffizient sind, ein Mindestmaß an recycelten Materialien beinhalten, einfach reparierbar sind, leicht zu demontieren sind (um die Rückgewinnung von Ressourcen aus dem Recycling am Ende ihrer Nutzungsphase zu ermöglichen) und nur eine klar begrenzte Menge an gefährlichen Substanzen enthalten.",
    },
    LabelIDType.EU_ECO_WR.name: {
        "name": "EU Ecolabel - Wasch- & Reinigungsmittel",
        "description": "Mit dem EU-Umweltzeichen zertifizierte Wasch- und Reinigungsmittel erfüllen hohe Standards, die ihre Umweltauswirkungen über mehrere Stufen des Produktlebenszyklus, von der Rohstoffgewinnung über die Produktion bis hin zur Verwendung und Entsorgung, verringern. Das EU-Umweltzeichen wird an Produkte vergeben, die besonders nachhaltig gestaltet sind, Innovationen fördern und zum EU-Ziel der Klimaneutralität bis 2050 sowie zur Kreislaufwirtschaft beitragen.",
    },
    LabelIDType.EU_BIO.name: {
        "name": "EU-Bio-Siegel",
        "description": "Das EU-Bio-Siegel kennzeichnet Produkte aus kontrolliert biologischem Anbau (kbA). Ziel ist die Förderung der biologischen Landwirtschaft über klar definierte gesetzliche Regelungen. Die Regelungen der EU-Ökoverordnung umfassen keine gesonderten sozialrechtlichen Regelungen.",
    },
    LabelIDType.ECO_VEG.name: {
        "name": "EcoVeg",
        "description": "EcoVeg ist das erste unabhängig kontrollierte Gütesiegel für vegane Lebensmittel in Bio-Qualität.",
    },
    LabelIDType.ENERGY_STAR.name: {
        "name": "Energy Star",
        "description": "Das Siegel zeichnet besonders energieeffiziente Produkte aus. Basis hierfür sind die Stromspar-Kriterien der EPA und des US-Energieministeriums. Sie beziehen sich vor allem auf den Energieverbrauch der Geräte. Hersteller, die das Siegel nutzen, prüfen selbst, ob ihr Produkt den Anforderungen entspricht. Die Messergebnisse werden der zuständigen Behörde (in EU-Ländern der Europäischen Kommission) mitgeteilt. Sie werden stichprobenartig geprüft.",
    },
    LabelIDType.ETI.name: {
        "name": "Ethical Trading Initiative",
        "description": "Ziel der Initiative ist die Verbesserung von Arbeitsbedingungen weltweit. Zu den Mitgliedsunternehmen gehören Einzelhändler, Supermärkte, Kaufhausketten und Zulieferer. Sie verpflichten sich, den ETI Verhaltenskodex im Unternehmen und bei ihren Zulieferern schrittweise umzusetzen.",
    },
    LabelIDType.FNG.name: {
        "name": "FAIR 'N GREEN",
        "description": "Ziel des Siegels ist es, Winzer:innen dabei zu helfen, nachhaltig zu wirtschaften. Außerdem sollen nachhaltige Weine anhand des Siegels auf der Flasche für Konsument:innen kenntlich gemacht werden.",
    },
    LabelIDType.FFL.name: {
        "name": "Fair For Life Programme",
        "description": "Das Siegel kennzeichnet Produkte aus sozialverträglichem und umweltfreundlichem Anbau, die zusätzlich unter fairen Bedingungen gehandelt wurden.",
    },
    LabelIDType.FC.name: {
        "name": "FairChoice",
        "description": "Das Siegel kennzeichnet landwirtschaftliche Erzeugnisse aus nachhaltiger Produktion mit Schwerpunkt im Bereich Wein- und Getränkewirtschaft. Es umfasst 44 Kriterien in den Bereichen Ökologie, Ökonomie und Soziales, die auf dem UN Global Compact und der Global Reporting Initiative (GRI) basieren. Voraussetzung ist die Selbstverpflichtung zu einer ökologisch verträglichen, sozial gerechten und wirtschaftlich tragfähigen Produktion und Vermarktung.",
    },
    LabelIDType.FT.name: {
        "name": "Fairtrade",
        "description": "Ziel von Fairtrade ist es, Handelsbedingungen für benachteiligte landwirtschaftliche Produzenten und Arbeiter in Entwicklungsländern zu verbessern. Die Produzenten sollen zum Beispiel von fairen Preisen und der Etablierung langfristiger Handelsbeziehungen profitieren. Um eine Fairtrade-Zertifizierung zu erhalten, müssen Produzenten, Händler und Unternehmen soziale, ökologische und wirtschaftliche Standards einhalten.",
    },
    LabelIDType.FT_CP.name: {
        "name": "Fairtrade-Baumwollprogramm",
        "description": "Es liegen dieselben Anforderungen an die Baumwollproduktion zugrunde wie beim Siegel Fairtrade - Baumwolle. Das Fairtrade-Baumwollprogramm richtet sich an Unternehmen in der Textilproduktion. Diese verpflichten sich, einen bestimmten Anteil der Baumwolle in Fairtrade-Qualität einzukaufen. Dieser Anteil wird schrittweise gesteigert.",
    },
    LabelIDType.FR.name: {
        "name": "Flustix Recycled",
        "description": "Durch Vor-Ort-Audit und Analyse der gesamten Lieferkette und des Fertigungsprozesses ermittelt DIN CERTCO die Echtheit und Herkunft sowie den Anteil von Kunststoff-Rezyklaten (PCR/PIR/MIX) in Rohstoffen und Produkten.",
    },
    LabelIDType.FSC.name: {
        "name": "Forest Stewardship Council",
        "description": "Das FSC-Siegel steht für die umweltfreundliche, sozial förderliche und zugleich wirtschaftlich tragfähige Bewirtschaftung von Wäldern. Der FSC entwickelt international einheitliche Anforderungen. Auf nationaler Ebene werden diese auf das jeweilige Land angepasst.",
    },
    LabelIDType.FSC_M.name: {
        "name": "Forest Stewardship Council - Mix",
        "description": "Das „FSC Mix“-Siegel gewährleistet, dass mindestens 70 Prozent der Fasern von Holz- oder Papierprodukten aus FSC-Holz und /oder Altpapier stammen.",
    },
    LabelIDType.FSC_R.name: {
        "name": "Forest Stewardship Council - Recycled",
        "description": "Das „FSC Recycled“-Siegel gewährleistet, dass ein Holz- oder Papierprodukt ausschließlich aus Recyclingmaterial besteht.",
    },
    LabelIDType.G_IT.name: {
        "name": "Fujitsu - Green IT",
        "description": "Besonders umweltverträgliche Produkte von Fujitsu erhalten die Auszeichnung. Ihr liegt ein dreistufiges Bewertungssystem zugrunde. Ein bis drei Sterne stellen die Umweltverträglichkeit dar. Die Bewertung bezieht sich auf das verwendete Material, die Recyclingfähigkeit und den Energieverbrauch eines Gerätes.",
    },
    LabelIDType.GGN.name: {
        "name": "GGN Certified",
        "description": "Das GGN Label steht für zertifizierte, verantwortungsvolle Landwirtschaft und Transparenz. Ein ganzheitlicher Ansatz einschließlich Lebensmittelsicherheit und Rückverfolgbarkeit stellt sicher, dass die Lebensmittel und Pflanzen, auf denen das Label zu finden ist, unter verantwortungsvollen Bedingungen produziert wurden, durch die Boden und Wasser geschont, Energie effizient genutzt, Abfall reduziert, die biologische Vielfalt gefördert und sowohl Menschen als auch Tiere in den Betrieben geschützt werden. Für GLOBALG.A.P. sind all diese Aspekte der Schlüssel zur guten landwirtschaftlichen Praxis, der auf Transparenz und eine nachhaltige Zukunft abzielt.",
    },
    LabelIDType.GREEN_BRANDS.name: {
        "name": "GREEN BRANDS",
        "description": "Die Kriterien der Validierungsverfahren berücksichtigen alle Dimensionen der ökologischen Nachhaltigkeit eines Unternehmens bzw. der Produkte, von der Logistik bis hin zum Abfall-, Energie und Wassermanagement, Transport, Ressourcenverbrauch, Verpackung, dem Mitarbeiterbewusstsein und vieles mehr. Die Validierungsergebnisse sind Grundlage einer finalen Jury-Entscheidung zur Auszeichnung.",
    },
    LabelIDType.GEPA.name: {
        "name": "Gepa fair+",
        "description": "Als Pionier des Fairen Handels ist es unser Ziel, mehr zu leisten und über die allgemeinen Fair- Handelskriterien hinauszugehen. „fair +“ macht zusätzlich zum GEPA-Logo unsere Einzigartigkeit deutlich. Es ist kein zusätzliches Siegel, sondern darf nur in Kombination mit unserem Markenlogo „GEPA“ abgedruckt werden.",
    },
    LabelIDType.GRS.name: {
        "name": "Global Recycled Standard",
        "description": "Der GRS verfolgt das Ziel, den Anteil an recycelten Materialien in einem Produkt zu erhöhen. Der Standard ermöglicht es Unternehmen, den genauen Anteil an recyceltem Material in einem Produkt zu erfassen und durch die Produktionskette weiter zu verfolgen. Der GRS enthält zudem Anforderungen zu den verwendeten Zusatzstoffen bei GRS Produkten sowie Richtlinien zu Umweltmanagement und sozialer Verantwortung im Unternehmen. Die Rückverfolgbarkeit von recycelten Materialien sowie die Transparenz in der Produktionskette geschieht mit Hilfe des übergeordneten Content Claim Standard (CCS). Die Unternehmen, die mit diesem Standard arbeiten, müssen gewährleisten, dass mindestens 20 Prozent des Produkts aus recycelten Materialien besteht. Das GRS Logo hingegen darf nur dann auf einem Endprodukt verwendet werden, wenn das Produkt mindestens zu 50 Prozent aus recycelten Materialien besteht.",
    },
    LabelIDType.GAEA.name: {
        "name": "Gäa - Ökologischer Landbau",
        "description": "Das Siegel hat zum Ziel, den ökologischen Landbau zu fördern. Angestrebt wird dabei ein möglichst in sich geschlossener Betriebskreislauf. Dieser deckt die Bereiche Landschaftspflege, Pflanzenbau und Tierhaltung ab. Er soll die Fruchtbarkeit der Böden erhalten und verbessern. Daneben soll er den Schutz und die Züchtung von Pflanzenarten und Tierrassen fördern.",
    },
    LabelIDType.HM_C.name: {
        "name": "H&M Conscious",
        "description": "H&M setzt auf Selbstverpflichtungen, um Mode nachhaltiger zu gestalten. So hat sich das Unternehmen zum Beispiel darauf verpflichtet, bis zum Jahr 2020 ausschließlich Baumwolle zu nutzen, die entweder bio-zertifiziert, recycelt oder im Rahmen der Better Cotton Initiative (BCI) angebaut ist.",
    },
    LabelIDType.HIH.name: {
        "name": "HAND IN HAND - Rapunzel",
        "description": "HAND IN HAND verknüpft die Idee des kontrolliert biologischen Anbaus mit der des Fairen Handels und soll dies für Verbraucher:innen auch sichtbar machen. Das Siegel zeichnet Produkte aus, deren Rohstoffe zu mehr als 50% von HAND IN HAND-Partner:innen stammen und die zu HAND IN HAND-Konditionen gehandelt wurden. Langjährige Zusammenarbeit, stetiger Austausch sowie persönliche Besuche sollen höchste Produkt-Qualität garantieren. Unabhängige Inspektor:innen sichern durch regelmäßige Kontrollen die Qualität und Einhaltung des Standards zusätzlich ab.",
    },
    LabelIDType.HVH.name: {
        "name": "Holz von Hier",
        "description": "Das Siegel kennzeichnet Holzprodukte, die Holz aus nachhaltiger Waldwirtschaft enthalten und die besonders klimafreundlich durch kurze Wege vom Wald bis zum Verbraucher:in produziert worden sind. Mit dem Kauf so gekennzeichneter Holzprodukte können Verbraucher:innen einen wichtigen Beitrag zum Klimaschutz leisten.",
    },
    LabelIDType.IR.name: {
        "name": "Insect Respect",
        "description": "Insect Respect steht für einen neuen Umgang mit Insekten. Denn die Tiere sind wichtig, aber bedroht. Das Gütezeichen INSECT RESPECT steht deshalb für einen Dreiklang: Insektenbekämpfung 1) reduzieren durch Bewusstseinswandel in der Gesellschaft und Präventionstipps 2) ökologisieren durch insektizidfreie, abwehrende oder rettende Produkte und 3) kompensieren durch die Anlage von insektenfreundlichen Lebensräumen als Ausgleich.",
    },
    LabelIDType.ISCC.name: {
        "name": "International Sustainability and Carbon Certification",
        "description": "Das erklärte Ziel von ISCC ist der Schutz von Wäldern, die Erhaltung der Biodiversität, und die Einhaltung wichtiger Sozial- und Arbeitsstandards. Zudem setzt sich ISCC für den Übergang zu einer Kreislaufwirtschaft und nachhaltigen Bioökonomie ein. Recycelte und bio-basierte Materialien, die nach dem ISCC PLUS Standard zertifiziert sind, geben Konsument:innen die Gewissheit, dass hohe Anforderungen an die Rückverfolgbarkeit der Materialien sowie die Nachhaltigkeit der Rohstoffe eingehalten wurden.",
    },
    LabelIDType.LS_OEKO_TEX.name: {
        "name": "LEATHER STANDARD by OEKO-TEX®",
        "description": "Das Siegel zielt auf die Reduktion von Schadstoffen ab. Das LEATHER STANDARD Siegel signalisiert, dass der gekennzeichnete Artikel erfolgreich auf gesundheitsbedenkliche Chemikalien überprüft wurde. Der Nachweis dafür erfolgt über die Untersuchung der Endprodukte auf schädliche Chemikalien.",
    },
    LabelIDType.LEVEL.name: {
        "name": "LEVEL",
        "description": "Büro- und Objektmöbel sollen unter ökologischen, sozialen und wirtschaftlichen Kriterien nachhaltig hergestellt werden. Das LEVEL-Zertifikat wird auf der Grundlage des FEMB Nachhaltigkeitsstandards für Büro- und Objektmöbel in Innenräumen vergeben. Bei der Zertifizierung werden nicht nur das zu zertifizierende Produkt, sondern auch der Produktionsstandort und das Unternehmen selbst unter die Lupe genommen. Begutachtet werden Anforderungen in den vier Wirkungsbereichen Material, Energie und Atmosphäre, Gesundheit von Mensch und Ökosystem (Chemikalien-Management) und soziale Verantwortung. Damit erfüllt LEVEL die Anforderungen an ein ISO 14024 Type 1 Label.",
    },
    LabelIDType.LP.name: {
        "name": "Leaping-Bunny",
        "description": "Das Siegel basiert auf dem Humane Household Products Standard. Es zeichnet Produkte aus, die ganzheitlich auf Tierversuche verzichten.",
    },
    LabelIDType.LWG.name: {
        "name": "Leather Working Group",
        "description": "Ziel der LWG ist es, ein globaler Nachhaltigkeitsstandard für die Lederherstellung zu werden, der alle Elemente und Akteure der Lederwertschöpfungskette abdeckt. Die Organisation konzentriert sich darauf, hohe Umweltstandards in der Lederproduktion und Transparenz innerhalb der Lederlieferkette zu gewährleisten. Lederherstellungsbetriebe (Gerbereien) werden auf verschiedene Aspekte ihrer Produktion geprüft, darunter Wasser- und Energieverbrauch, Abfallwirtschaft, Luftverschmutzung und Lärmbelästigung sowie Chemikalienmanagement. Händler und Lieferanten werden auf ihre Fähigkeit geprüft, ihre Produkte zurückzuverfolgen.",
    },
    LabelIDType.MSC.name: {
        "name": "Marine Stewardship Council",
        "description": "Das MSC-Siegel steht international für die Kennzeichnung von Produkten aus zertifizierter nachhaltiger Fischerei. Fisch- und Meeresfrüchte, die mit dem MSC-Siegel gekennzeichnet sind, stammen aus einer Fischerei, die ihre Fanggeräte umweltverträglich einsetzt und Fischbestände verantwortungsvoll nutzt. Die Fischerei wird von unabhängigen Experten nach MSC-Standard geprüft und regelmäßig kontrolliert. Ziele: 1. Erhalt von Fischbeständen und gesunden Meeren. 2. Sicherung von Fisch als Nahrungsquelle für zukünftige Generationen und Lebensunterhalt für die in der weltweiten Fischerei Beschäftigten. 3. Die globale Fischerei insgesamt in nachhaltigere Bahnen lenken.",
    },
    LabelIDType.AISE_NG.name: {
        "name": "Nachhaltigkeitsinitiative der A.I.S.E. - Logo ohne grünes Siegel",
        "description": "Ziel ist es, den gesamten Industriesektor zu bestärken, kontinuierliche Verbesserungen im Hinblick auf Nachhaltigkeit anzustrengen. Zudem sollen Endverbraucher dazu ermuntert werden, nachhaltiger zu waschen und zu reinigen. Die A.I.S.E.-Charter ist ein wissenschaftlich fundiertes Rahmenwerk, welches zudem auf Lebenszyklus-Analysen basiert. Es erleichtert einen gemeinschaftlichen Industrie-Ansatz hinsichtlich nachhaltiger Praktiken und Berichterstattung. Dieser beinhaltet u.a. Produktsicherheit, soziale Unternehmensverantwortung, Gesundheit und Sicherheit am Arbeitsplatz, effiziente Ressourcen-Nutzung sowie Endverbraucher-Informationen.",
    },
    LabelIDType.NL_L.name: {
        "name": "Naturland - Lebensmittel",
        "description": "Naturland verbindet Ökologischen Landbau mit Sozialer Verantwortung und Fairem Handel - regional und weltweit. Das Ziel ist der Erhalt einer gemeinsamen Lebensgrundlage durch umfassende Nachhaltigkeit entlang der gesamten Wertschöpfungskette - ganz im Sinne der globalen Nachhaltigkeitsziele der UN (SDGs). Ziel dieses Siegels ist es, bei Anbau und Verarbeitung von Nahrungsmitteln hohe ökologische Standards zu setzen. Es berücksichtigt auch soziale Aspekte, wie den Ausschluss von Kinderarbeit oder die Wahrung der Menschenrechte.",
    },
    LabelIDType.NL_W.name: {
        "name": "Naturland - Wildfisch",
        "description": "Naturland verbindet Ökologischen Landbau mit Sozialer Verantwortung und Fairem Handel - regional und weltweit. Das Ziel ist der Erhalt einer gemeinsamen Lebensgrundlage durch umfassende Nachhaltigkeit entlang der gesamten Wertschöpfungskette - ganz im Sinne der globalen Nachhaltigkeitsziele der UN (SDGs). Das Ziel dieses Siegels ist es, ökologische und soziale Nachhaltigkeit in der Fischerei und die Transparenz vom Fischfang bis zum Verbrauch zu fördern. Im Fokus der Naturland Wildfisch-Zertifizierung stehen vor allem kleine handwerkliche oder auch besonders vorbildliche Fischereien.",
    },
    LabelIDType.NLF_L.name: {
        "name": "Naturland Fair - Lebensmittel",
        "description": "Naturland verbindet Ökologischen Landbau mit Sozialer Verantwortung und Fairem Handel - regional und weltweit. Das Ziel ist der Erhalt einer gemeinsamen Lebensgrundlage durch umfassende Nachhaltigkeit entlang der gesamten Wertschöpfungskette - ganz im Sinne der globalen Nachhaltigkeitsziele der UN (SDGs). Dieses Siegel hat zum Ziel, ökologischen Anbau mit fairen Handelsbeziehungen zu verbinden.",
    },
    LabelIDType.NE_L.name: {
        "name": "Nordic Ecolabel - Leder",
        "description": "Das Nordic Swan Ecolabel verfolgt das Ziel, die Umweltbelastung durch die Produktion und den Konsum von Waren und Dienstleistungen zu reduzieren - und es Verbrauchern und professionellen Einkäufern leicht zu machen, die umweltfreundlichsten Waren und Dienstleistungen auszuwählen.",
    },
    LabelIDType.NE_T.name: {
        "name": "Nordic Ecolabel - Textiles",
        "description": "Das Nordic Swan Ecolabel verfolgt das Ziel, die Umweltbelastung durch die Produktion und den Konsum von Waren und Dienstleistungen zu reduzieren - und es Verbrauchern und professionellen Einkäufern leicht zu machen, die umweltfreundlichsten Waren und Dienstleistungen auszuwählen. Textilien müssen Umwelt-, Gesundheits- und Qualitätskriterien erfüllen, um die Umwelteinwirkungen der verschiedenen Produktionsstufen zu vermindern und die Gesundheit von Arbeiter:innen und Konsument:innen zu schützen.",
    },
    LabelIDType.S100_OEKO_TEX.name: {
        "name": "OEKO-TEX 100",
        "description": "Das Siegel zielt auf die Reduktion von Schadstoffen ab. Ist ein textiler Artikel mit dem STANDARD 100 by OEKO-TEX Label ausgezeichnet, wurden alle Bestandteile dieses Artikels, d.h. auch alle Fäden, Knöpfe und sonstige Accessoires, auf Schadstoffe geprüft, sodass der Artikel somit gesundheitlich unbedenklich ist. Der Nachweis dafür erfolgt über die Untersuchung der Endprodukte auf schädliche Chemikalien.",
    },
    LabelIDType.PP.name: {
        "name": "Pro Planet",
        "description": "Als Handels- und Touristikkonzern sieht die REWE Group ihre zentrale Aufgabe darin, Kund:innen mit hochwertigen Produkten und Dienstleistungen zu versorgen. Vor diesem Hintergrund hat die REWE Group im Jahr 2010 das PRO PLANET-Label entwickelt, welches grundsätzlich für alle Eigenmarkenprodukte der REWE Group anwendbar ist, sofern die entsprechenden PRO PLANET-Anforderungen erfüllt werden. PRO PLANET steht für das Ziel der REWE Group, Produkte nachhaltiger zu gestalten und den nachhaltigen Konsum bei einer breiten Verbrauchergruppe zu fördern. REWE, PENNY und toom Baumarkt kennzeichnen mit dem PRO PLANET-Label Eigenmarkenprodukte, die soziale, ökologische und Aspekte des Tierwohls berücksichtigen.",
    },
    LabelIDType.PROVEG.name: {
        "name": "ProVeg",
        "description": "Das V-Label ist eine international geschützte Marke zur Kennzeichnung von vegetarischen und veganen Produkten. Produkte, die mit dem V-Label lizenziert sind, werden auf ihre Zusammensetzung und jeden Produktionsschritt überprüft. Es dient den Endverbraucher:innen als Entscheidungshilfe und ermöglicht die sichere und bequeme Auswahl von Lebensmitteln und Non-Food-Artikeln ohne die Zutatenliste studieren oder bei einem Unternehmen anfragen zu müssen.",
    },
    LabelIDType.PEFC.name: {
        "name": "Programme for the Endorsement of Forest Certification",
        "description": "Waldzertifizierung nach den Standards von PEFC basiert auf Richtlinien für die nachhaltige Bewirtschaftung von Wäldern. Diese Bewirtschaftung wird durch kompetente und unabhängige Organisationen kontrolliert. Trägt ein Produkt aus Holz das PEFC-Siegel, dann heißt das: Die gesamte Produktherstellung - vom Rohstoff bis zum gebrauchsfertigen Endprodukt - ist zertifiziert und wird durch unabhängige Gutachter:innen kontrolliert.",
    },
    LabelIDType.PEFC_R.name: {
        "name": "Programme for the Endorsement of Forest Certification Schemes - recycelt",
        "description": "Waldzertifizierung nach den Standards von PEFC basiert auf Richtlinien für die nachhaltige Bewirtschaftung von Wäldern. Diese Bewirtschaftung wird durch kompetente und unabhängige Organisationen kontrolliert. Trägt ein Produkt aus Holz das PEFC-Siegel, dann heißt das: Die gesamte Produktherstellung - vom Rohstoff bis zum gebrauchsfertigen Endprodukt - ist zertifiziert und wird durch unabhängige Gutachter:innen kontrolliert.",
    },
    LabelIDType.PEFC_Z.name: {
        "name": "Programme for the Endorsement of Forest Certification Schemes (PEFC) - zertifiziert",
        "description": "Waldzertifizierung nach den Standards von PEFC basiert auf Richtlinien für die nachhaltige Bewirtschaftung von Wäldern. Diese Bewirtschaftung wird durch kompetente und unabhängige Organisationen kontrolliert. Trägt ein Produkt aus Holz das PEFC-Siegel, dann heißt das: Die gesamte Produktherstellung - vom Rohstoff bis zum gebrauchsfertigen Endprodukt - ist zertifiziert und wird durch unabhängige Gutachter:innen kontrolliert.",
    },
    LabelIDType.QUL.name: {
        "name": "QUL - Qualitätsverband umweltverträgliche Latexmatratzen e.V.",
        "description": "Eine hohe Produktqualität sowie Sicherheit und gesundheitliche Unbedenklichkeit sollen durch das Siegel zum Ausdruck kommen. Der Nachweis hierfür sind Emissions- und Schadstoffprüfungen der Endprodukte. Das Siegel kennzeichnet Matratzen und Kissen aus nachwachsenden Rohstoffen wie Naturlatex sowie pflanzliche und tierische Fasern. Die Baumwoll-Bezugsstoffe stammen aus kontrolliert biologischem Anbau.",
    },
    LabelIDType.RAL.name: {
        "name": 'RAL Gütezeichen "Rezyklate aus haushaltsnahen Wertstoffsammlungen"',
        "description": "Das Gütezeichen %-Recycling-Kunststoff steht für Umwelt- und Ressourcenschutz bei Verpackungen durch die Förderung des Wertstoffkreislauf durch Recycling aus haushaltsnahen Wertstoffsammlungen. Mit dem Gütezeichen können Unternehmen dokumentieren, dass Kunststoffe aus dem Gelben Sack / der Gelben Tonne (oder ähnlicher Systeme) hochwertig verwertet und in ihren Verpackungen/ Produkten wiedereingesetzt werden. Mit der Angabe des prozentualen Anteils können Verbraucher:innen nachvollziehen, zu wie viel Prozent die jeweilige Verpackung aus Recycling-Kunststoff besteht.",
    },
    LabelIDType.RA.name: {
        "name": "Rainforest Alliance",
        "description": "Der Rainforest Alliance Standard für nachhaltige Landwirtschaft unterstützt die drei Säulen der Nachhaltigkeit: sozial, wirtschaftlich und ökologisch. Der Standard deckt die folgenden Kernbereiche ab:",
    },
    LabelIDType.RDS.name: {
        "name": "Responsible Down Standard",
        "description": "Der Responsible Down Standard will sicherstellen, dass die Enten und Gänse, von denen Daunen gewonnen werden, gemäß diverser Tierwohl-Kriterien gehalten werden - z.B. werden keine lebenden Tiere entfedert und es findet keine Zwangsernährung statt.",
    },
    LabelIDType.RSB.name: {
        "name": "Roundtable on Sustainable Biomaterials",
        "description": "Der RSB-Standard umfasst Biomasse sowie Brennstoffe und materielle Produkte aus biobasiertem und recyceltem Kohlenstoff, einschließlich fossiler Abfälle. Dazu gehören flüssige Biokraftstoffe, gasförmige Biokraftstoffe, Kraftstoffe aus recyceltem Kohlenstoff, nicht-biobasierte erneuerbare Kraftstoffe, Biomasse für Wärme und Energie, Chemikalien und Polymere, Textilien und Fasern. Der RSB ist bestrebt, die Entwicklung nachhaltiger biobasierter und recycelter Produkte zu unterstützen und dabei Kriterien wie Nahrungs- und Wasserunsicherheit, Klimawandel und Verlust der biologischen Vielfalt zu berücksichtigen.",
    },
    LabelIDType.RSPO.name: {
        "name": "Roundtable on Sustainable Palm Oil",
        "description": "Ziel ist es, nachhaltige Anbaumethoden für Palmöl zu fördern und so die Umweltschädigung zu begrenzen. Die Richtlinien vom RSPO sollen gewährleisten, dass die Grundrechte der indigenen Landbesitzer:innen, der umliegenden Dorfgemeinschaften und der Mitarbeiter:innen respektiert werden. Schützenswerte Gebiete und Regenwaldareale dürfen nicht für den Anbau von Palmöl genutzt werden. Außerdem müssen die Anbaubetriebe und Palmöl-Mühlen ihre Umweltbelastungen so niedrig wie möglich halten.",
    },
    LabelIDType.SGS.name: {
        "name": "SGS Institut Fresenius",
        "description": "SGS Institut Fresenius verfolgt mit seinem Qualitätssiegel einen strengen und ganzheitlichen Qualitätsansatz. Dieser umfasst die gesamte Entstehung des Produkts - von der Gewinnung der Rohstoffe über die Unternehmensgrundsätze und Arbeitsbedingungen bis hin zur tatsächlichen Beschaffenheit. Nach der Siegelvergabe erfolgen in regelmäßigem Abstand weitere Qualitätskontrollen.",
    },
    LabelIDType.STEP_OEKO_TEX.name: {
        "name": "STeP by OEKO-TEX®",
        "description": "STeP by OEKO-TEX® unterstützt Betriebe zielgerichtet dabei, umweltfreundliche Produktionsprozesse dauerhaft umzusetzen: vom Chemikalieneinsatz über den verantwortlichen Umgang mit Abwässern und Emissionen bis hin zur Reduzierung des CO2-Fußabdrucks. STeP trägt dazu bei, Produktionsprozesse kontinuierlich zu verbessern sowie Ressourcen effizient zu nutzen, und schafft damit die Grundlage für eine optimale Wettbewerbsposition.",
    },
    LabelIDType.UTZ.name: {
        "name": "UTZ",
        "description": "Die drei wesentlichen Bestandteile von UTZ zur Erreichung dieser Ziele sind: Das UTZ-System zur Rückverfolgung, der UTZ Verhaltenskodex und die Dokumente für die Überwachung der Lieferkette.",
    },
    LabelIDType.VGS.name: {
        "name": "Vaude Green Shape",
        "description": "Das Siegel zertifiziert Produkte, die aus nachhaltigen Materialien ressourcenschonend und fair hergestellt wurden. Bei der Zertifizierung wird der gesamte Produktlebenszyklus erfasst. Das Siegel basiert auf verschiedenen unabhängigen Standards, beispielsweise bluesign® system, Global Organic Textile Standard - GOTS, EU Ecolabel - Textiles und Fair Wear Foundation.",
    },
    LabelIDType.VEGANBLUME.name: {
        "name": "Veganblume",
        "description": "Das Siegel kennzeichnet vegane Produkte. Das heißt Produkte, in denen keinerlei tierische Inhaltsstoffe enthalten sind.",
    },
    LabelIDType.WRAP.name: {
        "name": "Worldwide Responsible Accredited Production",
        "description": "Ziel ist eine sozialverantwortliche Produktion. Das Siegel verlangt die Einhaltung von Sozialstandards sowie der Arbeitsschutz- und -sicherheitsgesetze in den jeweiligen Produktionsländern. Die WRAP- Prinzipien basieren auf internationalen Arbeitsplatzstandards und lokalen Gesetzen. Sie orientieren sich außerdem an den Konventionen der Internationalen Arbeitsorganisation.",
    },
    LabelIDType.RA.name: {
        "name": "ASDF",
        "description": "ASDF",
    },
    LabelIDType.BIORE.name: {
        "name": "bioRe",
        "description": "Das Siegel bioRe ® Sustainable Textiles bezieht sich auf die gesamte textile Produktionskette, vom Rohstoffanbau der Biobaumwolle bis zur fertigen Konfektion. Ziel ist eine umfassende ökologische und faire Modeproduktion. Grundlagen hierfür sind die Sozialkriterien der Internationalen Arbeitsorganisation und umfassende ökologische Standards. Es wird ausschließlich Biobaumwolle aus kontrolliertem Anbau verwendet, welche den bioRe® Sustainable Cotton Standard erfüllen. Direkte Lieferanten in Hochrisikoländern müssen SA8000 zertifiziert sein. Für deren Unterlieferanten, welche nicht SA8000 zertifiziert sind, wird das amfori BSCI Audit auf dem Weg zur SA8000 Zertifizierung genutzt. Jedes Produkt ist mit einem Code versehen, welcher den Kund:innen die Rückverfolgung der Produktion bis zum Anbaugebiet ermöglicht. Das gesamte während der Produktion entstandene CO2 wird durch CO2-Projekte in den Baumwoll-Anbaugebieten wieder eingespart. Das Siegel bioRe® Sustainable Cotton garantiert die Herkunft der Biobaumwolle aus kontrolliert biologischem Anbau durch bioRe® Bauern in Indien und Tansania. Die Bäuer:innen erhalten eine Prämie von 15% über dem Marktpreis und eine Abnahmegarantie für Ihre Produktion. Dieses Gütesiegel umfasst soziale und ökologische Standards vom gentech-freien Saatgut Über die Biobaumwolle bis zur Garnherstellung.",
    },
    LabelIDType.ECO_INSTITUTE.name: {
        "name": "eco-INSTITUT",
        "description": "Eine hohe Produktqualität sowie Sicherheit und gesundheitliche Unbedenklichkeit sollen durch das Siegel zum Ausdruck kommen. Der Nachweis hierfür sind Emissions- und Schadstoffprüfungen der Endprodukte. Das Siegel kennzeichnet beispielsweise. Matratzen, Bettwaren und Möbel.",
    },
    LabelIDType.KLIMANEUTRAL.name: {
        "name": "klimaneutral",
        "description": "Das klimaneutral-Siegel der natureOffice GmbH ist auf Verpackungen, Produkten, Webseiten, Druckerzeugnissen oder Fahrzeugen zu finden. Es weist Verbraucher:innen darauf hin, dass die CO2-Emissionen, die bei der Herstellung des gekennzeichneten Produktes oder der Prozesse (Fahren, Fliegen, etc.) entstehen, ermittelt und durch ein Invest des Herstellers in ein Klimaschutzprojekt, welches CO2-Zertifikate generiert, ausgeglichen worden sind.",
    },
    LabelIDType.MYCLIMATE.name: {
        "name": "myclimate",
        "description": "Das myclimate Klimaneutralitäts-Label zeichnet Produkte, Aktivitäten, Veranstaltungen, Standorte und Unternehmen aus, deren Emissionen in myclimate-Klimaschutzprojekten kompensiert werden. Der Kompensationsbeitrag fließt in myclimate Klimaschutzprojekte in Entwicklungs- und Schwellenländern. So zielen myclimate Projekte nicht nur darauf ab Treibhausgas-Emissionen zu reduzieren, sondern auch auf darauf die soziale, ökologische und wirtschaftliche Entwicklung in der Region zu fördern. Die Projekte erfüllen die Qualitäts-Standards CDM, Gold Standard und Plan Vivo.",
    },
    LabelIDType.NATUREPLUS.name: {
        "name": "natureplus",
        "description": "Das Siegel natureplus zeichnet Baustoffe, Bauprodukte und Einrichtungsgegenstände aus. Da einige Produkte aus Holz bestehen, stellt das Siegel auch Anforderungen an die Holzgewinnung und -herkunft.",
    },
    LabelIDType.OEKOPAPLUS.name: {
        "name": "ÖKOPAplus",
        "description": "ÖKOPAplus kennzeichnet umweltfreundliche Papierprodukte. Sie müssen zu 100 Prozent aus Altpapier hergestellt sein. Das spart CO2, Energie und Wasser ein. Überdies reduziert es die Gewässer- und Luftverschmutzung. Um das sicherzustellen, muss das verarbeitete Papier mit dem Blauen Engel ausgezeichnet sein.",
    },
    LabelIDType.OE_UZ_WR.name: {
        "name": "Österreichisches Umweltzeichen - Wasch- & Reinigungsmittel",
        "description": "Für die eingesetzten Chemikalien in Wasch- und Reinigungsmitteln gelten strenge Regeln in Bezug auf etwaige Gesundheitsbelastungen. Bei Duft- und Konservierungsstoffen wurde besonderen Wert darauf gelegt, allergieauslösende Stoffe möglichst zu reduzieren. Reduktion der Wasserverschmutzung: Alle eingesetzten Chemikalien müssen möglichst gut abbaubar sein. Chemikalien, die Wasserorganismen gefährden, und auch Mikroplastik sind verboten oder auf ein Minimum beschränkt. Verpackung sparen: Das Gewicht der Verpackung im Verhältnis zum Produkt muss möglichst gering sein. Zusätzlich sind bei Kunststoffverpackungen nur Kombinationen an Materialien erlaubt, die die Recyclingfähigkeit nicht stören. Trotzdem ein gut funktionierendes Produkt: Die Reinigungsmittel wurden einem Gebrauchstauglichkeitstest unterzogen. Dadurch ist mindestens die gleiche Spülwirkung wie bei herkömmlichen Produkten garantiert.",
    },
    LabelIDType.VFI.name: {
        "name": '"sozial-fair" VFI Sozialstandard für Fertigwaren',
        "description": "Ziele des Verfahrens SocialFair ist die größere Selbständigkeit der Produzent:innen, die in ihrem eigenen Interesse und auf der Basis ihrer eigenen Fähigkeiten Verbesserungen durchführen. Hinzu kommt, dass die German Importers für ihre eigenen Betriebsstätten (Verwaltung, Warenlager und ggf. Geschäfte) das Initiative SocialFair Verfahren anwenden, um auch in Deutschland einen effizienten Ressourceneinsatz und weniger Umweltbelastungen zu gewährleisten. Und alles wird bilanziert und dokumentiert, wodurch ein faktenbasierter Dialog mit den Stakeholder:innen ermöglicht wird.",
    },
}

sustainability_labels = [
    SustainabilityLabel(
        id=label_id,
        timestamp=information_from,
        name=label_information_dict["name"],
        description=label_information_dict["description"],
        ecological_evaluation=label_information_dict.get("ecological_evaluation", None),
        social_evaluation=label_information_dict.get("social_evaluation", None),
        credibility_evaluation=label_information_dict.get("social_evaluation", None),
    )
    for label_id, label_information_dict in __label_information.items()
]
