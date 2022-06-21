"""
    Made by Victor Chemin @c_victor_astro
    21 June 2022
    
    Module to compute distances from a stereo camera. The class stores important informations
    such as the focal length, the distance between the cameras, etc. and then uses them to
    make the calculations.
"""

import numpy as np
import cv2 as cv

import percy_default_param as pdp

def upscale_width(pic, x_upscale):
        new_width = int(pic.shape[1] * x_upscale)
        height = pic.shape[0]
        return cv.resize(pic, (new_width, height), interpolation=cv.INTER_CUBIC)

def rotate_image(image, angle):
    # https://stackoverflow.com/questions/9041681/opencv-python-rotate-image-by-x-degrees-around-specific-point
    image_center = tuple(np.array(image.shape[1::-1]) / 2)
    rot_mat = cv.getRotationMatrix2D(image_center, angle, 1.0)
    result = cv.warpAffine(image, rot_mat, image.shape[1::-1], flags=cv.INTER_CUBIC)
    return result

class StereoCam:
    def __init__(self, toe_in_angle = None, pixel_size = None, stereo_dist = None, focal_length = None,
                 down_sampling = 1., left_cam = None, right_cam = None, x_upscale = 1):
        """
            Initialize the parameters of the stereo camera. If a parameter is missing, the default parameters
            for the Mastcam of Perseverance will be set.
        """
        self.toe_in_angle = pdp.TOE_IN_ANGLE if toe_in_angle is None else toe_in_angle
        self.pixel_size = pdp.PIXEL_SIZE if pixel_size is None else pixel_size
        self.stereo_dist = pdp.STEREO_DISTANCE if stereo_dist is None else stereo_dist
        self.focal_length = focal_length
        self.down_sampling = down_sampling
        self.left_cam = left_cam
        self.right_cam = right_cam
        self.file_name = None
        self.x_upscale = x_upscale
        if left_cam is not None and right_cam is not None:
            self.load_pics(left_cam, right_cam)
        elif left_cam is not None:
            self.load_both_from_one(left_cam)
        elif right_cam is not None:
            self.load_both_from_one(right_cam)

    def load_pics(self, left_cam, right_cam, percy_mastcam = True):
        """
            Loads left and right pics based on the FULL paths of the files.
        """
        self.name = left_cam
        self.left_cam = cv.imread(left_cam)
        self.right_cam = cv.imread(right_cam)
        if self.left_cam is None or self.right_cam is None or self.left_cam.size == 0 or self.right_cam.size == 0:
            if self.left_cam is None or self.left_cam.size == 0:
                print("Could not read left image.")
            if self.right_cam is None or self.right_cam.size == 0:
                print("Could not read right image.")
            self.name = None
            self.left_cam = None
            self.right_cam = None
            return -1
        if percy_mastcam:
            self.right_cam = rotate_image(self.right_cam, -pdp.RIGHT_SENSOR_ANGLE)
            self.guess_focal_length()
        self.left_cam_upscaled = upscale_width(self.left_cam, self.x_upscale)
        self.right_cam_upscaled = upscale_width(self.right_cam, self.x_upscale)
        return 0

    def load_both_from_one(self, cam, cam_type = "Mastcam"):
        """
            Loads left and right Mastcam from Perseverance pics based on the FULL path of one of the files.
            Files names must not be altered.
            cam_type argument is not used yet.
        """
        
        folder_path = cam[:cam.rfind("/")+1]
        file_name = cam[cam.rfind("/")+1:]

        if "ZR" not in file_name and "ZL" not in file_name:
            print("File name has been altered. ZL and/or ZR are missing.")
            return -2
        
        other_cam = file_name.replace("ZR", "ZL") if "ZR" in file_name else file_name.replace("ZL", "ZR")
        other_cam = folder_path + other_cam

        if "ZR" in file_name:
            cam, other_cam = other_cam, cam

        if self.load_pics(cam, other_cam) != 0:
            return -1

        self.name = file_name
        return 0

    def guess_focal_length(self):
        """
            Guess the focal length of the Mastcam based on the filename.
        """
        if self.name is not None:
            idx = self.name.rfind("_") + 1
            self.focal_length = float(self.name[idx:idx+3]) * 1e-3
            self.down_sampling = 2.0**float(self.name[idx+3])

    def distance_from_shift(self, x_right, x_left):
        """
            Gives the distance of a feature based on the shift in pixels between the two pictures.
        """
        dx = x_right - x_left
        dx = 2.0 * self.focal_length * self.toe_in_angle / (self.pixel_size * self.down_sampling) - dx
        distance = self.stereo_dist * self.focal_length / (dx * self.pixel_size * self.down_sampling)
        if distance < 0:
            distance = np.Infinity
        return distance

    def dist_2_obj(self, dist_1, dist_2, pos_1, pos_2):
        res = np.sqrt((pos_2[1] - pos_1[1])**2 + (pos_2[0] - pos_1[0])**2)
        res *= (self.pixel_size * self.down_sampling) / self.focal_length
        return np.sqrt(dist_1**2 + dist_2**2 - 2*dist_1 * dist_2 * np.cos(res))
