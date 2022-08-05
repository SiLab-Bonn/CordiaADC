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
ADC_i= 128 # 12000  ADC_1 : Number of iterations (A/D conversion  / sample ) 
CH=1 # CH : the ADC under test (4 instances : 0 .. 3 )
Fs=2.5 # ADC sampling frequency in [M sample/sec] 
EN_DA=0 # EN_DA : optional configuration : with/without DIF-AMP (ext. input signal driver) || EN_DA -->  "1" or "0"
# CH=0 o or CH=1 --> RE=0 || CH=2 o or CH=3 --> RE=1 
   
if CH==0 or CH==1:
  RE=0  # RE : RE = 0 without redundancy / Re=1 with 
else:
  RE=1
# ..................................................


#++++++++++++++++ config. of the digital ramp @ the ADC input  ++++++++++++++++

GPAC_DAC=FALSE #   True : using DACs of the GPAC otherwise SMU 

#  generate the digital ramp 
Nsample = 4095 # 8191 # number of input samples  

VCM=0.6 # [V] common-mode signal 
F_scale= 0.84 # input scaling factor   

#VCM=0.5
#F_scale=0.75 # 
#VCM=0.7
#F_scale=0.75 # 
#VCM=0.5*0.9
#F_scale=0.75*0.9 # 

VREF_ADC=1.2 # ADC full scale input reference  
Vmax=VREF_ADC*F_scale # [V] maximum "differential" applied voltage 
Vmin=-VREF_ADC*F_scale # [V] minimum "differential" applied voltage
STEP=(Vmax-Vmin)/(Nsample)  # [V] step of the "differential" applied voltage
VIN_DIFF = np.arange(Vmin, Vmax+ 1E-6, STEP) # [V]  differential mode signals, !!! "+1E-6" just a trick to include VMAX in the VIN_DIFF array (no effect)  !!! 
#print(VIN_DIFF)

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

print(' ************************ VREF *********************************')
print('VREF_N:\t', format(dut['VREF_N'].get_voltage(unit='V'), '.3f'))
print('VREF_P:\t', format(dut['VREF_P'].get_voltage(unit='V'), '.3f'))
print('-----------------------------------------------------------------------')
#---------------------- *********** -------------------------------


#++++++++++++++++ Applying a digital ramp @ the ADC input  ++++++++++++++++
# -----------------------------------------

if GPAC_DAC==TRUE:
  V_offset=0.02 #To be checked!!  the input "0" (or "0.0") leads to an error !! added 20mV offset !!

  for i in tqdm(range(len(VIN_DIFF))):
      dut['VIN_P'].set_voltage(V_offset + VCM - 0.5*VIN_DIFF[i], unit='V')
      dut['VIN_N'].set_voltage(V_offset + VCM + 0.5*VIN_DIFF[i], unit='V')
      #print("Delta_VI=%f " % (VIN_DIFF[i]))
      time.sleep(0.2) # voltage setteling time 
      #triger the ADC conversion and get the data back 
      trigger(dut)
      #END trigger(dut)
else: 
  # with SMU
  # SMU configuration       

  dut_SMU = Dut("keithley_2602a.yaml")
  dut_SMU.init()  
  time.sleep(0.5)
  dut_SMU['SMU'].on(channel=1)
  dut_SMU['SMU'].on(channel=2)
  dut_SMU['SMU'].source_volt(channel=1)
  dut_SMU['SMU'].source_volt(channel=2)
  dut_SMU['SMU'].set_current_limit(0.005, channel=1)
  dut_SMU['SMU'].set_current_limit(0.005, channel=2)
  dut_SMU['SMU'].set_voltage_limit(1.4, channel=1)
  dut_SMU['SMU'].set_voltage_limit(1.4, channel=2)
  dut_SMU['SMU'].set_voltage_range(1.2,channel=1)
  dut_SMU['SMU'].set_voltage_range(1.2,channel=2)
  
  time.sleep(0.5)
  for i in tqdm(range(len(VIN_DIFF))):
    dut_SMU['SMU'].set_voltage(VCM - 0.5*VIN_DIFF[i], channel=2)
    dut_SMU['SMU'].set_voltage(VCM + 0.5*VIN_DIFF[i], channel=1)
    time.sleep(0.3) # voltage setteling time 
    #triger the ADC conversion and get the data back 
    trigger(dut)
    #END trigger(dut)



# DATA Reading 
print("fifo size: " + str(dut['DATA']['FIFO_SIZE']))
data0 = dut['DATA'].get_data() # read data
print("data bytes received:" + str(len(data0)))
print("  ### cheking data Integrity  #### \n")
Ld=len(data0) # data size 
Le=len(VIN_DIFF)*ADC_i # expected data size

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
header_1=["ADC_CH : "+str(CH),"VCM [V]="+str(VCM),"Fs [MS/s]="+str(Fs)]
header_2=["PCB:" + PCB,"||||","ADC Test results :  "]
# data   -->   N sample | VIN_DIF | ADC_OUT_1 | ADC_OUT_2 | .... ADC_OUT_i|  

header_3_0=["N sample","VIN_DIF [uV]"]
header_3_1=[]
for r in range(ADC_i):
  header_3_1.append("ADC_OUT_"+str(r))
header_3=header_3_0+header_3_1


ADC_OUT= np.zeros((len(VIN_DIFF),ADC_i+2),dtype=int) # "+2" --> to add VDIF and N sample to the results matrix   

for j in range(len(VIN_DIFF)):
  ADC_OUT[j][0]=j
  ADC_OUT[j][1]=1E6*VIN_DIFF[j] # [uV]
  for k in range(ADC_i):      
    ADC_OUT[j][k+2]=Yd[k+ADC_i*j]
    

with open('meas_out_file.csv', 'w', newline='') as csv_out_file:
    writer = csv.writer(csv_out_file, delimiter='\t')
    writer.writerow(header_0)
    writer.writerow(header_1)
    writer.writerow(header_2)
    writer.writerow(header_2_1)
    writer.writerow(header_3)
    writer.writerows(ADC_OUT)
  


csv_out_file.close()

print(" ++++++++ ------------------ ++++++++ \n")       


# END ADC meas frame 
# optical indication (LED2=ON)  
dut['GPIO']['LED2'] = 0
dut['GPIO'].write()


dut.close()


if GPAC_DAC==FALSE:
 source_inst="input source : SMU" 
 dut_SMU.close()
else:
 source_inst="input source : GPAC_DAC"  


header_eval="||".join(["ADC Transfer Function", "Date :" + str(now.day)+"." + str(now.month)+"." + str(now.year),"PCB:" + PCB,"ADC_CH : "+str(CH),"VCM [V]="+str(VCM),"Fs [MS/s]="+str(Fs),"N Samples ="+str(len(VIN_DIFF)),"N iterations / conversion="+str(ADC_i),source_inst])
eval(ADC_OUT,ADC_i,len(VIN_DIFF),header_eval)
header_hist="||".join(["Noise evaluation", "Date :" + str(now.day)+"." + str(now.month)+"." + str(now.year),"PCB:" + PCB,"ADC_CH : "+str(CH),"VCM [V]="+str(VCM),"Fs [MS/s]="+str(Fs),"N iterations / conversion (evaluation set)="+str(ADC_i),source_inst])
#eval_hist(ADC_OUT,ADC_i,len(VIN_DIFF),header_hist)