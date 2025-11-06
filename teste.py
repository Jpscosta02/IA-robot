#!/usr/bin/env pybricks-micropython

from pybricks.hubs import EV3Brick
from pybricks.ev3devices import (Motor, TouchSensor, ColorSensor, UltrasonicSensor)
from pybricks.parameters import Port
from pybricks.tools import wait


mt_ataque = Motor(Port.B)


# Inicialização do EV3
ev3 = EV3Brick()
def ataque():
    ev3.speaker.beep()
    # Motores
    mt_ataque.run_until_stalled(800)            # espera 1 segundo
    wait(500)             # espera 1 segundo
    mt_ataque.run_angle(1500,-190)    # roda continuamente
    wait(500)             # espera 1 segundo
    mt_ataque.run_until_stalled(-2000)  
    return 

for i in range(4): #4 balls to attack 
    ataque()

