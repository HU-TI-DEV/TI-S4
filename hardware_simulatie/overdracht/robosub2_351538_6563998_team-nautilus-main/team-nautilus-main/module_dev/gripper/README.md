# Gripper

Na meeting 3 met collin hebben we de volgende afbeelding mee gekregen.

<img width="1313" height="792" alt="image" src="/notes/images/gripper_explanation.png" />

Helaas is voor deze realisatie een probleem met Gazebo, gazebo ziet de gripper zelf als parent element en die wordt geduwd door de child element 1 (de bewegingschanierpunten) dat is geen probleem. 
Dan komt het 2e child element, de statische schanierpunten op het moment dat die worden toegevoegd en vast gezet crasht gazebo omdat een parent element niet door 2 child elementen kan worden bewogen waardoor je dus niet de "tilt" krijgt als je de bewegingschanierpunten heen en weer beweegt.
De workaround die hiervoor toepassenlijk is om de eerste child element weg te laten en alleen de 2e child element te gerbuiken en hier inplaats van een statisch punt van te maken een revolute joint van te maken dus dat we de gripper van de 2e schanier draaien inplaats van de 1ste schanier duwen. zie afbeelding ->

<img width="1313" height="792" alt="image" src="/notes/images/Screenshot 2026-03-31 111229.png" />

Na maken van de schets heb is de indivuele gripper in urdf format gemaakt zie afbeelding ->

<img width="1313" height="792" alt="image" src="/notes/images/Screenshot 2026-03-31 123016.png" />

De schuinen blokken van de vingers zijn 140mm lang, tussen stuk 30,75mm.
Het grijze deel is de base (er is altijd een base nodig om op te roteren) aan de base zitten de groene schanier punten waar de fingers op draaien.
De vingers staan nu op hun "rust positie" de vingers moeten een gat er tussen hebben van min 0° en max 90°. de "rust positie is 6.30°" hij draait dus 6.30° naar binnen, de max is dan ook 90°/2 45° min de huidige rust positie van 6.30° dat is dus een max draai naar buiten van 38.7°. Hier nog een afbeelding ter demonstratie-> 

<img width="1313" height="792" alt="image" src="/notes/images/Screenshot 2026-03-31 124031.png" />
