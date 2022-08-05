#
# ------------------------------------------------------------
# Copyright (c) SILAB , Physics Institute of Bonn University
# ------------------------------------------------------------
#
# Author : Lamine 
# SILAB 
# CoRdia project / ADC test script 
# 11 bits ADC with/without RE
# created on 25.10.21 
# -----------------------------------------------------------------------
# +++ ||||| ++++++++   sub-function used in meas.py   +++ ||||| ++++++++



import time as time



def trigger(dut):
    
    #print(' ******* start conversion *********  \n' )
    
    #dut['SEQ'].start()  # soft triger of start sequencer    
    
    dut['GPIO']['EN_SEQ'] = 1
    dut['GPIO'].write()
    
    time.sleep(0.04) # the time of one A/D conversion s ||  Fs=2.5Ms/s > Ts=0.4us   10ms >> max 25k samples  (10ms/0.4us)  / 40ms >> max 100k samples

    dut['GPIO']['EN_SEQ'] = 0
    dut['GPIO'].write()
    
    #data = dut['DATA'].get_data() # read data
    #return data 

