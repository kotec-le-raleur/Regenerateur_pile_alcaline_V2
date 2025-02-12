#  version 3 sans les fonctions PWM sur les commandes de charge
#  24 mars 2024


import machine
from machine import SPI,Pin, PWM, UART
import utime
from st7735 import TFT
import sysfont
import neopixel
import math
import sys
from fonctions import *

my_uart = UART(0, baudrate=115200, tx=Pin(0), rx=Pin(1))
my_uart.init(bits=8, parity=None, stop=2)
snum = "  "

analog_value = machine.ADC(machine.Pin(28))  

# valeurs lues directement dans le fichier Piles.ini
V_R4 = 0
V_R3 = 0
V_R2 = 0
V_R1 = 0
Ecart_H = 1.00   
Ecart_L = 1.00   # 5 % en moins
ListParam = []
VP1 = 0
VP2 = 0
Vcc = 3.300  #  par defaut 
OFFSET_P1  = 340
OFFSET_P2  = 340

# Color definitions pour la diode WS2812
W_BLACK   = (0, 0, 0)
W_WHITE   = (160, 160, 160)
W_RED     = (128, 0, 0)
W_GREEN   = (0, 128, 0)
W_BLUE    = (0, 0, 128)
W_YELLOW  = (128, 90, 0)
W_MAGENTA = (100, 0, 100)
W_CYAN    = (0, 255, 255)
W_GREY    = (20,20,20)

# DEBUG = True   # remplace le test sur la tension par une commande clavier du REPL
DEBUG = False  # lecture des interrupteurs sur la carte

#  Zone de test par petits appels unitaires
#-----------------------------------------------------


#  moyenne sur 16 mesures espaces de 1 mS
def GetTension():   
    Vin = 0
    Nx = 8
    for x in range (0,Nx,1):
        Vin  = (analog_value.read_u16())  + Vin    
        utime.sleep_ms(1)
    return (int(Vin /Nx) - OFFSET)
    
 
# renvoi le numero du bouton sur un appui  prend environ 17 mS
def  GetButton():
     Vx=GetTension() 
     if Vx < 1000:
         Vx2=GetTension()  # deuxième lecture 
         if Vx2 < 1000 :         
             return 0   # on a bien rien ==> return 0
            
     Vx=GetTension() 
     if Vx > 4000:
         utime.sleep_ms(10)  # attente de la stabilisation
         Vx = GetTension()   # deuxième lecture 
         if Vx >  4000 :         
             if ((Vx < V_R4*Ecart_H)  and (Vx > V_R4*Ecart_L)):
                 return 4
             elif ((Vx < V_R3*Ecart_H) and (Vx > V_R3*Ecart_L)):
                 return 3
             elif ((Vx < V_R2*Ecart_H) and (Vx > V_R2*Ecart_L)):
                 return 2
             elif ((Vx < V_R1*Ecart_H) and (Vx > V_R1*Ecart_L)):
                 return 1
             else:         # valeur inconnue 
                 return 5
     
#  test GetButton()
def Test_GetButton():
    while True:
        Btn1 = GetButton()
        return Btn1
      
# -----------   Ouvrir le fichier en mode lecture  ---------------
def Parse_Ligne (Lg):
    
    global V_R1, V_R2, V_R3,V_R4
    global Ecart_H, Ecart_L, Vcc
    global OFFSET, OFFSET_P1, OFFSET_P2
    
    print("parsing", Lg)
    valeurs = Lg.split(';')
    sVal = valeurs[0]
    if sVal == "V_R1" :
        V_R1 = int(valeurs[1])
    if sVal == "V_R2" :
        V_R2 = int(valeurs[1])
    if sVal == "V_R3" :
        V_R3 = int(valeurs[1])
    if sVal == "V_R4" :
        V_R4 = int(valeurs[1])
    if sVal == "Ecart_H" :
        Ecart_H = float(valeurs[1])
    if sVal == "Ecart_L" :
        Ecart_L = float(valeurs[1])
    if sVal == "Vcc" :
        Vcc = float(valeurs[1])
    if sVal == "OFFSET" :
        OFFSET = int(valeurs[1])
    if sVal == "OFFSET_P1" :
        OFFSET_P1 = int(valeurs[1])
    if sVal == "OFFSET_P2" :
        OFFSET_P2 = int(valeurs[1])
    if sVal == "P0" :
        ListParam.append(valeurs[1:])
    if sVal == "P1" :
        ListParam.append(valeurs[1:])
    if sVal == "P2" :
        ListParam.append(valeurs[1:])
    if sVal == "P3" :
        ListParam.append(valeurs[1:])
    if sVal == "P4" :
        ListParam.append(valeurs[1:])
    if sVal == "P5" :
        ListParam.append(valeurs[1:])

