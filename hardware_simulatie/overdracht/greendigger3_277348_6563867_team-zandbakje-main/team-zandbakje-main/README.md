![alt text](digger.png)

# Green Digger Project by team Zandbakje

`Green Digger:`  
> [https://www.greendigger.org/](https://www.greendigger.org/)

`Team members:`

| Group members | Github name |
|---------------|-------------|
| Luuk          | Ocarian     |
| Robin         | GrijzePanda |
| Kjell         | ShelleKjell |
| Alea          | Replitard   |

`Start-date : 2nd of March 2026`  

# Documentation website

This is the handover guide for the Green Digger project. It maps the repository files and folders, with links and short descriptions, so future teams can find the key code, configuration, context and documentation quickly.

`Author: Ocarian`  
`Contributor: Replitard`

## General recommendations

### Setting up the world

To set up the environment, read the docker container instructions: [README Docker](https://github.com/2025-TICT-TV2SE4-24-3-V/team-zandbakje/blob/main/docker/README.md)

Make sure you have the s4_2026 docker image (may have different naming in the future).  
You can get this image from teachers at Hogeschool Utrecht.

Once you have set up the docker container, read the `Runner Readme` in [README Runner](https://github.com/2025-TICT-TV2SE4-24-3-V/team-zandbakje/blob/main/documentation/runner/README.md). This document will guide you through the steps to create the Gazebo simulation and teaches the general workflow.

For more information about how the world is set up and created read the `World Setup` in [Extended README Environment](https://github.com/2025-TICT-TV2SE4-24-3-V/team-zandbakje/blob/main/documentation/environment/TECHNICAL_DOCUMENTATION.md).

### Making edits to the main logic of the digger

For this project we use what we call the `Behaviour Manager`. This code acts as the central loop that runs the digger. For more info read: [README Behaviour Manager](https://github.com/2025-TICT-TV2SE4-24-3-V/team-zandbakje/tree/main/documentation/behaviour_manager).

The `Behaviour Manager` uses code written in [src](https://github.com/2025-TICT-TV2SE4-24-3-V/team-zandbakje/tree/main/src) like `drive_poi.py` as modules that can be executed like a state machine would.  
This makes it so new project features can be created in seperate files and then added as new states to the `Behaviour Manager`.

### Interacting with Gazebo

For this project we have made an `interface` that acts as the central communicator between the code and the Gazebo world. More info about this interface can be found at [README Interface](https://github.com/2025-TICT-TV2SE4-24-3-V/team-zandbakje/tree/main/documentation/interface).

Make sure that whenever a new sensor, topic our subscriber/publisher gets added to code, it communicates to the interface which then communicates with the world.  
Running the `interface.py` program gives valuable terminal feedback such as positions and contact.

### Documentation

Documentation is stored within the [Documentation](https://github.com/2025-TICT-TV2SE4-24-3-V/team-zandbakje/tree/main/documentation) folder. Here you can find markdown files that act as a guide for using the written code and how to iterate and develop further.

## Repository Overview

- [documentation](https://github.com/2025-TICT-TV2SE4-24-3-V/team-zandbakje/tree/main/documentation) — Documentation for code, general instruction, technical breakdowns and usage of parts within the project.
- [src](https://github.com/2025-TICT-TV2SE4-24-3-V/team-zandbakje/tree/main/src) — Source code folder that has all the code related to this project.
- [docker](https://github.com/2025-TICT-TV2SE4-24-3-V/team-zandbakje/tree/main/docker) — Docker compose, devcontainer configuration, and container build files.
- [docs](https://github.com/2025-TICT-TV2SE4-24-3-V/team-zandbakje/tree/main/docs) — Documents related to teamwork, requirements, client-specifications and other notes

## [Documentation](https://github.com/2025-TICT-TV2SE4-24-3-V/team-zandbakje/tree/main/documentation)

This folder contains technical documentation for the codebase, environment, interface, points of interest, lidar and testscripts. Use it when you need design references, implementation details, or system architecture guidance.

### [behaviour_manager](https://github.com/2025-TICT-TV2SE4-24-3-V/team-zandbakje/tree/main/documentation/behaviour_manager)

- [README.md](https://github.com/2025-TICT-TV2SE4-24-3-V/team-zandbakje/blob/main/documentation/behaviour_manager/README.md) — behaviour manager architecture, state machine logic, and usage examples for the main control loop.

### [environment](https://github.com/2025-TICT-TV2SE4-24-3-V/team-zandbakje/tree/main/documentation/environment)

- [README.md](https://github.com/2025-TICT-TV2SE4-24-3-V/team-zandbakje/blob/main/documentation/environment/README.md) — terrain generation, dynamic digging simulation, and the heightmap-based environment setup.
- [TECHNICAL_DOCUMENTATION.md](https://github.com/2025-TICT-TV2SE4-24-3-V/team-zandbakje/blob/main/documentation/environment/TECHNICAL_DOCUMENTATION.md) — deeper technical documentation for terrain and environment implementation details.

### [interface](https://github.com/2025-TICT-TV2SE4-24-3-V/team-zandbakje/tree/main/documentation/interface)

- [README.md](https://github.com/2025-TICT-TV2SE4-24-3-V/team-zandbakje/blob/main/documentation/interface/README.md) — Gazebo/Python interface layer, sensor state management, and arm/drive command publishing.

### [lidar](https://github.com/2025-TICT-TV2SE4-24-3-V/team-zandbakje/tree/main/documentation/lidar)

- [README.md](https://github.com/2025-TICT-TV2SE4-24-3-V/team-zandbakje/blob/main/documentation/lidar/README.md) — LiDAR Object Detection and Clustering

### [pid](https://github.com/2025-TICT-TV2SE4-24-3-V/team-zandbakje/tree/main/documentation/pid)

- [README.md](https://github.com/2025-TICT-TV2SE4-24-3-V/team-zandbakje/blob/main/documentation/pid/README.md) — core behaviour, description of pid terms, and integration with point-of-interest navigation
- [TECHNICAL_DOCUMENTATION.md](https://github.com/2025-TICT-TV2SE4-24-3-V/team-zandbakje/blob/main/documentation/pid/TECHNICAL_DOCUMENTATION.md) — technical reference for the PID controller, sensor input, yaw extraction and normalization, control logic, main public function, navigation integration, and tuning guidance.

### [points_of_interest](https://github.com/2025-TICT-TV2SE4-24-3-V/team-zandbakje/tree/main/documentation/points_of_interest)

- [README.md](https://github.com/2025-TICT-TV2SE4-24-3-V/team-zandbakje/blob/main/documentation/points_of_interest/README.md) — point-of-interest navigation, route definition, and POI-based autonomous driving behaviour.
- [TECHNICAL_DOCUMENTATION.md](https://github.com/2025-TICT-TV2SE4-24-3-V/team-zandbakje/blob/main/documentation/points_of_interest/TECHNICAL_DOCUMENTATION.md) — technical reference for POI navigation, route execution, and control integration.

### [project-style](https://github.com/2025-TICT-TV2SE4-24-3-V/team-zandbakje/blob/main/documentation/project-style)

- [architecture.md](https://github.com/2025-TICT-TV2SE4-24-3-V/team-zandbakje/blob/main/documentation/project-style/architecture.md) — architecture explanation for the Green Digger simulation.
- [project_architecture.drawio](https://github.com/2025-TICT-TV2SE4-24-3-V/team-zandbakje/blob/main/documentation/project-style/project_architecture.drawio) — diagram showing the overall project architecture and component relationships.
- [style.md](https://github.com/2025-TICT-TV2SE4-24-3-V/team-zandbakje/blob/main/documentation/project-style/style.md) — code style, git workflow, and documentation standards used by the team.

### [runner](https://github.com/2025-TICT-TV2SE4-24-3-V/team-zandbakje/tree/main/documentation/runner)

- [README.md](https://github.com/2025-TICT-TV2SE4-24-3-V/team-zandbakje/blob/main/documentation/runner/README.md) — runner script behaviour, usage, and notes.

### [tests](https://github.com/2025-TICT-TV2SE4-24-3-V/team-zandbakje/tree/main/documentation/tests)

- [README.md](https://github.com/2025-TICT-TV2SE4-24-3-V/team-zandbakje/blob/main/documentation/tests/README.md) — test scripts and debugging tools for validating camera, manual control, heading, and navigation components.

## [Src](https://github.com/2025-TICT-TV2SE4-24-3-V/team-zandbakje/tree/main/src)

This folder consists of source code used for this project. Within this folder you will find things like: the Gazebo environment code (sdf files), code for the interface layer that communicates with Gazebo, the behaviour manager (central logic), all code components of the general logic like digging and path-finding and scripts for testing and debugging.

<details><summary>Click to expand</summary>

- [behaviour_manager.py](https://github.com/2025-TICT-TV2SE4-24-3-V/team-zandbakje/blob/main/src/behaviour_manager.py) — state machine that decides digger actions based on interface input and sensor state.
- [dig_halfmoon.py](https://github.com/2025-TICT-TV2SE4-24-3-V/team-zandbakje/blob/main/src/dig_halfmoon.py) — digging strategy for creating half-moon shaped trenches.
- [dig_tile.py](https://github.com/2025-TICT-TV2SE4-24-3-V/team-zandbakje/blob/main/src/dig_tile.py) — runtime terrain modifier that updates the heightmap when the bucket digs into the terrain.
- [drive_pid.py](https://github.com/2025-TICT-TV2SE4-24-3-V/team-zandbakje/blob/main/src/drive_pid.py) — PID-based drive control.
- [drive_poi.py](https://github.com/2025-TICT-TV2SE4-24-3-V/team-zandbakje/blob/main/src/drive_poi.py) — point-of-interest driving behaviour.
- [make_heightmap.py](https://github.com/2025-TICT-TV2SE4-24-3-V/team-zandbakje/blob/main/src/make_heightmap.py) — script to generate a noisy grayscale heightmap for the terrain.
- [navigate.py](https://github.com/2025-TICT-TV2SE4-24-3-V/team-zandbakje/blob/main/src/navigate.py) — navigation logic for reaching target points.
- [poi_route.json](https://github.com/2025-TICT-TV2SE4-24-3-V/team-zandbakje/blob/main/src/poi_route.json) — route definition for points of interest.

### [environment](https://github.com/2025-TICT-TV2SE4-24-3-V/team-zandbakje/tree/main/src/environment)

- [media](https://github.com/2025-TICT-TV2SE4-24-3-V/team-zandbakje/tree/main/src/environment/media) — pre-generated heightmaps, textures, and normal maps used by the environment.
- [models](https://github.com/2025-TICT-TV2SE4-24-3-V/team-zandbakje/tree/main/src/environment/models) - models used by the environment for visuals.
- [arm.sdf](https://github.com/2025-TICT-TV2SE4-24-3-V/team-zandbakje/blob/main/src/environment/arm.sdf) — Gazebo model definition for the crane/arm mechanism.
- [digger.sdf](https://github.com/2025-TICT-TV2SE4-24-3-V/team-zandbakje/blob/main/src/environment/digger.sdf) — Gazebo model definition for the digging vehicle base and manipulator.
- [marker.sdf](https://github.com/2025-TICT-TV2SE4-24-3-V/team-zandbakje/blob/main/src/environment/marker.sdf) — marker model used in the Gazebo world.
- [terrain.sdf](https://github.com/2025-TICT-TV2SE4-24-3-V/team-zandbakje/blob/main/src/environment/terrain.sdf) — terrain model using the generated heightmap and texture assets.
- [world.sdf](https://github.com/2025-TICT-TV2SE4-24-3-V/team-zandbakje/blob/main/src/environment/world.sdf) — Gazebo world file assembling the terrain, digger, and arm models.

### [interface](https://github.com/2025-TICT-TV2SE4-24-3-V/team-zandbakje/tree/main/src/interface)

- [arm_helper.py](https://github.com/2025-TICT-TV2SE4-24-3-V/team-zandbakje/blob/main/src/interface/arm_helper.py) — helper functions for controlling the excavator arm.
- [interface.py](https://github.com/2025-TICT-TV2SE4-24-3-V/team-zandbakje/blob/main/src/interface/interface.py) — main high-level interface script for the simulated digger.

### [tests](https://github.com/2025-TICT-TV2SE4-24-3-V/team-zandbakje/tree/main/src/tests)

- [camera_test.py](https://github.com/2025-TICT-TV2SE4-24-3-V/team-zandbakje/blob/main/src/tests/camera_test.py) — test script for camera and image capture behaviour.
- [CMakeLists.txt](https://github.com/2025-TICT-TV2SE4-24-3-V/team-zandbakje/blob/main/src/tests/CMakeLists.txt) — build configuration for sensor-related C++ components.
- [keyboard_publisher.py](https://github.com/2025-TICT-TV2SE4-24-3-V/team-zandbakje/blob/main/src/tests/keyboard_publisher.py) — keyboard input publisher for manual control testing.
- [lidar.cpp](https://github.com/2025-TICT-TV2SE4-24-3-V/team-zandbakje/blob/main/src/tests/lidar.cpp) — LIDAR sensor simulation source code using pointcloud.
- [navigate_to_point.py](https://github.com/2025-TICT-TV2SE4-24-3-V/team-zandbakje/blob/main/src/tests/navigate_to_point.py) — navigation test for reaching a target point.
- [pid_heading.py](https://github.com/2025-TICT-TV2SE4-24-3-V/team-zandbakje/blob/main/src/tests/pid_heading.py) — PID heading control test.
- [subscriber_publisher.py](https://github.com/2025-TICT-TV2SE4-24-3-V/team-zandbakje/blob/main/src/tests/subscriber_publisher.py) — combined subscriber/publisher for topics.</details>

## [Docker](https://github.com/2025-TICT-TV2SE4-24-3-V/team-zandbakje/tree/main/docker)

This folder contains the container configuration and launch scripts used to build and run the project in a reproducible development environment. Use the files here to set up the dev container, install required dependencies, and start the project with the working directory mounted to the docker container.


<details><summary>Click to expand</summary>

- [Dockerfile](https://github.com/2025-TICT-TV2SE4-24-3-V/team-zandbakje/blob/main/docker/Dockerfile) — Docker image build instructions.
- [compose.yaml](https://github.com/2025-TICT-TV2SE4-24-3-V/team-zandbakje/blob/main/docker/compose.yaml) — Docker Compose definition for starting the project container.
- [devcontainer.json](https://github.com/2025-TICT-TV2SE4-24-3-V/team-zandbakje/blob/main/docker/devcontainer.json) — VS Code DevContainer configuration for development.
- [README.md](https://github.com/2025-TICT-TV2SE4-24-3-V/team-zandbakje/blob/main/docker/README.md) — Docker usage notes and setup documentation.

</details>

## [Docs](https://github.com/2025-TICT-TV2SE4-24-3-V/team-zandbakje/tree/main/docs)

This folder holds project management documents, team reports and client specifications. Here you can review requirements, meeting decisions, sprint history, and the documentation that supported project planning and delivery.

### [project-items](https://github.com/2025-TICT-TV2SE4-24-3-V/team-zandbakje/tree/main/docs/project-items)

Client-related documents and project planning documents.

<details><summary>Click to expand</summary>

#### [client-documentation](https://github.com/2025-TICT-TV2SE4-24-3-V/team-zandbakje/tree/main/docs/project-items/client-documentation)

- [bundPVEGreenDigger.pdf](https://github.com/2025-TICT-TV2SE4-24-3-V/team-zandbakje/blob/main/docs/project-items/client-documentation/bundPVEGreenDigger.pdf) — client specifications for bund construction, erosion control and the expected behaviour of the Green Digger in the field.
- [Functional Requirements.pdf](https://github.com/2025-TICT-TV2SE4-24-3-V/team-zandbakje/blob/main/docs/project-items/client-documentation/Functional%20Requirements.pdf) — the functional requirements for the entire GreenDigger project provided by the client.
- [GreenDigger - Nobleo project plan.pdf](https://github.com/2025-TICT-TV2SE4-24-3-V/team-zandbakje/blob/main/docs/project-items/client-documentation/GreenDigger%20-%20Nobleo%20project%20plan.pdf) — formal project plan from Nobleo, including objectives, schedule, and stakeholder expectations.
- [GreenDigger - The Power of Half-Moons.pdf](https://github.com/2025-TICT-TV2SE4-24-3-V/team-zandbakje/blob/main/docs/project-items/client-documentation/GreenDigger%20-%20The%20Power%20of%20Half-Moons.pdf) — explanation of the half-moon digging strategy and why it is important for the project.
- [Instructies virtuele GreenDigger.docx](https://github.com/2025-TICT-TV2SE4-24-3-V/team-zandbakje/blob/main/docs/project-items/client-documentation/Instructies%20virtuele%20GreenDigger.docx) — visual and simulation requirements for the virtual Green Digger demonstration.
- [Project Plan Structure Student Team.docx](https://github.com/2025-TICT-TV2SE4-24-3-V/team-zandbakje/blob/main/docs/project-items/client-documentation/Project%20Plan%20Structure%20Student%20Team.docx) — planning template provided by the client.

#### [demo-items](https://github.com/2025-TICT-TV2SE4-24-3-V/team-zandbakje/tree/main/docs/project-items/demo-items)

- [img](https://github.com/2025-TICT-TV2SE4-24-3-V/team-zandbakje/tree/main/docs/project-items/demo-items/img) — folder containing images used for documentation and demo purposes.
- [20260402-0859-01.9693312.mp4](https://github.com/2025-TICT-TV2SE4-24-3-V/team-zandbakje/blob/main/docs/project-items/demo-items/20260402-0859-01.9693312.mp4) — demo recording of Lidar within a seperate environment.
- [20260408-0708-56.7265126.mp4](https://github.com/2025-TICT-TV2SE4-24-3-V/team-zandbakje/blob/main/docs/project-items/demo-items/20260408-0708-56.7265126.mp4) — demo recording of basic arm movements.
- [Screencast_20260406_185408.webm](https://github.com/2025-TICT-TV2SE4-24-3-V/team-zandbakje/blob/main/docs/project-items/demo-items/Screencast_20260406_185408.webm) — demo recording of basic turn movements for the digger.
- [screenshot.jpg](https://github.com/2025-TICT-TV2SE4-24-3-V/team-zandbakje/blob/main/docs/project-items/demo-items/screenshot.jpg) — image that shows digging capabilities within the environment.
- [sensors.mp4](https://github.com/2025-TICT-TV2SE4-24-3-V/team-zandbakje/blob/main/docs/project-items/demo-items/sensors.mp4) — demo recording of basic sensor topic readouts in the terminal with emphasis on the contactsensor.

#### [requirements](https://github.com/2025-TICT-TV2SE4-24-3-V/team-zandbakje/tree/main/docs/project-items/requirements)

- [functional_requirements.md](https://github.com/2025-TICT-TV2SE4-24-3-V/team-zandbakje/blob/main/docs/project-items/requirements/functional_requirements.md) — functional requirements for the project.
- [non_functional_requirements.md](https://github.com/2025-TICT-TV2SE4-24-3-V/team-zandbakje/blob/main/docs/project-items/requirements/non_functional_requirements.md) — non-functional requirements for the project.
- [KeyDrivers.md](https://github.com/2025-TICT-TV2SE4-24-3-V/team-zandbakje/blob/main/docs/project-items/requirements/KeyDrivers.md) — key drivers for the project.
- [project_plan_structure.md](https://github.com/2025-TICT-TV2SE4-24-3-V/team-zandbakje/blob/main/docs/project-items/requirements/project_plan_structure.md) — objectives, deliverables and scope for the project.
- [use_cases.md](https://github.com/2025-TICT-TV2SE4-24-3-V/team-zandbakje/blob/main/docs/project-items/requirements/use_cases.md) — project use cases.
- [VSD.md](https://github.com/2025-TICT-TV2SE4-24-3-V/team-zandbakje/blob/main/docs/project-items/requirements/VSD.md) — value sensitive design document describing the social and environmental impact considerations of the project.

#### [research](https://github.com/2025-TICT-TV2SE4-24-3-V/team-zandbakje/tree/main/docs/project-items/research)

- [hardware-rendering](https://github.com/2025-TICT-TV2SE4-24-3-V/team-zandbakje/tree/main/docs/project-items/research/hardware-rendering/README.md) — hardware rendering research for Gazebo with WSL and CUDA.
</details>

### [team-items](https://github.com/2025-TICT-TV2SE4-24-3-V/team-zandbakje/tree/main/docs/team-items)

Documents related to team collaboration, project planning, and progress tracking.

<details><summary>Click to expand</summary>

#### [attendance](https://github.com/2025-TICT-TV2SE4-24-3-V/team-zandbakje/tree/main/docs/team-items/attendance)

- [attendance_sheet.md](https://github.com/2025-TICT-TV2SE4-24-3-V/team-zandbakje/blob/main/docs/team-items/attendance/attendance_sheet.md) — team attendance log.

#### [demo](https://github.com/2025-TICT-TV2SE4-24-3-V/team-zandbakje/tree/main/docs/team-items/demo)

- [demo_class.md](https://github.com/2025-TICT-TV2SE4-24-3-V/team-zandbakje/blob/main/docs/team-items/demo/demo_class.md) — demo planning notes and presentation details for the project showcase.

#### [meetings](https://github.com/2025-TICT-TV2SE4-24-3-V/team-zandbakje/tree/main/docs/team-items/meetings)

Meeting notes and discussion records for the team, coaches, project leads, and demo planning. Use this section to understand past decisions and stakeholder feedback.

- [bartbozon_initial_meeting.md](https://github.com/2025-TICT-TV2SE4-24-3-V/team-zandbakje/blob/main/docs/team-items/meetings/bartbozon_initial_meeting.md) — notes from the initial meeting with Bart Bozon (teamcoach).
- [bartbozon_meeting_2.md](https://github.com/2025-TICT-TV2SE4-24-3-V/team-zandbakje/blob/main/docs/team-items/meetings/bartbozon_meeting_2.md) — notes from the second teamcoach meeting.
- [bartbozon_meeting_3.md](https://github.com/2025-TICT-TV2SE4-24-3-V/team-zandbakje/blob/main/docs/team-items/meetings/bartbozon_meeting_3.md) — notes from the third teamcoach meeting.
- [bartbozon_meeting_5.md](https://github.com/2025-TICT-TV2SE4-24-3-V/team-zandbakje/blob/main/docs/team-items/meetings/bartbozon_meeting_5.md) — notes from the fifth teamcoach meeting.
- [demo_meeting_1.md](https://github.com/2025-TICT-TV2SE4-24-3-V/team-zandbakje/blob/main/docs/team-items/meetings/demo_meeting_1.md) — notes from the first demo planning meeting.
- [greendigger_initial_meeting.md](https://github.com/2025-TICT-TV2SE4-24-3-V/team-zandbakje/blob/main/docs/team-items/meetings/greendigger_initial_meeting.md) — initial project meeting notes for the Green Digger project.
- [greendigger_meeting_2.md](https://github.com/2025-TICT-TV2SE4-24-3-V/team-zandbakje/blob/main/docs/team-items/meetings/greendigger_meeting_2.md) — second Green Digger meeting notes.
- [greendigger_meeting_3.md](https://github.com/2025-TICT-TV2SE4-24-3-V/team-zandbakje/blob/main/docs/team-items/meetings/greendigger_meeting_3.md) — third Green Digger meeting notes.
- [projectlead_meeting.md](https://github.com/2025-TICT-TV2SE4-24-3-V/team-zandbakje/blob/main/docs/team-items/meetings/projectlead_meeting.md) — notes from the meeting with project leads.
- [sprint1_team_meeting.md](https://github.com/2025-TICT-TV2SE4-24-3-V/team-zandbakje/blob/main/docs/team-items/meetings/sprint1_team_meeting.md) — sprint 1 team meeting notes.
- [sprint3_team_meeting.md](https://github.com/2025-TICT-TV2SE4-24-3-V/team-zandbakje/blob/main/docs/team-items/meetings/sprint3_team_meeting.md) — sprint 3 team meeting notes.
- [teamcontract_feedback.md](https://github.com/2025-TICT-TV2SE4-24-3-V/team-zandbakje/blob/main/docs/team-items/meetings/teamcontract_feedback.md) — feedback on the team contract.

#### [sprints](https://github.com/2025-TICT-TV2SE4-24-3-V/team-zandbakje/tree/main/docs/team-items/sprints)

Sprint reports and retrospectives documenting work completed, priorities, and lessons learned each sprint.

- [sprint_verslag_1.md](https://github.com/2025-TICT-TV2SE4-24-3-V/team-zandbakje/blob/main/docs/team-items/sprints/sprint_verslag_1.md) — sprint 1 report.
- [sprint_verslag_2.md](https://github.com/2025-TICT-TV2SE4-24-3-V/team-zandbakje/blob/main/docs/team-items/sprints/sprint_verslag_2.md) — sprint 2 report.
- [sprint_verslag_3.md](https://github.com/2025-TICT-TV2SE4-24-3-V/team-zandbakje/blob/main/docs/team-items/sprints/sprint_verslag_3.md) — sprint 3 report.
- [sprint_verslag_4.md](https://github.com/2025-TICT-TV2SE4-24-3-V/team-zandbakje/blob/main/docs/team-items/sprints/sprint_verslag_4.md) — sprint 4 report.
- [sprint_verslag_5.md](https://github.com/2025-TICT-TV2SE4-24-3-V/team-zandbakje/blob/main/docs/team-items/sprints/sprint_verslag_5.md) — sprint 5 report.
- [sprint_verslag_6.md](https://github.com/2025-TICT-TV2SE4-24-3-V/team-zandbakje/blob/main/docs/team-items/sprints/sprint_verslag_6.md) — sprint 6 report.
- [sprint_verslag_template.md](https://github.com/2025-TICT-TV2SE4-24-3-V/team-zandbakje/blob/main/docs/team-items/sprints/sprint_verslag_template.md) — sprint report template.

#### [team-contract](https://github.com/2025-TICT-TV2SE4-24-3-V/team-zandbakje/tree/main/docs/team-items/team-contract)

- [teamcontract.md](https://github.com/2025-TICT-TV2SE4-24-3-V/team-zandbakje/blob/main/docs/team-items/team-contract/teamcontract.md) — the team contract document defining collaboration agreements and team norms.

#### [weekly-targets](https://github.com/2025-TICT-TV2SE4-24-3-V/team-zandbakje/tree/main/docs/team-items/weekly-targets)

Weekly planning and target tracking documents used to align work with sprint goals week by week.

- [target_1.md](https://github.com/2025-TICT-TV2SE4-24-3-V/team-zandbakje/blob/main/docs/team-items/weekly-targets/target_1.md) — weekly target 1.
- [target_2.md](https://github.com/2025-TICT-TV2SE4-24-3-V/team-zandbakje/blob/main/docs/team-items/weekly-targets/target_2.md) — weekly target 2.
- [target_3.md](https://github.com/2025-TICT-TV2SE4-24-3-V/team-zandbakje/blob/main/docs/team-items/weekly-targets/target_3.md) — weekly target 3.
- [target_4.md](https://github.com/2025-TICT-TV2SE4-24-3-V/team-zandbakje/blob/main/docs/team-items/weekly-targets/target_4.md) — weekly target 4.
- [target_5.md](https://github.com/2025-TICT-TV2SE4-24-3-V/team-zandbakje/blob/main/docs/team-items/weekly-targets/target_5.md) — weekly target 5.
- [target_6.md](https://github.com/2025-TICT-TV2SE4-24-3-V/team-zandbakje/blob/main/docs/team-items/weekly-targets/target_6.md) — weekly target 6.
- [target_7.md](https://github.com/2025-TICT-TV2SE4-24-3-V/team-zandbakje/blob/main/docs/team-items/weekly-targets/target_7.md) — weekly target 7.
- [target_8.md](https://github.com/2025-TICT-TV2SE4-24-3-V/team-zandbakje/blob/main/docs/team-items/weekly-targets/target_8.md) — weekly target 8.
- [target_9.md](https://github.com/2025-TICT-TV2SE4-24-3-V/team-zandbakje/blob/main/docs/team-items/weekly-targets/target_9.md) — weekly target 9.
- [target_10.md](https://github.com/2025-TICT-TV2SE4-24-3-V/team-zandbakje/blob/main/docs/team-items/weekly-targets/target_10.md) — weekly target 10.
- [weekly_targets_template.md](https://github.com/2025-TICT-TV2SE4-24-3-V/team-zandbakje/blob/main/docs/team-items/weekly-targets/weekly_targets_template.md) — template for weekly targets

</details>

