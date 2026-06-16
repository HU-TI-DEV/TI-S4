# Meeting with Colin

_2026/03/04_

----

Hoe moet de arm er uit komen te zien?
- Uiteindelijk  simulatie waarop je kan doorbouwen
- Ideally bouwen wij een framework waarmee zij hier iets kunnen creeren irl

maak een planning met milestones op volgorde van complexiteit en kijk hoe ver we komen

wat zijn de verwachtingen qua eigenschappen van MVP?
- er wordt verwacht dat er een kinematica focused simulatie is, dit betekent in de praktijk dat we primarily bezig zijn met positie, snelheid en acceleratie. Externe krachten erin meenemen (dynamica) zou mooi zijn, maar is not a primary concern (could have)

plan opzetten voor beginnen and run it past Colin

planning met milestones per week

Wekelijkse meeting afspraken worden per calendar appointment verstuurd

worden er andere documenten verwacht dan alleen de simulatie?
- Overdraagbaarheid is een key factor. Ons werk moet preferably door gegeven kunnen worden aan volgende groepjes die er dan weer mee verder kunnen, de milestones bevorderen ook de overdraagbaarheid

welke functionaliteiten moet de robotarm hebben?
- moet ergens naar toe kunnen bewegen
- iets vastpakken
- kwartslag draaien (van de hand)
- onderkant kan roteren, 
- arm bestaat uit 3 segmenten

----

	"hand" can open and close as well as rotate 90 degrees---  >:-o  ----third arm segment
                                                                   \  ---second arm segment
                                                                    \
                                                                     o
                                                                    /  --first arm segment
                                                                   /	
                                                                 _o_ ----arm can rotate on the base  
                                                                /___\  --base

preferably kan de robot een valve zien, vastpakken en een kwartslag omdraaien, ideally rekening houdende met dynamica

in principe zit de camera boven de arm schuin naar beneden gericht

er zitten hoeksensoren in de arm om te meten welke hoeken elk stuk heeft, dit kan gebruikt worden om te bepalen in welke positie de arm staat.

In hoeverre moeten we rekening houden met de rest van de robot?
- Ideally nemen we ook de dynamica van de robot mee incl. tegenkrachten, MAAR eerst gewoon op de arm zelf focussen
use parallel tracks, have people work on multiple parts in parallel (someone on vision, someone on the arm, etc.)

beide groepen hetzelfde of andere richtingen?
- mag samen met 10 naar 1 geheel, mag ook allebei andere richting 
- moeten nog bespreken hoe onze twee teams tot elkaar verhouden
- wel individuele traceerbaarheid hebben

moeten nu eerst planing maken en complexiteit inschatten, then run it past him.

python simulatie van arm staat online (ergens)

wat nu voor volgende week?
- laten zien wat we geleerd hebben
- planning met milestones ordered by complexity marking where we expect to get
- how can we make certain things more complex?
