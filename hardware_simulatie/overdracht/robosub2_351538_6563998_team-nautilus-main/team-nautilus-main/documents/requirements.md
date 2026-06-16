
# Functional

Naam | Beschrijving | Rationale | Prioriteit
-----|--------------|-----------|------------
F01 (Semi)realistische omgeving|De omgeving moet een (versimpelde) representatie bieden van waterweerstand.|Om een goede representatieve simulatie van de realiteit te maken zijn bepaalde omgevingsfactoren (zoals waterweerstand) essentieel.|Must have
F02 Draaiende base|Base moet kunnen draaien.|Voor een goed bereik van de arm moet die kunnen draaien.|Must have
F03 Bewegende segmenten|De 3 segmenten moeten omhoog en omlaag kunnen bewegen.|Voor een goed bereik van de arm moeten de segmenten kunnen bewegen.|Must have
F04 Grijper open en dicht|De grijper moet open en dicht kunnen gaan.|Om dingen zoals een handvat vast te kunnen pakken moet de grijper open en dicht kunnen.|Must have
F05 Grijper draaien|De grijper moet kunnen draaien.|Om een schuif te kunnen openen moet de grijper kunnen draaien.|Must have
F06 Balk pakken|De arm moet een balk kunnen pakken.|Om het handvat van de schuif te kunnen vastpakken moet de grijper een balkvormig object kunnen oppakken.|Must have
F07 Handmatige besturing|Elk onderdeel van de arm moet handmatig bestuurd kunnen worden.|Voor troubleshooting moeten de afzonderlijke onderdelen van de arm handmatig bestuurd kunnen worden.|Must have
F08 Autonome besturing|De arm moet zelf op basis van gegeven coordinaten iets op die coordinaten aantikken of oppakken.|De AUV moet autonoom zijn (AUTONOMOUS underwater vehicle), dus de arm zelf ook.|Should have
F09 Object detection|De AUV moet objecten kunnen herkennen en de positie van die objecten kunnen omzetten naar coordinaten.|Om de AUV in staat te stellen autonoom objecten op te pakken, moet deze die objecten ook herkennen.|Should have
F10 Dynamica|De arm moet rekening houden met dynamica zoals water weerstand of druk.|Om de beste representatie te bieden van de realiteit moet er ook rekening gehouden worden met de dynamica.|Could have

# Non Functional

Naam | Beschrijving | Rationale | Corresponding Functional Requirement
-----|--------------|-----------|------------
NF01 Base rotatie|Base moet van -135° tot 135° kunnen draaien.|Dit is de aangeleverde rijkwijdte.|F02 Draaiende base
NF02 Beweging segment 1|Het eerste segment moet van 8° naar 110.5° kunnen bewegen.|Dit is de aangeleverde rijkwijdte.|F03 Bewegende segmenten
NF03 Beweging segment 2|Het tweede segment moet van 172° naar 87.8° kunnen bewegen.|Dit is de aangeleverde rijkwijdte.|F03 Bewegende segmenten
NF04 Beweging segment 3|Het derde segment moet van 20.5° naar 99.3° kunnen bewegen.|Dit is de aangeleverde rijkwijdte.|F03 Bewegende segmenten
NF05 Grijper opening |De grijper moet van 0° (dicht) naar 90° (open) kunnen gaan.|Dit is de aangeleverde rijkwijdte.|F04 Grijper open en dicht
NF06 Grijper rotatie |De grijper moet 90° kunnen draaien.|Dit is de aangeleverde rijkwijdte.|F05 Grijper draaien
NF07 Balk pakken|De arm moet een balk van 25mm wijdte met 65mm diepte kunnen pakken.|Dit zijn de afmetingen van het handvat van de schuif.|F06 Balk pakken
NF08 Object detection|De AUV moet de rgb(226,83,3)in water herkennen.|De schuif is deze kleur.|F09 Object detection
