An Analysis of Berkeley’s Algorithm and the Precision Time Protocol (PTP) on Simulated Distributed Systems Using SimGrid

Jonny Olswang  
Joshua Reyes  
 Professor: Hailu Xu  
 CECS 327-02  
California State University \- Long Beach  
 [Jonny.Olswang01@student.csulb.edu](mailto:Jonny.Olswang01@student.csulb.edu)  
Josh.Reyes@student.csulb.edu  
May 11, 2024

    ***Abstract*****—This paper will analyze the effectiveness of two distributed system clock synchronization algorithms based on factors such as network-wide clock accuracy, hardware requirements, network topology, and clock utilization. The selected algorithms were Berkeley’s Algorithm and the Precision Time Protocol. SimGrid is a framework for simulating the development of distributed application executions on distributed platforms, which we used with Python for experimentation. Data will be provided to offer a pragmatic view of the different algorithms’ uses.**

***Keywords—Simulated Distributed Systems, Clock Synchronization, SimGrid, Berkeley’s Algorithm, Precision Time Protocol (PTP)***

1. # INTRODUCTION

Clock accuracy is a vital feature of a functional distributed system. Given the tendency for individual clocks to drift over time, network clock synchronization is a necessity for operations like data consistency, task scheduling, resource management, and event logging.   
Many algorithms exist for synchronizing clocks across a distributed system that differ depending on the required accuracy and how the system defines synchronization. For example, should network clocks be accurate to the order of milliseconds? Microseconds? Nanoseconds? Is the absolute time of the clocks important, or does the order of distributed events take precedence? How should outlier clocks be handled during the synchronization process?   
For our testing, we chose to implement Berkeley’s Algorithm and the Precision Time Protocol in Python, and ran them through the SimGrid simulation framework.

2. BACKGROUND

1. *SimGrid*

SimGrid provides comprehensive documentation in regards to its components and functionality. The framework advertises the ability to compare distributed designs for developers, debug real applications via SimGrid’s reproducibility, and analyze distributed algorithms for research purposes \[1\]. This paper will be focused on utilizing the third of these three options.  
Projects run with SimGrid have four major components \[1\]:

* ***Applications*** \- one or more processes that implement distributed algorithms, and use SimGrid’s API.   
* ***Simulated Platform*** \- a file description of the distributed system’s hardware.  
* ***Deployment Description*** \- a file description of how the execution of the application is deployed on the platform.  
* ***Platform Models*** \- documented SimGrid models that can be configured to fit use cases.

Additionally, SimGrid provides an example project repository to pull from, with examples of these components available for reference or as a starting point for one’s own project. We elected to code on Ubuntu distributions, which made downloading Python’s SimGrid dependencies relatively simple.

2. *Berkeley’s Algorithm*

The clock identified as most reliable is given the role of master clock. The rest of the clocks are classified as slave clocks and aligned with the boundary clocks that are synchronized to the previously selected master clock. This is for network time synchronization for better coordinated operations.

| ![][image1]  |
| :---- |

