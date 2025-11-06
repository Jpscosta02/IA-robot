#!/usr/bin/env pybricks-micropython

from pybricks.hubs import EV3Brick
from pybricks.ev3devices import (Motor, TouchSensor, ColorSensor, UltrasonicSensor)
from pybricks.parameters import Port
from pybricks.tools import wait


mt_ataque = Motor(Port.B)


# Inicialização do EV3
ev3 = EV3Brick()

def ataque() -> None:

    """
    1. Dá um sinal sonoro.
    2. Roda o motor para a tras até encontrar resistência (stall).
    3. Espera 500 ms.
    4. Roda ate deixar a bola cair.
    5. Espera mais 500 ms.
    6. Roda para atacar ate econtrar resistencia.
    7. Dá outro sinal sonoro para indicar o fim do ataque.
    """
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

    



