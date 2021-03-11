import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox

# There seems to be a shift on the y axis between the Reft and
# Right camera. So, to measure this shift and to correct it,
# we first create a version of the pictures where the colors
# of the pixels with the same y coordinate are averaged.
def average_col_row(im,n_col=0):
    h=im.shape[0]
    w=n_col
    if n_col==0:
        w=im.shape[1]
    dim=(h,w)
    imAv=np.round(np.average(im,axis=1))
    imAv = np.array(imAv, dtype='uint8')
    imAv=imAv[np.newaxis,:,:]
    imAv=cv2.resize(imAv,dim)
    imAv=np.rot90(imAv,k=-1)
    return(imAv)

# We compute the y shift by subtracting both pictures, modified
# with the average_col_row function, and doing a step by step shift.
# Then we look for which shift the average color was the darkest. This
# means that both pictures overlay very well.
def yshift_compute(imR,imL):
    imR=average_col_row(imR,1)
    imL=average_col_row(imL,1)
    h=imR.shape[0]
    test=np.empty((0,2))
    for i in range(0,int(h/2)):
        imTempR=imR
        imTempL=imL
        overlay=cv2.subtract(imTempR[np.abs(i):,:],imTempL[:h-np.abs(i),:])
        overlay2=cv2.subtract(imTempL[:h-np.abs(i),:],imTempR[np.abs(i):,:])
        overlay=cv2.add(overlay,overlay2)      
        note=np.average(overlay)
        test=np.append(test,np.array([[i,note]]),axis=0)
    for i in range(1,int(h/2)):
        imTempR=imL
        imTempL=imR
        overlay=cv2.subtract(imTempR[np.abs(i):,:],imTempL[:h-np.abs(i),:])
        overlay2=cv2.subtract(imTempL[:h-np.abs(i),:],imTempR[np.abs(i):,:])
        overlay=cv2.add(overlay,overlay2)
        note=np.average(overlay)
        test=np.append(test,np.array([[i,note]]),axis=0)
    ymax_index=np.argmin(test,axis=0)[1]
    return(int(test[ymax_index][0]))

# We use the same general method than for the yshift. However, we just move
# the selected area so that it's faster. Also, in case the y shift wasn't
# well computed, we also move the selected area along the y axis for a few
# number of pixels.

def xshift_compute(xR,yR,imR,imL,sx,sy):
    n_av=25
    dy=10
    yL=yR-yshift_compute(imR,imL)
    w=imR.shape[1]
    test=np.empty((0,2))
    for j in range(-dy,dy+1):
        for i in range(sx,w-sx):
            imTempR=imR
            imTempL=imL
            overlay=cv2.subtract(imTempR[yR-sy:yR+sy,xR-sx:xR+sx],imTempL[yL-j-sy:yL-j+sy,i-sx:i+sx])
            overlay2=cv2.subtract(imTempL[yL-j-sy:yL-j+sy,i-sx:i+sx],imTempR[yR-sy:yR+sy,xR-sx:xR+sx])
            overlay=cv2.add(overlay,overlay2)
            note=np.average(overlay)
            test=np.append(test,np.array([[i,note]]),axis=0)
    xshift_dat=test[test[:,1].argsort()][:n_av,:]
    xshift_vals=xshift_dat[:,0]
    xshift_minIntensity=xshift_dat[:,1]
    certainty=np.median(test[:,1])/xshift_minIntensity[0]
    xshift_weights=1/np.arange(1,n_av+1,1)**2
    result=np.average(xshift_vals,weights=xshift_weights)
    return(result,certainty)

# Triangulation algorithm based on the position of the feature along the
# x axis on both pictures.
def dist_pix(xR,xL):
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

# Function to select the region of interest with the mouse by clicking and
# draging. Then, it makes all the necessary calculations and displays the
# estimated distance on the picture and in the command prompt.
def click_event(event, x, y, flags, param):
    global minx
    global maxx
    global maxy
    global miny
    global isDown
    global imTemp
    font = cv2.FONT_HERSHEY_SIMPLEX
    if event == cv2.EVENT_LBUTTONDOWN:
        imTemp=imgR.copy()
        isDown=1
        minx=x
        miny=y
    if event == cv2.EVENT_LBUTTONUP:
        isDown=0
        maxx=x
        maxy=y
        if maxx<minx:
            maxx,minx=minx,maxx
        if maxy<miny:
            maxy,miny=miny,maxy
        posx=int(np.round(np.average([maxx,minx])))
        posy=int(np.round(np.average([maxy,miny])))
        sx=int(np.ceil(np.abs(maxx-minx)/2))
        sy=int(np.ceil(np.abs(maxy-miny)/2))
        contrast_test=imgR.copy()
        contrast_test=contrast_test[miny:maxy,minx:maxx]
        contrast_test=cv2.cvtColor(contrast_test, cv2.COLOR_BGR2GRAY)
        contrast = contrast_test.std()
        xL=xshift_compute(posx,posy,imgR,imgL,sx,sy)
        certainty=xL[1]
        xL=xL[0]
        dist=dist_pix(posx, xL)
        if(contrast<15):
            print("Contrast of chosen area too low.")
        if(certainty<2):
            print("Result too uncertain.")
            print("The chosen feature might be out of the Left image.")
            print("The chosen area might be too large.")
            cv2.putText(imTemp, "Uncertain", (minx,miny-12), font, 1, (0,0,0), 5)
            cv2.putText(imTemp, "Uncertain", (minx,miny-12), font, 1, (0,255,0), 2)
        elif(contrast>=15):
            print(posx,",",posy," | ",np.round(dist,2)," m")
            cv2.putText(imTemp, str(round(dist,2))+" m", (minx,miny-12), font, 1, (0,0,0), 5)
            cv2.putText(imTemp, str(round(dist,2))+" m", (minx,miny-12), font, 1, (0,255,0), 2)
        cv2.imshow("image", imTemp)
    if event == cv2.EVENT_MOUSEMOVE:
        if isDown==1:
            imTemp=imgR.copy()
            cv2.rectangle(imTemp,(minx,miny),(x,y),color=(0,0,255),thickness=2)
            cv2.imshow("image", imTemp)
        
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

isDown=0
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
    cv2.setMouseCallback("image", click_event)
    cv2.waitKey(0)
    cv2.destroyAllWindows()