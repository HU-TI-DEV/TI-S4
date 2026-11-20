# Edge AI

Edge AI is the idea to have your AI model "running" on your local microcontroller, the "edge" device [(Edge Impulse, n.d.-a)](https://docs.edgeimpulse.com/knowledge/courses/edge-ai-fundamentals/what-is-edge-ai). It is a form of computing where data is analyzed and processed near where the data is generated or collected. Normal AI (cloud-based AI), involves data being transmitted across the internet to be processed on a remote server.   
The potential benefits of edge AI  would entail:
* Stand alone operation, no internet connection needed.
* Reduced latency, the data is processed on the device.
* Lower energy cost
* Increased privacy/security

The market for Edge AI is projected to grow exponentially [(Grand View Research, 2026)](https://www.grandviewresearch.com/industry-analysis/edge-ai-market-report): 
![alt text](images\image.png)

If this projection will become reality is still uncertain. 

In this manual we will make our first steps on AI territory. We will first implement an AI model on a smart phone. This is just a quick "getting your feet wet". Next steps would involve implementing an AI model on a microcontroller. 

# Edge Impulse
Edge impulse is a webbased framework for implementing AI models on edge devices [(Edge Impulse, n.d.-b)](https://www.edgeimpulse.com/). We will use this framework as it removes a large part of the bottlenecks in the process.   
  
In general using Edge AI involves the following steps:
1) Collecting the training & validation data on your edge device
2) Use that training data to train the AI model. This step takes place on a pc or in the cloud, so NOT on your edge device. 
3) Compressing the AI model and implement/upload the compressed model on the edge device.
4) Testing the compressed model on your edge device. 

PLAATJE VAN PROCESS

## Manual
1) Open the https://www.edgeimpulse.com/ website. 

2) Set up an free acount:   
![alt text](<images\Screenshot 2026-11-20 093549.png>)  

3) Create a new project "PHONE1:  
![alt text](<images\Screenshot 2026-11-20 094109.png>)

4) In the devices tab create a new device:    
![alt text](<images\Screenshot 2026-11-20 094306.png>)

5) Use the QR code to connect your phone:
![alt text](<images\Screenshot 2026-11-20 094330.png>)

6) In the dashboard select "collect new data":  
![alt text](<images\Screenshot 2026-11-20 094448.png>)

7) Fill in the name of the label/activity you want to do and leave the rest of the settings for "collect data" as is. Press "start sampling":  
![alt text](<images\Screenshot 2026-11-20 095308.png>)


8) It could be that you have to give permission in the website on your phone to sample the accelerometer (scroll down a bit and press the blue bar):  
 ![alt text](images\IMG_5702.PNG)

9) The phone should now sample a 10 second clip of your acceleration data. During this time you should "wave" your telehone:   
![alt text](images\IMG_5705.PNG)

10) The website should have sampled your data:   
![alt text](images\IMG_5705-1.PNG)

11) Repeat this for jumping with your phone (give the label a different name), If you scroll down a bit you can see the data:
![alt text](<images\Screenshot 2026-11-20 095503.png>)

12) We now have our training data (a very small set, but a usable one nonetheless).

13) Select the "Create Impulse" tab:
![alt text](<images\Screenshot 2026-11-20 095705.png>)  
![alt text](<images\Screenshot 2026-11-20 095726.png>)

14) Add a processing block (Spectral Analysis):   
![alt text](<images\Screenshot 2026-11-20 095805.png>)

15) Add a learning block (Classification):
![alt text](image-1.png)

16) Save the model:   
![alt text](<images\Screenshot 2026-11-20 124034.png>)

17) Select the Spectral features tab and save the settings as is:  
![alt text](<images\Screenshot 2026-11-20 124519.png>)

18) Generate the features:  ![alt text](<images\Screenshot 2026-11-20 100018.png>) 

19) Select the classifier tab and save & train your model:
![alt text](<images\Screenshot 2026-11-20 100117.png>)  

20) Select the deployment tab and deploy your model on your phone: 
![alt text](<images\Screenshot 2026-11-20 100521.png>)

21) Your phone will sample 10 seconds chunks and determin if you are waving or jumping your phone: 
![alt text](images\IMG_5705-2.PNG)

How cool is that!

### References
Edge Impulse. (n.d.-a). *What is edge AI?* In *Edge AI fundamentals*. Edge Impulse Documentation. Retrieved November 20, 2026, from <https://docs.edgeimpulse.com/knowledge/courses/edge-ai-fundamentals/what-is-edge-ai>

Grand View Research. (2026). *Edge AI market size, share & forecast report, 2026-2033* (Report No. GVR-4-68040-050-4). https://www.grandviewresearch.com/industry-analysis/edge-ai-market-report

Edge Impulse. (n.d.-b). *Edge Impulse: MLOps for edge AI and physical AI*. Retrieved November 20, 2026, from https://www.edgeimpulse.com/
