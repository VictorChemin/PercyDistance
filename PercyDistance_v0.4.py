# -*- coding: utf-8 -*-
"""
Created on Sun Mar 14 18:11:24 2021

@author: victo
"""

import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog

# Triangulation algorithm based on the position of the feature along the
# x axis on both pictures.
def dist_pix(xR,xL):
    dR=(imgsize[1]/2-xR)*pixel_size*downsampling
    dL=(xL-imgsize[1]/2)*pixel_size*downsampling
    angle_R=np.pi/2-alpha-np.arctan(dR/focal_length)
    angle_L=np.pi/2-alpha-np.arctan(dL/focal_length)
    Dist_R=l*np.sin(angle_L)/np.sin(angle_L+angle_R)
    Dist_L=l*np.sin(angle_R)/np.sin(angle_L+angle_R)
    D=(Dist_R+Dist_L)/2
    if D<0:
        D=np.Infinity
    return(D)

def perpendicular_dist(xR,xL):
    dR=(imgsize[1]/2-xR)*pixel_size*downsampling
    dL=(xL-imgsize[1]/2)*pixel_size*downsampling
    angle_R=np.pi/2-alpha-np.arctan(dR/focal_length)
    angle_L=np.pi/2-alpha-np.arctan(dL/focal_length)
    D=l*(np.sin(angle_L)*np.sin(angle_R))/(np.sin(angle_L+angle_R))
    if D<0:
        D=np.Infinity
    return(D)

def dist_2_obj(distZ1,distZ2,pos1,pos2):
    pz1=distZ1
    pz2=distZ2
    px1=pos1[1]*pixel_size*pz1/focal_length
    py1=pos1[0]*pixel_size*pz1/focal_length
    px2=pos2[1]*pixel_size*pz2/focal_length
    py2=pos2[0]*pixel_size*pz2/focal_length
    dx=np.abs(px2-px1)
    dy=np.abs(py2-py1)
    dz=np.abs(pz2-pz1)
    d_dist=np.sqrt(dx**2+dy**2+dz**2)
    return(d_dist)

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
    number_decimals=4
    
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
        xpos=np.average([xmax,xmin])
        ypos=np.average([ymax,ymin])
        
        # Pattern matching algorithm
        template=imgR[ymin:ymax,xmin:xmax]
        match=cv2.matchTemplate(imgL,template,cv2.TM_CCORR_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(match)
        xL=max_loc[0]+np.abs(xmax-xmin)/2
        match_result=imgL[max_loc[1]:max_loc[1]+ymax-ymin,max_loc[0]:max_loc[0]+xmax-xmin]
        
        # Distance calculation
        dist_1=dist_pix(xpos, xL)
        
        # Display matched areas
        imTemp[1:ymax-ymin+1,1:xmax-xmin+1]=template
        imTemp[ymax-ymin+1:(ymax-ymin)*2+1,1:xmax-xmin+1]=match_result
        cv2.rectangle(imTemp,(1,1),(xmax-xmin+1,(ymax-ymin)*2+1),color=(0,0,255),thickness=2,lineType=cv2.LINE_AA)
        
        # Final result
        cv2.putText(imTemp, str(round(dist_1,number_decimals))+" m", (xmin,ymin-12), font, font_size, (0,0,0), shadow_thickness,lineType=cv2.LINE_AA)
        cv2.putText(imTemp, str(round(dist_1,number_decimals))+" m", (xmin,ymin-12), font, font_size, font_color, font_thickness,lineType=cv2.LINE_AA)
        cv2.imshow("image", imTemp)
        print(xpos,",",ypos," | ",np.round(dist_1,number_decimals)," m")
        
        dist_1=perpendicular_dist(xpos, xL)        
        position_1=[ypos-int(h/2),xpos-int(w/2)]
        
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
            xpos=np.average([xmax,xmin])
            ypos=np.average([ymax,ymin])

            # Pattern matching algorithm
            template=imgR[ymin:ymax,xmin:xmax]
            match=cv2.matchTemplate(imgL,template,cv2.TM_CCORR_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(match)
            xL=max_loc[0]+np.abs(xmax-xmin)/2
            match_result=imgL[max_loc[1]:max_loc[1]+ymax-ymin,max_loc[0]:max_loc[0]+xmax-xmin]
            
            # Distance calculation
            dist_2=dist_pix(xpos, xL)

            # Display matched areas
            imTemp2[1:ymax-ymin+1,w-(xmax-xmin)-1:w-1]=template
            imTemp2[ymax-ymin+1:(ymax-ymin)*2+1,w-(xmax-xmin)-1:w-1]=match_result
            
            cv2.rectangle(imTemp2,(w-1,1),(w-(xmax-xmin)-1,(ymax-ymin)*2+1),color=(255,0,0),thickness=2,lineType=cv2.LINE_AA)
            
            # Final result
            position_2=[ypos-int(h/2),xpos-int(w/2)]
            cv2.line(imTemp2, (int(position_1[1]+w/2),int(position_1[0]+h/2)), (int(position_2[1]+w/2),int(position_2[0]+h/2)), (0, 255, 0), thickness=2, lineType=cv2.LINE_AA)
            cv2.putText(imTemp2, str(round(dist_2,number_decimals))+" m", (xmin,ymin-12), font, font_size, (0,0,0), shadow_thickness, lineType=cv2.LINE_AA)
            cv2.putText(imTemp2, str(round(dist_2,number_decimals))+" m", (xmin,ymin-12), font, font_size, font_color, font_thickness, lineType=cv2.LINE_AA)
            dist_2=perpendicular_dist(xpos, xL)
            distance_between_obj=dist_2_obj(dist_1, dist_2, position_1, position_2)
            cv2.putText(imTemp2, "D: "+str(round(distance_between_obj,number_decimals))+" m", (xmin,ymin-35), font, font_size, (0,0,0), shadow_thickness, lineType=cv2.LINE_AA)
            cv2.putText(imTemp2, "D: "+str(round(distance_between_obj,number_decimals))+" m", (xmin,ymin-35), font, font_size, font_color, font_thickness, lineType=cv2.LINE_AA)
            cv2.imshow("image", imTemp2)
            print(xpos,",",ypos," | ",np.round(dist_2,number_decimals)," m")
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
    
    # Load images
    # If the first image is the Left camera picture, it will change to
    # the Right camera picture.
    fullFileName=fullFileName.replace("_ZLF_", "_ZRF_")
    imgR = cv2.imread(fullFileName)
    fullFileName=fullFileName.replace("_ZRF_", "_ZLF_")
    imgL = cv2.imread(fullFileName)
    fileName=fullFileName[fullFileName.rfind("_ZLF_"):]
    
    # Set the default folder to the last folder used
    folderName=fullFileName[:fullFileName.rfind("/")]
    
    # Set constants
    # Focal length and downsampling are based on the file's name
    focal_length=float(fileName[46:49])/1000 #get focal length of picture
    downsampling=2**float(fileName[49]) #get downsampling
    alpha=1.172/180*np.pi  #stereo toad-in angle
    l=24.3e-2 #stereo distance
    pixel_size=7.4e-6 #pixel size of sensor
    imgsize=imgR.shape #dimensions of image
    
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