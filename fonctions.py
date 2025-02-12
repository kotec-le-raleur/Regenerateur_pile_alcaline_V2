



# fonctions diverses pour le régénérateur
import machine
from machine import Pin, PWM, UART
from st7735 import TFT
import sysfont
import neopixel
import utime 

USE_TELEPLOT      =  True
USE_CONSOLE	      =  True
USE_SERIAL_PLOT	  =  False
USE_LOGVIEW	      =  False

# Color definitions pour la diode WS2812
W_BLACK   = (0, 0, 0)
W_WHITE   = (160, 160, 160)
W_RED     = (228, 0, 0)
W_GREEN   = (0, 128, 0)
W_BLUE    = (0, 0, 128)
W_YELLOW  = (228, 150, 0)
W_MAGENTA = (200, 0, 200)
W_CYAN    = (0, 255, 255)
W_GREY    = (20,20,20)


# pour la diode WS8212
p = machine.Pin(16)
n = neopixel.NeoPixel(p, 1)
Pile_1_value = machine.ADC(machine.Pin(27))  
Pile_2_value = machine.ADC(machine.Pin(26))  

# Pin connectées aux bases des mosfets
Load_P1   = Pin(5, machine.Pin.OUT)
Load_P2   = Pin(4, machine.Pin.OUT)
Charge_P1 = Pin(7, machine.Pin.OUT)
Charge_P2 = Pin(6, machine.Pin.OUT)

my_uart = UART(0, baudrate=115200, tx=Pin(0), rx=Pin(1))
my_uart.init(bits=8, parity=None, stop=2)
TxtBuf = "  "

def Init_Output():
    Load_P1.low()     # turn off gate
    Load_P2.low()     # turn off gate
    Charge_P1.low()   # turn off  Q8  et  Q6
    Charge_P2.low()   # turn off  Q4  et  Q3
    
    #  moyenne sur 64 mesures espaces de 2 mS
def Get_P1_P2(My_Constantes):
#    print ("  IN Get_P1_P1:", My_Constantes)

    Vin1 = 0
    Vin2 = 0
    Nx = 32
    for x in range (0,Nx,1):
        Vin1  = (Pile_1_value.read_u16())  + Vin1    
        utime.sleep_ms(1)
        Vin2  = (Pile_2_value.read_u16())  + Vin2   
        utime.sleep_ms(1)
        
 #   print("Vin1 =", Vin1, "   Vin2 = ", Vin2)
        
    My_Constantes[1] = int(Vin1 /Nx) - My_Constantes[4]
    My_Constantes[2] = int(Vin2 /Nx) - My_Constantes[5]
#    print ("  OUT Get_P1_P1:", My_Constantes)
    
    return
    
    
def Load_P1_ON():
    Load_P1.high() # turn on gate
    
def Load_P1_OFF():
    Load_P1.low() # turn off gate
    
def Load_P2_ON():
    Load_P2.high() # turn on gate
    
def Load_P2_OFF():
    Load_P2.low() # turn off gate
   

def Charge_ON (Id , Ratio):
    Ton = Ratio 
    if Id == 1:
        for i in range (0,10):
             Charge_P1.high()
             utime.sleep_ms(Ton)
             Charge_P1.low()
             utime.sleep_ms(100-Ton)
    if Id == 2:
        for i in range (0,10):
             Charge_P2.high()
             utime.sleep_ms(Ton)
             Charge_P2.low()
             utime.sleep_ms(100-Ton)
             
    if Id == 0:
        for i in range (0,10):
             Charge_P1.high()
             Charge_P2.high()
             utime.sleep_ms(Ton)
             Charge_P1.low()
             Charge_P2.low()
             utime.sleep_ms(100-Ton)
      
        
def Charge_OFF (Id):
    if Id == 1:
         Charge_P1.low()   
    if Id == 2:
         Charge_P2.low()   
    if Id == 0:
         Charge_P1.low()   
         Charge_P2.low()   
    

