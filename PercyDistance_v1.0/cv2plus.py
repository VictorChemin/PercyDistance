"""
    Made by Victor Chemin @c_victor_astro
    21 June 2022
    
    Module to extend opencv functions. For exemple, a resize function which keeps the aspect ratio.
"""
from math import ceil
import numpy as np
import cv2 as cv

def homothety(img, wmax, hmax):
    """
        Resizes a picture by keeping the aspect-ratio and keeping
        the width below wmax and the height below hmax.
        Returns the resized image and the factor by which it was
        resized.
    """
    h, w = img.shape[:2]
    factor = min(hmax / h, wmax / w)
    h, w = ceil(factor * h), ceil(factor * w)
    return cv.resize(img, (w, h), interpolation=cv.INTER_CUBIC), factor

def highlight(img,  pt1, pt2, dark_factor = 0.3, dark_version = None):
    """
        Highlights a rectangular part of an image, between point pt1 and
        point pt2, by darkening the rest of the picture (RGB values
        multiplied by dark_factor).

        In the case of the repeated use of this function on the same
        image, it would be ideal to provide the dark_version of the image.
        If so, the darkening of the picture wouldn't be done inside the
        function and the argument dark_factor wouldn't be used.
    """
    if dark_version is None:
        dark_version = (img * dark_factor).astype(np.uint8)
    x1, x2 = min([pt1[0], pt2[0]]), max([pt1[0], pt2[0]])
    y1, y2 = min([pt1[1], pt2[1]]), max([pt1[1], pt2[1]])
    darker_copy = dark_version.copy()
    darker_copy[y1:y2,x1:x2] = img[y1:y2,x1:x2]
    return darker_copy

FONT_FACE = cv.FONT_HERSHEY_DUPLEX
FONT_SCALE = 0.5
FONT_THICKNESS = 1
OFFSET = 7

def write_around_box(img, text, pt1, pt2, align=(0,0), color=[255,255,255], font_face=FONT_FACE,
                     font_scale=FONT_SCALE, font_thickness=FONT_THICKNESS, offset=OFFSET):
    """
        Writes text above or below a given rectangle, with text aligned
        either on the left or the right of the rectangle.

        align[0] : 0 is left, 1 is center, 2 is right
        align[1] : 0 is down, 1 is center, 2 is down
    """
    img = img.copy()
    text_half_size = cv.getTextSize(text, font_face, font_scale, font_thickness)[0]
    dx = (abs(pt2[0] - pt1[0]) - text_half_size[0]) / 2
    dy = (abs(pt2[1] - pt1[1]) + text_half_size[1]) / 2 + offset
    x = min(pt1[0], pt2[0]) + round(dx * align[0])
    y = min(pt1[1], pt2[1]) + round(dy * align[1]) - offset

    cv.putText(img, text, (int(x), int(y)), font_face, font_scale,
                color, font_thickness, cv.LINE_AA)
    
    return img

def draw_cross(img, center, half_length, color=[0,0,0], thickness=1):
    """
        Draws a cross centered on center. Each branch has a length
        of half_length.
    """
    res = img.copy()
    cv.line(res, (center[0] - half_length, center[1]), (center[0] + half_length, center[1]),
                    color=color, thickness=thickness, lineType=cv.LINE_AA)
    cv.line(res, (center[0], center[1] - half_length), (center[0], center[1] + half_length),
                    color=color, thickness=thickness, lineType=cv.LINE_AA)
    return res

def overlay(under, over, pos, border=False, shadow=False, shadow_shift=5):
    """
        Overlays a smaller image (over) on another larger image (under), optionnaly
        adding a shadow and a border.
    """
    x, y = pos
    under = under.copy()
    # Creates a shadow if asked
    if shadow:
        under[shadow_shift + y:over.shape[0] + shadow_shift + y,
              shadow_shift + x:over.shape[1] + shadow_shift + x] //= 2
    # Overlays the over-image over the under-image
    under[y:(over.shape[0] + y),x:(over.shape[1] + x)] = over
    # Creates a border if asked
    if border:
        cv.rectangle(under, (x, y), (over.shape[1] + x, over.shape[0] + y),
                     color=[0,0,0], thickness = 1, lineType=cv.LINE_AA)
    return under