Fig. 1\. Architecture of a PTP network. [https://www.hyve.com/wp-content/uploads/sites/5/2023/04/hyve-PTP-infographic.png?w=1920\&q=75](https://www.hyve.com/wp-content/uploads/sites/5/2023/04/hyve-PTP-infographic.png?w=1920&q=75)

C.   *Precision Time Protocol (PTP)*  
	PTP necessitates the network must be organized in a hierarchical structure. One clock, known as the grandmaster, acts as the undisputed source of correct time on the network. This status is maintained by its connection to a highly accurate Global Positioning System (GPS) or atomic clock. The grandmaster is connected to a set of boundary (aka master) clocks, which in turn are connected to a set of client (aka slave) clocks \[2\]. The boundary clocks have master-slave relationships with the client clocks, and the grandmaster has master-slave relationships to boundary clocks. To prevent a single point of failure, multiple grandmaster clocks can be prepared to step in should the operating time source fail. PTP has shown to consistently provide sub-microsecond accuracy \[2\], and is the standard for industries that deal with time-sensitive or life-threatening situations. However, it requires specialized hardware support to operate optimally, such as atomic/GPS clocks or hardware timestamping.

3. METHODOLOGY

1. *SimGrid*

SimGrid proved to be an excellent tool for experimentation. It was able to produce large amounts of results without the deployment of large distributed systems or networks, and the real world run-time was a fraction of the simulated time. This allowed for the easy repetition of experiments with large data sets.  
The framework did have one unfortunate drawback: individual simulated processes did not have their own clocks. Instead, all processes operated off of a shared clock that ran for the duration of the simulation \[1\].

2. *Berkeley’s Algorithm*

The methodology behind Berkeley's algorithm was to try and create an efficient clock synchronization model using a time synchronization algorithm. How this works is by a couple steps, Each computer in the system will check its local time which will  be used later. The master which is selected at the beginning as the most efficient will collect all the times from the rest of the workers.With that info provided it will then calculate the offset of each one with their given local times. Offset is calculated as:

Offset \= tremote \- tlocal 

    Cristian’s algorithm is also used to handle round trip time from the communication between the clocks while sending their time communication:  
                Offset \= ((tserv \- tclient) \+ (tclient-tclient))/2 

 It will then use the offset that was calculated to adjust their respective clocks therefore synchronizing them back up with master.. This process is repeated throughout the runtime, ensuring they stay synchronized through it all. It’s important to note no special hardware is required for either clock during the time retrieval and offset calculations which one advantage it holds over other models, which we will go over later. It is recommended and needed for more precise synchronization if wanted, but again not required.  
As mentioned above, SimGrid will run all its processes off of one simulated clock. In order to imitate clock desynchronization across the network, clients were preset with an offset variable, which when added to act as that individual process’s clock. We also made sure to repeat our simulation 50 times to check that it produced the same results.

| ![][image2] |
| :---- |

Fig. 2\. PTP synchronization process. [https://moniem-tech.com/wp-content/uploads/sites/3/2023/02/Master%E2%80%93Slave-Hierarchy-in-PTP.png](https://moniem-tech.com/wp-content/uploads/sites/3/2023/02/Master%E2%80%93Slave-Hierarchy-in-PTP.png)

3. *Precision Time Protocol (PTP)*

Clocks in the master role of a relationship are responsible for initiating the syncing process. As shown in Fig. 2, four messages are exchanged between a master and slave. Once the slave has collected the four necessary timestamps, the offset can be calculated as:

 Offset \= ((t2-t1) \- (t4-t3))2   
In colloquial terms, the offset is the difference between the master and slave clock, minus the one-way delay of sending a message \[3\]. Intuitively the logic stands, as the easiest way to sync a network is to have a reliable time source send out its own time for all listening components to copy as their own. PTP’s additional calculations are necessary because it is impossible to predict the state or latency of network connections.  
As mentioned above, SimGrid runs all its processes off of one simulated clock. In order to imitate clock desynchronization across the network, client processes kept track of an offset float-type variable, which when added to the global simulation clock would act as that individual process’s clock. The decided range for the offset would be within 5 seconds. As we lack the academic funding to purchase our own atomic clocks or implement hardware timestamping, there will be some uncertainty with our results compared to running PTP in the real world. This can be somewhat accounted for by adjusting the SimGrid platform file, but only to a limited extent.  
In order to offer meaningful insight, the PTP simulation was run with 5, 50, then 100 clients, each for 50 rounds. It is worth noting repeating the experiments always produced the same results, thanks to SimGrid’s advertised reproducibility. If different results are desired with the same number of rounds and clients, the platform file describing how processes are connected to each other in the distributed system must be altered.   

4. DISCUSSION

1. *Berkeley’s Algorithm*

There are multiple factors that go into choosing a clock synchronization method but there are clear goals that come with Berkeley's Algorithm. As mentioned earlier this method does not require specialized hardware which is a huge plus for implementing it into your systems. Other big mentions would be the fact that it is a decentralized method, making it a great option for a wide range of distributed systems/ network environments. It also has a plus of not having reduced network load. This overall creates an algorithm made for most systems no worry about load capabilities or special hardware requirements. With the decentralized model there is no worry about the size of your system. It is important to note its faults which every system has. In Berkeley’s case it has three big drawbacks. The biggest drawback being that the accuracy is heavily dependent on network conditions as it requires the workers to get local time and send it to the master node. Another big one is the vulnerability to malicious nodes. Since there is no centralized authority to check the validity of the times sent back any malicious node can give back incorrect times to screw up the clock synchronization. This is a huge problem as there is no way for Berkeley’s algorithm to check if it is receiving correct info from its nodes it will simply go through with calculating based on the time it is given. Lastly it has limited precision which is partly due to what we mentioned earlier in which specialized hardware is required for higher accuracy. This is because most machines have a limit to how granular it can measure time(milliseconds or microseconds). Other things that can decrease precision is the clock drift and network latency.

2. *Precision Time Protocol (PTP)*

PTP simulations did show sub-microsecond accuracy when performing the network-wide clock synchronization. Three experiments were run:

* 5 clients, 50 rounds (250 syncs)  
* 50 clients, 50 rounds (2500 syncs)  
* 100 clients, 50 rounds (5000 syncs)

The clients are pulled from the same pool of worker nodes, so the first five clients are the same for all three experiments, the first 50 clients are the same for experiment 2 and 3, etc.

TABLE I.		FIRST 10 ROUNDS OF 5 CLIENT SIM

| Round \# | Mean (sec) | Standard Deviation (sec) |
| :---: | :---: | :---: |
| 1 | \-6.4286047e-8 | 1.1357125e-8 |
| 2 | \-6.4286047e-8 | 1.1357126e-8 |
| 3 | \-6.4286047e-8 | 1.1357125e-8 |
| 4 | \-6.4286049e-8 | 1.1357129e-8 |
| 5 | \-6.4286047e-8 | 1.1357122e-8 |
| 6 | \-6.4286048e-8 | 1.1357124e-8 |
| 7 | \-6.4286047e-8 | 1.1357127e-8 |
| 8 | \-6.4286049e-8 | 1.1357120e-8 |
| 9 | \-6.4286049e-8 | 1.1357120e-8 |
| 10 | \-6.4286049e-8 | 1.1357120e-8 |

TABLE II.		5 CLIENT SIM DATA

| Expected Value of Mean | \-6.4286045e-8 |
| :---- | ----: |
| Expected Value of Standard Deviation | 1.1357121e-8  |
| Min. Offset | \-5.2472785e-8 |
| Max. Offset | \-7.5070261e-8 |

The 5 client simulation ran for 565.9 simulated seconds.

TABLE III.	FIRST 10 ROUNDS OF 50 CLIENT SIM

| Round \# | Mean (sec) | Standard Deviation (sec) |
| :---: | :---: | :---: |
| 1 | \-6.3990800e-8 | 4.6949277e-8 |
| 2 | \-6.3990798e-8 | 4.6949278e-8 |
| 3 | \-6.3990797e-8 | 4.6949281e-8 |
| 4 | \-6.3990800e-8 | 4.6949275e-8 |
| 5 | \-6.3990800e-8 | 4.6949275e-8 |
| 6 | \-6.3990803e-8 | 4.6949269e-8 |
| 7 | \-6.3990805e-8 | 4.6949274e-8 |
| 8 | \-6.3990801e-8 | 4.6949278e-8 |
| 9 | \-6.3990805e-8 | 4.6949274e-8 |
| 10 | \-6.3990805e-8 | 4.6949274e-8 |

TABLE IV.	50 CLIENT SIM DATA

| Expected Value of Mean | \-6.3990804e-8 |
| :---- | ----: |
| Expected Value of Standard Deviation | 4.6949287e-8  |
| Min. Offset | \-1.5786099e-8 |
| Max. Offset | \-2.0950847e-7 |

The 50 client simulation ran for 4419.9 simulated seconds.

TABLE V.		FIRST 10 ROUNDS OF 100 CLIENT SIM

| Round \# | Mean (sec) | Standard Deviation (sec) |
| :---: | :---: | :---: |
| 1 | \-7.0787094e-8 | 5.2001844e-8 |
| 2 | \-7.0787094e-8 | 5.2001843e-8 |
| 3 | \-7.0787094e-8 | 5.2001847e-8 |
| 4 | \-7.0787099e-8 | 5.2001847e-8 |
| 5 | \-7.0787099e-8 | 5.2001847e-8 |
| 6 | \-7.0787098e-8 | 5.2001847e-8 |
| 7 | \-7.0787090e-8 | 5.2001842e-8 |
| 8 | \-7.0787090e-8 | 5.2001842e-8 |
| 9 | \-7.0787090e-8 | 5.2001842e-8 |
| 10 | \-7.0787090e-8 | 5.2001842e-8 |

TABLE VI.	100 CLIENT SIM DATA

| Expected Value of Mean | \-7.0787120e-8 |
| :---- | ----: |
| Expected Value of Standard Deviation | 5.2001870e-8  |
| Min. Offset | \-1.5786099e-8 |
| Max. Offset | \-2.0950847e-7 |

The 100 client simulation ran for 8560.8 simulated seconds.

As depicted above, the 5 client experiment produced the lowest standard deviation by far, but as the sample size was so small, some extreme values can be expected. The 50 client experiment produced the smallest mean offsets, making it the most accurate of the three. Interestingly, the 100 client experiment showed a decrease in mean offset accuracy, even lower than that of the 5 client experiment. The expected standard deviation is the largest as well. More research can be done to determine where the optimal amount of client clocks for 50 round clock synchronization lies.  
Given the nature of SimGrid to produce the same results from the same inputs, it is not worthwhile to compare the minimum and maximum offsets. They exist to form a baseline range for the post-synchronization offsets.

5. CONCLUSION

Berkeley’s Algorithm and PTP barely occupy the same pseudo-ecological niche in the dangerous environment that is a distributed system. They serve different purposes, and both have their benefits and drawbacks.     
When it comes to Berkeley’s Algorithm, it easily settles itself as a go-to system for usability and scalability. Its simplicity and lack of required extra hardware makes it perfect for systems who don’t have the privilege for special tools, yet still works for when/if you ever decide to grow your system. Disregarding its lower accuracy, Berkeley’s works perfectly for self-contained systems that are more concerned with the order of distributed events than with absolute time accuracy. It is only when it comes to security and pushing lower latency is it that you should consider other options from Berkeley’s.  
The Precision Time Protocol is many degrees more accurate than Berkeley’s Algorithm, and ensures the network is synchronized to a legitimate time source. Conversely, it requires hardware support that may not be viable for every distributed system, and the synchronization process can produce non-negligible amounts of network traffic. However, PTP remains the industry standard for clock synchronization. Its accuracy can be life-saving when implemented in real-time systems.

##### 

##### 

##### 

##### 

##### **References**

\[1\] The SimGrid Team. “The Modern Age of Computer Systems Simulation.” SimGrid. [https://simgrid.org/doc/latest/index.html](https://simgrid.org/doc/latest/index.html) (Accessed May 11, 2024). 

\[2\]   “PTP \- Precision Time Protocol.” Perle Systems. [https://www.perle.com/supportfiles/precision-time-protocol.shtml](https://www.perle.com/supportfiles/precision-time-protocol.shtml) (Accessed May 11, 2024).

\[3\]	“How works the Precision Time Protocol (PTP)?” Bodet Time. [https://www.bodet-time.com/resources/blog/1774-how-works-the-precision-time-protocol-ptp.html](https://www.bodet-time.com/resources/blog/1774-how-works-the-precision-time-protocol-ptp.html) (Accessed May 11, 2024). 

 

 

[image1]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAREAAAChCAYAAADgKYtPAAAYA0lEQVR4Xu2d3W8cVZrG+QtQ/oGRSGIc7MwFt+zNeu+Q9oarYXaFZqxRtKxYNAs7AoldNJgkTpzMzjg4X+QLk83XkATyAcF2Z0MzzMQwwGCWzAgGZceIhQU2hkZBiiKi0NtPud/y20+fLnfb3e2u8vOTXnXXOaeq2t1VP59z6tSpW24RQixbZmZmiohCoXAn5wkhRE1MHhxcTgghKmBp1ApeTwixzPnyyy9HWRQ7dh8ujo1NFCcmctF7zpdMhBBBefzu4uvFQ0eej+Th49ivTxXP5yerRCKZCLEMKRQKt7EI3njjrSp5XL36TRQ+7dz4q1USkUiEWCaE5IFAc8WL4rXXflu8du1aVRqvhwDI530JITIGn/wheVy48EosBR+8npcH4vSZc5KIEFmlVPvoYwEgWBSNyAO1EuSbhNBfwvsVQmSEsbHzfV988XnUPGEhTH/0cZU4GpHHe5f+KIkIkXUgEV/bSJIJpyNQ/srMV7E8Xjo3Fm/LtotLwbxfIURG8BLxMmFZcFy//m0sj737j0X9Hrwdk4r6RITIMCGJzCcTq2VAHgeePR69P3FxS4U8UPvYtedItKzmjBAZxiRizZBQgJs3v4vlgZoFBMLlIA/kWZ/I5ct/kUSEyDomEZz4vk/DhxcDX/ZFoDZiZWwovAkHy+oTESLDsEQsakkEtQoTBOSBGgmaLSYPCyxbzeTEybOSiBBZhSWyL/9Acc/ZgQqZsERQWzF52FB4a7rYtnyTR80ZITKM71j94IMPIwHs3DtaUyJ4Rc3i2f84UVHzsDwIxsp+VShIIkJkndDVGZNJLYlwedRIvDwQ1uSxPhberxAiI4QkYmE32XFzxgRhl3gtD/fW2LqQB+SCWov6RITIML5PhCViwRLBsskDy0jncSK+yaPmjBAZhjtWQzLh5gw6U00ePrjJYzUZSUSIDOMlsuvotqorMyGJhORhl3QtzZo8z7/wYvTK+xVCZASTCC7RmjwOvHNvhUi4OWOCQBqWLW8s91KFeNDkQa3lueOnJREhsgp3rHqZ1JIIAnJAGvJsPduGycWaPGrOCJFhWCIWGOMRkkhUUynVMKyZ4gN5vllz48YNSUSIrFNLIj5YIpwfyrMmj9VGeL9CiIzAV2dYECwR7hPBpVzLm5x8PV7HmjyotagmIkSGYYkgbB6QWhKBHEweNiKVx4lAHihj6/B+hRAZwUsEcvjk089imVhTxEsEgsFI1dCUASYVk5Bv0vB+hRAZwfeJYLpDiAATLJtIWCL2miQPhHWq2qhV3q8QIiOEOlZNJiGJcJ+Iz5uaejfeho0PQa1FNREhMkxIIhanzpwPSsQmZkaaTUZkfSI2t6qfvFkSESLDmES4M9WHl0jSTGZIt5GqSFOfiBDLAL46E5IJd6z6W/5tXZTxkzfbhESWxvsVQmQEL5HnTr4cywT9GSGJcJ9IrRvvbPJmS+f9CiEygknELu3+ZvIPkQhMJiGJJM1kxjUS3p8QImNwx6ofJxKSiN145+WB5o1N3ix5CLEM8RKxsKYNSwSieOuttyvKeqnk8/kVvH0hxDJgYmJigEXy2mu/rZII94lIHkJkiOHh4RUD6wcX1ZQoyWSYZcIS8fKAfHgbQogUsX5wsB/i8MFlFkKSRCQPITICy6NZAvGwRBBcRgiRYqwJ0yqJCCEyjAlkTiSb8lxGCCFq4mseA08ODrgsIYQQQgghhOgk7HIupwshxLwMDg7e2U6BdHXdcRenCSFSTDsFsqq7J8dpQghRN6u6e59cdXvPMN53dfWuxevq7p5PZ5dnayirV3//e4io/O09B2xdKyeEEJEcVq3pPcnpALIICSOUJoRYAkrNl9F2NmE8EEGpNvK+LeN9khxmy882gZLKJfLznw8Ut2/f3cfpQoiFsVQCWTIOvHNvsb+/v7hx48bizp177+R80bns2LHjoe0jI8X5AuV4XdF8lu1lXJOIvXK+6DyqJLHrYMW0eHGU0rksb0uIRXP00v0VEinFAF51wHUe27fvOhWLY+f+OVmU3rMsEsts3z7F2xZiwew7NFwlEfdeMukQRkZG+mM51KhlJIXVVuLlkZFR3odonHYPJOtIzv/31uLQ0JbiPz/+o0gaTz31VCwRNXE6By8QFkQj4eXD+xCNMbBhcGrZCwRAItu2bSs+O3VfLBFu4vA6ov2wDBYavlnD+xD1I4E4jo79MpIIZGISsfchiWAZ5VHOp4vWwjJoRvA+RP2gGcNpyxaIAlKATGBWkwjSakkE6evu/3FUxueJ1sECaEbwPoRYEBDCY489FtVEMFakJIlYIgf/6ydVEtm0aVMkEfShmGR2jIxM+zKi+WCSXZbAYkKT9jbO7DSGasJUYSLwEoFAfBPHl7caipfIE7tn+1NwcPqyonnYbN0sg0Zj545dmvl7AUggCeDktyaKScSaOIiQRLbv3Fb8x5/+uEIieB81c9atQ1qfX0csHv8sEcTTu3dXCWK+4G3wPkSYkjwKEkgCJgLEgw8+GEvEaichiSB9x/6hqF8E+XvODsQSKa/b59fJCkNDWwqc1i5w0uO7ZRFYHDt2rHhg/+yVF7ximctY2HZ4HyKMJlKeBxOGk0miRB5//PEoHYPUrBzEsu/iTzItEQgE42kQnNcO7OS3YDHUE7w+70MsH2ZmZvKlKFpwfl3gIDp86HBx56vVEtnz+g8r0vx6WD791r9HEjHJ4MoOXRbu8+tkBZPIUoiEReCXD//+oeLZVw5WCOOlC8ei9JBEbJn3IebIavOlUCj0eXlwcPl5yeVy/TiY0I9h4vA1EROMXwfLGJiG2sf4+7+okMjZD/7NttPn10kzLAwnkrY2bbwMQmLg2kkojYP3IWYpd6K29fdtNSV53MPCqBVXrlw5zevPS+mAKuCgghBwudckUqsmgvSNv3okrn3sOvpE9B6RpZpIqOZRej/Nae0g1DHq48TFLRXLz00+URzLvVRVzgLb432IbAqEJVFvlGQywNualwknk/kkgku8JhFcnbEO13Jan1+HwTppOIhLohg2YWzYsLnPpZtc2nY3LL6v/W/eVyWDRgNiwe+Xhu9/KchKJ2qp5rGCpbDQ4G3XhR1wJhOfZ2mQiN1vY5d4bZDafBJB2U4eWzI0NDQ69766NoIhz5zWauwyrTVTkmoZtcLWtW3xPtLM9evfFpsdvI+0wBJoVvB+6gIH3tmzL84edOUpFH1NxIRiEkGfSD01EZOI1XTQJ9MpB3VIDvWmtZJTp05H3xGajiYDH2jOvPyfL8S1jRdemxOODxMILgHzPpJY2X3Hz/Da1dV1q6XZ7OH2arOMW5qVDc3dGUpLotakwwYLgCM+jl2Mjo5WlUuzRPikny+++OLz6JhA3ybnJQXvd17y+fwKHJh2EHuJmAQsDVGPRCAbLxFbHzIZGRnJc/l2Eqp5JKVt3jx8m6W1EvwGOPG5RtJI+JMH2+N9JGES8bBE7DEElmZSMWGs7O5ZF5ctpUEylmePLsA2MLnwyjW9P4jSy/LgV4YFYLHn6T1V8ggFr5cmifBJXm/4Y+Pyp+9V5SdFqbnU+A2IY2Njt+HAe/hfHo52ysPe7X25idPH63sgGgjD1vFi+tWLfxct8zrtItRUGR4eXsFptrxhcOiUpbUS3yzB0HU7+DHoD30lLAwWh4XfDu8jCUiEn6zmJVIrDyd9LIrSe5OAF0v0eAOEm6UcRCJy8ljV3fOGz/ewABD8t1+Z+Sox34SD1zRIpHQyT/PJPV/8+fPJxOVGgj9P3UxMnD+FAxCjW1kiiPXP1CcRXBa29UP34/A67YSFEUoL1U5aifVpeAmEquihOHHiZFXfyEIkwmlcEwnlgVgi3b1P+iaOPVwJIvGvSTWRWs2gJIGE8njZ11g6XSIzC5DHxemDFf9cOL+R+KpQKH7wwYeL/35yuVweByK+dC+RsgT6uLzHJHLiTw/HEkHUkgimBkRtwKe1kpAcOG1oaGue01qJnfwWXgr1Bq/P+0gzXgpeCCyQUIQE0okSwSVXPqEbiT/8z5not19M7QPYvL38+WqCL5bTPHaAWpOkHongRr+DL8yNcrXLw7ipD8ESwTLu05nvszSLkBw4bSlqIl4EfhljQlgYCE7ndXkfacZLYaEC+eTTz6LX9y79sakSGVg/OM1pjcIn83yBfkf/T4PzGw0vj4YkMj6eG7UvmPMYOzD/6ZHoqk0f53vwR9mMamgWmUT8/Ti+vAnK+ktQ3uc3k5AccMm3Oq3cJ7Jh0z2W1kpYECwGL4eQMELB+0gzSRLhZU73AvFleR8LBceITSUwsH5TfAWrEfikrifsGBj7cGNVXr0RkkdDEgGlg22qXpEAHJz+x/B5loY/DE0giKN853AsERiUJWJ9JpCISQZR2lZTRxbiSovJAQ8isnRL27JlS/wQKJZKK8jlcv2lHyuPOHiw8t4YH6H7ZEL301TkH2rgIEgBJgbrJ/LNEpYDp0EgSJv+6OMWSWRz35xE5oLLJTE19W50QvNJ3qoAe585USUOCzy+hD9jIqWDrhCSAoN8XD586dxYdDs6Dlb/Y1mYRCAMkwju08E8JdbE8duFRHBSsERwn84jjz7aVJnY1RlbrtX3EUprBiVx3MknPMJ+PE5fSJz5zb55f0vABz0f+Jzn8zm91euaHNCJjL/NXkPS8GEC4XImEd7PgBsSH8ir8Tk35bkcl03ChlkgLl/+S/TZ+KRvViTVPCwW3D9ZOrjj555wnqXjj+Qfyf6D+jR/l7BJBO9RE7Hn4PjtW3PHyuHVLhEjytvL+3Wahcki1JRphUTsYMF/gf/9vyvFCxdeiU/+ZogE3xcGrIV+xzRjEvjdxdcrRBAShM8P0YqrMwuRh/HyyxP38O8Irl27ViWBhQY4N/5qlTB87N5zaIA/W8Pg8q79AHNpc4Lw7xE2FR/e28OTsI7VRNydw9HB7e/HmdvrnEQwBYFJxJo4Fq2QSEgWvsnjyzYDO0CeO/lyJBAfkQCePR7/oPibj0w+WiWJUKCD1b4njCnh3zALhGTBEuE8Y+badHHrxb+Orl4YzZQIxLHg/9634LiYGObf1CL6/AEp1Bs3btwonjpzvkoYPnbuPtLPn2lRTFDTxv9BSLNmjC3758SWB0kVTCImBAtIJNQnglpHSCKYIKmVEgEsi5BYmgW+M3xPJo7z+cn4Pardlm8SaTT25R+oED7vP82ERMGDy3wYkAcCww3w6uF9LCUsDw7AgkiKmze/i/qAWBgU0/w5moYJAmFtTzswfZ59mE2/fDo68dFXgny8Z4nYe7sxz+8Py5hlHhLhy8JWvlUS8bRWIBMD+G587QPfG9dG/I+cNFLVh699eMnzZ0gzXhC+SVNLJGD88uYqceAJB5bG+1hqbNR4rUDTF7AwfFy9+k00UCwgDB8tP5fQBxLXRnz4mcTxYUwQ9uGsWmRlLN8kUmuwmeVDIuW7hCumHiiv09I/vCSOqTmJbG36vvB97NpzpEIaP/zpoxXL+PG9SPj7Twq08/mg48+QZlgS/m/HycX5VgOxAJzG++gUSr/dNP+WPiAKhJcH+k/wdweEURG8r0WDm+5w05cfkGMflA9SXDLkNItaD4/GdsbGxuuWyN7xh+KaCMIkUh752vQTm5kVyNw0Ac3E5OCl8Vf3rKtY5tqIP3Dst7JJmrHMB1f0fZfnE8F7/gxphiXBIrFALQXVeC8ND5af+v3fRu95H53GRHn+n1qBKzmgjppHe/7WsbHzfahy2wnM921YOfsDTp85F72iCeO3EwLlsD3/GAqfbxLBJV4vkeOv/sLP9dpyibQSfAcsEa6JJEmknvBNHCzzZ0gzLBAL/EdmkSA8XAMxeB+dCv/OPg4deb5KGG2XB4MPZiex/SB2V6mVyeVy/W6VurBr4eVn3wQl4l/tPQSC0a9ZlAj+vr/5+5/FEZIIyhx86x+qBpZhGek+zcraMn+GNMPyCIX/x4e+vCRQnvfRycz+k6+WyN79x6rEsWTy8NgH3LFjRzSCE9KwuS64bKNYB6M9QwVpviay9eTs0HdLO3rp/szWRP71qfui1zffvhTXSqycl4ivXXhhcBoHf4blyNdff72VBcJl0sT4+PmH/G/ccfKYD+s74fSFYNfGsT0vEV8TwX06WMa9AVmQCP5rcPOFwx8Y/mDhiZp5mYP3L7KF/c6pkYeBJgk3bRaLfRmQBksE79GPUp6qMdUSseooS4PDHxgshjqjbZNLpw27x4XTRZvByWDtTs5bDHYS2FQBJhGLtEsE4O+zJg3mfGCB8ICzgCCSYpr3J6rBjZcSSQeAKQRwz0yzRQLspMiqRJ47fjq6BIm/iSVi+aEqKu6vyOVyeRf9Pl/Uz8CGwSmJpANA06aZfSQMTijcMeyaOKmXCMDfhctyLBCuhfB6orkMZOwBVqml9N/wTkikVTO4Wz8CZIUpATg/jUyUBxBhfA1m2IJAbKQqxt5IIkK0AJMJmjicl0bQFKH+DF8LUd9GmxlowvSGQiwJuMyN/g3M42APDxPtZ3YekI3xrHZCCNEwi50TpJ3YYzXwSA5+5IYQYglJ4xUbfl4PXv372YeC9T7p04UQyxh7IJgxn0T8qxBCRKzq7snhFU8bZIn4JxmyRPzD2oUQLSaNTRshRAeBR4tIJEKIRVGSyKhEIoQQQgghhEg5aNb45zcLIUTDRMPjNwxq0iexNGjEYDZQjUQsCSyPrq477lp1e8+B1WvW3m2DhTBIqJQ2bAOCymWGXd4BvPf3SPB7rIt92YAjn88jHcXC0RWbBsCYe7/MI+BEffBNUvz9IT3pu+U8X4bL27KNauR8IdoKH4B8EHO+CMPf09yJPitp1BySvlPOw2u8DaqNsERE68DsaGm583fJ4AOal4HG49cHmiYru3vW4b01N7C8evX3v4flubTKvMq0ytfZbVY2XaLbw13TR79P69Co1jqIbvApHaj2H5MlErXpu3vf92lCLDckEiHEolCNRHQkuDrDaUIIUTd+XgiRTpaydjIzM1P0wfkio9i4EGASqbgiU+5oFZ2Lv/MXr3h0JxVpKSwPDi4vMobvuI6vupQv1eKVaye8LDoDXPqNhsiXg/NbActivuD1RYawMSCodUSva9beba8+35efW1ssJfacXw4u10xYDg2GngIoRKcREgmXaQYBISw4CoXCPbx9IUQHMLB+U362X2RT007S0kmfZwk0K0oyuY33J4ToADZvHr6N0xplpoXy4OB9CyFSDJoafJK3I/hzCCFSRulE7ucTu53Bn0cIkRJKNY8VfEK3M8CO3YclESHSCJ/Q7QyThwV/NiFEh3Pjxo2qE7sdwfKQRIRIKRMTueiE5pO8VQEOHXm+Sh6SiBApBRJBXLjwSvHmze+qTvpmBba995kTVdLg4M8nhOhwTCIWV69+01SZYFtvvn0pEsSeswNV0uDgzyeE6HBYIhboK/mqUKiSQr1x7dq14vn8ZCyHA+/cW9z/5n1V0vCheWOFSCEsD45G+0uuX/82qs14ebAsApHnzyWESAksjVoxn0xQa/nk088q5MACqaqJPH1Yd/MKkXZYFkkxNfVu1Mzx8kCtw1+uhThMHruObgumI/hzCCFSTC6Xy7MwkmJy8vVIHNMffRxLYe/4Q1HHqRfFztE9VbUR3rcQIkOwLOYLq23U6jRFutVGdu4+0s/7E0JkkFKtpJ9lUStMFPvyD1SIw9c+du0ajefvFUIsI0qSmGJpcHCtI6pxlJowaNqo6SKEiGBxWJw+c66iOeMHkvE2hBCiSibHfn0qrnmYPDRYTAiRyIRr4hx49rhvzmiwmBCifiCTvfuPFbdv33WK84QQQgghhBBCCCHSjn9U6qo1vSd9HujquuMuTktCj14VYpnhn79sEsGzmlfd3nMAryu7e9ZFed29T9o6loaHvttD4W0beO3q6l3b1dV1q5UXQmQYf/JDIj6QbjWR+GHw9NB3o1IijdVehBApJtScQU1i9Zq1d0dppRqJ5TOonYRrIl23opZSWVoIIYQQQgghhBCivaDfAp2doQ5Ro5HOUJT1V2tCJO1LCJEyrMMUMkFEV2Jch2jp/RsmkZIc3kfH6Gx67/u1rsYYPt/Wsfd2mdeXsW3ObUEI0fGwCHDlBMv+Ckq5dhELILrMW5KL5TMQRHQVp7xdvhozK5HetXhvl4xtv76cECIF+JGovtaAwWSWbjURq4VYehIYdGZlrdax6vaeaKpEL66Va3p/YOvUu20hhBBCiNbx//Nl7sp0+JuaAAAAAElFTkSuQmCC>

[image2]: <data:image/png;base64,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>