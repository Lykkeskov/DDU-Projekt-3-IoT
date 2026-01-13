import serial
import time

#brug rigtig data men koden virker ikke lige nu så

def co2():
    #tal af hvor stor emails er
    size = [120, 1000, 90, 133, 124, 122, 99]

    MB = []
    KB = []

    #sortere efter størrelse
    for item in size:
        if item < 1000:
            KB.append(item) 
        else:
            MB.append(item)

    #find CO2 udput 
    CO2 = (0.3 * len(KB)) + (50 * len(MB))

    number = round(CO2, 2)

    return number

def sammenligning():
    
    bil = 131.8
    km = co2_forbrug / bil #udregner hvor mange km man kunne køre for den co2 man har brugt på emails
    tal = round(km, 2)
    
    return tal

port = "/dev/cu.usbmodem1101"   #Brug ens egn port (comx på windows) 
ser = serial.Serial(port, 9600)
time.sleep(2)  # rest

co2_forbrug = co2() 
km = sammenligning()

message = f"Dit forbrug var: {co2_forbrug} g CO2e. "
forskel = f"Man kunne kore {km} km i en bil" #kan ikke vise ø, så o står der i stedet for

ser.write((message + forskel + "\n").encode("utf-8")) #beskeden der bliver vist
