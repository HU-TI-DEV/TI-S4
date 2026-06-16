# Advice for parts GreenDigger
During the last semester our three teams have worked in individual groups to figure out how to implement the best version of their assigned parts. In this document a recommendation will be given on which parts of each project we (handig om te gebruiken?) would combine.

## Excavation Arm
Since both team GroeneGravers and team Zandbakje have worked on an excavation tool we recommend future developers to combine the two projects. Team GroeneGravers has delivered a full excavation arm with inverse kinematics. This excavation tool performs well but does not influence the dug area. This limitation restricts the reliability of the simulated reality.
Team Zandbakje has delivered a full tool which digs out an area in the simulated environment but has not developed a fully functional excavation arm.  This change is why we recommend the combination of the two systems.

## Pathfinding
Both teams MoonDiggers and Zandbakje have worked on a pathfinding algorithm. The pathfinding algorithm of MoonDiggers contains a full implementation of the A* algorithm to find the right path across the specified terrain. Team Zandbakje has chosen to develop a limited version of a pathfinding algorithm which was enough to show the implementations they made on their main components. 

Since it was not the task of team Zandbakje to code a full pathfinding algorithm it is not expected of them to deliver one. This is also why we would recommend the pathfinding algorithm MoonDigger has delivered. The implemented A* algorithm could be expanded to better fit the Autonomous Mobile Platform. More about this expansion can be found in the handoff document supplied by MoonDiggers.

## Object detection
Team Zandbakje has chosen to implement a LiDAR system to find any obstacles around the Autonomous Mobile Platform and report these. Setting this up cost them quite some time and resources. LiDAR demands some serious hardware and is not yet fully developed which is why we recommend to develop this further to the best extend. Until this time, the object detection, team MoonDiggers has set up, contains all requirements but has a clear limit to its capabilities. This limit has almost been reached and unfortunately, we believe this will not be an end all solution.

## Code Structure
All teams have delivered full Object Oriented packages which can therefore easily be implemented on top of each other. Team Zandbakje has however, chosen to develop this even more. Because of this choice, we recommend all code is supplemented to the base delivered by team Zandbakje. For more info on how to do this, review the handoff document supplied by Zandbakje.