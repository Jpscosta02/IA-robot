#!/usr/bin/env pybricks-micropython

from pybricks.hubs import EV3Brick
from pybricks.ev3devices import (Motor, TouchSensor, ColorSensor, UltrasonicSensor)
from pybricks.parameters import Port
from pybricks.tools import wait


mt_ataque = Motor(Port.B)


# Inicialização do EV3
ev3 = EV3Brick()

def ataque() -> None:
    ev3.speaker.beep()
    mt_ataque.run_until_stalled(800)      
    wait(500)             
    mt_ataque.run_angle(1500,-190)   
    wait(500)          
    mt_ataque.run_until_stalled(-2000)
    ev3.speaker.beep()

def atacar(n:int ) -> None:
    
    if(n <= 0 ):
        return

    for i in range(n):
        ataque()

    



