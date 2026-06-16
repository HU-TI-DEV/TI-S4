## Functional Requirements

`Authors: Ocarian, Replitard, GrijzePanda, ShelleKjell` 

| Name Requirements | Feature                                        | Rationale                                                                                      | Priority    |
| ----------------- | ---------------------------------------------- | ---------------------------------------------------------------------------------------------- | ----------- |
| F-001             | status reporting                               | The digger should be able to communicate the contents of the sensors.                          | Must Have   |
| F-002             | Local Obstacle Detection                       | The digger has to be able to autonomously detect (potential) obstacles                         | Must Have   |
| F-003             | Localization                                   | The digger should know where it is, relative to any given target.                              | Should Have |
| F-004             | Obstacle Avoidance                             | The digger must be able to make an avoiding maneuver for any detected obstacle.                | Should Have |
| F-005             | Local Planning/Control                         | The digger drives a set path on which it does the digging pattern.                             | Could Have  |
| F-006             | Excavation Control                             | The digger is able to go through a standard set of movements to dig it, without external data. | Must Have   |
| F-007             | stance compenstation                           | The digger is able to make a digging plan based on the surrounding obstacles.                  | Should Have |
| F-008             | Excavation Fallback Behavior - Skip Excavation | The digger skips a section of land it has to plot if an obstacle is detected.                  | Should Have |
| F-009             | Actuator control                               | The digger must respond to direct user inputs.                                                 | Should Have |
| F-010             | Digger Path Planning                           | The digger can autonomously plan a path and follow it.                                         | Could Have  |
| F-011             | Locomotion                                     | The digger must be able to drive around.                                                       | Must Have   |
| F-012             | Object Recgonition                             | The digger must be able to recognize objects.                                                  | Could Have   |

