## Weekly Production Document

This document is intended to record weekly targets and act as a reference alongside the scrum board. Each team member has a dedicated space to outline their goals, which can then be tracked and updated individually on the scrum board according to what makes sense for their workflow.

---
### First meeting of the week</br>
Date : 20/04/2026 </br>
Present :
1. [x] Alea
2. [x] Robin
3. [x] Kjell
4. [x] Luuk

<span style="color:orange">**In broad terms, what do we want to get done this week?**</span></br>

> Continue working on Lidar filtering (ground)
> Overhaul locomotion for cleaner PID and location sensor results
> Continue working on digging
> Continue work on the interface layer

<span style="color:orange">**In specifics, what is realistic to get done this week?**</span></br>

> Research and try to work with ransack for lidar filtering
> Make 4-wheel skid steering stable for better locomotion
> Make a initial version of digging
> Improve c > python parsing for interface layer

<span style="color:orange">**Task Distribution**</span></br>
1. [x] Alea </br>
   > Improve c > python parsing for interface layer
2. [x] Robin </br>
   > Make a initial version of digging
3. [x] Kjell </br>
   > Research and try to work with ransack for lidar filtering
4. [x] Luuk </br>
   > Make 4-wheel skid steering stable for better locomotion

---
### Tuesday Update
<span style="color:orange">**Contribution**</span></br>
1. [x] Alea </br>
   > Worked on interface
2. [x] Robin </br>
   > Worked on digging
3. [x] Kjell </br>
   > Worked on Ransack average
4. [x] Luuk </br>
   > No progress

---
### Wednesday Update
<span style="color:orange">**Contribution**</span></br>
1. [x] Alea </br>
   > Python sockets added to interface
2. [x] Robin </br>
   > Added contact sensor to digging
3. [x] Kjell </br>
   > No progress
4. [x] Luuk </br>
   > Research diff drive plugin

---
### Thursday Update
<span style="color:orange">**Contribution**</span></br>
1. [x] Alea </br>
   > Made a demo for the interface and added arm states
2. [x] Robin </br>
   > Added a heightmap and created digging demo
3. [x] Kjell </br>
   > No progress
4. [x] Luuk </br>
   > No progress

---
### Final Update
<span style="color:orange">**Completion Check**</span></br>
1. [x] Alea
2. [x] Robin
3. [ ] Kjell
4. [ ] Luuk

> Write here the take away for next week.

- We now have a basic interface layer where we can send commands to the SDF. We will now only use this interface to talk to the SDF.
- We have a proof of concept for digging where we are able to dynamically update the terrain.
- We have added heighmaps.

> What we still need to do.

- Fix locomotion for a way to use the PID implementation
- Make sure we have LIDAR filtering for the ground at least

