import serial, time
ser = serial.Serial("COM4", 115200)
time.sleep(2)
ser.write(b"ABC\r\n")
ser.close()