def Lire_Param():
    with open('Piles.ini', 'r') as fichier:
    # Lire chaque ligne du fichier
        for ligne in fichier:
            # Afficher la ligne lue
            if ligne.strip() == "#" :
                continue
            if ligne.strip() == "end":
                break
            Parse_Ligne(ligne.strip())
            
def  Do_Action_2(LgM2):
    print(" appel vers action_2 LgM2 =",LgM2 )
    
    

# menu qui gere le bouton droit (2) 
def Do_Menu_2():
    global ListParam
    global Ligne
   
    LgM2 = 1
    Btnx = 0
    print (" entree dans do_menu_2")
    print (" Do_Menu_2:", My_Constantes)
    print (" Ligne=:   ", Ligne)

    tft.fill(TFT.BLACK) 
    tft.text((2, 0),    ListParam[Ligne][0], TFT.YELLOW, sysfont.sysfont, 2)  # type de pile choisie
#     if Ligne <= 1:  avant !
    if Ligne <= 6:
        tft.text((2, 20),    "Recharge", TFT.WHITE, sysfont.sysfont, 2)  # cas pile alcaline , seule la recharge est possible
#        tft.text((2, 60),    "Lancement", TFT.WHITE, sysfont.sysfont, 2)  
#        tft.text((2, 80),    "  de la ", TFT.WHITE, sysfont.sysfont, 2)  
#        tft.text((2, 100),   "regen", TFT.WHITE, sysfont.sysfont, 2) 
        Do_Charge(ListParam, Ligne, tft, My_Constantes)
        tft.fill(TFT.RED)
        tft.text((20, 60),    "ARRET !", TFT.GREEN, sysfont.sysfont, 2)  
        sys.exit()


# menu qui gere le bouton droit (2) decharge des accus uniquement
def Do_Menu_3():
    global ListParam
    global Ligne
   
    LgM2 = 1
    Btnx = 0
    print (" entree dans do_menu_3")
    print (" Do_Menu_3:", My_Constantes)
    print (" Ligne=:   ", Ligne)

    tft.fill(TFT.BLUE) 
    tft.text((2, 0),    ListParam[Ligne][0], TFT.YELLOW, sysfont.sysfont, 2)  # type de pile choisie
    if Ligne > 1:  
        tft.text((2, 20),    "Decharge", TFT.WHITE, sysfont.sysfont, 2)  # cas pile alcaline , seule la recharge est possible
        Do_Decharge(ListParam, Ligne, tft, My_Constantes)
        tft.fill(TFT.RED)
        tft.text((20, 60),    "ARRET !", TFT.GREEN, sysfont.sysfont, 2)  
        sys.exit()


#------------------------------------------------------------------------------------------------------------------
#  pour cette version on prend en compte seulement la fonction de charge
#  29 mai 2024 Siedliska
#------------------------------------------------------------------------
#     elif Ligne > 1:
#         tft.text(( 2, 20), "Charge",   TFT.WHITE,  sysfont.sysfont, 2)   # autres sorte de piles / accus
#         tft.text(( 2, 40), "Decharge", TFT.WHITE,  sysfont.sysfont, 2)
#         tft.text(( 2, 60), "Capacite", TFT.WHITE,  sysfont.sysfont, 2)
#         tft.text(( 2, 80), "Cyclage",  TFT.WHITE,  sysfont.sysfont, 2)
#         tft.text((100, 20), "=>",       TFT.YELLOW, sysfont.sysfont, 2)  # curseur en 1ere place
    
# on teste le clavier
    while True:
        if DEBUG:
            Btnx = int(input("Cmd 2?"))
            print ("M2l=",LgM2, "  btnx=",Btnx)
            utime.sleep_ms(100)

        else:
           Btnx = GetButton()
           while (GetButton() != 0):
               utime.sleep_ms(10)
