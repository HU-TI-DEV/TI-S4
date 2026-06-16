# Requirements & Key Drivers

## 1. Functional Requirements

| Nr.  | Requirement                          | Beschrijving                                                                 | MOSCOW                    |
|------|--------------------------------------|------------------------------------------------------------------------------|---------------------------|
| FR-1 | Prints van buildplate verwijderen    | De robotarm moet prints van de buildplate kunnen losmaken en oppakken.        | Must have                |
| FR-2 | Buildplate van printer verwijderen   | De buildplate moet automatisch uit de printer gehaald kunnen worden.          | Nice to have             |
| FR-3 | Prints wassen                        | De prints moeten in een wasbad gereinigd worden (resin verwijderen).          | Should have              |
| FR-4 | Prints drogen                        | Na het wassen moeten de prints gedroogd worden voordat ze uitgehard worden.   | Should have              |
| FR-5 | Prints uitharden                     | De prints moeten met UV-licht uitgehard worden na het drogen.                 | Should have              |
| FR-6 | Productie-overzicht                  | Het systeem moet een overzicht bieden van de huidige productiecapaciteit.     | Nice to have             |
| FR-7 | Prints verpakken                     | De afgewerkte prints moeten automatisch in een doos geplaatst worden.         | Should have              |
| FR-8 | Positioneren in stations   | De arm moet de blokjes in de openingen van de was-, droog- en UV-units kunnen plaatsen.                          | Should have |
| FR-9 | UV-kamer bediening         | De simulatie moet de UV-lampen activeren zodra de robotarm het blokje heeft geplaatst en zich heeft teruggetrokken.    | Could have |
| FR-10| Synchronisatie             | De robotarm wacht op signalen (bijv. "print klaar" of "wasbeurt klaar") voordat de volgende actie in de simulatie start. | Could have |

## 2. Non-Functional Requirements

| Nr.   | Requirement                  | Beschrijving                                                                         | MOSCOW                  |
|-------|------------------------------|--------------------------------------------------------------------------------------|-------------------------|
| NFR-1 | Schaalbaarheid               | Het systeem moet schaalbaar zijn tot 50.000 exemplaren per maand.                    | Should have             |
| NFR-2 | Bereik robotarm              | De robotarm moet alle processtations kunnen bereiken binnen zijn maximale radius.    | Must have               |
| NFR-3 | Wasstation capaciteit        | Het systeem moet een doorvoersnelheid hebben die aansluit bij de printoutput.        | Should have             |
| NFR-4 | Ruimtelijke beperking        | De volledige opstelling moet passen binnen een ruimte van 9m x 7m x 2,3m.            | Must have               |
| NFR-5 | Positioneringsfout           | De simulatie moet rekening houden met een minimale afwijking van 0,5 mm om te bewijzen dat de gripper het blokje altijd raakt.                                                                                                                 | Should have             |
| NFR-6 | Clash-detectie               | De software moet aantonen dat de robotarm nergens tegenaan botst (bijv. de rand van de printer of het UV-station).                                                                                                                  | Must have               |
| NFR-7 | Product-tolerantie           | De grijpdruk op de blokjes moet in de simulatie zo zijn ingesteld dat er minder dan 1% vervorming              optreedt.                                                                                                                     | Could have              |
| NFR-8 | Belichtingstolerantie        | De simulatie moet garanderen dat het blokje 360 graden rondom gelijkmatig wordt blootgesteld aan UV-licht.                                                                                                                     | Nice to have            |

## 3. Key Drivers

| Nr.  | Driver              | Beschrijving                                                                          |
|------|---------------------|---------------------------------------------------------------------------------------|
| KD-1 | Automatisering      | Het gehele proces van printen tot verpakken moet zo autonoom mogelijk verlopen.       |
| KD-2 | Schaalbaarheid      | Het systeem moet eenvoudig uitgebreid kunnen worden om hogere volumes te halen.       |
| KD-3 | Modulariteit        | Componenten moeten modulair zijn zodat onderdelen onafhankelijk vervangen of toegevoegd kunnen worden. |
| KD-4 | Schadevrije handling| Het systeem moet alle soorten prints veilig kunnen oppakken en verplaatsen zonder deze te vervormen, ook als ze nog zacht en kwetsbaar zijn.                                                                                                   |
| KD-5 | Tijdsefficiëntie    | Het proces moet geoptimaliseerd zijn om doorlooptijd te minimaliseren.                |


