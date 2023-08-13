
from board import SCL, SDA
from time import sleep
import busio

# Import the PCA9685 module.
from adafruit_pca9685 import PCA9685

# Create the I2C bus interface.
i2c_bus = busio.I2C(SCL, SDA)

# Create a simple PCA9685 class instance.
pca = PCA9685(i2c_bus)



MIN = 5500
MAX = 10000

def servoGoTo(id_channel, position):
    pca.channels[id_channel].duty_cycle = position
    sleep(1)
    pca.channels[id_channel].duty_cycle = 0
