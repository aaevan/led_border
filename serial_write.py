from time import sleep
import serial
from random import randint, choice
from xlib_dropper import *

def rand_rgb(ceiling=50):
    return [randint(0, ceiling) for _ in range(3)]

def main():
    ser = serial.Serial('/dev/ttyUSB0', 57600) # Establish the connection on a specific port
    counter = 0
    led_index = 0
    border_coords = get_edge_sample_coords(
        num_horiz_cells=15,
        num_vert_cells=10,
    )
    print("border_coords:\n", border_coords)
    print("len(border_coords):", len(border_coords))
    rand_cell = choice(border_coords)
    print("rand_cell:", rand_cell)
    rand_cell_rgb = mean_rgb_from_samples(take_n_samples_from_rect(rand_cell))
    print("rand_cell_rgb:", rand_cell_rgb)
    while True:
        #dummy_data = [rand_rgb() for _ in range(3)]
        #counter = (counter + 1) % 50
        counter = randint(0, 49)
        #rand_led_index = randint(0, 49);
        print("rand_led_index:", counter)
        rand_cell = border_coords[counter]
        print("rand_cell:", rand_cell)
        rand_cell_rgb = mean_rgb_from_samples(take_n_samples_from_rect(rand_cell))
        if rand_cell_rgb[0] <= 50:
            rand_cell_rgb[0] = 0
        print("rand_cell_rgb:", rand_cell_rgb)
        #rand_nums = [randint(0, 50) for _ in range(3)]
        joined_nums = ','.join([str(val) for val in rand_cell_rgb])
        comma_separated = '{},{}\n'.format(counter, joined_nums)
        print("comma_separated:", comma_separated)
        #comma_separated = '{}\n'.format(joined_nums)
        print(comma_separated)
        """
        samples work fine, not it's a matter of feeding in a bunch of rgb values 
        over serial. This might require batching the new values into smaller chunks.
        It's easy to generate a set of samples, feeding 50 3 digit tuples over serial sounds like a bad plan.
        some kind of basic compression? calculate rgb distance and, if under a certain threshold, don't change
        the pixel?
        """
        ser.write(comma_separated.encode()) # Convert the decimal number to ASCII then send it to the Arduino
        sleep(1 / 250) # Delay for one tenth of a second

main()
