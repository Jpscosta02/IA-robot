#!/usr/bin/env pybricks-micropython
# DEFENDER-BOT COM HEURISTICA DE 98% + SLOTS FIXOS

from pybricks.hubs import EV3Brick
from pybricks.ev3devices import Motor, UltrasonicSensor, GyroSensor, ColorSensor
from pybricks.parameters import Port, Color
from pybricks.tools import wait

# ==========================================================
# EV3 SETUP
# ==========================================================
ev3 = EV3Brick()
ev3.speaker.set_volume(100)

mt_ataque = Motor(Port.B)
mt_meio = Motor(Port.C)
mt_garra = Motor(Port.A)

sensor_som = UltrasonicSensor(Port.S1)
gyro = GyroSensor(Port.S3)
color_sensor = ColorSensor(Port.S4)

# ==========================================================
# CONSTANTES
# ==========================================================
VIDA_DEF_MAX = 750
ENERGIA_MAX = 500

vida_defender = VIDA_DEF_MAX
energia = ENERGIA_MAX

ATACANTE_TURNOS = 7
DEFENDER_TURNOS = 6

# ==========================================================
# DADOS DO JOGO
# ==========================================================
ATAQUES_DEF = {
    Color.RED: {"nome": "GRUA", "dano": 200, "custo": 300},
    Color.YELLOW: {"nome": "TOQUE", "dano": 100, "custo": 150},
    Color.GREEN: {"nome": "SOM", "dano": 50, "custo": 50},
}

# Curas
CURAS = {
    1: {"vida": 100, "custo": 200},
    2: {"vida": 200, "custo": 300},
    3: {"vida": 400, "custo": 400},
}

# Unidades atacantes
UNIDADES = {
    "TANQUE": {"cor": Color.RED, "hp": 200, "force": 200, "attacks": 2},
    "ARTILHARIA": {"cor": Color.YELLOW, "hp": 50, "force": 500, "attacks": 1},
    "INFANTARIA": {"cor": Color.GREEN, "hp": 100, "force": 100, "attacks": 3},
}

# Cores válidas
CORES_VALIDAS = (Color.RED, Color.YELLOW, Color.GREEN)
COR_PARA_TIPO = {Color.RED: "TANQUE", Color.YELLOW: "ARTILHARIA", Color.GREEN: "INFANTARIA"}

# Scan 360 parâmetros
TRIGGER_CM = 50
RAW_MAX = 2000
ROT_OFFSET = -6
ROT_SPEED = 140
SAMPLES = 2

inim_detectados = []
slots = [{}, {}, {}, {}, {}, {}]

# Slots (6 slots, 0..5)
SLOT_CENTROS = [15, 75, 135, 195, 255, 315]

# ==========================================================
# FUNÇÕES AUXILIARES FÍSICAS
# ==========================================================

# Normaliza um angulo para o intervalo [0, 360).
def normalizar_angulo(a):
    a = a % 360
    if a < 0:
        a += 360
    return a

# Retorna o indice do slot (1..6) mais proximo do angulo.
def slot_por_angulo(ang):
    ang = normalizar_angulo(ang)
    best_i = 0
    best_d = 9999
    for i, c in enumerate(SLOT_CENTROS):
        d = abs(ang - c)
        d = min(d, 360 - d)
        if d < best_d:
            best_d = d
            best_i = i
    return best_i + 1  # 1..6

# Wrapper de espera para manter chamadas consistentes.
def wait2(ms):
    wait(ms)

