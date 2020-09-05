#!/usr/bin/env python

# Adapted from the xlib example from
# https://blog.wizardsoftheweb.pro/quickly-detect-cursor-position-and-color/#caveats

from os import getenv
from time import sleep
from random import randint
from math import sqrt

from Xlib.display import Display
from Xlib.X import ZPixmap

# Pull display from environment
DISPLAY_NUM = getenv('DISPLAY')
# Activate discovered display (or default)
DISPLAY = Display(DISPLAY_NUM)
# Specify the display's screen for convenience
SCREEN = DISPLAY.screen()
# Specify the base element
ROOT = SCREEN.root
# Store width and height
ROOT_GEOMETRY = ROOT.get_geometry()
# Ensure we can run this
EXTENSION_INFO = DISPLAY.query_extension('XInputExtension')

def get_mouse_location():
    return ROOT.query_pointer()

def get_rgb_of_pixel(coords=(0, 0)):
    """
    TODO: check whether taking a larger area and sampling
          from there is faster than taking many 1x1 screenshots
    """
    # create an X dump at the coordinate we want
    DISPLAY_IMAGE = ROOT.get_image(
        x=coords[0],
        y=coords[1],
        width=1,
        height=1,
        format=ZPixmap,
        plane_mask=int("0xFFFFFF", 16)
    )
    # strip its color info
    PIXEL = getattr(DISPLAY_IMAGE, 'data').hex()
    # pick out just the relevant hex digits
    red = PIXEL[4:6] 
    green = PIXEL[2:4]
    blue = PIXEL[0:2]
    # convert from hex to int
    r, g, b = [int(val, 16) for val in (red, green, blue)]
    return (r, g, b)    

def linear_distance(coord_a=(0, 0), coord_b=(10, 10)):
    x1, y1, x2, y2 = *coord_a, *coord_b
    rise, run = x2 - x1, y2 - y1
    distance = sqrt(((x2 - x1) ** 2) + ((y2 - y1) ** 2))
    return distance

def min_spaced_samples(
    n_samples=10, 
    min_distance=25, #tuned to a width and height of 100
    origin_coord=(0, 0), 
    width=100, 
    height=100,
    max_fail_count=1000,
):
    output_samples = []
    x1, y1, x2, y2 = (
        *origin_coord, 
        origin_coord[0] + width,
        origin_coord[1] + height,
    )
    fails = 0
    while len(output_samples) < n_samples:
        new_point = [randint(x1, x2), randint(y1, y2)]
        valid = False
        if output_samples == []:
            output_samples.append(new_point)
        for point in output_samples:
            if fails >= max_fail_count:
                print("min_spaced_samples failed out")
                return
            distance = linear_distance(coord_a=new_point, coord_b=point)
            if distance < min_distance:
                valid = False
                fails += 1
                break
            else:
                valid = True
        if valid:
            output_samples.append(new_point)
    if fails > 1000:
        print("fails:", fails)
    return output_samples

def fixed_samples_from_border_coords(
    border_coords,
    n_samples=10,
    sample_width=100,
    sample_height=100,
    edge_buffer=2,#pixels
):
    fixed_samples = []
    for coord in border_coords:
        x1, y1 = coord
        x2, y2 = (
            (x1 + sample_width) - edge_buffer, 
            (y1 + sample_height) - edge_buffer,
        )
        sample_coords = [rand_coord_in_rect(x1, y1, x2, y2) for _ in range(n_samples)]
        fixed_samples.append(sample_coords)
    return fixed_samples

def take_n_samples_from_rect(
    top_left_coord=(0, 0),
    n_samples=10, 
    sample_width=100,
    sample_height=100,
    edge_buffer=2,#pixels
    fixed_samples=None
):
    x1, y1 = top_left_coord
    x2, y2 = (
        (x1 + sample_width) - edge_buffer, 
        (y1 + sample_height) - edge_buffer,
    )
    if fixed_samples is not None:
        coords = fixed_samples
    else:
        coords = [rand_coord_in_rect(x1, y1, x2, y2) for _ in range(n_samples)]
    rgb_samples = [get_rgb_of_pixel(coords=coord) for coord in coords]
    return rgb_samples

def mean_rgb_from_samples(samples):
    r_sum, g_sum, b_sum = 0, 0, 0
    for sample in samples:
        r_val, g_val, b_val = sample
        r_sum += r_val
        g_val += g_val
        b_val += b_val
    r_mean, g_mean, b_mean = [val // len(samples) for val in (r_sum, g_val, b_val)]
    return [r_mean, g_mean, b_mean]

def rand_coord_in_rect(x1, y1, x2, y2):
    x = randint(x1, x2)
    y = randint(y1, y2)
    return (x, y)

def get_edge_sample_coords(
    width = 1600,
    height = 900,
    sample_width = 100, 
    num_horiz_cells = 7,
    num_vert_cells = 5,
    debug=False,
):
    """
    the coordinates assume we're using the top left coordinate of a square that
    is sample_width high and sample_width tall.

    a coord of (0, 0) implies a sample to be taken from a box with top left 
    coord (0, 0) and bottom right coord of (100, 100)
         1>>2>>3>>4>>5
        +--------------+
     ^18|□  □  □  □  □ | 6 v
     ^17|□           □ | 7 v
     ^16|□           □ | 8 v
     ^15|□  □  □  □  □ | 9 v
        +--------------+
         14<13<12<11<10

    returns a list of top-left coordinates for each box.
    (the above sample uses a num_horiz_cells of 5 and a num_vert_cells of 4)
    """
    #trim off the last values, those squares would extend off the screen
    top_edge_x_vals = list(range(0, width, width // num_horiz_cells))
    right_edge_y_vals = list(range(0, height, height // num_vert_cells))
    if len(top_edge_x_vals) > num_horiz_cells:
        top_edge_x_vals = top_edge_x_vals[:-1]
    for index, edge_coord in enumerate(top_edge_x_vals):
        if (edge_coord + sample_width) > width:
            top_edge_x_vals[index] = width - sample_width
    if len(right_edge_y_vals) > num_vert_cells:
        right_edge_y_vals = right_edge_y_vals[:-1]
    for index, edge_coord in enumerate(right_edge_y_vals):
        if (edge_coord + sample_width) > height:
            right_edge_y_vals[index] = height - sample_width
    bottom_edge_x_vals = top_edge_x_vals[::-1] #reverse order
    left_edge_y_vals = right_edge_y_vals[::-1] #reverse order
    top_edge_coords = [(x_val, 0) for x_val in top_edge_x_vals]
    right_edge_coords = [(width - sample_width, y_val) for y_val in right_edge_y_vals]
    bottom_edge_coords = [(x_val, height - sample_width) for x_val in bottom_edge_x_vals]
    left_edge_coords = [(0, y_val) for y_val in left_edge_y_vals]
    if debug:
        print("top:", top_edge_coords)
        print("right:", right_edge_coords)
        print("bottom:", bottom_edge_coords)
        print("left:", left_edge_coords)
    output_coord_list = top_edge_coords + right_edge_coords + bottom_edge_coords + left_edge_coords
    return output_coord_list
