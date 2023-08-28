from time import sleep
import asyncio
from adafruit_pca9685 import PCA9685
import busio
from board import SCL, SDA
# Create the I2C bus interface.
i2c_bus = busio.I2C(SCL, SDA)

# Create a simple PCA9685 class instance.
pca = PCA9685(i2c_bus)
pca.frequency = 60

MIN = 6000
MAX = 9500


def range_2ways(start,stop):
    return range(start, stop, 1 if start < stop else -1)

class stepMotor():
    def __init__(self,channel, min_position = MIN, max_position = MAX):
        self.min_position = min_position
        self.max_position = max_position
        self.current_position = None
        self.channel = channel
        self.initMotor()
    
    def initMotor(self):
        """centrale position"""
        print((self.min_position+self.max_position)/2)
        sleep(1)
        print(0)
        self.current_position = (self.min_position+self.max_position)/2
       
    async def goTo(self,target, speed = 1):
        print('target : ',target)
        try:
            for p in range_2ways(int(self.current_position), target): 
                #print(p)
                pca.channels[self.channel].duty_cycle = p
                await asyncio.sleep(0.001)
            print('Mouvement terminé {}, déplacement de {}'.format(self.channel, self.current_position - target) )
        except asyncio.CancelledError:
            print('Mouvement annulé en route !') # Si le mouvement est arrếté
        finally:
            self.current_position = p
            pca.channels[self.channel].duty_cycle = 0
            print(0) # Si le mouvement est annulé avant la fin ou terminé, on coupe le moteur.


base = stepMotor(0)
epaule = stepMotor(1)

async def main():
    while True :
        task = asyncio.create_task(base.goTo(6200)) # Annuler toute autre tache qui concerne ce moteur !
        task2 = asyncio.create_task(epaule.goTo(8500))
        await asyncio.sleep(15)


asyncio.run(main())



