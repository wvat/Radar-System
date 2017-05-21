import datetime
import serial
from threading import Thread
from matplotlib import pyplot as plt
from matplotlib import animation
from matplotlib.lines import Line2D
import numpy as np


BAUDRATE = 1200
SOL = 3e8

def main():
    freq_start = 2.4e9
    freq_stop = 2.5e9
    sample_rate = 64e-6
    sweep_length = 40e-3

    print('**********************')
    print('****FMCW Radar DSP****')
    print('**********************')
    print('Version 1.0')
    print('by Fred Vatnsdal - 134033')
    print(datetime.date.today(),'\n','\n','\n')
    port = 0
    while True:
        selected_port = input('Enter a COM port number >>')
        try:
            selected_port = int(selected_port)
        except(ValueError):
            print(selected_port,'is not a number. Please enter a number.')
            continue
        if((selected_port >= 0) and (selected_port < 5)):
            break
        else:
            print('COM', selected_port, 'is out of range. Choose a number from 0 - 4.')

    port = 'COM' + str(selected_port)
    ser = init_ser(port)
    print('Reading from:', port)

    print()
    print()
    print('Default Radar Characteristics:')
    print('***Start Frequency(Hz):', freq_start)
    print('***Stop Frequency(Hz):', freq_stop)
    print('***Sweep Bandwidth(Hz):', freq_stop-freq_start)
    print('***Sample Rate(s):',sample_rate)
    print('***Sweep Length(s):',sweep_length)
    print()

    while True:
        confopt = input('Configure Radar Characteristics (y/n)>>')
        if confopt == 'y':
            print()
            print('       Options Menu    ')
            print('=======================')
            print('1...Start Frequency(Hz)')
            print('2...Stop Frequency(Hz)')
            print('3...Sample Rate(s)')
            print('4...Sweep Length(s)')
            print('e to exit')
            while True:
                selection = input('Select a menu option (1-5)>>')
                if selection == '1':
                    while True:
                        temp = input ('Enter a start frequency in Hz, or e to exit >>')
                        print('Selected value:',temp)
                        if temp == 'e':
                            break
                        try:
                            freq_start = float(temp)
                            break
                        except TypeError:
                            print('Bad Input')

                elif selection == '2':
                    while True:
                        temp = input ('Enter a stop frequency in Hz, or e to exit >>')
                        print('Selected value:',temp)
                        if temp == 'e':
                            break
                        try:
                            freq_stop = float(temp)
                            break
                        except TypeError:
                            print('Bad Input')

                elif selection == '3':
                    while True:
                        temp = input ('Enter a sample rate in s, or e to exit>>')
                        print('Selected value:',temp)
                        if temp == 'e':
                            break
                        try:
                            sample_rate = float(temp)
                            break
                        except TypeError:
                            print('Bad Input')

                elif selection == '4':
                    while True:
                        temp = input ('Enter a sweep length in s, or e to exit >>')
                        print('Selected value:',temp)
                        if temp == 'e':
                            break
                        try:
                            sweep_length = float(temp)
                            break
                        except TypeError:
                            print('Bad Input')
                elif selection == 'e':
                    break;
                else:
                    print('Bad input:',selection)
            break
        elif confopt == 'n':
            break
        else:
            print('Bad input:',confopt)

    print('Initial Setup Complete. Starting DSP')

    ani = Plot(ser,get_data(ser))
    plt.grid()
    plt.show()
    print('Plot Created')

def init_ser(port):
     try:
        return serial.Serial(port=port,
                             baudrate=1200,
                             bytesize=serial.EIGHTBITS,
                             parity=serial.PARITY_EVEN,
                             stopbits=serial.STOPBITS_TWO,
                             timeout=0.1)

     except(serial.serialutil.SerialException):
            print('Error: The serial port', port, 'is in use, or is invalid')
            print('Exiting...')
            exit(0)

def get_data(ser):
    data_buff = []
    while True:
        try:
            c = ser.read(1)  #Read the start byte
            print('Waiting for start byte -- Input:', ord(c))
            if ord(c) == 77: #Start character detected.
                break
        except TypeError:
            print('Bad Data:',c)
            continue
    try:
        c = ser.read(1)
        points = ord(c)
    except TypeError:
        points = 256    #Default to 256 points

    points = 64
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

class Plot(animation.TimedAnimation):
    def __init__(self, ser, data):
        data_y = data
        self.ser = ser
        fig = plt.figure()
        axis_time = fig.add_subplot(1, 1, 1)


        self.t = np.linspace(0, 80, 400)
        self.x = np.arange(len(data_y))
        self.y = data_y

        axis_time.set_xlabel('Sample Number')
        axis_time.set_ylabel('Voltage (V)')
        self.line1 = Line2D([], [], color='black')
        axis_time.add_line(self.line1)
        axis_time.set_xlim(0, len(data_y))
        axis_time.set_ylim(0, 5)
      #  ax1.set_aspect('equal', 'datalim')

        animation.TimedAnimation.__init__(self, fig, interval=1, blit=True)
    def _draw_frame(self, framedata):
        i=framedata
        self.line1.set_data(self.x[:i], self.y[:i])
        self._drawn_artists = [self.line1]
    def new_frame_seq(self):
        return iter(range(self.t.size))
    def _init_draw(self):
        self.line1.set_data([],[])
        self.data_y = get_data(self.ser)
        self.x = np.arange(len(self.data_y))
        self.y = self.data_y



if __name__ == '__main__': #run main() on startup
    main()
