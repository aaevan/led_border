from time import sleep
import serial
from random import randint, choice
from xlib_dropper import *
from find_corners import *

def rand_rgb(ceiling=50):
    return [randint(0, ceiling) for _ in range(3)]

def get_opposite_color(rgb_tuple):
    red, green, blue = [255 - val for val in rgb_tuple]
    return [red, green, blue]

def main():
    #TODO: auto scan USB ports and fail gracefully if no device connected
    ser = serial.Serial('/dev/ttyUSB0', 57600) # Establish the connection on a specific port
    screen_name = "VGA1"
    top_left, width, height = find_corners(screen_name=screen_name)
    print(screen_name, top_left, width, height)
    x_offset, y_offset = top_left
    print("width of {} is {}".format(screen_name, width))
    print("height of {} is {}".format(screen_name, height))
    border_coords = get_edge_sample_coords(
        width=width, 
        height=height,
        x_offset=x_offset,
        y_offset=y_offset,
        num_horiz_cells=15,
        num_vert_cells=10,
    )
    print("border_coords:\n", border_coords)
    fixed_samples = fixed_samples_from_border_coords(border_coords)
    print("fixed_samples:\n", '\n'.join([str(sample) for sample in fixed_samples]))
    while True:
        rand_index = randint(0, len(border_coords) - 1)
        rand_sample = fixed_samples[rand_index]
        rgb_sample_values = get_values_from_fixed_sample(rand_sample)
        rand_cell_rgb = mean_rgb_from_samples(rgb_sample_values)
        joined_nums = ','.join([str(val) for val in rand_cell_rgb])
        comma_separated = '{},{}\n'.format(rand_index, joined_nums)
        print("comma_separated:", comma_separated)
        print(comma_separated)
        ser.write(comma_separated.encode()) 
        sleep(1 / 100) 

if __name__ == "__main__":
    main()
