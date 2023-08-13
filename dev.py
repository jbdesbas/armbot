# dev sur desktop

from time import sleep
import asyncio


MIN = 6000
MAX = 9500


class stepMotor():
    def __init__(self,channel, min_position = MIN, max_position = MAX):
        self.min_position = min_position
        self.max_position = max_position
        self.current_position = None
        self.initMotor()
    
    def initMotor(self):
        """centrale position"""
        print((self.min_position+self.max_position)/2)
        sleep(1)
        print(0)
        self.current_position = (self.min_position+self.max_position)/2
       
    async def goTo(self,target, speed = 1):
        try:
            for p in range(int(self.current_position), target):
                print(p)
                await asyncio.sleep(0.01)
            print('Mouvement terminé, déplacement de {}'.format(self.current_position - target) )
        except asyncio.CancelledError:
            print('Mouvement annulé en route !') # Si le mouvement est arrếté
        finally:
            self.current_position = p
            print(0) # Si le mouvement est annulé avant la fin ou terminé, on coupe le moteur.


motor = stepMotor(0)

async def main():
    while True :
        await asyncio.sleep(5)
        task = asyncio.create_task(motor.goTo(8000)) # Annuler toute autre tache qui concerne ce moteur !


asyncio.run(main())

"""
import threading
toto='debut'
def termine():
    toto='fin'

def main():
    print('Hello ...')
    sleep(3)
    print('... World!')
    termine()


t1 = threading.Thread(target=main)
t2 = threading.Thread(target=main)

t1.start()
t2.start()

while True :
    print(toto)
    sleep(0.5)
    
   
@asyncio.coroutine
def stepper():
    for e in range(0,100):
        print(e)
        sleep(0.02) 
    
"""

