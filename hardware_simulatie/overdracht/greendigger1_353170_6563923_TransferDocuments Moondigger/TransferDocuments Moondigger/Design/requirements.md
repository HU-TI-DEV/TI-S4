# Requirements & Constraints

## Constraints

| Name                | ``C01 - Limited size simulation environment``                                                                               |
| ------------------- | --------------------------------------------------------------------------------------------------------------------------- |
| Description         |  The simulation environment needs to not be too large.                                                                      |
| Rationale           |  The laptops need to be able to run the simulation.                                                                         |
| Priority            |  Must Have |

## Functional Requirements

### Simulation environment

| Name                | ``F01 - Simulated autonomous mobile platform``                                                                              |
| ------------------- | --------------------------------------------------------------------------------------------------------------------------- |
| Description         |  The autonomous mobile platform is in the simulation.                                                                       |
| Rationale           |  The goal is to build a simulated environment containing the product.                                                       |
| Priority            |  Must Have |

| Name                | ``F02 - Slope of simulated surface``                                                                                        |
| ------------------- | --------------------------------------------------------------------------------------------------------------------------- |
| Description         |  The plane that represents the surface needs to be on an incline.                                                           |
| Rationale           |  The area where the autonomous mobile platforms will be deployed, is also on an incline.                                    |
| Priority            |  Must Have |

| Name                | ``F03 - Obstacles in simulation``                                                                                           |
| ------------------- | --------------------------------------------------------------------------------------------------------------------------- |
| Description         |  The simulation must contain obstacles.                                                                                     |
| Rationale           |  This represents the area where the autonomous mobile platforms will be deployed.                                           |
| Priority            |  Must Have | 

| Name                | ``F04 - Irregular surface height``                                                                                          |
| ------------------- | --------------------------------------------------------------------------------------------------------------------------- |
| Description         |  The simulation's surface must contain irregular variations in height.                                                      |
| Rationale           |  This represents potential hills and other terrain elements the area can contain where the autonomous mobile platforms will be deployed.|
| Priority            |  Should Have |

| Name                | ``F05 - Physics engine for simulation environment``                                                                         |
| ------------------- | --------------------------------------------------------------------------------------------------------------------------- |
| Description         |  The simulation environment uses a physics engine.                                                                          |
| Rationale           |  This is to to simulate basis laws of nature.                                                                               |
| Priority            |  Should Have |

| Name                | ``F06 - Large size of simulated environment``                                                                               |
| ------------------- | --------------------------------------------------------------------------------------------------------------------------- |
| Description         |  The simulated environment needs a large amount of traverseable terrain.                                                    |
| Rationale           |  In order to test the autonomous mobile platform, the autonomous mobile platform needs to be able to move.                  |
| Priority            |  Must Have |

### Autonomous mobile platform properties

| Name                | ``F07 - Autonomous mobility``                                                                                               |
| ------------------- | --------------------------------------------------------------------------------------------------------------------------- |
| Description         |  The autonomous mobile platform needs to be able to move autonomously in the simulated environment.                         |
| Rationale           |  To ensure proper placement for bunds, the autonomous mobile platform needs to be able to move.                             |
| Priority            |  Must Have |

| Name                | ``F08 - Autonomous navigation between points``                                                                              |
| ------------------- | --------------------------------------------------------------------------------------------------------------------------- |
| Description         |  The autonomous mobile platform needs to be able to navigate autonomously and safely between points.                        |
| Rationale           |  The autonomous mobile platform needs to be able to navigate to the right point to ensure proper bund placement.            |
| Priority            |  Must Have |

| Name                | ``F09 - Obstacle recognition (GD)``                                                                                         |
| ------------------- | --------------------------------------------------------------------------------------------------------------------------- |
| Description         |  The autonomous mobile platform can recognize objects.                                                                      |
| Rationale           |  To support autonomous operation by giving the autonomous mobile platform the ability to assess its environment.            |
| Priority            |  Must Have |

| Name                | ``F10 - Autonomous mobile platform excavation tool``                                                                        |
| ------------------- | --------------------------------------------------------------------------------------------------------------------------- |
| Description         |  The autonomous mobile platform has an excavation tool.                                                                     |
| Rationale           |  The autonomous mobile platform should be able to create bunds.                                                             |
| Priority            |  Must have |

### Excavation process

| Name                | ``F11 - Safe excavation (GD)``                                                                                              |
| ------------------- | --------------------------------------------------------------------------------------------------------------------------- |
| Description         |  The autonomous mobile platform avoids hurting flora and fauna during the excavation process.                               |
| Rationale           |  This is to protect the already damaged environment while excavating.                                                       |
| Priority            |  Could Have |

