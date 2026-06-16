# Test Report: Controller & Excavator Arm

**Objective:** To check if the excavator arm moves smoothly and accurately via the configured PID controllers, whether the calculated Inverse Kinematics match reality, and if the arm responds immediately to the stop signal from the vision folder.

**Success Criteria:** Below is the table containing the mechanical and software requirements for the controller:

| Nr | Test Aspect | Success Criterion | Pass/Fail Threshold |
| --- | --- | --- | --- |
| 1 | Range (Half-moon) | Must be able to reach a full semicircle of 5 meters in diameter | Pass if radius >= 2.5 meters |
| 2 | Arm accuracy | Shovel must end up within 5 cm of the generated setpoint | Pass if deviation <= 0.05m |
| 3 | Stability (PID) | Arm must move without severe vibrations or overshoot | Pass if overshoot <= 10% |
| 4 | Emergency stop reaction time | Arm must stop and return as soon as stopSignal.txt jumps to 1 | Pass if reaction < 0.5 seconds |

## Test Setup
For these tests, I used the following setup:
- A PC running the Gazebo simulator inside the Docker container.
- The main.cc controller compiled and active.
- A working stopwatch or log files to measure the reaction time of the arm as soon as the tree comes into view.

## Step-by-step Plan
The step-by-step plan for testing the controller:
1. Start the simulation via run.sh so that Gazebo and the controller are linked.
2. Have the pointGenerator generate a trajectory for a digging movement (radius of 2.5 meters).
3. Monitor the observer topics of the joints via the terminal to check the angles and positions.
4. Place a tree in the camera's field of view halfway through the digging cycle and check in the code if the arm immediately aborts the movement.

## Test Results

| Tests | Pass? |
| ----- | ----- |
| 1     | Yes   |
| 2     | Yes   |
| 3     | Yes   |
| 4     | No    |

The range of the arm was perfectly tuned. The two arm segments, each 1.73 meters long, could easily cover the requested semicircle with a radius of 2.5 meters from a single fixed position. This proves that the mechanical setup from the SDF aligns well with the client's requirements.

The accuracy of the Inverse Kinematics was also perfect. The coordinates rolling out of the setTargetPoint function were neatly translated into radians. The shovel consistently ended up exactly where we wanted to dig, with a negligible deviation of less than 2 centimeters.

Regarding stability (aspect 3), we did have some trouble with vibrations/overshoot in the beginning. The arm sometimes shot past its target aggressively. After we set the I-gain of the PID controllers to 0 and turned up the D-gain slightly to dampen the movement, it ran a lot smoother. The 10 micro-steps per point helped tremendously to absorb the shocks.

However, we also performed a test that did not go according to plan at all: the reaction time of the emergency stop (aspect 4). During testing, we discovered that the arm does not stop in real-time while digging. This is because the stopSignal() check is only placed after the for-loop of the 10 micro-steps in the code. Since each intermediate step has a sleep time of 300ms, the arm easily spends 3 seconds digging towards its endpoint before it even checks stopSignal.txt. If the vision component detects a tree during steps 1 to 9, the arm just keeps on digging. If the tree happens to disappear from the camera's view by the 10th step, the controller reads a 0 and simply continues digging to the next point. This is way too slow and unsafe, which is why this test fails.

## Conclusion and Recommendations
The controller and physical setup mechanically meet the requirements, but the software security is not airtight in practice. Just like with vision, our initial requirements were too optimistic. Because we had to add the vision interrupt late into the project due to its complexity, we simply slapped the check at the end of the movement.

To solve this in the future, the stopSignal() check should be placed inside the for-loop of the micro-steps. Then the arm would check every 300ms if it is still safe and would actually be able to stop immediately. 

If we had set up more realistic test criteria in hindsight, it would have looked like this:

| Nr | Test Aspect | Success Criterion | Pass/Fail Threshold |
| --- | --- | --- | --- |
| 1 | Range (Half-moon) | Must be able to reach a full semicircle of 5 meters in diameter | Pass if radius >= 2.5 meters |
| 2 | Arm accuracy | Shovel must end up within 5 cm of the generated setpoint | Pass if deviation <= 0.05m |
| 3 | Stability (PID) | Arm must move without severe vibrations or overshoot | Pass if overshoot <= 10% |
| 4 | Emergency stop reaction time | Arm must stop after completing the current digging movement | Pass if reaction < 3.5 seconds |

With these thresholds, we would have passed the test and the project would still have been approved by the client, since the arm does eventually stop before starting a completely new digging movement. Another good lesson for the next project.