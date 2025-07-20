from time import sleep
import asyncio
from lib.micropython_pca9685 import PCA9685
from machine import I2C, Pin

# Create the I2C bus interface.
i2c_bus = I2C(0, scl=Pin(22), sda=Pin(21))
# Create a simple PCA9685 class instance.
pca = PCA9685(i2c_bus, address=0x40)
pca.frequency = 60

MIN = 6000
MAX = 9500

motors_config = {
    'base' : {'channel' : 0, 'min_position' : 6000, 'max_position': 9500},
    'shoulder' : {'channel' : 1, 'min_position' : 5500, 'max_position': 10000},
    'elbow' : {'channel' : 2, 'min_position' : 3000, 'max_position': 8000},
    'wrist' : {'channel': 3, 'min_position' : 5000, 'max_position': 10000},
    'clamp': {'channel': 4, 'min_position': 7500, 'max_position': 10000}

}


def range_2ways(start,stop, rge):
    return range(start, stop, rge if start < stop else -1*rge)


class StepMotor:
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
        p = self.current_position
        if target > self.max_position or target < self.min_position :
            print('{} is out of range <{},{}>'.format(target, self.min_position, self.max_position))
            target = min(max(self.min_position, target), self.max_position)
        print('{} go to {}'.format(self.channel, target) )
        await self.lock.acquire()
        try:
            for p in range_2ways(int(self.current_position), int(target), 2):
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

    def blocking_goto(self, target, speed = 1):
        #async def _run():
        #    await self.goTo(target, speed)
        try:
            loop.run_until_complete(self.goTo(target, speed))
        except Exception as e:
            print("Erreur pendant le mouvement :", e)


    def goToMin(self):
        return self.goTo(self.min_position)

    def goToMax(self):
        return self.goTo(self.max_position)

class Motion:
    """A motion is a combinaition of motor motion to reach a position"""
    def __init__(self):
        self.lock = asyncio.Lock()
        self.moves = list() # Si plusieurs fois le même moteur, les déplacements ne sont pas effectué simultanément (grâce au lock sur la la class Motor). TODO : Empêcher d'avoir plusieurs fois le même moteur ?
        self.loop = asyncio.get_event_loop()
    def append(self, task):
        self.moves.append(task)

    async def go_async(self):
        tasks = [asyncio.create_task(m) for m in self.moves]
        await asyncio.gather(*tasks)
        self.moves = list()

    def go(self):
        self.loop.run_until_complete(self.go_async())

    def input(self, stepmotor):
        print("Tape 'a'=up, 'z'=down, 'q'=quit")
        while True:
            try:
                key = input("> ").strip().lower()
            except KeyboardInterrupt:
                print("Interrompu.")
                break

            if key == 'a':
                self.append(stepmotor.goTo(stepmotor.current_position + 100))
                self.go()
            elif key == 'z':
                self.append(stepmotor.goTo(stepmotor.current_position - 100))
                self.go()
            elif key == 'q':
                print("Sortie.")
                break
            else:
                print("Inconnu.")


class Arm:
    def __init__(self):
        self.motion = Motion()
        self.motor = dict(
            base = StepMotor(**motors_config['base']),
            shoulder = StepMotor(**motors_config['shoulder']),
            elbow = StepMotor(**motors_config['elbow']),
            wrist=StepMotor(**motors_config['wrist']),
            clamp = StepMotor(**motors_config['clamp'])
        )



