#!/usr/bin/env pybricks-micropython

from pybricks.hubs import EV3Brick
from pybricks.ev3devices import Motor, TouchSensor, UltrasonicSensor
from pybricks.parameters import Port
from pybricks.tools import wait

# Inicialização do EV3
ev3 = EV3Brick()

# Motores e sensores
mt_ataque = Motor(Port.B)
mt_garra = Motor(Port.A)
mt_meio = Motor(Port.C)
sensor_toque = TouchSensor(Port.S1)
sensor_som = UltrasonicSensor(Port.S3)

def ataque():
    ev3.speaker.beep()
    mt_ataque.run_until_stalled(800)
    wait(500)
    mt_ataque.run_angle(1500, -190)
    wait(500)
    mt_ataque.run_until_stalled(-2000)
    return


def motor_ativo(motor):
    """Retorna True se o motor estiver em movimento, False se estiver parado."""
    angulo_anterior = motor.angle()
    wait(100)  # espera 0.1 segundos
    angulo_atual = motor.angle()
    return angulo_anterior != angulo_atual

def som():
    print("🔄 A rodar e a medir distâncias (em mm)...\n")

    # Guardar o ângulo inicial
    ang_inicial = mt_meio.angle()

    # Iniciar movimento (sentido negativo, 10000 graus) sem bloquear
    mt_meio.run_angle(-100, 10000, wait=False)

    mt_ativo = True

    # Enquanto o motor não atingir o destino
    while abs(mt_meio.angle() - ang_inicial and mt_ativo) < 10000:
        
        distancia = sensor_som.distance()  # devolve em milímetros

        # Converter para cm só uma vez (não duas!)
        distancia_cm = distancia / 10


        # Verifica a distância
        if (distancia_cm < 60):  # 5 cm = 50 mm
            print("🚨 Objeto detetado a", distancia_cm, "cm — a atacar!")
            wait(800)
            mt_ativo = False
            mt_meio.stop()   # parar o movimento
            ataque()         # chamar a função de ataque
            break
        else:
            ev3.speaker.beep()
        
        wait(200)  # lê a cada 0.2 segundos

    # Parar o motor no fim (garantia extra)
    mt_meio.stop()
    print("\n✅ Movimento concluído.")
    ev3.speaker.beep()

som()

'''
def toque():
    # Movimento da garra para dentro
    mt_garra.run(-1000)
    print("A aguardar que o sensor de toque seja pressionado...")

    # Espera até o sensor ser pressionado
    while not sensor_toque.pressed():
        wait(10)  # pequena pausa para não sobrecarregar o processador

    # Quando for pressionado:
    mt_garra.stop()  # para o motor
    ev3.speaker.beep()
    print("✅ Sensor de toque a funcionar!")

# Exemplo de uso
toque()
'''






