# Advice for parts GreenDigger
During the last semester our three teams worked independently to develop the best version of their assigned parts. This document presents a recommendation on which parts of the three projects could be combined to create the best final solution.

## Excavation Arm
Since both Team GroeneGravers and Team Zandbakje have worked on an excavation tool, we recommend that future developers combine the two projects. Team GroeneGravers has delivered a full excavation arm with inverse kinematics. This excavation tool performs well but does not influence the dug area. This limitation restricts the reliability of the simulated reality. Team Zandbakje has delivered a full tool which digs out an area in the simulated environment but has not developed a fully functional excavation arm. These different strengths are why we recommend the combination of the two systems.

## Pathfinding
Both teams MoonDiggers and Zandbakje have worked on a pathfinding algorithm. The pathfinding algorithm of MoonDiggers contains a full implementation of the A* algorithm to find the right path across the specified terrain. Team Zandbakje chose to develop a limited version of a pathfinding algorithm which was enough to show the implementations they made on their main components. 

Since it was not the task of Team Zandbakje to code a full pathfinding algorithm it is not expected of them to deliver one. This is why we recommend the pathfinding algorithm delivered by Team MoonDiggers. The implemented A* algorithm could be expanded to better fit the Autonomous Mobile Platform. More about this expansion can be found in the handoff document supplied by MoonDiggers.

## Object detection
Team Zandbakje has chosen to implement a LiDAR system to detect obstacles around the Autonomous Mobile Platform and report them. Setting this up cost them quite some time and resources. LiDAR demands some significant hardware resources and is not yet fully developed which is why we recommend further development of this system. In the meantime, the object detection system developed by Team MoonDiggers meets all requirements but has clear limitations. These limitations have almost been reached and unfortunately, we do not believe this solution will be sufficient in the long term.

## Code Structure
All teams have delivered fully object-oriented software packages which can therefore easily be implemented on top of each other. Team Zandbakje has, however, taken this a step further. Because of this, we recommend using Team Zandbakje their codebase as the foundation and integrating the other components into it. For more info on how to do this, review the handoff document supplied by Zandbakje.