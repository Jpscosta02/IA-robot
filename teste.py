#!/usr/bin/env pybricks-micropython

from pybricks.hubs import EV3Brick
from pybricks.ev3devices import Motor, UltrasonicSensor, GyroSensor, ColorSensor
from pybricks.parameters import Port, Color
from pybricks.tools import wait

ev3 = EV3Brick()
ev3.speaker.set_volume(100)  # maximum volume (0–100)

mt_ataque = Motor(Port.B)
mt_meio = Motor(Port.C)
mt_garra = Motor(Port.A)
sensor_som = UltrasonicSensor(Port.S1)
gyro = GyroSensor(Port.S3)
color_sensor = ColorSensor(Port.S4)

TRIGGER_CM = 60
RAW_MAX = 2000
ROT_SPEED = 110
SAMPLES = 2

inimigos_detectados = []


# ========== ATTACK ROUTINE ==========
def ataque():
    ev3.speaker.beep()
    mt_ataque.run_until_stalled(800)
    wait(500)
    mt_ataque.run_angle(1500, -190)
    wait(500)
    mt_ataque.run_until_stalled(-2000)
    return


# ========== DISTANCE MEASUREMENT ==========
def medir_cm():
    vals = []
    for _ in range(SAMPLES):
        d = sensor_som.distance()
        if 0 < d < RAW_MAX:
            vals.append(d / 10)
        wait(10)
    if not vals:
        return float('inf')
    vals.sort()
    return vals[len(vals) // 2]




# ========== COLOR CONFIRM LOGIC (MULTICOLOR) ==========
def confirm_enemy_color():
    """
    Move forward slowly and check color.
    Detects RED, GREEN, YELLOW or BLUE.
    Announces type of attack and returns True for attack().
    """

    # --- TABELA DE INIMIGOS ---
    inimigo_frases = {
        Color.RED:    "Hey, it's a tank!",
        Color.GREEN:  "Hey, it's a soldier!",
        Color.YELLOW: "Hey, it's an artillery!",
        Color.BLUE:   "Hey, it's a sniper!"
    }

    # --- Função auxiliar para anunciar e gravar ---
    def processar_inimigo(cor):
        inimigos_detectados.append(inimigo_frases[cor])
        ev3.speaker.say(inimigo_frases[cor])
        return True

    # =========================
    # 1) PRIMEIRA LEITURA
    # =========================
    mt_meio.run(120)
    wait(350)
    mt_meio.stop()
    wait(150)

    detected = color_sensor.color()
    print("Color 1st check:", detected)

    if detected in inimigo_frases:
        return processar_inimigo(detected)


    # =========================
    # 2) SEGUNDA LEITURA
    # =========================
    print("⚠ Cor nao detetada, fazendo 2 movimento...")
    mt_meio.run(110)
    wait(300)
    mt_meio.stop()

    detected2 = color_sensor.color()
    print("Color 2nd check:", detected2)

    if detected2 in inimigo_frases:
        return processar_inimigo(detected2)

    return False


def alinhar_garra ():
    mt_garra.run_until_stalled(-300)
    wait(300)
    if confirm_enemy_color():
        ataque()
    else:
        print("Continuar scan…")
    wait(300)
    mt_garra.run_angle(300, 110)
    mt_garra.stop()


# ========== 360° SCAN ==========
def scan360():
    print("⟳ Scan 360° com evasão do inimigo…")
    mt_ataque.reset_angle(0)
    mt_meio.reset_angle(0)
    mt_garra.reset_angle(0)
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

        # --- DETECT OBJECT ---
        if dist <= TRIGGER_CM:
            wait(400)

            print("⚠️ OBJECT DETECTED at", dist, "cm")
            mt_meio.stop()
            wait(200)

            # ✔ Move forward and confirm color
            alinhar_garra()

            # 2) fazer avanço artificial de 20 graus
            ang_before = gyro.angle()
            mt_meio.run_angle(200, -200, wait=True)
            ang_after = gyro.angle()

            # 3) somar avanço ao total
            total_rot += abs(ang_after - ang_before)

            # 4) atualizar last_angle
            last_angle = ang_after

            # 5) continuar a rodar
            mt_meio.run(-ROT_SPEED)

        # --- FINALIZAR 360° ---
        if total_rot >= 310:
            print("✔ Scan completo de 360°!")
            break

        wait(40)

    mt_meio.stop()
    ev3.speaker.beep()
    print("Inimigos detectados:", inimigos_detectados)



# ========== RUN SCAN ==========
# 1) virar ligeiramente à esquerda
scan360()



'''
#!/usr/bin/env pybricks-micropython

from pybricks.hubs import EV3Brick
from pybricks.ev3devices import Motor, UltrasonicSensor, GyroSensor, ColorSensor
from pybricks.parameters import Port, Color
from pybricks.tools import wait

ev3 = EV3Brick()

mt_ataque = Motor(Port.B)
mt_meio = Motor(Port.C)
sensor_som = UltrasonicSensor(Port.S3)
gyro = GyroSensor(Port.S2)
color_sensor = ColorSensor(Port.S4)     # <-- NEW

TRIGGER_CM = 60
RAW_MAX = 1000
ROT_SPEED = 60

SAMPLES = 2

# ========== ATTACK ROUTINE ==========

def ataque():
    ev3.speaker.beep()
    mt_ataque.run_until_stalled(800)
    wait(500)
    mt_ataque.run_angle(1500, -190)
    wait(500)
    mt_ataque.run_until_stalled(-2000)
    return



# ========== MEDIR DISTÂNCIA ==========
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

# ========== COLOR CONFIRM LOGIC ==========
def confirm_enemy_color():
    """
    Move forward slowly and check color.
    If not red, move a bit more and check again.
    """

    # --- First slow move ---
    mt_meio.run(70)       # slow speed
    wait(350)
    mt_meio.stop()

    detected = color_sensor.color()
    print("Color 1st check:", detected)

    if detected == Color.RED:
        print("✔ Enemy confirmed on first check!")
        return True

    # --- Second slow move (extra chance to detect red) ---
    print("⚠ Not red, doing second slow move...")
    mt_meio.run(60)       # even slower
    wait(300)
    mt_meio.stop()

    detected2 = color_sensor.color()
    print("Color 2nd check:", detected2)

    if detected2 == Color.RED:
        print("✔ Enemy confirmed on second check!")
        return True

    # --- Still not red ---
    print("✖ Not red. Enemy ignored.")
    return False

# ========== MAIN SCAN FUNCTION ==========
def scan360():
    print("⟳ Scan 360° with color confirmation…")

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
        wait(200)

        # --- DETECT OBJECT ---
        if dist <= TRIGGER_CM:
            print("⚠️ OBJECT DETECTED at", dist, "cm")
            mt_meio.stop()
            wait(200)

            # ✔ Move forward and confirm with color
            if confirm_enemy_color():
                ataque()
            else:
                print("Continuing scan…")

            # Add artificial rotation
            ang_before = gyro.angle()
            mt_meio.run_angle(60, -110, wait=True)
            ang_after = gyro.angle()

            total_rot += abs(ang_after - ang_before)
            last_angle = ang_after

            mt_meio.run(-ROT_SPEED)

        # --- FINISH 360° ---
        if total_rot >= 360:
            print("✔ Scan complete!")
            break

        wait(40)

    mt_meio.stop()
    ev3.speaker.beep()

scan360()
'''
'''
#pedro code for 360 turn

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
'''