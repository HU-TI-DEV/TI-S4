<img src = ./StylisticFeatures/teamlogo.png align="right" width="135">

# MoonDiggers GreenDigger Collaboration
At the start of February, the company GreenDigger visited the Hogeschool Utrecht and proposed an assignment. Every member of the Moondigger team was captivated by the possibilities and wanted to contribute to this project. After getting assigned this project some logistics had to pass until the development could get started. These logistics also concerned splitting the assignment along the three groups which were assigned the GreenDigger assignment. 

After all the Logistics had passed the assignment had slightly changed for each group. The assignment this folder will elaborate upon concerned implementing an autonomous mobile platform in a simulated gazebo environment without the use of LiDAR. As some may notice, there is no mention of an excavation tool. This task was transferred to the other development teams. 

But when is a platform autonomous? This definition is difficult to make but since the assignment states that the subject is a mobile platform, it is safe to assume the platform should be able to traverse a terrain fully without interference. From this the conclusion can be drawn that the platform should be able to drive different directions, it should drive to a certain setpoint without instructions and it should avoid obstacles while driving. 

## About us
<details>
<summary style="font-size:1.1rem"> <b>Jelle Warries - 1859477</b> </summary>
Jelle has been largely in charge of the depth camera and the object recognition which the code behind the depth camera performs. 
<br></details>
<details>
<summary style="font-size:1.1rem"> <b>Ruben Kroon - 1880525</b> </summary>
Ruben has provided great additions to the object recognition algorithm and has played a critical role in how the bounding boxes are drawn.
<br></details>
<details>
<summary style="font-size:1.1rem"> <b>Ryan Smit - 1880150</b> </summary>
Ryan has been our SCRUM master during this project. Next to keeping our planning in order he has also developed a large part of the traversing code. Ryan has also written all the math so the coordinates of the detected obstacle can be calculated.
</details>
<details>
<summary style="font-size:1.1rem"> <b>Samuel Epp - 1885625</b> </summary>
Samuel has made sure we always had a traversable surface and has written software so all following keypoints are determined. Samuel has also made sure small issues were patched.
</details>
<details>
<summary style="font-size:1.1rem"> <b>Yannick Hogetoorn - 1892413</b> </summary>
Yannick has been the technical lead of our group. He has also been very largely involved in the customer contact and meetings with the team coach and product owner. Yannick has also developed the pathfinding algorithm and has, as instructed under his function, made sure all software could communicate clearly.
</details><br>

## Contents
Now a project has been established and the collaborators of the project have been introduced, it is time to walk you through the project. 

#### Planning
<details>
<summary style="font-size:0.9rem"> <b>Requirements</b> </summary>
<p>Before starting to develop software a planning has been made. This planning takes the form of requirements, a object model and a class model. The requirements can be found <a href= "./Design/requirements.md">here </a>. These requirements have largely been derived from requirements GreenDigger supplied at the beginning of the project. The requirements they supplied had to be cleaned and formulated towards our project. After this process had been finished, a lot of requirements were still missing and a couple meetings with GreenDigger had proceeded. From these meetings additional requirements could be set. The reason behind needing to clean the requirements is the earlier use case of the requirements. GreenDigger had asked a company to perform a study on how their idea would perform. This study was about an entire fleet of different platforms. For our project this was not a necessity. Following this, the requirements were ranked in their priority using the MoSCoW method, as displayed in the markdown document.</p> 
<p>The largest problems faced during this process were simply ignoring and filtering out the unnecessary requirements. As stated above our project would only entail driving and planning around obstacles. In the documents supplied by GreenDigger a lot of design choices could already be found in the requirements which we could just throw out. In the requirements document there are still some requirements about an excavation tool. These requirements had been formulated since this is an original ask of GreenDigger. These requirements have been abandoned as the focus became the development of the autonomous mobile platform and not the GreenDigger fully.</p>
</details>

<details>
<summary style="font-size:0.9rem"> <b>Object Model</b> </summary>
<p>After the requirements had been confirmed by GreenDigger some software planning could finally happen. This software planning went through phases with the first phase being the Object model. This model portrayed the structure of what later the code would look like. It also portrays how the different objects communicate with each other. </p>
<p>The use of no entities in our model is fully thought out. The use of an entity would mean isolating the data from the object making changes to it. This makes the process unnecessarily complicated. Instead of using entities we used global std::vector variables in an object to communicate data. The reason behind A* having a lot of different function calls is the modularity of the algorithm. Since this algorithm can be used for a lot of different purposes the object was kept fairly standard.</p>
<img src="./Planning/objecModel.png">
<p>No real challenges were faced in the making of this diagram. It did later go through a second design iteration as the knowledge about Gazebo was limited while making the first iteration. The above picture is a result of the second iteration</p>
<br></details>

<details>
<summary style="font-size:0.9rem"> <b>Class Diagram</b> </summary>
<p>The second phase of the software planning is building a Class Diagram. This diagram shows all classes we have and the important public functions. It also shows how they can communicate with each other. The diagram might not be fully compatible with the way it was taught to us by the "design like a robot" reader we were provided, this is by design. The diagram is made to resemble the reality of our code base as closely as possible. It is also important to note that not all function have been noted on this diagram. A lot of local or debugging functions have been left out since these are for internal use and not important for a third party to see. If any class needs more explanation, it is encouraged to look at the README of the topic it belongs to.</p>
<img src="./Planning/klassenDiagram.png">
<p>The process controller shown in the middle of the diagram is designed to function as a main function or main controller. This is by design since this controller has links to all surrounding classes and made connecting everything up a lot easier.</p>
<br></details>

#### Other documents
After the planning has been done the project could be fully developed. This was done by splitting the project up into multiple topics and dividing the code accordingly. This also meant that all further choices, problems or code is intertwined with one of these topics. These topics are as follows: Traversing, Pathfinding, ObjectHerkenning, Demo and Overig. These topics can also be found in the corresponding folders inside this folder. Inside each folder there is a README. This README contains all choices, research, important code snippets or problems we have encountered or which should be explained. 

The files explain themselves for the most part. Underneath the header is how we handled a situation and how we would either do it differently or why we did it in the way that we did. There is also a header called Advice. This header tells the reader about the advice we give them and why we think it would be best to either add something or make a different choice. 

## The Topics
In the following Pathfinding directory a README can be found which will explain all important details about the code or how we decided to use or implement certain choices. It will also discuss which algorithm we used and why. 
- [Pathfinding Directory](./Pathfinding/README.md)

In the following directory the choices, problems and advice about Object Recognition will be discussed. This process contains everything from receiving a raw image from the depth camera up to and including calculating the position of an artificially created bounding box on said image. 
- [Objectherkenning Directory](./ObjectRecognition/README.md)

While developing the Autonomous Mobile Platform, the simulation environment Gazebo was used. This program supplied us with sensors and a testing environment. This meant working with a .sdf file format and a lot of other tools to get the most out of our new environment. This process contained a lot of hardship but also a lot of learnt lessons. More about this in the following repository.
- [Overig Directory](./Other/README.md)

If a demo is more for your speed, all the instructions to run our latest demo can be found in this directory:
- [Demo Directory](./Demo/README.md)