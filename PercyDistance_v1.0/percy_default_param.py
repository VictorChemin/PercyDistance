"""
    Made by Victor Chemin @c_victor_astro
    21 June 2022

    Default parameters of the Perseverance's Mastcam.
"""

from numpy import pi

## ALL MEASURES IN RADIANS AND METERS

# Angle between the line of sight of a camera and the normal vector
# of the plane on which both cameras are. A positive angle means the
# cameras point towards the "inside", and a negative angle means they
# point towards the "outside".
TOE_IN_ANGLE = 1.1705 / 180. * pi

# Size of a pixel on the sensor.
PIXEL_SIZE = 7.4e-6

# Distance between the two cameras.
STEREO_DISTANCE = 24.3e-2

# Sensor rotation error (the right camera is rotated by 0.81° anti-clockwise,
# so the right image needs a 0.85° clockwise correction)
RIGHT_SENSOR_ANGLE = 0.85