#----------------------------------------------------------------------------------------------------------------
        if Btnx==3 :  # down
            if LgM2 <=3:
                tft.text((100, LgM2*20), "=>", TFT.BLACK, sysfont.sysfont, 2)
                LgM2 +=1
                tft.text((100, LgM2*20),    "=>", TFT.YELLOW, sysfont.sysfont, 2)
                WS8212_Write(50,50,0)
                    
        elif Btnx==4:  # up
            if LgM2 >=2:
                tft.text((100, LgM2*20), "=>", TFT.BLACK, sysfont.sysfont, 2)
                LgM2 -=1
                tft.text((100, LgM2*20),    "=>", TFT.YELLOW, sysfont.sysfont, 2)
                WS8212_Write(0,50,50)
                
        elif Btnx==2:  # right  == go sub menu
            tft.fill(TFT.BLACK)
            tft.text((2, 0),    "Action", TFT.YELLOW, sysfont.sysfont, 2)
            WS8212_Write(50,0,50)
            Do_Action_2(LgM2)
                
        elif Btnx==0:  # 0  break  retour au menu 1
            tft.fill(TFT.BLUE)
            WS8212_Write(5,5,5)
            break
     
      
def Read_Kb():
    Btn = GetButton()
    if Btn != 0:
        while GetButton() != 0:
             utime.sleep_ms(10)
    return (Btn)
    

#-------------------------------------------------------------------
#-----------------------------   MAIN   ----------------------------
#-------------------------------------------------------------------
#  INITIALISATION
spi = SPI(1, baudrate=20000000, polarity=0, phase=0, sck=Pin(10), mosi=Pin(11), miso=None)
tft=TFT(spi,8,12,9)
tft.initr()
tft.rgb(False)
tft.fill(TFT.BLACK)
Ligne = 0
Btn = 0
CV_Coef = float (Vcc / (65535))

# ecriture du menu, puis attente d'un bouton pour changer de ligne
Display_Entete(tft)
tft.text((85, 20 * Ligne),"<==", TFT.YELLOW, sysfont.sysfont, 2)  # curseur en 1ere place
WS8212_Color(W_GREY)

Lire_Param()
CV_Coef = float (Vcc / (65536))
My_Constantes =[DEBUG, VP1, VP2, CV_Coef, OFFSET_P1, OFFSET_P2, Vcc]
print (" main:", My_Constantes)
print(My_Constantes[1],My_Constantes[2])

Init_Output()
print("start scan boutons")

# while True:
#     print(" kb=", Read_Kb())
#     utime.sleep_ms(100)
 
#zone de test du pwm et des CAN pour la tensions des piles

while True:
    if DEBUG:
        print ("l=",Ligne, "  b=",Btn)
        Btn = int(input("Cmd?"))
        utime.sleep_ms(100)

    else:
       Btn = Read_Kb()
       if Btn != 0 :
           snum = "Btn=" + str(Btn) + "  Ligne=" + str(Ligne) + "\n\r"
           my_uart.write(snum)
       else :
           utime.sleep_ms(30)
           continue
           
    
    if Btn==1 :  # down
        if Ligne <=4:
            tft.text((85, Ligne*20), "<==", TFT.BLACK, sysfont.sysfont, 2)
            Ligne +=1
            tft.text((85, Ligne*20),    "<==", TFT.YELLOW, sysfont.sysfont, 2)
            WS8212_Write(100,0,0)
            
    elif Btn==4:  # up
        if Ligne >=1:
            tft.text((85, Ligne*20), "<==", TFT.BLACK, sysfont.sysfont, 2)
            Ligne -=1
            tft.text((85, Ligne*20),    "<==", TFT.YELLOW, sysfont.sysfont, 2)
            WS8212_Write(0,100,0)
        
    elif Btn==2:  # right  == go sub menu
        tft.fill(TFT.BLACK)
        tft.text((2, 0),    "Action", TFT.YELLOW, sysfont.sysfont, 2)
        WS8212_Write(0,0,100)
        Do_Menu_2()
        print (" retour de do menu ")
        break
 
    elif Btn==3:  # left  == go menu 3  décharge des accus seulement
        tft.fill(TFT.BLUE)
        tft.text((2, 0),    "Action", TFT.YELLOW, sysfont.sysfont, 2)
        WS8212_Write(100,100,100)
        
#        Do_Menu_3()
#        Init_Teleplot()

        if (USE_TELEPLOT == True):
#limite basse 
            print(">P1: 0.500 \n")
            print(">P2: 0.500 \n")
            utime.sleep_ms(400)
            print(">R1: 0.1  >R2: 0.1 \n")
            utime.sleep_ms(400)

# limite haute
            print(">P1: 1.800 \n")
            print(">P2: 1.800 \n")
            utime.sleep_ms(400)
            print(">R1: 2.5  >R2: 2.5 \n")
            utime.sleep_ms(400)

        break


print(" fin du programme")



