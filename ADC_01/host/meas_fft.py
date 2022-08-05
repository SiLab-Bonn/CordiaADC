# ------------------------------------------------------------
# Copyright (c) SILAB , Physics Institute of Bonn University
# ------------------------------------------------------------
#
# Author : Lamine 
# SILAB 
# CoRdia project / ADC test script 
# 11 bits ADC with/without RE
# created on 25.10.21 
# -----------------------------------------------------
# +++ ||||| ++++++++   Main script   +++ ||||| ++++++++
# -----------------------------------------------------

from faulthandler import disable
from pickle import FALSE, TRUE
import time
import _thread
import yaml
import sys

import ADC01_constants as c
from basil.dut import Dut
import matplotlib.pyplot as plt
import numpy as np
from tqdm import tqdm

import pylab as pl
import time
from bitarray import bitarray
import logging
import csv


from meas_config import config
from meas_trigger import trigger

from datetime import datetime
from meas_eval import eval
from meas_hist import eval_hist


import pyvisa as visa


logging.getLogger('matplotlib.font_manager').setLevel(logging.WARNING)# set level to warning [Debug] will be ignored ! // set to [error] warning+debug will be ignored   
# suppress all notifications  logging.getLogger('matplotlib.font_manager').disabled = True

logging.getLogger('pyvisa').setLevel(logging.WARNING) 
# suppress all notifications  llogging.getLogger('pyvisa').disabled = True



# ---------------------------------------------------
# +++++++  ********  GPAG+ DUT CONFIG  ****** +++++ 
# -------------------------------------------------
# construct the test object (DUT + GPAC) with configuration from the yaml file
  
dut = Dut("meas_ADC01.yaml")
dut.init()  ## initialize DUT object

# -------------------- END --------------------------

#************************************************************************************************************************************************
#------------------------------------------------------------------------------------------------------------------------------------------------
# +++++++++++++++++++                                            SET CONFIG                                           +++++++++++++++++++++++++++

PCB='A1.1' # Board/DUT used in test  

N=8192# FFT data input 
ADC_i= N # ADC_1 : Number of iterations (A/D conversion  / sample ) 
CH=0 # CH : the ADC under test (4 instances : 0 .. 3 )
Fs=2.5 # ADC sampling frequency in [M sample/sec] 
EN_DA=0 # EN_DA : optional configuration : with/without DIF-AMP (ext. input signal driver) || EN_DA -->  "1" or "0"
# CH=0 o or CH=1 --> RE=0 || CH=2 o or CH=3 --> RE=1 
   
if CH==0 or CH==1:
  RE=0  # RE : RE = 0 without redundancy / Re=1 with 
else:
  RE=1
# ..................................................

F_input= [9765.625, 19531.250, 39062.500, 78125.000, 156250.000, 312500.000, 625000.000, 703125.000, 781250.000, 859375.000, 937500.000, 1015625.000, 1054687.500, 1132812.500, 1171875.000, 1210937.500, 1230468.750, 1249000.000]

#F_input= [7812.500, 62500.000, 500000.000, 750000.000, 999000.00]  # when 2 MS/s is used 


F0=F_input[0] 

# actual frequency of the input signal

# +++++++++++++++++++                                        END SET CONFIG                                           +++++++++++++++++++++++++++
#------------------------------------------------------------------------------------------------------------------------------------------------
#************************************************************************************************************************************************


# set the configuration 
config(dut,Fs,RE,CH,ADC_i,EN_DA) 



# DCM SOFT RESET 
 
dut['GPIO']['SOFT_RST'] = 1 # set reset 
dut['GPIO'].write()
time.sleep(0.01)
dut['GPIO']['SOFT_RST'] = 0 # release reset 
dut['GPIO'].write()

# initializing registers : SRAM / SPI 
dut['ADC_RX'].reset()
dut['DATA'].reset()
dut['ADC_RX'].set_en(1)  # enable SPI 

# Start ADC meas frame 
# optical indication (LED2=ON)  
dut['GPIO']['LED2'] = 1
dut['GPIO'].write()


