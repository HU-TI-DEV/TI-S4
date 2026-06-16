### Initial Meeting
Date : 11-03-2026  
Members : *Chris*,*Rein*, Luuk, Kjell, Robin, Alea.

---

### questions for the meeting:
- Wat willen jullie tenminste gesimuleert hebben? (MVP)
- Hoe veel moeten we als drie groepen van elkaar afwijken (allemaal iets anders?)
- Hoever moeten wij de zonnepannelen simuleren (stroom berekenen?, gewichtsverdeling?)
- *over de PDF* Wij hebben de pagina's: 6, 18, 21, 35, 46, 48 genoteerd als interresant, zijn er nog stukken die jullie belangrijk vinden?
- Wat zijn de maximale afmetingen die de graafmachine kan negeren (geen lidar etc.)
- Welke van de nu gemaakte simulaties zijn relevant voor de uiteindelijke uitwerking. Zijn er nog meer obstakels waar wij rekening mee moeten houden

---

*Catalog pages:* 

pagina 6: system component overview - laat weten wat de graafmachine kan.  
pagina 18-21: digging behavior - wat voor manen gaat de graafmachine graven en afmetingen.  
pagina 35: task assignment and path planning - routes van de graafmachinie, object herkenning en afbakening gebied.  
pagina 46: hardware components - lijst van alle hardware onderdelen.  
pagina 48: solar yield - hoeveel vangt de green digger op qua energie en hoeveel kost het om een periode te draaien. 

---

### Answers & Additional notes
Meeting notes:

⦁    Wat willen jullie tenminste gesimuleert hebben? (MVP) (graaf gedrach, rijden, obstakel herkening)
> Their goal is to simulate the **fleet** in the envrioment. They want it to be a few hectares.  
> They want an enviroment, and driving behaviour, and digging behaviour.  
> Movement of the Green Digger over the enviroment, just locomotion.  

⦁    Hoe veel moeten we als drie groepen van elkaar afwijken (allemaal iets anders?)
> They seem to be very fast and lose in terms of distributing the project. We’re pretty much free to tell them what *they* want.

⦁    over de PDF Wij hebben de pagina's: 6, 18, 21, 35, 46, 48 genoteerd als interresant, zijn er nog stukken die jullie belangrijk vinden?
> We will have to follow up in a mail.  
> The machines themselves are very simple (dumb), and its controlled by a cloud? Service. The digger itself can decide where to dig, based on scans it does.  
> They don’t know yet.

⦁    Wat zijn de maximale afmetingen die de graafmachine kan negeren (geen lidar etc.)
> There are no concrete measurements yet, they are still quite lose on this. As long as they’re variable.  
> Tot 20% van de wielbasis. (10 cm)

⦁    Do they want 1 or 3 products.
> Bespreek met Bart.

⦁    How often meetings? And where?
> Teams is preferred, Once a week, then less as time goes on.


**Additional notes:**  
⦁    Rijn used to make software products for people, so he does have soe insight. We can ask him if the documentation is preferred in a spesific way. Have him check the style guide, repo structure.  
⦁     The surface layer is hardpan, which is rather tough. We should see to finding out how much pressure is needed to break through it.  
⦁    There are trees, it seems. Source: JustDiggIt : The Great Green Wall : World Food Programme.  
⦁    The digging machine is smaller then the types they use in their marketing. We are able to scale it down significantly and also reduce power consumption.  
⦁    They want the machines to be able to be monitored continuously under their SuperVision project.  
⦁    The terrain does not contain steep hills. It does contain scrubs and (short) trees. There will be rocks, grepples, a lot of dust and high temperatures. Do research on env variables.  
⦁    Machine weights roughly 1000 kg.  
⦁    There is a 8% max hill steepness. No mountainous terrain. Just flats.  
⦁    They are using wheels on the diggers, instead of tank tyres. There is no decision about how the steering works.  
⦁    No strict requirements for the documentation, only that it is in english.  

---

### Discussion with other groups.
![w1](../../../media/img/whiteboard_concept1.jpg)  
![w2](../../../media/img/whiteboard_concept2.jpg)