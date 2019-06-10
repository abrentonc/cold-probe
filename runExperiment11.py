# -*- coding: utf-8 -*-
"""
Created on Mon Apr 18 15:48:48 2016

@author: adamcraycraft
"""

#! /usr/bin/env python

# Read the output of an Arduino which may be printing sensor output,
# and at the same time, monitor the user's input and send it to the Arduino.
# See also
# http://www.arcfn.com/2009/06/arduino-sheevaplug-cool-hardware.html
# Runs with runExperiment10.ino 

import os, sys, serial, select, time
import numpy as np
import pandas as pd

def v_to_pressure(v):
	return 419.58 * v + 10.818
	
tarray = np.array([])
parray = np.array([])	
start_time = time.time()
date_string = time.strftime("%Y%m%d")
try:
	os.listdir('/Users/adamcraycraft/Desktop/Research/data/%s' % date_string)
except OSError:
	os.mkdir('/Users/adamcraycraft/Desktop/Research/data/%s' % date_string)

class Arduino() :
    def run(self, baud=9600) :
        # Port may vary, so look for it:
        self.ser = serial.Serial('/dev/cu.usbmodem14201',9600)
        self.ser.flushInput()
        desc = input("Enter run description: ")
        #desc = "Condensing"
        cmd_log = [(desc + '   START   ',time.strftime('%I:%M:%S %p',time.localtime(start_time)))]
        t = 0
        ts = []
        ps = []
        start_string = time.strftime('%I%M%p')
        filling = False
        fill_t = time.time()-3590
        start_t = time.time()
        last_t = 0
        data_file = '/Users/adamcraycraft/Desktop/Research/data/%s/pressure%s.csv' %(date_string, start_string)
        while True:
            inp, outp, err = select.select([sys.stdin, self.ser], [], [], .2)
# Check for user input:
            if sys.stdin in inp :
                line = sys.stdin.readline()
                if line == "qt\n":
                	break
                self.ser.write(line.encode('utf-8'))
                cmd_log.append((line.strip(),time.ctime(time.time())))
# check for Arduino output:
            if self.ser in inp :
                counts = float(self.ser.readline().strip())
                t = time.time()
                t_string = time.strftime('%I:%M:%S %p')
                ts.append(t)
                ps.append(counts)
                tarray = np.array(ts)
                parray = np.array(ps)
                data = pd.Series(parray, index = tarray, name = 'voltages (v)')
                data.to_csv(data_file)
                print(counts, t_string)
                if t > start_t + 3600:
                	start_t = t
                	start_string = time.strftime('%I%M%p')
                	data_file = '/Users/adamcraycraft/Desktop/Research/data/%s/pressure%s.csv' %(date_string, start_string)
                	ts = []
                	ps = []
                if t > fill_t + 4500:
                	line = 'pmp\n'
                	self.ser.write(line.encode('utf-8'))
                	fill_t = t
                	filling = True
                if filling and t > fill_t + 60:
                	line = '\n'
                	self.ser.write(line.encode('utf-8'))
                	filling = False
        end_comment = input("Final Comments? ")
        cmd_log.append((end_comment + '   END   ', t_string))
        self.ser.close()
        np.savetxt('/Users/adamcraycraft/Desktop/Research/data/%s/cmd_log%s.txt' %(date_string, start_string), cmd_log, fmt = '%s', delimiter = ' ')
		

arduino = Arduino()
try :
    if len(sys.argv) > 1 :
        print("Using", sys.argv[1], "baud")
        arduino.run(baud=sys.argv[1])
    else :
        arduino.run()
except serial.SerialException :
    print("Disconnected (Serial exception)")
except IOError :
    print("Disconnected (I/O Error)")
except KeyboardInterrupt :
    print("Interrupt")