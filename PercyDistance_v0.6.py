# -*- coding: utf-8 -*-
"""
Created on Sun Jun 13 17:22:20 2021

@author: chmn_victor
"""

import math
import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog

# Triangulation algorithm based on the position of the feature along the
# x axis on both pictures.
def dist_pix(xR,xL):
    dp=xR-xL
    dp=2*focal_length*alpha/(pixel_size*downsampling)-dp
    D=l*focal_length/(dp*pixel_size*downsampling)
    if D<0:
        D=np.Infinity
    return(D)

def dist_pix_uncertainty(xR,xL):
    Dinf=dist_pix(xR-1,xL)
    if Dinf<0:
        Dinf=np.Infinity
    Dsup=dist_pix(xR+1,xL)
    if Dsup<0:
        Dsup=np.Infinity
    return(Dinf,Dsup)

def dist_2_obj(dist1,dist2,pos1,pos2):
    a=np.sqrt((pos1[1]-pos2[1])**2+(pos1[0]-pos2[0])**2)
    a=a*(pixel_size*downsampling)/focal_length
    return np.sqrt(dist1**2+dist2**2-2*dist1*dist2*np.cos(a))

def round_sig(x,n):
    if x==np.Infinity or x==-np.Infinity:
        return(np.Infinity)
    k=n-np.ceil(math.log10(x))
    return(np.round(x,int(k)))

