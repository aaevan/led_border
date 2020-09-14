from time import sleep
import serial
from random import randint, shuffle
from get_samples import *
from find_corners import *
from itertools import cycle

def rand_rgb(ceiling=50):
    return [randint(0, ceiling) for _ in range(3)]

def get_opposite_color(rgb_tuple):
    red, green, blue = [255 - val for val in rgb_tuple]
    return [red, green, blue]

def interpolate_rgb(
    origin_rgb=[0, 0, 0], 
    dest_rgb=[255, 255, 255],
    fade_ratio=.75,
):
    r1, g1, b1 = origin_rgb
    r2, g2, b2 = dest_rgb
    r_diff, g_diff, b_diff = [
        round((r2 - r1) * fade_ratio),
        round((g2 - g1) * fade_ratio),
        round((b2 - b1) * fade_ratio),
    ]
    return [r1 + r_diff, g1 + g_diff, b1 + b_diff]

def init_brightness_map(
    num_cells=255,
    #tuned to hit 255 exactly at index 255 with a small dead zone:
    multiplier=1.022055709,
    start_val=1
):
    arr = []
    val = start_val
    for i in range(num_cells):
        arr.append(val)
        val *= multiplier
    return [round(val) for val in arr]

def scale_by_brightest(
    rgb_value=(200, 100, 50),
    brightness_map=init_brightness_map(),
):
    max_val = max(rgb_value)
    if max_val == 0:
        return rgb_value
    scaled_max_val = brightness_map[max_val - 1]
    scaling_factor = scaled_max_val / max_val
    output_rgb = [int(val * scaling_factor) for val in rgb_value]
    return output_rgb


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
    last_set = [[0, 0, 0] for i in range(num_leds)]
    dest_rgb = last_set[::]
    brightness_map = init_brightness_map()
    print("len brightness_map: ", len(brightness_map))
    while True:
        led_index = next(fixed_ordering_cycle)
        rand_sample = fixed_samples[led_index]
        rgb_sample_values = get_values_from_fixed_sample(rand_sample)
        mean_rgb = mean_rgb_from_samples(rgb_sample_values)
        dest_rgb[led_index] = mean_rgb
        current_val = last_set[led_index]
        dest_val = dest_rgb[led_index]
        new_val = interpolate_rgb(current_val, dest_val, fade_ratio=.9)
        last_set[led_index] = new_val
        #apply a non-linear brightness map:
        #new_val = [brightness_map[val - 1] for val in new_val] #TODO: fix strange hyper-saturated colors
        new_val = scale_by_brightest(new_val, brightness_map)
        #TODO: fix inverted colors??
        #zero out small values
        if sum(new_val) < 10:
            new_val = [0, 0, 0]
        joined_nums = ','.join([str(val) for val in new_val])
        comma_separated = '{},{}\n'.format(led_index, joined_nums)
        if debug:
            print("comma_separated:", comma_separated.rstrip())
        ser.write(comma_separated.encode()) 
        sleep(1 / 300) 

if __name__ == "__main__":
    main()
