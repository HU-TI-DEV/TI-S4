# Documentation Groene Gravers

## Keydrivers

| **Key Driver**            | **Application drivers**                                                          |
| ------------------------- | -------------------------------------------------------------------------------- |
| **Reputation**             | - Safety  <br> - Quality                                                   |
| **Performance**           | - Accuracy  <br> - Reach <br> - Movement speed <br> - Scalability   |
| **Leeruitkomsten**        | - Use of Gazebo <br> - System intelligence                           |

<br>

## Requirements
### Functionele Requirements

|   ID    | Functional Requirement                                        | priority    |
| ------- | ------------------------------------------------------------- | ----------- |
| **F01** | The product will be represented in a simulation                     | Must have   |
| **F02** | The excavator has a digging arm                           | Must have   |
| **F03** | The excacator has a rotating base                     | Must have   |
| **F04** | The arm must be able to move multiple joints independently             | Must have   |
| **F05** | The movements of the arm will be autonomous                 | Should have   |
| **F06** | The digger had a front shovel that can move back and forth      | Must have   |
| **F07** | The digging arm determines the fastest path to its target point          | Must have   |
| **F08** | The excavator is able to drive                              | Could have  |
| **F09** | The excavator can detect obstacles                            | Could have  |
| **F10** | The system stops when an emergency button is pressed | Could have  |
| **F11** | Diggers adjust action based on feedback                       | Could have  |
| **F12** | Digger prevents harm during excavation                        | Could have  |
| **F13** | Digger skips a planned excavation if an obstacle is detected  | Could have |
| **F14** |The excavator is manually controllable for demostrations | Could have |

<br>

### Non-Functional Requirements

|    ID    | Non-Functional Requirement                                   | priority  |
| -------- | ------------------------------------------------------------ | --------- |
| **NF01** | The digging arm must be able to reach a target point with a maximum deviation of 5 centimeters in the simulation.                                                     | Must have |
| **NF02** | The emergency stop (F10) must freeze all movements in the simulator within 500ms after activation.                                                            | Must have |
| **NF03** |  The simulation must run smoothly without lagging or freezing                                                            | Should have |
| **NF04** | The digging arm moves smoothly from point a to point b without stuttering                                                            | Must have |
| **NF05** | For demonstrations, the excavator is controllable via keyboard (F14)                                                             | Should have |
| **NF06** |   The simulation must run in a Docker container with Gazebo                                                      | Must have |
| **NF07** | The arm must be able to work together with the rotating base so it can dig in 3D                                                        | Must have |
| **NF08** |  The excavator is made with basic shapes, without detail                                                       | Must have |
| **NF09** |  The digging arm calculations are performed using inverse kinematics.                                                        | Must have |
| **NF10** |  The arm can extend at least 2.5 meters, allowing you to dig a semicircle of 5 meters                                                    | Must have |
| **NF11** |  The front shovel can be controlled independently from the arm                                                    | Must have |


### Constraints

|    ID    | Constraints                                   
| -------- | --------------------------------------------- 
| **C01**  | The product must be simulated in Gazebo 
| **C02**  | The excavator must use a front shovel.                                        
| **C03**  | The platform of the excavator must be 4.5 meters wide and 2 meters long.
| **C04**  | The tires of the excavator must have a diameter of 0.8 meters.
| **C05**  | The excavator arm must be able to dig a semicircle with a radius of 5 meters.
| **C06**  | The pivot point of the excavator arm must extend beyond the wheels so that they do not obstruct its movement, and must be located on the side of the platform with a counterweight on the opposite side.

<br>

## Keydriver Chart
![100](references/GreenDiggers_KeydriverChart.jpg)

Here we see the Keydrivers, application drivers and requirements. The lines indicate the connections between them, showing the relevance of all aspects. 