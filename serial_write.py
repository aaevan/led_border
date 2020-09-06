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
    #TODO: incorporate using fixed samples (and uniformly spaced points among smaples)
    fixed_samples = fixed_samples_from_border_coords(border_coords)
    print("fixed_samples:\n", '\n'.join([str(sample) for sample in fixed_samples]))
    while True:
        rand_index = randint(0, len(border_coords) - 1)
        rand_sample = fixed_samples[rand_index]
        rgb_sample_values = get_values_from_fixed_sample(rand_sample)
        rand_cell_rgb = mean_rgb_from_samples(rgb_sample_values)
        #if rand_cell_rgb[0] <= 50: #zero out low values of the red component
            #rand_cell_rgb[0] = 0
        print("rand_cell_rgb:", rand_cell_rgb)
        joined_nums = ','.join([str(val) for val in rand_cell_rgb])
        comma_separated = '{},{}\n'.format(rand_index, joined_nums)
        print("comma_separated:", comma_separated)
        print(comma_separated)
        """
        samples work fine, not it's a matter of feeding in a bunch of rgb values 
        over serial. This might require batching the new values into smaller chunks.
        It's easy to generate a set of samples, feeding 50 3 digit tuples over serial sounds like a bad plan.
        some kind of basic compression? calculate rgb distance and, if under a certain threshold, don't change
        the pixel?
        """
        ser.write(comma_separated.encode()) # Convert the decimal number to ASCII then send it to the Arduino
        #sleep(1 / 250) # Delay for one tenth of a second
        #sleep(1 / 100) # Delay for one tenth of a second
        sleep(.05) # Delay for one tenth of a second

if __name__ == "__main__":
    main()

#TODO: remove print statements and other uncecessary slowdowns
#TODO:
#write a function that generates a list of n points that are all at least a
#certain distance from all other points.
#create an empty list and add a point
#while the list is less than desired length,
#pick a random point
#if that random point is closer than min_distance for any point already in points
#break
#if fails > ... 500? (a large number?), fail loudly.
#it should be possible to pick a number that's small enough that unsolveable 
#point combos are rare/impossible
