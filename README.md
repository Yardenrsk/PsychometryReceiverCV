
# PsychometryReceiverCV

An automation that creates a DB of math questions and answers to 
the PsychomteryBot.
Instead of cropping each question's picture (and there's a lot) and adding answers manually,
I decided to develop this automation which runs over a list of pdf urls and locating the questions
using OpenCV.



## How It Works?
In the "source" csv file, I listed any of the math pdf files
 from "HighQ.com" and looped over the list using Pandas.
For each file, I converted the file type from PDF to JPEG and detected the 
seperating lines between the questions using OpenCV.
Afterwards, save each questions (the area between to lines) with a uniqe name
and relevant folder.
For the answers, I used regex to detect the answer number of each question in the answers PDF 
and added it to the "result" file.

In order to assure that there are no errors (and I've had some..),
I created the "control" file to check mismatches between the amount of answers and questions.

### An example of the question extraction process:

![alt text](https://github.com/Yardenrsk/PsychometryReceiverCV/blob/master/DATA/EXAMPLE/examples.png?raw=true)