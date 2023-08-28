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

motors_config = {
    'base' : {'channel' : 0, 'min_position' : 6000, 'max_position': 9500},
    'shoulder' : {'channel' : 1, 'min_position' : 5500, 'max_position': 10000},
    'elbow' : {'channel' : 2, 'min_position' : 3000, 'max_position': 8000}
}

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
        pca.channels[self.channel].duty_cycle = int((self.min_position+self.max_position)/2)
        print('Init', self.channel)
        sleep(3) #Pour que les moteurs s'initient 1 par 1
        pca.channels[self.channel].duty_cycle = 0
        self.current_position = (self.min_position+self.max_position)/2
       
    async def goTo(self,target, speed = 1):
        print('{} go to {}'.format(self.channel, target) )
        try:
            for p in range_2ways(int(self.current_position), target): 
                #print(p)
                pca.channels[self.channel].duty_cycle = p
                await asyncio.sleep(0.001)
        except asyncio.CancelledError:
            print('Mouvement annulé en route !', self.channel) # Si le mouvement est arrếté
        finally:
            pca.channels[self.channel].duty_cycle = 0
            print('{} is now {} ({})'.format(self.channel,  p, self.current_position - target) )
            self.current_position = p


base = stepMotor(**motors_config['base'])
shoulder = stepMotor(**motors_config['shoulder'])
elbow = stepMotor(**motors_config['elbow'])

async def main():
    while True :
        asyncio.create_task(base.goTo(6200)) # Annuler toute autre tache qui concerne ce moteur !
        asyncio.create_task(shoulder.goTo(7000))
        asyncio.create_task(elbow.goTo(7000))
        await asyncio.sleep(15)
        asyncio.create_task(base.goTo(9000)) # Annuler toute autre tache qui concerne ce moteur !
        asyncio.create_task(shoulder.goTo(9000))
        asyncio.create_task(elbow.goTo(4000))
        await asyncio.sleep(15)


asyncio.run(main())