### Navigation software

| Name                | ``F12 - Obstacle avoidance (GD)``                                                                                           |
| ------------------- | --------------------------------------------------------------------------------------------------------------------------- |
| Description         |  The autonomous mobile platform avoids obstacles.                                                                           |
| Rationale           |  This is to prevent the autonomous mobile platform from getting damaged or stuck.                                           |
| Priority            |  Must Have |

| Name                | ``F13 - Excavation avoidance (GD)``                                                                                         |
| ------------------- | --------------------------------------------------------------------------------------------------------------------------- |
| Description         |  The autonomous mobile platform avoids dug bunds.                                                                           |
| Rationale           |  This is to prevent the autonomous mobile platform from damaging previous work done by itself or other parts of the fleet.  |
| Priority            |  Must Have |

| Name                | ``F14 - Safe navigation (GD)``                                                                                              |
| ------------------- | --------------------------------------------------------------------------------------------------------------------------- |
| Description         |  The autonomous mobile platform avoids hurting flora and fauna during navigation.                                           |
| Rationale           |  This is to protect the already damaged environment while moving.                                                           |
| Priority            |  Must Have |

## Non-Functional Requirements

### Simulation environment

| Name                | ``NF01 - Simulation in Gazebo``                                                                                                             |
| ------------------- | ------------------------------------------------------------------------------------------------------------------------------------------- |
| Description         |  The simulation itself has to be inside of Gazebo.                                                                                          |
| Rationale           |  To ensure proper future-proofing due to Gazebo's ability to run on multiple types of devices.                                              |
| Priority            |  Must have |

| Name                | ``NF02 - Minimal amount obstacles``                                                                                                         |
| ------------------- | ------------------------------------------------------------------------------------------------------------------------------------------- |
| Description         |  There should be atleast 4 obstacles present, 2 of which with a low centre of gravity and 2 with a high centre of gravity.                  |
| Rationale           |  The autonomous mobile platform needs to be able to detect obstacles and navigate around them.                                              |
| Priority            |  Must have |

| Name                | ``NF03 - Height variation in surface``                                                                                                      |
| ------------------- | ------------------------------------------------------------------------------------------------------------------------------------------- |
| Description         |  There should be 1 height irregularity in the simulated surface.                                                                            |
| Rationale           |  To ensure the autonomous mobile platform has proper difficult terrain detection and avoidance, a height irregularity needs to be present.  |
| Priority            |  Should have | 

| Name                | ``NF04 - DART physics engine``                                                                                                              |
| ------------------- | ------------------------------------------------------------------------------------------------------------------------------------------- |
| Description         |  The standard Gazebo DART physics engine needs to be present and active inside of the simulation.                                           |
| Rationale           |  This is to ensure the fact the simulation is accurate, reliable and representative.                                                        |
| Priority            |  Must have |

### Autonomous mobile platform properties

| Name                | ``NF05 - Autonomous mobile platform dimensions (GD)``                                                                                       |
| ------------------- | ------------------------------------------------------------------------------------------------------------------------------------------- |
| Description         |  The autonomous mobile platform needs to be 4.5 meters long, 2 meters wide and have wheels with a diameter of 0.8 meters.                   |
| Rationale           |  These dimensions are the standard dimensions provided.                                                                                     |
| Priority            |  Must have |

| Name                | ``NF06 - Propulsion (GD)``                                                                                                                  |
| ------------------- | ------------------------------------------------------------------------------------------------------------------------------------------- |
| Description         |  The autonomous mobile platform uses 4 non-steering wheels.                                                                                 |
| Rationale           |  This is to ensure the autonomous mobile platform has the least amount of moving parts and highest energy efficiency.                       |
| Priority            |  Must have |

| Name                | ``NF07 - Steering (GD)``                                                                                                                    |
| ------------------- | ------------------------------------------------------------------------------------------------------------------------------------------- |
| Description         |  The autonomous mobile platform's wheels each can be powered individually to allow turning.                                                 |
| Rationale           |  For high energy efficiency and high degrees of rotation, the wheels need to be able to rotate at different speeds.                         |
| Priority            |  Must have |

| Name                | ``NF08 - Excavation tool type (GD)``                                                                                                        |
| ------------------- | ------------------------------------------------------------------------------------------------------------------------------------------- |
| Description         |  The autonomous mobile platform has a front shovel.                                                                                         |
| Rationale           |  For one-sided excavation a front shovel is optimal.                                                                                        |
| Priority            |  Must have |

