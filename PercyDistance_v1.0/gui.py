"""
    Made by Victor Chemin @c_victor_astro
    21 June 2022

    The two GUI components of the program: the images picker (tkinter), and the image interaction interface (opencv).
"""
import os

import tkinter as tk
from tkinter import filedialog as fd

import numpy as np
import cv2 as cv
import cv2plus as cvp

from stereocam import StereoCam as SC
from stereocam import upscale_width

DEFAULT_TEMPLATE_SIZE = 30
MAX_TEMPLATE_H = 60
MAX_TEMPLATE_W = 60
MAX_H = int(1080 * 0.75)
MAX_W = int(1920 * 0.75)


class Gui:
    def __init__(self):
        self.create_root()

    def pick_picture(self, n = 1):
        n = int(n)
        n = 1 if n < 1 else n
        self.filenames.clear()
        title_window = 'Open picture'

        for i in range(n):
            if n > 1:
                title_window = f'Open picture n°{i+1}'

            filetypes = (('Image', '*.png *.jpg *.tif'),
                        ('All files', '*.*'))

            file = fd.askopenfilename(title=title_window,
                                      initialdir=self.read_last_folder(),
                                      filetypes=filetypes)
            if file == "":
                self.filenames.clear()
                break
            self.save_last_folder(file[:file.rfind("/")+1])
            self.filenames.append(file)

        if len(self.filenames) > 0:
            self.root.destroy()

    def mainloop(self):
        self.root.mainloop()

        while len(self.filenames) > 0:
            if len(self.filenames) == 1:
                cams = SC(left_cam=self.filenames[0], x_upscale=int(self.uscale_val.get()))
            elif len(self.filenames) == 2:
                cams = SC(left_cam=self.filenames[0], right_cam=self.filenames[1], x_upscale=int(self.uscale_val.get()))
            else:
                print("Error.")
            imgs = Images(cams)
            imgs.show()
            self.filenames.clear()
            self.create_root()
            self.root.mainloop()

    def get_filenames(self, idx=None):
        if idx is None:
            return self.filenames
        return self.filenames[idx]

    def create_root(self):
        self.root = tk.Tk()
        self.root.title('Stereo Distance Calculator')
        self.root.geometry('300x150')

        self.frame = tk.Frame(self.root)
        self.open_button = tk.Button(self.frame, text='Open a picture',
                                     command=lambda: self.pick_picture(1))
        self.open_2_pics_button = tk.Button(self.frame, text='Open two pictures',
                                            command=lambda: self.pick_picture(2))
        self.uscale_val = tk.StringVar(value=1)
        self.spinbox = tk.Spinbox(self.frame, from_=1, to=10, textvariable=self.uscale_val)
        self.text = tk.Label(self.frame, text="Precision: ")

        self.open_button.grid(row=0, column=0, columnspan=2, pady=2, sticky="news")
        self.open_2_pics_button.grid(row=1, column=0, columnspan=2, pady=2, sticky="news")
        self.text.grid(row=2, column=0, columnspan=1, pady=2, sticky="news")
        self.spinbox.grid(row=2, column=1, columnspan=1, pady=2, sticky="news")

        self.frame.pack(fill="none", expand=True)
        self.filenames = []

    def save_last_folder(self, folder_path):
        with open("lastdir.dat", 'w') as out_file:
            out_file.write(folder_path)

    def read_last_folder(self):
        if os.path.exists("lastdir.dat"):
            with open("lastdir.dat", 'r') as in_file:
                folder = in_file.readline()
            return folder
        else:
            self.save_last_folder("/")
            return "/"