#Funcionamento do Jogo
'''
import random
enemybase = []
enemybase = enemybase + [{"type":"None","power":0,"hits":0,"maxhp":99999,"hp":99999,"turn":999}]
enemybase = enemybase + [{"type":"Tank","power":200,"hits":2,"maxhp":200,"hp":200,"turn":0}]
enemybase = enemybase + [{"type":"Infantry","power":100,"hits":3,"maxhp":100,"hp":100,"turn":0}]
enemybase = enemybase + [{"type":"Artillery","power":300,"hits":1,"maxhp":50,"hp":50,"turn":0}]

attackCost = [50,150,300]
attackPower = [50,100,200]
healCost = [200,300,400]
healAmount = [100,200,400]

turncount = 1
wins = 0
losses = 0


#robot = {"maxhp":750.0,"hp":750.0,"energy":500.0,"maxenergy":500.0,"canattack":[True,True,True,True,True,True],"canheal":True}

slots = [{},{},{},{},{},{}]

def newEnemy2(enemyType,turn):
    newEnemy = enemybase[enemyType]
    newEnemy["turn"] = turn
    return newEnemy

def newEnemy(enemyType,power,hits,maxhp,hp,turn):
    newEnemy = {}
    newEnemy["hp"] = enemyType
    newEnemy["type"] = enemyType
    newEnemy["hits"] = hits
    newEnemy["maxhp"] = maxhp
    newEnemy["turn"] = turn
    newEnemy["hp"] = hp
    newEnemy["power"] = power
    return newEnemy

def damageEnemy(enemy,amount):
    
    
    
    if enemy["hp"] <= amount:
        enemy = enemybase[0]
    else:
        enemy = newEnemy(enemy["type"],enemy["power"],enemy["hits"],enemy["maxhp"],enemy["hp"]-amount,enemy["turn"])
    return enemy

def decEnemyHits(enemy):
    enemy = newEnemy(enemy["type"],enemy["power"],enemy["hits"]-1,enemy["maxhp"],enemy["hp"],enemy["turn"])
    return enemy


def initSlots():
    
    for i in range(0,len(slots)):
        slots[i] = enemybase[0]
    return



def printRobot():
    #print(robot)
    print(f'HP: {robot["hp"]}')
    print(f'Energy: {robot["energy"]}')
    return

def damageRobot(amount):
    robot["hp"] = min(robot["hp"] - amount,robot["maxhp"]);
    #printRobot()
    if robot["hp"] <= 0:
        killRobot()
        return
    else:
        return
    
def killRobot():
    global keepgoing
    global losses
    if keepgoing:
        losses += 1
        keepgoing = False
        
        print("Defeat!")
        print(f'Losses: {losses}')
    
    return


def damageSlot(slot,amount):
    
    #print(f'Attacked slot index {slot}')
    #slots[slot] = {}
    slots[slot] = damageEnemy(slots[slot],amount)
    
    robot["canattack"][slot] = False
    return

def doEnemyAttack(enemy):
    damageRobot(enemy["power"]*enemy["hp"]/enemy["maxhp"])
    #enemy["hits"] = enemy["hits"]
    return

def createEnemy(slot,enemytype,turn):
    slots[slot] = newEnemy2(enemytype,turn)
    return

def printEnemy(enemy):
    print(f'Type: {enemy["type"]}')
    print(f'HP: {enemy["hp"]}')
    print(f'Hits Left: {enemy["hits"]}')
    return

def printEnemySimple(enemy,slotno,turnNo):
    
    if enemy["type"] != "None" and enemy["turn"] <= turnNo:
        print(f'{slotno+1}: {enemy["type"]} [{enemy["hp"]}/{enemy["maxhp"]}] - {enemy["hits"]};')
    else:
        print(f'{slotno+1}: None')
    
    return

def printSlots(turnNo):
    
    for i in range(0,len(slots)):
        printEnemySimple(slots[i],i,turnNo)
        #print(slots[i])
    return

def doEnemyTurn(turnNo):
    
    for i in range(0,len(slots)):
        if slots[i]["type"] != "None" and turnNo >= slots[i]["turn"] and slots[i]["hits"] > 0:
            
            doEnemyAttack(slots[i])
            slots[i] = decEnemyHits(slots[i])
        
    return

def doAttackMenu(turnNo):
    
    while True:
        print("Attack where?")
        printSlots(turnNo)
        print("X - Cancel")
        slotNo = input("")
        if slotNo == "X" or slotNo == "":
            return
        slotNo = int(slotNo)
        #print(slots)
        if slots[slotNo-1]["type"] == "None" or slots[slotNo-1]["turn"] > turnNo:
            print("Can't attack an empty slot!")
        else:
            print("Which attack?")
            print(f'1: Sound - {attackCost[0]} Energy')
            print(f'2: Contact - {attackCost[1]} Energy')
            print(f'3: Crane - {attackCost[2]} Energy')
            print("X - Cancel")
            print("")
            print(f'You have: {robot["energy"]} Energy')
            print(f'{slotNo}')
            
            attackType = input("")
            if attackType == "X" or attackType == "" or attackType == "x":
                return               
            attackType = int(attackType)
                     
            

            if robot["energy"] < attackCost[attackType-1]:
                print("Insufficient energy.")
                continue
            else:
                if robot["canattack"][slotNo-1]:
                    
                    damageSlot(slotNo-1,attackPower[attackType-1])
                    robot["energy"] -= attackCost[attackType-1]
                    break
                else:
                    print("Can't attack a slot twice in one turn!")
           

            
                   
            
            
    
    
    return

def doHealMenu(turnNo):
    while True:
        print("Select heal amount")
        print(f'Heal 1 - +{healAmount[0]} HP - {healCost[0]} Energy')
        print(f'Heal 2 - +{healAmount[1]} HP - {healCost[1]} Energy')
        print(f'Heal 3 - +{healAmount[2]} HP - {healCost[2]} Energy')
        print(f'X - Cancel')
        
        healType = input("")
        if healType == "1":
            if robot["energy"] >= healCost[0]:
                robot["energy"] -= healCost[0]
                damageRobot((-1)*healAmount[0])
                robot["canheal"] = False
                break
            else:
                print("Insufficient Energy.")
                continue
            
        if healType == "2":
            if robot["energy"] >= healCost[1]:
                robot["energy"] -= healCost[1]
                damageRobot((-1)*healAmount[1])
                robot["canheal"] = False
                break
            else:
                print("Insufficient Energy.")
                continue
        if healType == "3":
            if robot["energy"] >= healCost[2]:
                robot["energy"] -= healCost[2]
                damageRobot((-1)*healAmount[2])
                robot["canheal"] = False
                break
            else:
                print("Insufficient Energy.")
                continue    
        if healType == "X":
            return
        print("Invalid option")        
    
        
    

def doBaseMenu(turnNo): 
    global turncount
    global keepgoing
    global wins
    global losses
    print("Enemy Forces:")
    print("")
    printSlots(turnNo)
    print("")
    #print("Robot Status:")
    #print("")
    printRobot()
    print("")
    print("What will Defender-Bot do?")
    print("1 - Attack")
    print("2 - Heal")
    print("X - End Turn")
    print("Z - Surrender")
    print("")
    val = input("")
    if val == "1":
        doAttackMenu(turnNo)
        printSlots(turnNo)
    if val == "2":
        if robot["canheal"]:
            if robot["hp"] < robot["maxhp"]:
                doHealMenu(turnNo)
            else:
                print("Defender-Bot is at full health!")
        else:
            print("Defender-Bot has already healed this turn!")
    if val == "Z":
        print("Defeat!")
        losses += 1
        return False
    if val == "X":
        doEnemyTurn(turncount)
        robot["energy"] = min([robot["energy"]*1.5,robot["maxenergy"]])
        robot["canheal"] = True
        for i in range(0,6):
            robot["canattack"][i] = True
        turncount = turncount + 1
        if turncount == 8:
            if keepgoing:
                print("Victory!")
                wins += 1
                print(f'Wins: {wins}')
            keepgoing = False
        
        return keepgoing
    print("Invalid Option")
    return keepgoing
    
def randomiseEnemies():
    for i in range(0,6):
        createEnemy(i,random.randint(1,3),random.randint(1,6))
    return

def setScenario():
    createEnemy(0,1,1)
    createEnemy(1,1,1)
    createEnemy(2,1,1)
    createEnemy(3,2,6)
    createEnemy(4,2,6)
    createEnemy(5,2,6)
    return



print(turncount)
while True:
    turncount = 1
    turncount = 1
    keepgoing = True    
    initSlots()
    randomiseEnemies()
    #setScenario()
    
    robot = {"maxhp":750.0,"hp":750.0,"energy":500.0,"maxenergy":500.0,"canattack":[True,True,True,True,True,True],"canheal":True}
    
    while doBaseMenu(turncount):
        pass
'''