# Function to select the region of interest with the mouse by clicking and
# draging. Then, it makes all the necessary calculations and displays the
# estimated distance on the picture and in the command prompt.
def click_event(event, x, y, flags, param):
    global xmin
    global xmax
    global ymax
    global ymin
    global leftIsDown
    global rightIsDown
    global imTemp
    global imTemp2
    global left_click
    
    global dist_1
    global dist_2
    global position_1
    global position_2
    
    font = cv2.FONT_HERSHEY_DUPLEX
    font_size = 0.7
    font_thickness = 1
    shadow_thickness = 2
    font_color=(0,255,0)
    number_decimals=3
    
    if event == cv2.EVENT_MBUTTONDOWN:
        imTemp=imgR.copy()
        cv2.imshow("image", imTemp)
    if event == cv2.EVENT_LBUTTONDOWN:
        leftIsDown=1
        
        imTemp=imgR.copy()
        xmin=x
        ymin=y
    if event == cv2.EVENT_LBUTTONUP:
        leftIsDown=0
        
        h=int(imgR.shape[0])
        w=int(imgR.shape[1])
        xmax=x
        ymax=y
        
        if xmax<xmin:
            xmax,xmin=xmin,xmax
        if ymax<ymin:
            ymax,ymin=ymin,ymax
        
        # Position of ROI
        xR=np.average([xmax,xmin])
        yR=np.average([ymax,ymin])
        
        # Pattern matching algorithm
        template=imgR[ymin:ymax,xmin:xmax]
        match=cv2.matchTemplate(imgL,template,cv2.TM_CCORR_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(match)
        xL=max_loc[0]+np.abs(xmax-xmin)/2
        print("xR=",xR)
        print("xL=",xL)
        match_result=imgL[max_loc[1]:max_loc[1]+ymax-ymin,max_loc[0]:max_loc[0]+xmax-xmin]
        
        # Distance calculation
        dist_1=dist_pix(xR, xL)
        Udist_1=dist_pix_uncertainty(xR, xL)
        
        # Display matched areas
        imTemp[1:ymax-ymin+1,1:xmax-xmin+1]=template
        imTemp[ymax-ymin+1:(ymax-ymin)*2+1,1:xmax-xmin+1]=match_result
        cv2.rectangle(imTemp,(1,1),(xmax-xmin+1,(ymax-ymin)*2+1),color=(0,0,255),thickness=2,lineType=cv2.LINE_AA)
        
        # Final result
        cv2.putText(imTemp, str(round_sig(dist_1,number_decimals))+" m", (xmin,ymin-12), font, font_size, (0,0,0), shadow_thickness,lineType=cv2.LINE_AA)
        cv2.putText(imTemp, str(round_sig(dist_1,number_decimals))+" m", (xmin,ymin-12), font, font_size, font_color, font_thickness,lineType=cv2.LINE_AA)
        cv2.imshow("image", imTemp)
        print(xR,",",yR," | ",round_sig(dist_1,number_decimals)," m")
        print("(Between ",round_sig(Udist_1[0],number_decimals)," m and ",round_sig(Udist_1[1],number_decimals)," m)")
             
        position_1=[yR-int(h/2),xR-int(w/2)]
        
        left_click=1
        imTemp2=imTemp.copy()
    if event == cv2.EVENT_RBUTTONDOWN:
        if left_click==1:
            imTemp2=imTemp.copy()
            rightIsDown=1
            xmin=x
            ymin=y
    if event == cv2.EVENT_RBUTTONUP:
        if left_click==1:
            h=int(imgR.shape[0])
            w=int(imgR.shape[1])
            rightIsDown=0
            xmax=x
            ymax=y
            if xmax<xmin:
                xmax,xmin=xmin,xmax
            if ymax<ymin:
                ymax,ymin=ymin,ymax
                
            # Position of ROI
            xR=np.average([xmax,xmin])
            yR=np.average([ymax,ymin])

            # Pattern matching algorithm
            template=imgR[ymin:ymax,xmin:xmax]
            match=cv2.matchTemplate(imgL,template,cv2.TM_CCORR_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(match)
            xL=max_loc[0]+np.abs(xmax-xmin)/2
            match_result=imgL[max_loc[1]:max_loc[1]+ymax-ymin,max_loc[0]:max_loc[0]+xmax-xmin]
            
            # Distance calculation
            dist_2=dist_pix(xR, xL)
            Udist_2=dist_pix_uncertainty(xR, xL)

            # Display matched areas
            imTemp2[1:ymax-ymin+1,w-(xmax-xmin)-1:w-1]=template
            imTemp2[ymax-ymin+1:(ymax-ymin)*2+1,w-(xmax-xmin)-1:w-1]=match_result
            
            cv2.rectangle(imTemp2,(w-1,1),(w-(xmax-xmin)-1,(ymax-ymin)*2+1),color=(255,0,0),thickness=2,lineType=cv2.LINE_AA)
            
            # Final result
            position_2=[yR-int(h/2),xR-int(w/2)]
            cv2.line(imTemp2, (int(position_1[1]+w/2),int(position_1[0]+h/2)), (int(position_2[1]+w/2),int(position_2[0]+h/2)), (0, 255, 0), thickness=2, lineType=cv2.LINE_AA)
            cv2.putText(imTemp2, str(round_sig(dist_2,number_decimals))+" m", (xmin,ymin-12), font, font_size, (0,0,0), shadow_thickness, lineType=cv2.LINE_AA)
            cv2.putText(imTemp2, str(round_sig(dist_2,number_decimals))+" m", (xmin,ymin-12), font, font_size, font_color, font_thickness, lineType=cv2.LINE_AA)
            distance_between_obj=dist_2_obj(dist_1, dist_2, position_1, position_2)
            cv2.putText(imTemp2, "D: "+str(round_sig(distance_between_obj,number_decimals))+" m", (xmin,ymin-35), font, font_size, (0,0,0), shadow_thickness, lineType=cv2.LINE_AA)
            cv2.putText(imTemp2, "D: "+str(round_sig(distance_between_obj,number_decimals))+" m", (xmin,ymin-35), font, font_size, font_color, font_thickness, lineType=cv2.LINE_AA)
            cv2.imshow("image", imTemp2)
            print(xR,",",yR," | ",round_sig(dist_2,number_decimals)," m")
            print("(Between ",round_sig(Udist_2[0],number_decimals)," m and ",round_sig(Udist_2[1],number_decimals)," m")
            print("Dist: ",round_sig(distance_between_obj,number_decimals)," m")
            
    if event == cv2.EVENT_MOUSEMOVE:
        if leftIsDown==1:
            imTemp=imgR.copy()
            cv2.rectangle(imTemp,(xmin,ymin),(x,y),color=(0,0,255),thickness=2,lineType=cv2.LINE_AA)
            cv2.circle(imTemp, (int((xmin+x)/2),int((ymin+y)/2)), radius=2, color=(0, 0, 255), thickness=-1)
            cv2.imshow("image", imTemp)
        elif rightIsDown==1:
            imTemp2=imTemp.copy()
            cv2.rectangle(imTemp2,(xmin,ymin),(x,y),color=(255,0,0),thickness=2,lineType=cv2.LINE_AA)
            cv2.circle(imTemp2, (int((xmin+x)/2),int((ymin+y)/2)), radius=2, color=(255, 0, 0), thickness=-1)
            cv2.imshow("image", imTemp2)
        
# Function for when the 'Select file' button is pushed
def button_push():
        global fullFileName
        global keepGoing
        fullFileName=""
        fullFileName=filedialog.askopenfilename(initialdir=folderName)
        if fullFileName!="":
            root.destroy()
        
# Function for when the 'Same file' button is pushed
def same_file():
    global keepGoing
    root.destroy()
    if fullFileName=="":
        keepGoing=0
        root.destroy()
        
# Function for when the window is closd
def on_closing():
    global keepGoing
    keepGoing=0
    root.destroy()
    
def save_file():
    types=("Image","*.png")
    save_name=filedialog.asksaveasfilename(defaultextension=types)
    if save_name!="":
        cv2.imwrite(save_name,imTemp2)
    root.destroy()

rightIsDown=0
leftIsDown=0
folderName="D:/Users/victo/Desktop/PerseveranceFile/"
fullFileName=""
sup_mod=0
invisible=-1
keepGoing=1

while 1:
        
    # Create input window
    root=tk.Tk()
    root.geometry("500x100")
    root.title("PercyDistance v0.2")
    
    frame=tk.Frame(root)
    frame.pack()
    
    button = tk.Button(frame, text = "Select file", command = button_push)
    button.pack(pady=10)
    button2 = tk.Button(frame, text = "Use same file", command = same_file)
    button2.pack(pady=10)
    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    root.mainloop()
    
    if keepGoing==0:
        break
    
    if (fullFileName.find("_ZL")!=-1 or fullFileName.find("_ZR")!=-1):
        # Load images
        # If the first image is the Left camera picture, it will change to
        # the Right camera picture.
        fullFileName=fullFileName.replace("_ZL", "_ZR")
        imgR = cv2.imread(fullFileName)
        fullFileName=fullFileName.replace("_ZR", "_ZL")
        imgL = cv2.imread(fullFileName)
        fileName=fullFileName[fullFileName.rfind("_ZL"):]
        
        # Set the default folder to the last folder used
        folderName=fullFileName[:fullFileName.rfind("/")]
        
        # Set constants
        # Focal length and downsampling are based on the file's name
        focal_length=float(fileName[46:49])/1000.0 #get focal length of picture
        downsampling=2**float(fileName[49]) #get downsampling
        alpha=1.172/180*np.pi  #stereo toe-in angle
        l=24.3e-2 #stereo distance
        pixel_size=7.4e-6 #pixel size of sensor
        imgsize=imgR.shape #dimensions of image
        
    elif (fullFileName.find("_NL")!=-1 or fullFileName.find("_NR")!=-1):
        # Load images
        # If the first image is the Left camera picture, it will change to
        # the Right camera picture.
        fullFileName=fullFileName.replace("_NL", "_NR")
        imgR = cv2.imread(fullFileName)
        fullFileName=fullFileName.replace("_NR", "_NL")
        imgL = cv2.imread(fullFileName)
        fileName=fullFileName[fullFileName.rfind("_NL"):]
        
        # Set the default folder to the last folder used
        folderName=fullFileName[:fullFileName.rfind("/")]
        
        # Set constants
        # Focal length and downsampling are based on the file's name
        focal_length=19.1/1000.0 #get focal length of picture
        downsampling=2**float(fileName[49]) #get downsampling
        alpha=-0.18/180*np.pi  #stereo toe-in angle
        l=42.4e-2 #stereo distance
        pixel_size=6.4e-6 #pixel size of sensor
        imgsize=imgR.shape #dimensions of image
    else:
        print("NOT A STANDARD FILE")
        continue
    
    print(imgsize)
    
    # Show image
    cv2.namedWindow('image', cv2.WINDOW_NORMAL)
    cv2.imshow("image", imgR)
    cv2.resizeWindow("image", imgR.shape[0], imgR.shape[1])
    cv2.moveWindow("image", 0,0)
    
    # Wait for a mouse input
    left_click=0
    cv2.setMouseCallback("image", click_event)
    while cv2.getWindowProperty('image', 0) >= 0:
        k=cv2.waitKey(0)
        if k==115 and left_click==1:
            root=tk.Tk()
            root.geometry("500x70")
            root.title("PercyDistance v0.2")
            
            frame=tk.Frame(root)
            frame.pack()
            
            button = tk.Button(frame, text = "Save picture", command = save_file)
            button.pack(pady=10)
            
            root.mainloop()
        elif k==27:
            break
    cv2.destroyAllWindows()