# Meeting met Colin

_2026-06-03_

We starten met wat scherm problemen, want de monitor werkt niet mee XD

##### Handle angle detection. 

Maak een tabel voor de margin of error bij verschillende hoeken van vision angle en handle angle. 

##### PID

Wordt nu nog getuned maar is verder wel af.
Wat is de input van de PID en wat is de output in Gazebo? -> er gaat een doelhoek in en de output is de snelheid waarmee de joint aangestuurd moet worden.

Requirements voor PID
- Settling time -> hoelang duurt het om de doel te bereiken. Hier was Colin het meest in geïnteresseerd.
- Rising time -> Als je aangeeft dat het tussen een range mag liggen is dit hoe lang het duurt om binnen die range te komen.
- Offset -> De steady state offset. Dit moet binnen een graad nauwkeurig.
- Trilling -> Hoe groot de schommeling van de PID is wanneer het een doel heeft bereikt.
	
Zet dit in een grafiek.

##### Inverse kinematics

We gebruiken nu FABRIK, dit vanwege het implementatie gemak en snelheid.
De forward kinematics is inmiddels geïmplementeerd.
De interne logica van IK werkt, maar het moet nog verbonden worden met Gazebo en vision.

Test en demonstreer eerst de IK code gewoon met 2d lijntjes in python.

De tolerance voor de IK is 1 mm, dus die is goed right now, eventueel mogen we ook 5 mm proberen, mocht 1mm te klein blijken.

##### Tip van Colin:
Heb eisen waar het systeem aan moet voldoen (de requirements) en weet aan te tonen dat het systeem ook daadwerkelijk aan die eis voldoet.



##### Feedback vraag van Narwal

Wat zij gaan opleveren in hun eindproduct:
- Orientatiedocument (documentatie en implementatie keuzes)
- Onderzoeken
- Code (in de code zelf comments zetten voor wat het doet)

Voor de eindpresentatie moeten we ook de specifics hebben van welke requirements al aan voldaan zijn.
Wat doet het nu en voldoet het aan de eisen?

##### Extra punt van Colin over IK vergelijkbaarheid

Er zijn 3 verschillende IK modellen gebouwd, dus maak ze vergelijkbaar met elkaar zo dat Colin een geïnformeerde keuze kan maken over welke te kiezen.

Eisen aan de IK om te vergelijken:
- tijd om het punt te bereiken
- nauwkeurigheid (Toetsmethode: forward kinematics)
- welke hoeken worden gebruikt? (misschien kiezen andere IK implementaties andere hoeken om bij hetzelfde punt te komen
