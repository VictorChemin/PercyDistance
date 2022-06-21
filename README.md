# PercyDistance
A Python program to measure the distance between the rover Perseverance and any feature (&lt;1000 m far) in the landscape by using Mastcam pictures.

## How to run a Python program?
Unfortunately, I am not very good at Python, but here are a few easy steps to use this program if you are new to Python.

### 1. Install Anaconda
You can download and install Anaconda from their website: https://docs.anaconda.com/anaconda/install/

### 2. Install all the required packages
Open Anaconda.
![pythonw_J8zZFCURu9](https://user-images.githubusercontent.com/70653697/110837495-97058900-82a1-11eb-8053-317fa52f5a12.png)
Then, launch "CMD.exe Prompt".

![pythonw_YnI4Rzznq7](https://user-images.githubusercontent.com/70653697/110837593-b7354800-82a1-11eb-9682-c81fcbab3cca.png)

In the command prompt, type:
`conda install -c conda-forge opencv`
`conda install -c conda-forge tk`
You can then close the command prompt.

### 3. Launch Spyder

![pythonw_MsBLmlAKON](https://user-images.githubusercontent.com/70653697/110838150-683be280-82a2-11eb-9e15-4a0f18fb2fc7.png)

In Spyder, paste the code. Then, simply click the green arrow to start the program.

## How to use my program?
Nothing easier than using this program! However, there are some mistakes you shouldn't make, and some limitations you should be aware of.

### 1. Download the Mastcam pictures
To find these pictures, you will need to go on this Nasa website: https://mars.nasa.gov/mars2020/multimedia/raw-images/
There, you will click on the **Raw** and **Mastcam-Z - Left** and/or **Mastcam-Z - Right** filters. Then, you will choose any picture you want. After clicking on the picutre, you will click on *Full caption*.
![chrome_Qs4Lt7rXZ9](https://user-images.githubusercontent.com/70653697/110838904-4abb4880-82a3-11eb-9e57-40818f88c43a.png)

Then, in orange/red, on the right of the screen, you will be able to **download** the picture. It **doesn't** matter if it is from the *Right* or *Left* camera. To download the picture from the other camera, in the *url*, change **ZLF** to **ZRF** or **ZRF** to **ZLF**.
After doing so, you will reach the Web page of the picture taken at the same time and place as the other, but with the other camera.

### 2. Where to put these pictures?
Put them in any folder you want, but they need to be both in the **same** folder. **DO NOT CHANGE THEIR NAME**. The only changes you can make in the name must be before *\_ZRF\_* or *\_ZLF\_*.
For example, you can change the name from:
`Mars_Perseverance_ZLF_0004_0667301285_000FDR_N0010052AUT_04096_110085J.png`
to:
`My_First_Mars_Picture_ZLF_0004_0667301285_000FDR_N0010052AUT_04096_110085J.png`

### 3. Use the program
Simply start the program, pick the file (Right camera *or* Left camera), and then left-click-and-drag to draw a rectangle around the feature you are interested in measuring the distance from the camera. You can also just click, and it will draw a square around your selection. Then the distance between the selection and the camera will be displaye.

If you then do the same with the right-click, a line will be drawn between the two selections, and a new measure will be displayed: it is the distance, in 3D space, between the two selections. This measurement can be very unprecise for large distances.

A middle-click will erase your selections.

For each selections, 2 pictures will be displayed in the top left corner. The left one is the selection you made on the visible picture (the left camera picture), and the right one is the matched selection on the other picture (the right camera picture). They are displayed so that you can check if the algorithm did its job (or simply if the feature selected is also visible in the second picture). If both pictures do not match, then the measurement is wrong, and it is likely there is no way you will ever get a good measurement of your selection, as the algorithm is actually very performant and is able to match correctly 10-pixel-large patches of Mars sand. So if it failed the matching process, the most likely explanation is that the selected feature is not visible on the other picture.

### 4. Limitations
#### a. Choose a target visible in both pictures
The feature you chose must, obviously, be visible in both pictures. However, you will only be presented with the Right camera picture, so you won't necessarily know wether or not the feature is in both pictures. Normally, the program is supposed to detect if there is no good match, and so if the object isn't visible in both pictures, it should tell you that the result is *uncertain*. However, this can fail, and the program can believe it found a good match if, for example, two very similar rocks are aligned on the x-axis.
#### b. Choose a target with enough contrast
If you just pick a region of interest full of sand, it will match with most of the picture, and the result will be wrong. The program detects when the contrast is under a certain treshold, but the contrast may be above this treshold and still insufficient to make an accurate measurement.
#### c. Choose a precise enough target, yet large enough
Ideally, your region of interest should be 30 to 200 pixels wide. But these are very arbitrary numbers. It depends on many factors. The most important thing is to choose a target which is small enough to be at a "precise" distance. Indeed, if you pick a region where a rock is 20 m far, and another is 300 m far, the result won't be accurate.
/!\ Actually, the algorithm is now pretty good with small Regions Of Interest (ROI). But if you want to measure the distance of a big rock, it is still advised to pick the whole rock, to average the potential 1-pixel errors.
But what if, by selecting the whole rock, I select some things in the background?
The rule of thumb is that the sharpest and largest object in the selection will be the one which will be matched. The sharpness is actually the most important factor.
#### d. Don't choose a target which is too far
Due to technical limitations (pixel resolution, focal length, calibration precision), any object further than 1000 m will have its distance measure with a huge uncertainty. In theory, the maximum distance measurable is 33\*f, with f the focal length in mm.
