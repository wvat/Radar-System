import serial
import datetime

def get_data(ser):
    data_buff = []
    while True:
        try:
            c = ser.read(1)  #Read the start byte
            if ord(c) == 255: #Start character detected.
                break
        except TypeError:
            print('Bad Data:',c)
            continue
    try:
        c = ser.read(1)
        points = ord(c)
    except TypeError:
        points = 256    #Default to 256 points

    while points > 0:
        c = ser.read(1) #Read data
        try:
            value = ord(c)
        except TypeError:
            print('Bad Data:',c)
            continue
        data_buff.append(value*0.0196)  #Convert to voltage and append
        points -= 1
    print(data_buff)
    return data_buff
