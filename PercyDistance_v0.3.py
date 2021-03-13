import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox

# Triangulation algorithm based on the position of the feature along the
# x axis on both pictures.
def dist_pix(xR,xL):
    pR=(imgsize[1]/2-xR)*pixel_size*downsampling
    pL=(xL-imgsize[1]/2)*pixel_size*downsampling
    bR=np.arctan(pR/focal_length)
    bL=np.arctan(pL/focal_length)
    eR=np.pi/2-alpha-bR
    eL=np.pi/2-alpha-bL
    DistR=l*np.sin(eL)/np.sin(eL+eR)
    DistL=l*np.sin(eR)/np.sin(eL+eR)
    D=(DistR+DistL)/2
    #D=l*(np.sin(eL)*np.sin(eR))/(np.sin(eL+eR))
    if D<0:
        D=np.Infinity
    return(D)

def z_axis_dist(xR,xL):
    pR=(imgsize[1]/2-xR)*pixel_size*downsampling
    pL=(xL-imgsize[1]/2)*pixel_size*downsampling
    bR=np.arctan(pR/focal_length)
    bL=np.arctan(pL/focal_length)
    eR=np.pi/2-alpha-bR
    eL=np.pi/2-alpha-bL
    D=l*(np.sin(eL)*np.sin(eR))/(np.sin(eL+eR))
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
    global minx
    global maxx
    global maxy
    global miny
    global leftIsDown
    global rightIsDown
    global imTemp
    global imTemp2
    global left_click
    
    global dist_1
    global dist_2
    global position_1
    global position_2
    width_display=50
    font = cv2.FONT_HERSHEY_SIMPLEX
    if event == cv2.EVENT_LBUTTONDOWN:
        leftIsDown=1
        
        imTemp=imgR.copy()
        minx=x
        miny=y
    if event == cv2.EVENT_LBUTTONUP:
        leftIsDown=0
        
        h=int(imgR.shape[0])
        w=int(imgR.shape[1])
        maxx=x
        maxy=y
        
        if maxx<minx:
            maxx,minx=minx,maxx
        if maxy<miny:
            maxy,miny=miny,maxy
        
        # Position of ROI
        posx=int(np.round(np.average([maxx,minx])))
        posy=int(np.round(np.average([maxy,miny])))
        
        # Pattern matching algorithm
        pattern=imgR[miny:maxy,minx:maxx]
        match=cv2.matchTemplate(imgL,pattern,cv2.TM_SQDIFF)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(match)
        xL=min_loc[0]+np.abs(maxx-minx)/2
        
        # Distance calculation
        dist_1=dist_pix(posx, xL)
        
        # Display matched areas
        imTemp[:,:width_display*2]=imgL[:,int(xL)-width_display:int(xL)+width_display]
        imTemp[:,width_display*2:width_display*4]=imgR[:,int(posx)-width_display:int(posx)+width_display]
        
        # Final result
        cv2.line(imTemp, (width_display*4+2, 0), (width_display*4+2, h), (0, 0, 190), thickness=2)
        cv2.line(imTemp, (width_display*2, 0), (width_display*2, h), (0, 0, 255), thickness=2)
        cv2.putText(imTemp, str(round(dist_1,2))+" m", (minx,miny-12), font, 1, (0,0,0), 5)
        cv2.putText(imTemp, str(round(dist_1,2))+" m", (minx,miny-12), font, 1, (0,255,0), 2)
        cv2.imshow("image", imTemp)
        print(posx,",",posy," | ",np.round(dist_1,2)," m")
        
        dist_1=z_axis_dist(posx, xL)        
        position_1=[posy-int(h/2),posx-int(w/2)]
        
        left_click=1
    if event == cv2.EVENT_RBUTTONDOWN:
        if left_click==1:
            imTemp2=imTemp.copy()
            rightIsDown=1
            minx=x
            miny=y
    if event == cv2.EVENT_RBUTTONUP:
        if left_click==1:
            h=int(imgR.shape[0])
            w=int(imgR.shape[1])
            rightIsDown=0
            maxx=x
            maxy=y
            if maxx<minx:
                maxx,minx=minx,maxx
            if maxy<miny:
                maxy,miny=miny,maxy
                
            # Position of ROI
            posx=int(np.round(np.average([maxx,minx])))
            posy=int(np.round(np.average([maxy,miny])))

            # Pattern matching algorithm
            pattern=imgR[miny:maxy,minx:maxx]
            match=cv2.matchTemplate(imgL,pattern,cv2.TM_SQDIFF)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(match)
            xL=min_loc[0]+np.abs(maxx-minx)/2
            
            # Distance calculation
            dist_2=dist_pix(posx, xL)

            # Display matched areas
            imTemp2[:,:width_display*2]=imgL[:,int(xL)-width_display:int(xL)+width_display]
            imTemp2[:,width_display*2:width_display*4]=imgR[:,int(posx)-width_display:int(posx)+width_display]
            
            # Final result
            cv2.line(imTemp2, (width_display*4+2, 0), (width_display*4+2, h), (190, 0, 0), thickness=2)
            cv2.line(imTemp2, (width_display*2, 0), (width_display*2, h), (255, 0, 0), thickness=2)
            position_2=[posy-int(h/2),posx-int(w/2)]
            cv2.line(imTemp2, (position_1[1]+int(w/2),position_1[0]+int(h/2)), (position_2[1]+int(w/2),position_2[0]+int(h/2)), (0, 255, 0), thickness=2)
            cv2.putText(imTemp2, str(round(dist_2,2))+" m", (minx,miny-12), font, 1, (0,0,0), 5)
            cv2.putText(imTemp2, str(round(dist_2,2))+" m", (minx,miny-12), font, 1, (0,255,0), 2)
            dist_2=z_axis_dist(posx, xL)
            distance_between_obj=dist_2_obj(dist_1, dist_2, position_1, position_2)
            cv2.putText(imTemp2, "Distance: "+str(round(distance_between_obj,2))+" m", (width_display*4+12,50), font, 1, (0,0,0), 5)
            cv2.putText(imTemp2, "Distance: "+str(round(distance_between_obj,2))+" m", (width_display*4+12,50), font, 1, (0,255,0), 2)
            cv2.imshow("image", imTemp2)
            print(posx,",",posy," | ",np.round(dist_2,2)," m")
    if event == cv2.EVENT_MOUSEMOVE:
        if leftIsDown==1:
            imTemp=imgR.copy()
            cv2.rectangle(imTemp,(minx,miny),(x,y),color=(0,0,255),thickness=2)
            cv2.circle(imTemp, (int((minx+x)/2),int((miny+y)/2)), radius=2, color=(0, 0, 255), thickness=-1)
            cv2.imshow("image", imTemp)
        elif rightIsDown==1:
            imTemp2=imTemp.copy()
            cv2.rectangle(imTemp2,(minx,miny),(x,y),color=(255,0,0),thickness=2)
            cv2.circle(imTemp2, (int((minx+x)/2),int((miny+y)/2)), radius=2, color=(255, 0, 0), thickness=-1)
            cv2.imshow("image", imTemp2)
        
# Function for when the 'Select file' button is pushed
def button_push():
        global fullFileName
        global keepGoing
        fullFileName=""
        fullFileName=filedialog.askopenfilename(initialdir=folderName)
        if fullFileName=="":
            keepGoing=0
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
    if messagebox.askokcancel("Quit PercyDistance v0.1", "Do you want to quit?"):
        keepGoing=0
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
    alpha=1.1713/180*np.pi  #stereo toad-in angle
    l=24.3e-2 #stereo distance
    pixel_size=7.4e-6 #pixel size of sensor
    imgsize=imgR.shape #dimensions of image
    
    # Show image
    cv2.namedWindow('image', cv2.WINDOW_NORMAL)
    cv2.resizeWindow('jpg', imgR.shape[1], imgR.shape[0])
    cv2.imshow("image", imgR)
    
    # Wait for a mouse input
    left_click=0
    cv2.setMouseCallback("image", click_event)
    cv2.waitKey(0)
    cv2.destroyAllWindows()