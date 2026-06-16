# Vision Test Raport

**Objective:** To determine how long it takes for a new image to reload. The camera takes photos, which are then processed by Vision. This must occur at a certain speed to prevent problems.

**Success Criteria:** Below is a table with my requirements. First is the aspect, followed by whether it is met or not:


| Nr  | Test Aspect             | Succes Criterion                 | Pass/Fail Threshold |
| --- | ----------------------- | -------------------------------- | ------------------- |
| 1   | Camera smoothness       | Minimum of 0.4 FPS               | Pass if >= 0.4 FPS  |
| 2   | Vision frames           | Minimum of 0.2 FPS               | Pass if >= 0.2 FPS  |
| 3   | Accuracy Tree detection | 90% accuracy when detecting tree | Pass if >= 90%      |
| 4   | User Experience         | 90% of users report satisfaction | Pass if >= 90%      |

## Test Setup
For these tests, I used the following setup:
- A PC with the correct image in a Docker container.
- A working mouse to control your PC. This allows you to navigate to the correct folders if you need to test or adjust something.
- Preferably in a somewhat cool room, because your PC is going to heat up.

## Step-by-Step Guide 
The step-by-step guide I used to run the setup is very simple:
1. Start up your PC.
2. Log in and open the BAT file (everything should then start up).
3. After that, you can look in “MobaXterm,” where you’ll see windows open that let you follow the camera and view the updating image. The terminal will display the arm’s position as well as whether the boom has been detected. 

## Measurement results

## Meetresultaten

| Tests | Pass? |
| ----- | ----- |
| 1     | Yes   |
| 2     | Yes   |
| 3     | No    |
| 4     | Yes   |
Camera smoothness wasn’t an issue. It worked right away as it should—and actually much better than expected. It ran at a minimum of 50 FPS, which was significantly higher than what we initially required from the system. We were happy about that because it also meant that if we needed to make adjustments, it would be easy to do so. There’s virtually no lag, so we can always take photos faster if we want to.
Vision also worked as intended. We specifically ajusted it to process photos every 5 seconds. We tried increasing this interval, and it worked, but that wasn’t necessary for our project. 
We also ran a test that went exactly according to plan. We had set this goal a while ago, but since then we’ve discovered that OpenCV doesn’t work quite as perfectly as we’d hoped. The 90% accuracy does apply when the tree is fully in frame and does not visually overlap with other objects. As soon as something else overlaps the tree, the tree is no longer detected at all. That’s a real shame, but after adjusting filters and such, we’ve concluded that we can’t fix this within the timeframe and with the tools we currently have.
We’re wrapping things up on a positive note, though, because the user experience went well. The client was very happy with the final product, and other students we showed it to were also very positive about it.

## Conclusion and Recommendations
We now know that most things went well and actually worked much better than we had initially required. The problem, however, was that Vision could not be fully implemented the way we wanted. The plan was initially not to do this at all, but following discussions about the difficulty, it became clear that it had to be done after all. So we had to get this up and running in a short amount of time, and we ultimately succeeded, though not entirely according to all our requirements. Maybe we also overestimated aspect 3 a bit, but hey, that’s all hindsight. It doesn’t help us now. 

I did create an example of what could have been better tests in hindsight:

| Nr  | Test Aspect             | Succes Criterion                 | Pass/Fail Threshold |
| --- | ----------------------- | -------------------------------- | ------------------- |
| 1   | Camera smoothness       | Minimum of 40 FPS                | Pass if >= 0.4 FPS  |
| 2   | Vision frames           | Minimum of 0.2 FPS               | Pass if >= 0.2 FPS  |
| 3   | Accuracy Tree detection | 50% accuracy when detecting tree | Pass if >= 90%      |
| 4   | User Experience         | 90% of users report satisfaction | Pass if >= 90%      |

We had actually met all the requirements, and it still fell within the client’s specifications. But I suppose that’s how you learn.