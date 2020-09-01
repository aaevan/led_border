from time import sleep
import serial
from random import randint

def main():
    ser = serial.Serial('/dev/ttyUSB0', 57600) # Establish the connection on a specific port
    counter = 0
    led_index = 0
    while True:
        counter += 1
        led_index = (led_index + 1) % 50
        rand_nums = [randint(0, 255) for _ in range(3)]
        joined_nums = ','.join([str(val) for val in rand_nums])
        #comma_separated = '{},{}\n'.format(led_index, joined_nums)
        comma_separated = '{}\n'.format(joined_nums)
        print(comma_separated)
        ser.write(comma_separated.encode()) # Convert the decimal number to ASCII then send it to the Arduino
        #print(counter, "|", rand_nums)
        #print(ser.readline()) # Read the newest output from the Arduino
        sleep(1 / 60) # Delay for one tenth of a second
        #print(counter)
        counter %= 255

main()