# Mede distancia em cm usando mediana das amostras.
def medir_cm():
    vals = []
    for _ in range(SAMPLES):
        d = sensor_som.distance()
        if 0 < d < RAW_MAX:
            vals.append(d / 10)
        wait(10)
    if not vals:
        return float("inf")
    vals.sort()
    return vals[len(vals)//2]

# Espera o comando do utilizador para iniciar o jogo.
def esperar_inicio():
    print("\n" + "="*50)
    print("Slots gerados. Pressiona 'C'/'c' e Enter para comecar.")
    print("="*50)
    while True:
        try:
            entrada = input().strip().lower()
        except Exception:
            entrada = ""
        if entrada == "c":
            ev3.speaker.beep()
            print("Iniciando jogo...")
            break
        else:
            print("Ainda nao recebeu 'C'. Tenta outra vez.")

# Pausa entre rondas e anuncia vida/energia.
def esperar_entre_ronda():
    ev3.speaker.say("Ronda terminada. {} de vida e {} de energia".format(vida_defender, energia))
    print("\n" + "="*50)
    print("Fim da ronda, pressiona 'C'/'c' e Enter para continuar.")
    print("="*50)
    while True:
        try:
            entrada = input().strip().lower()
        except Exception:
            entrada = ""
        if entrada == "c":
            ev3.speaker.beep()
            print("Retomando jogo...")
            break
        else:
            print("Ainda nao recebeu 'C'. Tenta outra vez.")

# Imprime informacao dos slots ativos.
def imprimir_slots(slots):
    print("\n--- SLOTS FIXOS (TESTE) ---")
    for s in slots:
        if s["tipo"] == None:
            continue
        cor_txt = str(s["cor"])
        if hasattr(s["cor"], "name"):
            cor_txt = s["cor"].name
        print("Slot {}: {} | Cor: {} | Turno inicial: {} | Comeca ataque: {} | HP: {}".format(
            s["slot"], s["tipo"], cor_txt, s["turno_inicial"], 
            s["turno_comeca_ataque"], s["hp"]))
    print("--- FIM SLOTS ---\n")

# ==========================================================
# ATAQUES FÍSICOS
# ==========================================================

# Executa o ataque fisico de cor vermelha (grua).
def action_red_sting():
    print(">>> ATTACK: GRUA/STING (Red)")
    ev3.speaker.beep()
    mt_ataque.run_until_stalled(800)
    wait2(500)
    mt_ataque.run_angle(1500, -190)
    wait2(500)
    mt_ataque.run_until_stalled(-2000)

# Executa o ataque fisico de cor amarela (toque).
def action_yellow_touch():
    print(">>> ATTACK: TOUCH (Yellow)")
    mt_garra.run_time(-150, 500)
    wait2(300)
    mt_garra.run_until_stalled(200, duty_limit=50)
    wait2(500)
    mt_garra.run_time(-150, 500)
    wait2(200)

# Executa o ataque sonoro de cor verde.
def action_green_sound():
    print(">>> ATTACK: SOUND (Green)")
    ev3.speaker.play_notes(["C4/8", "E4/8", "G4/8", "C5/8"], tempo=120)
    wait2(500)

# ==========================================================
# ENERGIA
# ==========================================================
# Regenera energia no inicio do turno do defender.
def regen_energia_inicio_turno_defender():
    global energia
    energia = min(ENERGIA_MAX, energia + energia // 2)

# ==========================================================
# HEURÍSTICA 
# ==========================================================
# Retorna True se o item tem o maior numero de ataques restantes.
def is_most_attacks(item, lista):
    most = -1
    res = []
    for i in range(0, len(lista)):
        if lista[i]["attacks_left"] > most:
            most = lista[i]["attacks_left"]
            res = [i]
        elif lista[i]["attacks_left"] == most:
            res.append(i)
    for j in range(0, len(res)):
        if item == lista[res[j]]:
            return True
    return False

# Decide o plano de acoes do defender com base na heuristica.
def decidir_plano_defender_heuristic(slots, atacante_turn_index):
    global energia, vida_defender

    actions = []
    prox_turno = atacante_turn_index + 1

    #Antes de decidir qualquer ação, o agente filtra apenas os inimigos que estão vivos, já entraram no jogo, ainda podem atacar e cuja posição é conhecida. Isto reduz drasticamente o espaço de decisão.
    vivos = [
        s for s in slots
        if s["hp"] > 0 
        and s["turno_inicial"] <= atacante_turn_index 
        and s["attacks_left"] > 0
        and s["ang"] is not None
    ]

    #Se não há inimigos relevantes, o Defender não faz nada.
    if not vivos:
        return []

    artillery = [s for s in vivos if s["tipo"] == 'ARTILHARIA' and s["turno_comeca_ataque"] <= prox_turno]
    tanks = [s for s in vivos if s["tipo"] == 'TANQUE' and s["turno_comeca_ataque"] <= prox_turno]
    infantry = [s for s in vivos if s["tipo"] == 'INFANTARIA' and s["turno_comeca_ataque"] <= prox_turno]

    art = len(artillery)
    tnk = len(tanks)
    inf = len(infantry)
    tot = len(vivos)

    ds = (art, tnk, inf)
    #O vetor ta representa a distribuição desejada de tipos de ataque para este turno, em função da ameaça
    ta = [0, 0, 0]

    if tnk == 0:
        # Caso não existam tanques inimigos, evita-se o uso de ataques caros
        if tot == 0:
            # Nenhuma ameaça ativa
            ta = [0, 0, 0]
        if tot == 1:
            # Um único inimigo leve: ataque mínimo suficiente
            ta = [art, inf, 0]
        elif tot == 2:
            if inf == 0:
                # Dois inimigos frágeis: dois ataques de som
                ta = [2, 0, 0]
            else:
                # Inimigos diferentes: balanceamento de custo e eficácia
                ta = [1, 1, 0]
        elif tot == 3:
            if inf == 0:
                # Três inimigos sem infantaria: ataques fracos suficientes
                ta = [3, 0, 0]
            else:
                # Presença de infantaria: inclui ataque intermédio
                ta = [2, 1, 0]
        else:
            # Muitos inimigos sem tanques: máxima eficiência energética
            ta = [tot, 0, 0]
    elif tnk == 1:
        if tot == 1:
            if energia == 500:
                # Se houver apenas um tanque e a energia for máxima, define que deve ser usado um ataque de grua
                ta = [0, 0, 1]
            elif energia > 300:
                # Se houver apenas um tanque e a energia NÃO for máxima, define que deve ser usado um ataque de toque
                ta = [0, 1, 0]
            else:
                # Se houver apenas um tanque e a energia for menor ou igual a 300, define que deve ser usado um ataque de som
                ta = [1, 0, 0]
        elif tot == 2:
            # Se houver apenas um tanque e mais 1 inimigo divide atenção
            ta = [1, 1, 0]
        elif tot == 3:
            # Se houver apenas um tanque e mais 2 inimigos prioriza múltiplas ameaças
            ta = [2, 1, 0]
        else:
            # Se houver apenas um tanque e mais x inimigos, define que deve ser usado um ataque de som
            ta = [tot, 0, 0]
    elif tnk > 2:
        if tot < 4:
            # Quando há mais de 2 tanques e menos de 4 inimigos totais, define que deve ser usado um ataque de toque e um de som
            ta = [tot - 1, 1, 0]
        else:
            # Quando há mais de 2 tanques e 4 ou mais inimigos, define que deve ser usado um ataque de som a todos
            ta = [tot, 0, 0]

    # asf funciona como um contador que impede que o agente exceda a distribuição planeada de ataques
    asf = [0, 0, 0]

    # ARTILLERY FIRST
    # primeiro eliminar ameaças de alto dano com o menor custo possível
    for art2 in artillery:
        if energia >= 50:
            actions.append((art2, None, Color.GREEN))
            asf[0] = asf[0] + 1

    # INFANTRY
    for inf2 in infantry:
        # Se esta infantaria for das que ainda consegue atacar mais vezes,
        # se o plano permitir ataques de toque e se houver energia suficiente,
        # então o agente prioriza este inimigo
        if is_most_attacks(inf2, infantry) and ta[1] > asf[1] and energia >= 150:
            # se hp da infantaria for igual a 100, então usa ataque de toque
            if inf2["hp"] == 100:
                actions.append((inf2, None, Color.YELLOW))
                asf[1] = asf[1] + 1
            else:
                # se a vida for menor que 100 usa ataque de som
                actions.append((inf2, None, Color.GREEN))
                asf[0] = asf[0] + 1
        # Caso a infantaria não seja considerada prioritária ou já não haja espaço    
        else:
            asf[0] = asf[0] + 1
            actions.append((inf2, None, Color.GREEN))
    
    # TANKS
    for tnk2 in tanks:
        # Se esta unidade for uma das que ainda consegue atacar mais vezes e se o defender ainda puder fazer ataques e se a energia é >=300,
        if is_most_attacks(tnk2, tanks) and ta[2] > asf[2] and energia >= 300:
            # se hp do tanque for igual a 200, então usa ataque de grua
            if tnk2["hp"] == 200:
                actions.append((tnk2, None, Color.RED))
                asf[2] = asf[2] + 1
            # se hp do tanque for menor que 200 e maior que 50, então usa ataque de toque
            elif tnk2["hp"] > 50:
                actions.append((tnk2, None, Color.YELLOW))
                asf[1] = asf[1] + 1
            # se o hp for menor ou igual a 50 faz ataque de som
            else:
                actions.append((tnk2, None, Color.GREEN))
                asf[0] = asf[0] + 1
        # Se a tnk tiver ataques restantes e se o defender ainda puder fazer ataques e se a energia é >=150,
        elif is_most_attacks(tnk2, tanks) and ta[1] > asf[1] and energia >= 150:
            # se hp do tanque for menor que 200 e maior que 50, então usa ataque de toque
            if tnk2["hp"] > 50:
                actions.append((tnk2, None, Color.YELLOW))
                asf[1] = asf[1] + 1
            # se o hp for menor ou igual a 50 faz ataque de som
            else:
                actions.append((tnk2, None, Color.GREEN))
                asf[0] = asf[0] + 1
        # se tiver menos energia faz ataque minimo        
        else:
            actions.append((tnk2, None, Color.GREEN))
            asf[0] = asf[0] + 1
    
    # CURA DE EMERGÊNCIA
    dano_previsto = 0
    for s in vivos:
        if prox_turno >= s["turno_comeca_ataque"] and s["attacks_left"] > 0:
            dano_previsto += int(s["force"] * (s["hp"] / s["hp_max"]))
    
    if vida_defender <= dano_previsto:
        for tier in (3, 2, 1):
            cura = CURAS[tier]
            if energia >= cura["custo"]:
                if vida_defender + cura["vida"] > dano_previsto:
                    actions.append((None, tier, None))
                    break
    
    # Cura opcional
    if vida_defender < 300 and energia >= 400:
        actions.append((None, 3, None))
    
    return actions

# ==========================================================
# SCAN 360 E DETECÇÃO
# ==========================================================
# Varre 360 graus, deteta inimigos e atualiza slots.
def scan360_detect(atacante_turn_index):
    global inim_detectados
    global slots
    inim_detectados = []
    mt_meio.reset_angle(0)
    gyro.reset_angle(0)
    wait2(300)
    mt_meio.run(-ROT_SPEED)

    while True:
        dist = medir_cm()
        if dist <= TRIGGER_CM:
            wait2(30)
            ang = gyro.angle()
            dist2 = medir_cm()
            cor = color_sensor.color()
            if cor in CORES_VALIDAS:
                sg = slot_por_angulo(ang)
                if len(inim_detectados) == 0 or abs(ang - inim_detectados[-1]["ang"]) >= 45:
                    
                    inim_detectados.append({
                        "ang": ang,
                        "dist": dist2,
                        "slot_guess": sg,
                        "cor_detetada": cor
                    })

                    temptipo = COR_PARA_TIPO.get(cor)
                    tempuni = UNIDADES.get(temptipo)

                    if slots[sg-1]["tipo"] is None:
                        slots[sg-1] = {
                            "slot": sg,
                            "tipo": temptipo,
                            "cor": cor,
                            "hp": tempuni["hp"],
                            "hp_max": tempuni["hp"],
                            "force": tempuni["force"],
                            "attacks": tempuni["attacks"],
                            "attacks_left": tempuni["attacks"],
                            "turno_inicial": atacante_turn_index,
                            "turno_comeca_ataque": atacante_turn_index + 1,
                            "ang": None,
                            "dist": None,
                            "_tipo_detetado": None,
                        }

                    print("Detetado: Cor {} | ang: {} | dist: {} | slot: {}".format(cor, ang, dist2, sg))
                    ev3.speaker.beep()
            wait2(10)
        if gyro.angle() >= 360 + ROT_OFFSET:
            break
        wait2(10)
    mt_meio.stop()
    imprimir_slots(slots)
    print("Scan completo, detecções:", len(inim_detectados))
    wait2(250)

# Atualiza ângulo e distância dos slots baseado no scan físico
def atualizar_slots_com_scan(slots, atacante_turn_index):
    # Reset apenas dos slots que já estão em jogo
    for s in slots:
        if s["turno_inicial"] <= atacante_turn_index:
            s["ang"] = None
            s["dist"] = None
            s["_tipo_detetado"] = None
    
    # Fazer scan físico
    scan360_detect(atacante_turn_index)
    
    # Associar deteções aos slots
    for det in inim_detectados:
        s = det["slot_guess"]
        if not (1 <= s <= 6):
            continue
        slot = slots[s-1]
        if slot["turno_inicial"] > atacante_turn_index:
            continue  # Ainda não entrou em jogo
        slot["ang"] = det["ang"]
        slot["dist"] = det["dist"]
        slot["_tipo_detetado"] = COR_PARA_TIPO.get(det["cor_detetada"])

# ==========================================================
# MOVIMENTAÇÃO E EXECUÇÃO
# ==========================================================
# Roda a base ate atingir o angulo alvo.
def mover_para_angulo(target_angle):
    print("Target angle: ",target_angle)
    wait2(100)
    mt_meio.run(-ROT_SPEED)

    while abs(gyro.angle()- target_angle) % 360 > 3:
        wait2(10)
    mt_meio.stop()
    wait2(120)

# Executa o ataque pela cor escolhida e desconta energia.
def executar_ataque_por_cor(cor):
    global energia
    info = ATAQUES_DEF[cor]
    custo = info["custo"]
    if energia < custo:
        print("Energia insuficiente: {} | custo {}".format(energia, custo))
        return False
    energia -= custo
    if cor == Color.RED:
        action_red_sting()
    elif cor == Color.YELLOW:
        action_yellow_touch()
    elif cor == Color.GREEN:
        action_green_sound()
    return True

# Aplica cura ao defender se houver energia suficiente.
def aplicar_cura(cura_tipo):
    global energia, vida_defender
    if cura_tipo is None:
        return False
    ganho = CURAS[cura_tipo]["vida"]
    custo = CURAS[cura_tipo]["custo"]
    if energia < custo:
        return False
    energia -= custo
    vida_defender = min(VIDA_DEF_MAX, vida_defender + ganho)
    print("CURA {}: +{} vida | Vida Defender {} | Energia {}".format(cura_tipo, ganho, vida_defender, energia))
    return True

# Retorna o eixo para o angulo zero aproximado.
def voltar_para_zero():
    print("voltar ao ângulo 0")
    mt_meio.run(-ROT_SPEED if gyro.angle() > 0 else -ROT_SPEED)
    
    while abs(gyro.angle()) % 360 > 2:
        wait2(10)
    mt_meio.stop()
    wait2(150)

# ==========================================================
# TURNOS
# ==========================================================
# Processa ataques do atacante e atualiza vida do defender.
def turno_atacante(slots, atacante_turn_index):
    global vida_defender
    print("\n=== Turno ATACANTE {} ===".format(atacante_turn_index))
    
    total_dano = 0
    for inimigo in slots:
        if inimigo["hp"] <= 0:
            continue
        if atacante_turn_index < inimigo["turno_comeca_ataque"]:
            continue
        if inimigo["attacks_left"] <= 0:
            continue
        
        dano = int(inimigo["force"] * (inimigo["hp"] / inimigo["hp_max"]))
        vida_defender -= dano
        total_dano += dano
        inimigo["attacks_left"] -= 1
        
        print("{} (Slot {}) causa {} dano".format(inimigo["tipo"], inimigo["slot"], dano))
    
    print("Dano total: {} | Vida Defender: {}".format(total_dano, vida_defender))

# Processa turno do defender: regen, scan, ataque e cura.
def turno_defender(slots, def_index, atacante_turn_index):
    global energia, vida_defender

    print("\n=== Turno DEFENDER {} ===".format(def_index))
    
    regen_energia_inicio_turno_defender()
    print("Energia após regen: {}".format(energia))

    atualizar_slots_com_scan(slots, atacante_turn_index)

    plano_acoes = decidir_plano_defender_heuristic(slots, atacante_turn_index)

    if not plano_acoes:
        print("Nenhuma ação possível")
        return

    fez_cura = False

    for acto in plano_acoes:
        alvo = acto[0]
        cura_tipo = acto[1]
        cor_ataque = acto[2]
        if alvo and cor_ataque:
            print(">>> Atacando Slot {} ({}) com {}".format(alvo["slot"], alvo["tipo"], ATAQUES_DEF[cor_ataque]["nome"]))
            mover_para_angulo(alvo["ang"])
            if executar_ataque_por_cor(cor_ataque):
                dano = ATAQUES_DEF[cor_ataque]["dano"]
                alvo["hp"] = max(0, alvo["hp"] - dano)
                print("Dano: {} | HP inimigo: {}".format(dano, alvo["hp"]))
        
        if cura_tipo and not fez_cura:
            if aplicar_cura(cura_tipo):
                print("O robot realizou uma cura")
                fez_cura = True

    print("Energia final: {} | Vida Defender: {}".format(energia, vida_defender))
    voltar_para_zero()
# ==========================================================
# MAIN
# ==========================================================
# Ponto de entrada principal do jogo.
def main():
    global vida_defender, energia, slots
    
    print("\n" + "="*60)
    print("DEFENDER-BOT COM HEURÍSTICA DE 98% + SLOTS FIXOS")
    print("="*60)
    
    for i in range(0,6):
        slots[i]["hp"] = -1
        slots[i]["turno_inicial"] = 999
        slots[i]["tipo"] = None
    
    esperar_inicio()
    
    # JOGO
    for turno in range(1, ATACANTE_TURNOS + 1):
        turno_atacante(slots, turno)
        
        if vida_defender <= 0:
            print("❌ DERROTA")
            ev3.speaker.say("Defender Perdeu no turno {}".format(turno))
            ev3.speaker.play_notes(["C2/4", "C1/4"])
            break
            
        if turno <= DEFENDER_TURNOS:
            if turno > 1:
                esperar_entre_ronda()
            turno_defender(slots, turno, turno)
            
            if all(s["hp"] <= 0 for s in slots):
                print("nenhum inimigo disponível")
    
    print("\n" + "="*60)
    if vida_defender > 0:
        ev3.speaker.say("Vitory")
        ev3.speaker.play_notes(["C5/4", "E5/4", "G5/4", "C6/4"])
        print("✅ SOBREVIVEU! Vida final: {}".format(vida_defender))
    print("="*60)

if __name__ == "__main__":
    main()
