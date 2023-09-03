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

def range_2ways(start,stop, rge):
    return range(start, stop, rge if start < stop else -1*rge)

class stepMotor():
    def __init__(self,channel, min_position = MIN, max_position = MAX):
        self.min_position = min_position
        self.max_position = max_position
        self.current_position = None
        self.channel = channel
        self.initMotor()
        self.lock = asyncio.Lock()
    
    def initMotor(self):
        """centrale position"""
        pca.channels[self.channel].duty_cycle = int((self.min_position+self.max_position)/2)
        print('Init', self.channel)
        sleep(1.5) #Pour que les moteurs s'initient 1 par 1
        pca.channels[self.channel].duty_cycle = 0
        self.current_position = (self.min_position+self.max_position)/2
    
    
    async def goTo(self,target, speed = 1):
        if target > self.max_position or target < self.min_position :
            print('{} is out of range <{},{}>'.format(target, self.min_position, self.max_position))
            target = min(max(self.min_position, target), self.max_position)
        print('{} go to {}'.format(self.channel, target) )
        await self.lock.acquire()
        try:
            for p in range_2ways(int(self.current_position), target, 2): 
                #print(p)
                pca.channels[self.channel].duty_cycle = p
                await asyncio.sleep(0.001)
        except asyncio.CancelledError:
            print('Mouvement annulé en route !', self.channel) # Si le mouvement est arrếté
        finally:
            pca.channels[self.channel].duty_cycle = 0
            print('{} is now {} ({})'.format(self.channel,  p, self.current_position - target) )
            self.current_position = p
            self.lock.release()

class Motion():
    """A motion is a combinaition of motor motion to reach a position"""
    def __init__(self):
        self.lock = asyncio.Lock()
        self.moves = list() # Si plusieurs fois le même moteur, les déplacements ne sont pas effectué simultanément (grâce au lock sur la la class Motor). TODO : Empêcher d'avoir plusieurs fois le même moteur ?
        
    async def go(self):
        tasks = [asyncio.create_task(m) for m in self.moves]
        await asyncio.gather(*tasks)
        self.moves = list()

class Arm():
    def __init__(self):
        self.motion = Motion()
        self.motor = dict(
            base = stepMotor(**motors_config['base']),
            shoulder = stepMotor(**motors_config['shoulder']),
            elbow = stepMotor(**motors_config['elbow'])
        )

if __name__ == "__main__":

    arm = Arm()

    arm.motion.moves.append(arm.motor['base'].goTo(10000))
    arm.motion.moves.append(arm.motor['shoulder'].goTo(7000))
    arm.motion.moves.append(arm.motor['base'].goTo(7000))

    asyncio.get_event_loop().run_until_complete(arm.motion.go())