#---------------------- Power watch ------------------------------
print(' ************************ Power watch *********************************')
print('VDDIO:\t', format(dut['VDDIO'].get_voltage(unit='V'), '.3f'), 'V\t', format(dut['VDDIO'].get_current(), '.3f'), 'mA')
print('VDDD:\t', format(dut['VDDD'].get_voltage(unit='V'), '.3f'), 'V\t', format(dut['VDDD'].get_current(), '.3f'), 'mA')
print('VDDA:\t', format(dut['VDDA'].get_voltage(unit='V'), '.3f'), 'V\t', format(dut['VDDA'].get_current(), '.3f'), 'mA')
print('-----------------------------------------------------------------------')
#---------------------- *********** -------------------------------


#++++++++++++++++ Trigger the meas.  ++++++++++++++++
# -----------------------------------------
time.sleep(0.2)
trigger(dut)

#END trigger(dut)



# DATA Reading 
print("fifo size: " + str(dut['DATA']['FIFO_SIZE']))
data0 = dut['DATA'].get_data() # read data
print("data bytes received:" + str(len(data0)))
print("  ### cheking data Integrity  #### \n")
Ld=len(data0) # data size 
Le=ADC_i # expected data size

if Ld==Le:
  print("  data Integrity : OK \n")
  header_2_1=['data Integrity : OK']
else:
  print(" !!! Warning !!!  data size does not match the  number of meas. samples  !!!  \n") 
  header_2_1=['!!! Warning !!!  data size does not match the  number of meas. samples  !!!']
print(" ++++++++ ------------------ ++++++++ \n")

# load Weight matrix ------------------------
Wi=np.empty(16,dtype=int)
print(" ++++++++ load Weight matrix ++++++++ \n")
CSV_FILE_WEIGHT="meas_w" + str(CH) + ".csv" 
with open(CSV_FILE_WEIGHT, newline='') as csvfile:
     WM = list(csv.reader(csvfile, delimiter='\t'))
     if len(WM[0][:])!=16:
       print(" the length of the weights matrix is not equal to 16 -- error --   \n")
     else: 
       print(" the size of the weights matrix is OK   \n")    
     Wi = [int(h) for h in WM[0][:] ] 
csvfile.close() # close the file
print("Bit-Weights are :" + str(Wi))
#print(Wi)
# --------------------------------------------


Yi = np.empty((Ld,16),dtype=int)
Yd = np.empty(Ld,dtype=int)


for q in range(Ld):
  Xi=bin(data0[q])
  for z in range(16):
    X0=int(Xi[18+z])
    #Yi[q][z]=(1-X0) # inverting the bits !  
    Yi[q][z]=X0  

  # weighting bits depending on the redundancy
  if RE==0: 
   Yd[q]=sum(Wi*Yi[q]) # decimal weighted value 
  else:
    for z in range(16):
      if Yi[q][z]==0: 
        Yi[q][z]=-1
    Yd[q]=1024 + sum(Wi*Yi[q]) + 0.5*(Yi[q][15]-1)
  
  #print(q, hex(data0[q]), (data0[q] >> 16) & 0xfff , hex(data0[q] & 0xffff), Xi, Yi[q][:], Yd[q])

print(" ++++++++ ------------------ ++++++++ \n")



# Write the DATA to CSV

print("  ==== ****** ====  writing data to csv file  ==== ***** ==== ")

# Header 
now = datetime.now()
#print(now) 
header_0=["Time :", str(now.day)+"." + str(now.month)+"." + str(now.year), " || ",str(now.hour)+":"+str(now.minute)]
header_1=["ADC_CH : "+str(CH),"Fs [MS/s]=",str(Fs),"F0=",str(F0)]
header_2=["PCB:" + PCB,"||||","ADC Test results :  "]
header_3=["Set size (N samples) :", str(N)]
# data   -->   N sample 
ADC_OUT=Yd

   
with open('meas_out_file_fft.csv', 'w', newline='') as csv_out_file:
    writer = csv.writer(csv_out_file, delimiter='\t')
    writer.writerow(header_0)
    writer.writerow(header_1)
    writer.writerow(header_2)
    writer.writerow(header_2_1)
    writer.writerow(header_3)
    writer.writerow(ADC_OUT)

csv_out_file.close()

print(" ++++++++ ------------------ ++++++++ \n")       

# END ADC meas frame 
# optical indication (LED2=ON)  
dut['GPIO']['LED2'] = 0
dut['GPIO'].write()
dut.close()
