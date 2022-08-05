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

import csv
import time as time
from bitarray import bitarray





def config(dut,Fs,RE,CH,M,EN_DA): 
    # ---------------------------------------------------
    # +++++++  ******** ADC CONFIG VARIABLE  ****** +++++ 
    # ---------------------------------------------------
    # Fs : ADC sampling freq in MHz
    # RE : RE = 0 without redundancy / Re=1 with     
    # CH : the ADC under test (4 instances : 0 .. 3 )
    # M : Number of iterations (A/D conversion)    
    # EN_DA : optional configuration : with/without DIF-AMP (ext. input signal driver) || EN_DA -->  "1" or "0"
    # -------------------- END --------------------------

    # ---------------------------------------------------
    # +++++++  ******** GPAG Power config  ****** +++++ 
    # ---------------------------------------------------
    print('SET SUPPLIES \n' )
    VDD=1.2
    # Input/output PADRING supply 
    dut['VDDIO'].set_current_limit(20, unit='mA')
    dut['VDDIO'].set_voltage(VDD, unit='V')
    # Digital core supply
    dut['VDDD'].set_current_limit(20, unit='mA')
    dut['VDDD'].set_voltage(VDD, unit='V')
    # Analog core supply
    dut['VDDA'].set_current_limit(20, unit='mA')
    dut['VDDA'].set_voltage(VDD, unit='V')
    # Power on 
    dut['VDDIO'].set_enable(1)
    dut['VDDD'].set_enable(1)
    dut['VDDA'].set_enable(1)
    # -------------------- END --------------------------
    

    # ---------------------------------------------------
    # +++++++  ******** SET ADC REF  ****** +++++ 
    # ---------------------------------------------------
    print('SET REFs \n' )
    V_offset=0.02  # 0.02 #To be checked!!  the input "0" (or "0.0") leads to an error !! added 20mV offset !!
    VREF0=1.2
    VREFN=0 + V_offset  
    VREFP=VREF0 + V_offset    
    #VREFN=0.300  
    #VREFP=0.900
    dut['VREF_N'].set_voltage(VREFN, unit='V') # 
    dut['VREF_P'].set_voltage(VREFP, unit='V')
  
    # -------------------- END ------------------------
    
    # ---------------------------------------------------
    # +++++++  ******** SET ADC REF  ****** +++++ 
    # ---------------------------------------------------
     
    print("with/without DIF-AMP (ext. input signal driver) ? ")
    dut['GPIO']['EN_OPA'] = EN_DA
    dut['GPIO'].write()
    if (EN_DA ==1): 
     print("with")
    else:
      print("without")   
    print(" ++++++++ ------------------ ++++++++ \n")

    # ---------------------------------------------------
    #  +++++ ******** SET the SEQ  ********** ++++++++ 
    # ---------------------------------------------------
    print('SET SEQ \n' )
    # check whether with or without  redundancy
    if RE==0:
      CSV_FILE='meas_seq_11bit.csv'
      seq_loop_cnt = 32 + 2 # set sequencer cnt | see : FPGA_MODULES_wo_RE.ods !! 
    else: 
      CSV_FILE='meas_seq_13bit.csv'
      seq_loop_cnt = 36 + 2  # set sequencer cnt !! 13 bits with RE 

    # ADC/SEQ clk config 
  
    seq_clk = Fs * seq_loop_cnt
    dut['MIO_PLL'].init()
    dut['MIO_PLL'].setFrequency(seq_clk) # SEQ FREQ 


    # ************** import SEQ from CSV files ********** 
    with open(CSV_FILE, newline='') as csvfile:
      SEQ_DATA = csv.reader(csvfile, delimiter='\t')
      print('loading SEQ data \n' ) 
      print('CLK_CMP  CLK_SR   SAMPLE    RSTB   RX_EN0 \n' ) 
      SEQ0=[]
      for X in SEQ_DATA:
       print(', '.join(X))
       SEQ0.append(X[:])
    csvfile.close() # close the file

    CLK_COM0=[] 
    CLK_SR0=[]
    SAMPLE0=[]
    RST_B0=[]
    RX_EN0=[] 

    #print(len(SEQ0))
    for i in range(len(SEQ0)) :
      CLK_COM0.append(SEQ0[i][0]) 
      CLK_SR0.append(SEQ0[i][1])
      SAMPLE0.append(SEQ0[i][2])
      RST_B0.append(SEQ0[i][3])
      RX_EN0.append(SEQ0[i][4]) 
      

    CLK_COM=bitarray("".join(CLK_COM0))
    CLK_SR =bitarray("".join(CLK_SR0))
    SAMPLE =bitarray("".join(SAMPLE0))
    RST_B  =bitarray("".join(RST_B0))
    RX_EN  =bitarray("".join(RX_EN0))


    #sequencer configuration
    dut['SEQ'].reset() # clear sequencer registers
    dut['SEQ'].set_clk_divide(1) 
    #dut['SEQ'].set_repeat_start(0) 
    dut['SEQ'].set_repeat(M) # run  loops
    dut['SEQ'].set_en_ext_start(1)    
    #print("get_en_ext_start= " +str(dut['SEQ'].get_en_ext_start()))
    dut['SEQ'].set_size(seq_loop_cnt)  
    dut['GPIO']['EN_SEQ'] = 0 # set EN_SEQ to "0"
    dut['GPIO'].write()
    # sequence implementation

    dut['SEQ']['CLK_COMP'][0:seq_loop_cnt-1] =  CLK_COM
    dut['SEQ']['CLK_SR'  ][0:seq_loop_cnt-1] =  CLK_SR
    dut['SEQ']['SAMPLE'  ][0:seq_loop_cnt-1] =  SAMPLE
    dut['SEQ']['RST_B'   ][0:seq_loop_cnt-1] =  RST_B
    dut['SEQ']['RX_EN'   ][0:seq_loop_cnt-1] =  RX_EN
    
    dut['SEQ'].write()  # load sequencer memory

  
    print('END SET SEQ \n' )


    # ---------------------------------------------------
    #  +++++ ******** SEL ADC  ********** ++++++++ 
    # ---------------------------------------------------
    print('SEL ADC CH = %d \n' % (CH) )

    dut['GPIO']['SEL'] = CH
    dut['GPIO'].write()
    #  +++++ ******** END SEL ADC  ********** ++++++++ 
    #---------------------- *********** -------------------------------