| Name                | ``NF09 - Weight balancing (GD)``                                                                                                            |
| ------------------- | ------------------------------------------------------------------------------------------------------------------------------------------- |
| Description         |  The autonomous mobile platform has a counterweight to compensate the weight of the excavation arm.                                         |
| Rationale           |  This is to balance the weight in the autonomous mobile platform.                                                                           |
| Priority            |  Could have |

| Name                | ``NF10 - Excavation arm connection (GD)``                                                                                                   |
| ------------------- | ------------------------------------------------------------------------------------------------------------------------------------------- |
| Description         |  The autonomous mobile platform is connected to its excavation arm through a rotating disc.                                                 |
| Rationale           |  This will allow the excavation arm to rotate on the chassis of the autonomous mobile platform.                                             |
| Priority            |  Should have |

| Name                | ``NF11 - Excavation tool dimensions (GD)``                                                                                                  |
| ------------------- | ------------------------------------------------------------------------------------------------------------------------------------------- |
| Description         |  The front shovel has a bucket that is 30 centimeters wide.                                                                                 |
| Rationale           |  This is part of the optimal excavation process.                                                                                            |
| Priority            |  Must have |

| Name                | ``NF12 - Excavation arm joints (GD)``                                                                                                       |
| ------------------- | ------------------------------------------------------------------------------------------------------------------------------------------- |
| Description         |  The excavation arm joints are electronically controlled.                                                                                   |
| Rationale           |  Electronically controlled joints ensure that implementation doesn't get too complex.                                                       |
| Priority            |  Should have |

| Name                | ``NF13 - Surroundings capturing through camera``                                                                                            |
| ------------------- | ------------------------------------------------------------------------------------------------------------------------------------------- |
| Description         |  The autonomous mobile platform uses 1 simulated camera.                                                                                    |
| Rationale           |  This is to support autonomous operation by capturing its surroundings.                                                                     |
| Priority            |  Must have |

| Name                | ``NF14 - Obstacle recognition through software``                                                                                            |
| ------------------- | ------------------------------------------------------------------------------------------------------------------------------------------- |
| Description         |  The autonomous mobile platform uses software to analyse camera images.                                                                     |
| Rationale           |  This is to ensure autonomous operation through simulated awareness of its surroundings.                                                    |
| Priority            |  Must have |

### Navigation software

| Name                | ``NF15 - Obstacle avoidance``                                                                                                               |
| ------------------- | ------------------------------------------------------------------------------------------------------------------------------------------- |
| Description         |  The navigation software should pathfind around detected obstacles.                                                                         |
| Rationale           |  The autonomous mobile platform needs to avoid damage to itself or getting stuck while navigating its allocated space.                      |
| Priority            |  Must have |

### Excavation process

| Name                | ``NF16 - Bund dimensions (GD)``                                                                                                             |
| ------------------- | ------------------------------------------------------------------------------------------------------------------------------------------- |
| Description         |  The autonomous mobile platform digs a bund in the shape of a semicircle, 5 meters wide, 30 centimeters deep.                               |
| Rationale           |  These dimensions are required for a bund to work properly.                                                                                 |
| Priority            |  Could have |

| Name                | ``NF17 - Bund density (GD)``                                                                                                                |
| ------------------- | ------------------------------------------------------------------------------------------------------------------------------------------- |
| Description         |  The autonomous mobile platform plans and digs bunds with a density of 80 bunds per hectare.                                                |
| Rationale           |  This is the density required for the bunds to operate the most efficiently.                                                                |
| Priority            |  Must have |

| Name                | ``NF18 - Excavation method (GD)``                                                                                                           |
| ------------------- | ------------------------------------------------------------------------------------------------------------------------------------------- |
| Description         |  The autonomous mobile platform can dig the entire bund from 1 spot. [See this image for reference](ideeDigger.png)                         |
| Rationale           |  This ensures the bund is dug efficiently.                                                                                                  |
| Priority            |  Could have |

| Name                | ``NF19 - Bund placing (GD)``                                                                                                                |
| ------------------- | ------------------------------------------------------------------------------------------------------------------------------------------- |
| Description         |  The autonomous mobile platform plans and digs bunds in such a way, that it doesn't have to change direction to dig the next one.           |
| Rationale           |  This ensures efficient navigating and digging.                                                                                             |
| Priority            |  Should have |