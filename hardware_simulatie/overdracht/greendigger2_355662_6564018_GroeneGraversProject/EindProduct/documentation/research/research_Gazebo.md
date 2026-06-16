# Research & Process: Gazebo

## 1. Our Approach: Breaking it Down, Debugging, and OOP Refactoring
Because we were thrown straight into the deep end with Gazebo and robotics simulation at the start of the semester, we deliberately chose to break the project down into manageable pieces. Instead of building a complete excavator right away, we took a modular approach:

* **Step 1: Learning the Basics (PID & Physics)** Before even opening a model, we first figured out how PID controllers work within a simulated environment and how Gazebo handles forces. These consisted of 3 assignments provided by the school to teach us the basics. The rest we had to figure out completely on our own.
* **Step 2: Building Components Individually** We split the robot up completely. First, we built the turntable, the excavator arm, and the chassis as 3 separate SDF files. This made it easy to divide the work, give everyone a task, and iron out the first bugs before throwing everything together into one big pile. 
* **Step 3: Combining and Coding** From those 3 separate SDFs, we eventually created 1 single excavator SDF. Once the components were inside that single SDF, we immediately started writing the functionality. In the beginning, we basically hard-coded everything sequentially. No fancy structure, just purely focusing on the logic: how to integrate the Inverse Kinematics and get it fully working, and how to hook up the OpenCV Vision camera to the arm so it provides feedback to the main software. Only at the very end, once we got it somewhat working, did we focus on putting everything into models to get a clean structure, make things easy to adjust, and create a proper world.
* **Step 4: Transitioning to OOP** Once the code actually worked but had turned into a massive, unorganized wall of text in a single main file, we structured everything neatly. We completely refactored the functionality into Object-Oriented Programming (OOP). The code was stripped apart and distributed across separate, clear files (like specific classes for the controller and calculation functions) so the architecture makes sense.

---

## 2. The Great Gazebo Joint Drama
Looking back at where we lost the most time, it was definitely the joints in Gazebo. That was honestly the biggest problem of all.

The problem with the new Gazebo is that there is hardly anything to be found online. The Gazebo website lists 3 different ways to control joints. Because the documentation is so vague, you constantly run into issues where one plugin overrules the other, or the arm simply refuses to move because the syntax is slightly different in this Gazebo version. School also had something to say about it, because the easiest way to control joints wasn't enough to meet our learning objectives. So, we had to write our own custom PID controller for this as well.

We were stuck on this for quite a while and wasted countless hours brainstorming problems and dealing with trial-and-error. Ultimately, we got our breakthrough by sitting down with Bart and a few classmates. By bouncing ideas off each other and swapping tips on which plugins worked for them, we finally got the joints running properly. After that, the project thankfully went smoothly again.

---

## 3. Bugs and Solutions

### Model Path Resolution
* **Problem:** Gazebo crashed on startup because it couldn't find the meshes of our separate components (chassis, arm, turntable) via relative paths.
* **Solution:** Gazebo requires a hardcoded environment variable. We solved this in the `run.sh` script by exporting the directory right before startup:
    ```bash
    export GZ_SIM_RESOURCE_PATH=$(pwd)/models
    ```

### Instability After Combining
* **Problem:** Once the turntable, chassis, and arm were combined into the SDF and we connected the Inverse Kinematics controller, the arm started shaking at certain angles or couldn't move past a certain point.
* **Solution:** This turned out to be a combination of two things: the inertia in the SDF of the separate parts wasn't set realistically relative to each other, which was seemingly worsened because the controller initially sent steps that were too large all at once. By fine-tuning the masses in the SDF and adding a software dampening effect to the Inverse Kinematics output, this was fixed.

---

## 4. Current Status
The separate components now form 1 solid unit in desert.sdf. Thanks to the OOP refactoring, the code is incredibly clean and modular. The turntable rotates to the correct angle, the arm moves smoothly to the coordinates it receives via Inverse Kinematics, and the integration with the vision text file works perfectly. Fine-tuning took some time, but everything seems to be working flawlessly now. The project provides a great foundation for future GreenDiggers to build upon, especially now that everything has been moved into models and uses OOP code, which makes combining our project with the other 2 groups a lot easier.

---

## 5. Sources
* **Gazebo Sim Community Forums:** https://answers.gazebosim.org/
* **Official Gazebo Documentation:** https://gazebosim.org/docs/latest/getstarted/
* **SDFormat Specifications:** http://sdformat.org/spec
* **SDFormat Tutorials (Links & Joints):** http://sdformat.org/tutorials
* **Gazebo Sim GitHub Repository:** https://github.com/gazebosim/gz-sim
* **Mathematical Background of Inverse Kinematics:** https://en.wikipedia.org/wiki/Inverse_kinematics
* **Feedback and Brainstorming Sessions:** Input and documentation tips from our sessions with Bart, Hassan, and classmates.
* **School:** School provided 3 assignments including explanations.