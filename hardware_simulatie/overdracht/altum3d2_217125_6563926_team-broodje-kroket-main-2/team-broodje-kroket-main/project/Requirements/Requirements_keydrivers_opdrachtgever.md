# Requirements & Key Drivers

## 1. Functional Requirements (FR)

| Nr.  | Requirement                | Beschrijving                                                                                                   | MoSCoW       |
| :--- | :------------------------- | :------------------------------------------------------------------------------------------------------------- | :----------- |
| FR-1 | Object Lokalisatie (Vision)| De arm moet d.m.v. een gesimuleerde camera de exacte coördinaten van de print op de buildplate bepalen.        | Must have    |
| FR-2 | Autonome Pathfinding       | Het systeem berekent een botsingsvrij pad van de huidige positie naar het pick-up punt en de vervolgstations.  | Must have    |
| FR-3 | Object Koppeling (Attach)  | De simulatie moet het object aan de arm koppelen (bijv. via een vacuum-plugin) zodra de TCP binnen bereik is.  | Should have    |
| FR-4 | Station-navigatie          | De arm moet het gekoppelde object nauwkeurig in de was-, droog- en UV-units kunnen positioneren.               | Should have    |
| FR-5 | Object Ontkoppeling (Drop) | De arm moet het object op commando loslaten op de juiste doellocatie (bijv. in de verpakking).                 | Should have    |
| FR-6 | Simulatie Bediening        | Een interface (Rviz/Terminal) waarmee de gebruiker het proces kan monitoren en handmatig kan bijsturen.         | Should have  |
| FR-7 | Telemetry Logging          | Opslag van data over pad-efficiëntie en bereikte precisie voor evaluatiedoeleinden.                            | Could have   |

---

## 2. Non-Functional Requirements (NFR)

| Nr.  | Requirement                | Beschrijving                                                                                                   | MoSCoW       |
| :--- | :------------------------- | :------------------------------------------------------------------------------------------------------------- | :----------- |
| NFR-1 | Positioneringsprecisie     | De TCP moet binnen een straal van 0,5 mm van het berekende pick-up punt komen voordat koppeling mogelijk is.   | Must have    |
| NFR-2 | Collision-free Execution   | De arm mag tijdens de gehele simulatie geen enkel onderdeel van de omgeving of zichzelf raken.                 | Must have    |
| NFR-3 | Vision Accuraatheid        | De visie-node moet de positie bepalen met een maximale afwijking van 2 mm t.o.v. de 'ground truth' data.       | Must have    |
| NFR-4 | PID Stabiliteit            | De arm moet zonder overmatige oscillatie (doorschot < 5%) tot stilstand komen op de doelcoördinaten.           | Should have    |
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
