from time import sleep
import serial
from random import randint, shuffle
from xlib_dropper import *
from find_corners import *
from itertools import cycle

def rand_rgb(ceiling=50):
    return [randint(0, ceiling) for _ in range(3)]

def get_opposite_color(rgb_tuple):
    red, green, blue = [255 - val for val in rgb_tuple]
    return [red, green, blue]

def main(debug=False):
    #TODO: auto scan USB ports and fail gracefully if no device connected
    num_leds = 50
    ser = serial.Serial('/dev/ttyUSB0', 115200) # Establish the connection on a specific port
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
    fixed_ordering = [i for i in range(num_leds)]
    shuffle(fixed_ordering)
    fixed_ordering_cycle = cycle(fixed_ordering)
    print("running...")
    while True:
        rand_index = next(fixed_ordering_cycle)
        rand_sample = fixed_samples[rand_index]
        rgb_sample_values = get_values_from_fixed_sample(rand_sample)
        rand_cell_rgb = mean_rgb_from_samples(rgb_sample_values)
        #zero out small values
        if sum(rand_cell_rgb) < 10:
            rand_cell_rgb = [0, 0, 0]
        joined_nums = ','.join([str(val) for val in rand_cell_rgb])
        comma_separated = '{},{}\n'.format(rand_index, joined_nums)
        if debug:
            print("comma_separated:", comma_separated.rstrip())
        ser.write(comma_separated.encode()) 
        sleep(1 / 300) 

if __name__ == "__main__":
    main()
