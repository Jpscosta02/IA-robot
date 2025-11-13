#!/usr/bin/env pybricks-micropython

from pybricks.hubs import EV3Brick
from pybricks.ev3devices import Motor, UltrasonicSensor, GyroSensor
from pybricks.parameters import Port
from pybricks.tools import wait

ev3 = EV3Brick()

mt_ataque = Motor(Port.B)
mt_meio = Motor(Port.C)
sensor_som = UltrasonicSensor(Port.S3)
gyro = GyroSensor(Port.S1)

TRIGGER_CM = 60
RAW_MAX = 2000
ROT_SPEED = 150
SAMPLES = 2

def ataque():
    ev3.speaker.beep()
    mt_ataque.run_until_stalled(800)
    wait(500)
    mt_ataque.run_angle(1500, -190)
    wait(500)
    mt_ataque.run_until_stalled(-2000)
    return

def medir_cm():
    vals = []
    for _ in range(SAMPLES):
        d = sensor_som.distance()
        if 0 < d < RAW_MAX:
            vals.append(d/10)
        wait(10)
    if not vals:
        return float('inf')
    vals.sort()
    return vals[len(vals)//2]

def scan360():
    print("⟳ Scan 360° com evasão do inimigo…")

    gyro.reset_angle(0)
    wait(300)

    total_rot = 0
    last_angle = gyro.angle()

    mt_meio.run(-ROT_SPEED)

    while True:

        ang_atual = gyro.angle()
        delta = ang_atual - last_angle
        last_angle = ang_atual

        total_rot += abs(delta)

        dist = medir_cm()
        print("Rot:", round(total_rot), "Dist:", dist, "cm")
        wait(300)
        # --- DETETAR INIMIGO ---
        if dist <= TRIGGER_CM:
            print("⚠️ INIMIGO ENCONTRADO —", dist, "cm")

            # 1) parar
            mt_meio.stop()
            ataque()
            ev3.speaker.beep()
            wait(300)

            # 2) fazer avanço artificial de 20 graus
            ang_before = gyro.angle()
            mt_meio.run_angle(250, -115, wait=True)
            ang_after = gyro.angle()

            # 3) somar avanço ao total
            total_rot += abs(ang_after - ang_before)

            # 4) atualizar last_angle
            last_angle = ang_after

            # 5) continuar a rodar
            mt_meio.run(-ROT_SPEED)

        # --- FINALIZAR 360° ---
        if total_rot >= 360:
            print("✔ Scan completo de 360°!")
            break

        wait(40)

    mt_meio.stop()
    ev3.speaker.beep()

scan360()