def Display_Entete(tft):
    decalage = 20
    tft.text((2, 0),           "Alca 2A", TFT.WHITE, sysfont.sysfont, 2)
    tft.text((2, decalage),    "Alca 3A", TFT.WHITE, sysfont.sysfont, 2)
    tft.text((2, decalage*2),  "NiMh 2A", TFT.WHITE, sysfont.sysfont, 2)
    tft.text((2, decalage*3),  "NiMh 3A", TFT.WHITE, sysfont.sysfont, 2)
    tft.text((2, decalage*4),  "NiZn 2A", TFT.WHITE, sysfont.sysfont, 2)
    tft.text((2, decalage*5),  "NiZn 3A", TFT.WHITE, sysfont.sysfont, 2)

def WS8212_Write(r,v,b):     #  3 paramètres
    n[0] = (r, v, b)
    # write led
    n.write()

def WS8212_Color(Color):		#  juste la couleur en liste
    n[0] = (Color)
    # write led
    n.write()

def  Do_Resistance_interne(tft, My_Constantes):
    Get_P1_P2(My_Constantes)
    VP11 = My_Constantes[1] * My_Constantes[3]
    VP21 = My_Constantes[2] * My_Constantes[3]
    Load_P1_ON()
    Load_P2_ON()
    utime.sleep_ms(100)
    Get_P1_P2(My_Constantes)
    VP12 = My_Constantes[1] * My_Constantes[3]
    VP22 = My_Constantes[2] * My_Constantes[3]
    Load_P1_OFF()
    Load_P2_OFF()
    Ri1 = ((VP11-VP12)/VP11) * 7.50 
    Ri2 = ((VP21-VP22)/VP21) * 7.50 
    
    TxtBuf = ">R1:" + '{:.02f}'.format(Ri1)+ "\n"
    my_uart.write(TxtBuf)
    if (USE_TELEPLOT == True): print (TxtBuf)
    TxtBuf = ">R2:" + '{:.02f}'.format(Ri2)+ "\n"
    my_uart.write(TxtBuf)
    if (USE_TELEPLOT == True):
        print (TxtBuf)
    else:    
        print ("Ri 1 = ",'{:.02f}'.format(Ri1), "  Ri 2 = ",'{:.02f}'.format(Ri2))
    utime.sleep_ms(400)

def  Do_Resistance_interne_decharge(tft, My_Constantes):
    Get_P1_P2(My_Constantes)
    VP11 = My_Constantes[1] * My_Constantes[3]
    VP21 = My_Constantes[2] * My_Constantes[3]
    
    Load_P1_OFF()
    Load_P2_OFF()
    utime.sleep_ms(100)
    Get_P1_P2(My_Constantes)
    Load_P1_ON()
    Load_P2_ON()
    VP12 = My_Constantes[1] * My_Constantes[3]
    VP22 = My_Constantes[2] * My_Constantes[3]
    Ri1 = ((VP12-VP11)/VP12) * 7.50 
    Ri2 = ((VP22-VP21)/VP22) * 7.50
    TxtBuf = ">R1:" + '{:.02f}'.format(Ri1)+ "\n"
    if (USE_TELEPLOT == True): print (TxtBuf)
    my_uart.write(TxtBuf)
    TxtBuf = ">R2:" + '{:.02f}'.format(Ri2)+ "\n"
    my_uart.write(TxtBuf)
    if (USE_TELEPLOT == True):
        print (TxtBuf)
    else:    
        print ("Ri 1 = ",'{:.02f}'.format(Ri1), "  Ri 2 = ",'{:.02f}'.format(Ri2))
    utime.sleep_ms(40)


    

def  Do_Charge(ListParam, Option, tft, My_Constantes):
    global TxtBuf
    print ("A In:Do_Charge:", My_Constantes)
    print ("B In:Do_Charge:", Option)
    
    Vmax = 1.70
    Vmin = 1.00
    RatioMax = 40
    print ("C In:Do_Charge: Vmax=", Vmax, "  Ratio max= ",RatioMax)
    VP1 = 1.0
    VP2 = 1.0
    print(" Regeneration en cours" )
    Vmax = float(ListParam[Option][2])
    Vmin = float(ListParam[Option][3])
    Ratiomax = int(ListParam[Option][4])
    CV_Coef = My_Constantes[3]