class Images:
    def __init__(self, stereocam_module):
        self.sc_mod = stereocam_module
        self.img_L = stereocam_module.left_cam.copy()
        self.img_R = stereocam_module.right_cam.copy()
        self.img_L_upscaled = stereocam_module.left_cam_upscaled.copy()
        self.img_R_upscaled = stereocam_module.right_cam_upscaled.copy()
        self.img_L_resized, self.scale = cvp.homothety(self.img_L, MAX_W, MAX_H)
        self.processed_img = self.img_L_resized.copy()
        self.dark_version = (0.5 * self.img_L_resized).astype(np.uint8)
        # self.dark_version[:] = np.mean(self.dark_version, axis=2, keepdims=True)
        # self.dark_version = self.dark_version.astype(np.uint8)

        self.left_button_clicked_once = False
        self.left_button_is_down = False
        self.right_button_is_down = False
        
        # information about the left mouse click:
        #   self.mouseL[0] = [current_x_raw, current_y_raw]
        #   self.mouseL[1] = [saved_x_raw, saved_y_raw]
        #   self.mouseL[2] = [current_x, current_y]
        #   self.mouseL[3] = [saved_x, saved_y]
        self.mouseL = np.zeros((4, 2), dtype=int)
        self.mouseR = np.zeros((4, 2), dtype=int)

        self.distance_1 = 0.0
        self.distance_2 = 0.0

        cv.namedWindow("Left Image")
        cv.setMouseCallback("Left Image", self.click_event)
        cv.setWindowTitle("Left Image", "Left Image - Press Esc to close")

    def click_event(self, event, x, y, flags, param):
        

        if event == cv.EVENT_MOUSEMOVE:
            if self.left_button_is_down:
                self.right_button_is_down = False
                # raw x and y values, which are the actual x and y values
                # of the mouse, based on the displayed pictures
                self.mouseL[0] = [x, y]
                # converted x and y values, to match the coordinates of the
                # original images
                self.mouseL[2] = (self.mouseL[0] / self.scale).astype(int)
                self.process()

            elif self.right_button_is_down:
                # raw x and y values, which are the actual x and y values
                # of the mouse, based on the displayed pictures
                self.mouseR[0] = [x, y]
                # converted x and y values, to match the coordinates of the
                # original images
                self.mouseR[2] = (self.mouseR[0] / self.scale).astype(int)
                self.process(False)


        # If the left mouse button is down
        if event == cv.EVENT_LBUTTONDOWN:
            self.left_button_clicked_once = True
            # raw x and y values, which are the actual x and y values
            # of the mouse, based on the displayed pictures
            self.mouseL[0] = [x, y]
            # converted x and y values, to match the coordinates of the
            # original images
            self.mouseL[2] = (self.mouseL[0] / self.scale).astype(int)
            # We save the location is raw and transformed coordinates
            self.mouseL[1] = [x, y]
            self.mouseL[3] = (self.mouseL[1] / self.scale).astype(int)
            # We save the fact that the button is currently down
            self.left_button_is_down = True

        # If the left mouse button is down
        if event == cv.EVENT_LBUTTONUP:
            # We save the fact that the button is not down anymore
            self.left_button_is_down = False
            self.right_button_is_down = False
            
            if np.sum(self.mouseL[0] == self.mouseL[1]) > 0:
                # if the traced rectangle has one of its side with a 0 size, then we instead
                # pick a take a square centered around the center of this "rectangle"
                self.mouseL[1], self.mouseL[0] = self.squarize(self.mouseL[1], self.mouseL[0])
                self.mouseL[3], self.mouseL[2] = self.squarize(self.mouseL[3], self.mouseL[2], length=DEFAULT_TEMPLATE_SIZE / self.scale)
                self.process()

            x_L, x_R, template, matched = self.template_matching()
            self.distance_1 = self.sc_mod.distance_from_shift(x_R, x_L)

            if min(self.mouseL[0,1], self.mouseL[1,1]) > MAX_TEMPLATE_H + 10:
                self.processed_img = cvp.write_around_box(self.processed_img, f"{self.distance_1:.2f} m",
                                                          self.mouseL[0], self.mouseL[1], (0,0))
            else:
                self.processed_img = cvp.write_around_box(self.processed_img, f"{self.distance_1:.2f} m",
                                                          self.mouseL[0], self.mouseL[1], (0,2))
            template = cvp.homothety(template, MAX_TEMPLATE_W, MAX_TEMPLATE_H)[0]
            matched = cvp.homothety(matched, MAX_TEMPLATE_W, MAX_TEMPLATE_H)[0]
            self.processed_img = cvp.overlay(self.processed_img, template, (10, 10), False, True)
            self.processed_img = cvp.overlay(self.processed_img, matched, (matched.shape[1] + 23, 10), False, True)

        # If the left mouse button is down
        if event == cv.EVENT_RBUTTONUP:
            # We save the fact that the button is not down anymore
            self.left_button_is_down = False
            self.right_button_is_down = False
            
            if np.sum(self.mouseR[0] == self.mouseR[1]) > 0:
                # if the traced rectangle has one of its side with a 0 size, then we instead
                # pick a take a square centered around the center of this "rectangle"
                self.mouseR[1], self.mouseR[0] = self.squarize(self.mouseR[1], self.mouseR[0])
                self.mouseR[3], self.mouseR[2] = self.squarize(self.mouseR[3], self.mouseR[2], length=DEFAULT_TEMPLATE_SIZE / self.scale)
                self.process(mouse_left=False)

            x_L, x_R, template, matched = self.template_matching(False)
            self.distance_2 = self.sc_mod.distance_from_shift(x_R, x_L)
            self.distance_2 = self.sc_mod.dist_2_obj(self.distance_1, self.distance_2, self.center(raw=False, mouse_left=True),
                                                     self.center(raw=False, mouse_left=False))

            if min(self.mouseR[0,1], self.mouseR[1,1]) > MAX_TEMPLATE_H + 10:
                self.processed_img = cvp.write_around_box(self.processed_img, f"{self.distance_2:.3f} m",
                                                          self.mouseR[0], self.mouseR[1], (0,0))
            else:
                self.processed_img = cvp.write_around_box(self.processed_img, f"{self.distance_2:.3f} m",
                                                          self.mouseR[0], self.mouseR[1], (0,2))
            template = cvp.homothety(template, MAX_TEMPLATE_W, MAX_TEMPLATE_H)[0]
            matched = cvp.homothety(matched, MAX_TEMPLATE_W, MAX_TEMPLATE_H)[0]
            self.processed_img = cvp.overlay(self.processed_img, template, (10, 10), False, True)
            self.processed_img = cvp.overlay(self.processed_img, matched, (matched.shape[1] + 23, 10), False, True)

        if event == cv.EVENT_RBUTTONDOWN:
            if self.left_button_clicked_once:
                # raw x and y values, which are the actual x and y values
                # of the mouse, based on the displayed pictures
                self.mouseR[0] = [x, y]
                # converted x and y values, to match the coordinates of the
                # original images
                self.mouseR[2] = (self.mouseR[0] / self.scale).astype(int)
                # We save the location is raw and transformed coordinates
                self.mouseR[1] = [x, y]
                self.mouseR[3] = (self.mouseR[1] / self.scale).astype(int)
                # We save the fact that the button is currently down
                self.right_button_is_down = True
        
        if event == cv.EVENT_MBUTTONDOWN:
            self.left_button_clicked_once = False
            self.processed_img = self.img_L_resized.copy()

    def show(self):
        """
            Image showing loop.
        """
        while cv.waitKey(1) != 27:
            cv.imshow("Left Image", self.processed_img)
        cv.destroyAllWindows()
            
    def template_matching(self, mouse_left=True):
        if mouse_left:
            coord = self.mouseL[2:4].copy()
        else:
            coord = self.mouseR[2:4].copy()
        coord = np.sort(coord, axis=0)
        coord[:,0] = (coord[:,0] * self.sc_mod.x_upscale).astype(int)
        
        template = self.img_L_upscaled[coord[0,1]:coord[1,1],coord[0,0]:coord[1,0]]
        res = cv.matchTemplate(self.img_R_upscaled, template, cv.TM_CCOEFF_NORMED)
        res_loc = cv.minMaxLoc(res)[3]
        x_L = coord[0,0] / self.sc_mod.x_upscale
        x_R = res_loc[0] / self.sc_mod.x_upscale

        res_img = self.img_R_upscaled[res_loc[1]:res_loc[1] + (coord[1,1] - coord[0,1]),
                                      res_loc[0]:res_loc[0] + (coord[1,0] - coord[0,0])]

        template = upscale_width(template, 1.0 / float(self.sc_mod.x_upscale))
        res_img = upscale_width(res_img, 1.0 / float(self.sc_mod.x_upscale))

        return x_L, x_R, template, res_img
    
    def center(self, raw=True, mouse_left=True):
        """
            Gives the center of the current selection.
        """
        if mouse_left:
            if raw:
                return (self.mouseL[0] + self.mouseL[1]) // 2
            return (self.mouseL[2] + self.mouseL[3]) // 2
        if raw:
            return (self.mouseR[0] + self.mouseR[1]) // 2
        return (self.mouseR[2] + self.mouseR[3]) // 2

    def squarize(self, pos1, pos2, length=DEFAULT_TEMPLATE_SIZE):
        """
            Transform a rectangle into a squared of a given length with the same center as the rectangle.
        """
        length = round(length)
        pos1 = (pos1 + pos2) // 2 - length // 2
        pos2 = pos1 + length
        return pos1, pos2

    def process(self, mouse_left=True):
        """
            Processes the processed_img by drawing the cross and highlighting the selected
            area.
        """
        self.processed_img = self.img_L_resized.copy()
        if mouse_left:
            self.processed_img = cvp.draw_cross(self.processed_img, self.center(), 5)
            self.processed_img = cvp.highlight(self.processed_img, self.mouseL[0],
                                            self.mouseL[1], dark_version=self.dark_version)
        else:
            temp_darker = self.dark_version.copy()
            # We draw a line joining the 2 ROI on a temporary dark background and on the foreground
            cv.line(temp_darker, self.center(), self.center(mouse_left=False), color=[255,255,255],
                    thickness=1, lineType=cv.LINE_AA)
            cv.line(self.processed_img, self.center(), self.center(mouse_left=False), color=[0,0,0],
                    thickness=1, lineType=cv.LINE_AA)
            # We draw a cross for each ROI on the foreground
            self.processed_img = cvp.draw_cross(self.processed_img, self.center(mouse_left=False), 5)
            self.processed_img = cvp.draw_cross(self.processed_img, self.center(), 5)
            # Onto the dark background, we highlight the first ROI
            temp_darker = cvp.highlight(self.processed_img, self.mouseR[0],
                                            self.mouseR[1], dark_version=temp_darker)
            # Onto the dark background, we also highlight the 2nd ROI
            self.processed_img = cvp.highlight(self.processed_img, self.mouseL[0],
                                            self.mouseL[1], dark_version=temp_darker)