# Requirements & Key Drivers

## 1. Functional Requirements (FR)

| Nr.  | Requirement                | Beschrijving                                                                                                   | MoSCoW       |
| :--- | :------------------------- | :------------------------------------------------------------------------------------------------------------- | :----------- |
| FR-1 | Object Lokalisatie (Vision)| De arm moet d.m.v. een gesimuleerde camera de exacte coördinaten van de print op de buildplate bepalen.        | Must have    |
| FR-2 | Autonome Pathfinding       | Het systeem berekent een botsingsvrij pad van de huidige positie naar het pick-up punt en de vervolgstations.  | Must have    |
| FR-3 | Object Koppeling (Attach)  | De simulatie moet het object aan de arm koppelen (bijv. via een vacuum-plugin) zodra de TCP binnen bereik is.  | Must have    |
| FR-4 | Station-navigatie          | De arm moet het gekoppelde object nauwkeurig in de was-, droog- en UV-units kunnen positioneren.               | Must have    |
| FR-5 | Object Ontkoppeling (Drop) | De arm moet het object op commando loslaten op de juiste doellocatie (bijv. in de verpakking).                 | Must have    |
| FR-6 | Simulatie Bediening        | Een interface (Rviz/Terminal) waarmee de gebruiker het proces kan monitoren en handmatig kan bijsturen.         | Should have  |
| FR-7 | Telemetry Logging          | Opslag van data over pad-efficiëntie en bereikte precisie voor evaluatiedoeleinden.                            | Could have   |

---

## 2. Non-Functional Requirements (NFR)

| Nr.  | Requirement                | Beschrijving                                                                                                   | MoSCoW       |
| :--- | :------------------------- | :------------------------------------------------------------------------------------------------------------- | :----------- |
| NFR-1 | Positioneringsprecisie     | De TCP moet binnen een straal van 0,5 mm van het berekende pick-up punt komen voordat koppeling mogelijk is.   | Must have    |
| NFR-2 | Collision-free Execution   | De arm mag tijdens de gehele simulatie geen enkel onderdeel van de omgeving of zichzelf raken.                 | Must have    |
| NFR-3 | Vision Accuraatheid        | De visie-node moet de positie bepalen met een maximale afwijking van 2 mm t.o.v. de 'ground truth' data.       | Must have    |
| NFR-4 | PID Stabiliteit            | De arm moet zonder overmatige oscillatie (doorschot < 5%) tot stilstand komen op de doelcoördinaten.           | Must have    |
| NFR-5 | Cyclus-snelheid            | De berekening van een nieuw pad mag niet langer duren dan 1 seconde om de flow in de simulatie te behouden.    | Should have  |
| NFR-6 | Software Modulariteit      | De code moet opgedeeld zijn in losse ROS/Python modules voor Vision, Planning en Control.                      | Should have  |
| NFR-7 | Stabiliteit van Koppeling  | Het object mag tijdens beweging niet verschuiven ten opzichte van de TCP (geen 'drifting' in de simulatie).    | Should have  |

---

## 3. Key Drivers (KD)

| Nr.  | Driver                     | Beschrijving                                                                                                   |
| :--- | :------------------------- | :------------------------------------------------------------------------------------------------------------- |
| KD-1 | Focus op Intelligentie     | Prioriteit ligt bij de software-stack (vision/pathfinding) in plaats van complexe fysieke interacties.         |
| KD-2 | Precisie over Kracht       | Omdat er geen gripper is, moet de positionering van de arm extreem nauwkeurig zijn om de 'attach' te triggeren. |
| KD-3 | Systeem Robuustheid        | Het algoritme moet succesvol blijven werken, ook als het object telkens op een andere plek op de buildplate staat. |
| KD-4 | Schaalbaarheid van Code    | De structuur moet het toevoegen van extra stations (bijv. meer UV-units) eenvoudig maken in de code.           |
| KD-5 | Virtual-to-Physical        | De ontwikkelde pathfinding en vision-logica moeten abstract genoeg zijn om later op een echte arm te werken.   |