#    tft.text(( 2, 40),   "Regeneration", TFT.GREEN, sysfont.sysfont, 1)  # cas pile alcaline , seule la recharge est possible
    tft.text(( 2, 40),   "Type=" + ListParam[Option][1], TFT.PURPLE, sysfont.sysfont, 2)  # cas pile alcaline , seule la recharge est possible
    tft.text(( 2, 60),   "Ratio=" + str(Ratiomax), TFT.PURPLE, sysfont.sysfont, 2)  # cas pile alcaline , seule la recharge est possible
    while True:
        Do_Resistance_interne(tft, My_Constantes)
        Get_P1_P2(My_Constantes)
        VP1 = My_Constantes[1] * CV_Coef
        VP2 = My_Constantes[2] * CV_Coef
# affichage des tensions sur le display LCD
        tft.fillrect ( (2,84),(92,50),TFT.BLACK)
        tft.text((2, 85 ), "P2=" + '{:.03f}'.format(VP2), TFT.YELLOW, sysfont.sysfont, 2)
        tft.text((2, 110), "P1=" + '{:.03f}'.format(VP1), TFT.YELLOW, sysfont.sysfont, 2)
        if (USE_TELEPLOT == False):
            print ("Pile 1 = ",'{:.03f}'.format(VP1), "  Pile 2 = ",'{:.03f}'.format(VP2))
        TxtBuf = ">P1:" + '{:.03f}'.format(VP1)+ "\n"
        my_uart.write(TxtBuf)
        if (USE_TELEPLOT == True): print (TxtBuf)
        TxtBuf = ">P2:" + '{:.03f}'.format(VP2)+ "\n"
        my_uart.write(TxtBuf)
        if (USE_TELEPLOT == True):
            print (TxtBuf)
        for i in range (0,5):
            WS8212_Color(W_RED)
            if (VP1 < Vmax):			# alcaline max = 1.7 V
                Charge_ON (0,RatioMax)
            WS8212_Color(W_YELLOW)
            if (VP2 < Vmax):
                Charge_ON (0,RatioMax)
                
            WS8212_Color(W_BLUE)
            utime.sleep_ms(50)
            
    utime.sleep(2)




def  Do_Decharge(ListParam, Option, tft, My_Constantes):
    global TxtBuf
    print ("A In:Do_DeCharge:", My_Constantes)
    print ("B In:Do_DeCharge:", Option)
    
    Vmin = 1.00
    VP1 = 1.00
    VP2 = 1.00
    print(" Decharge en cours" )
    Vmin = float(ListParam[Option][3])
    CV_Coef = My_Constantes[3]
    tft.text(( 2, 40),   "Type=" + ListParam[Option][1], TFT.WHITE, sysfont.sysfont, 2)  # cas pile alcaline , seule la recharge est possible
    tft.text(( 2, 60),   "Vmin=" + ListParam[Option][3], TFT.WHITE, sysfont.sysfont, 2)  # cas pile alcaline , seule la recharge est possible
    while True:
        Load_P1_ON()
        Load_P2_ON()

        Get_P1_P2(My_Constantes)
        VP1 = My_Constantes[1] * CV_Coef
        VP2 = My_Constantes[2] * CV_Coef

# affichage des tensions sur le display LCD
        tft.fillrect ( (2,84),(92,50),TFT.BLUE)
        tft.text((2, 85 ), "P2=" + '{:.03f}'.format(VP2), TFT.YELLOW, sysfont.sysfont, 2)
        tft.text((2, 110), "P1=" + '{:.03f}'.format(VP1), TFT.YELLOW, sysfont.sysfont, 2)
        if (USE_TELEPLOT == False):
            print ("Pile 1 = ",'{:.03f}'.format(VP1), "  Pile 2 = ",'{:.03f}'.format(VP2))
        TxtBuf = ">P1:" + '{:.03f}'.format(VP1)+ "\n"
        my_uart.write(TxtBuf)
        if (USE_TELEPLOT == True): print (TxtBuf)
        TxtBuf = ">P2:" + '{:.03f}'.format(VP2)+ "\n"
        my_uart.write(TxtBuf)
        if (USE_TELEPLOT == True): print (TxtBuf)
        Do_Resistance_interne_decharge(tft, My_Constantes)
        if (VP1 < Vmin):			
            Load_P1_OFF()
            WS8212_Color(W_MAGENTA)

        if (VP2 < Vmin):
            Load_P2_OFF()
            WS8212_Color(W_MAGENTA)

               
        WS8212_Color(W_GREEN)
        utime.sleep_ms(500)
        WS8212_Color(W_RED)
        utime.sleep_ms(500)

    utime.sleep(2)
