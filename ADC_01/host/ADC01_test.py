"""
Script for ADC tests
"""

#import array
#import itertools
#import operator
#import time
import _thread
import yaml
import sys

from ADC01 import adc01
import ADC01_constants as c
from basil.dut import Dut
import matplotlib.pyplot as plt
import numpy as np
import pylab as pl
import time
from bitarray import bitarray
import logging
logging.getLogger().setLevel(logging.ERROR)

# initialise our DUT
dut = adc01("adc01.yaml")  # construct the test object (DUT + GPAC) with configuration from the yaml file
dut.init()  ## initialize dut object
dut.switch_on_power_supply_voltages(1)  # enable power supplies

# timing configuration
seq_loop_cnt = 64 # set sequencer depth (number of sequencer clock cycles before loop repeats)
# i.e. loop_cnt = 64, ADC clock cycles per sample = 16 --> 4 timing bins per ADC clock cycle
sample_freq = 1 # sample frequencey in MHz
seq_clk = sample_freq * seq_loop_cnt
dut['MIO_PLL'].setFrequency(seq_clk)
print("PLL clock = " + str(seq_clk))

# sequencer configuration
dut['SEQ'].reset() # clear sequencer registers
dut['SEQ'].set_clk_divide(1) 
dut['SEQ'].set_repeat_start(0) 
dut['SEQ'].set_repeat(0) # run infinite loops
dut['SEQ'].set_size(seq_loop_cnt)  

# sequence implementation
                                       # ADC clock:   0    1    2    3    4    5    6    7    8    9    10   11   12   13   14   15 
dut['SEQ']['CLK_COMP'][0:seq_loop_cnt-1] =  bitarray('0011 0011 0011 0011 0011 0011 0011 0011 0011 0011 0011 0011 0011 0011 0011 0011') 
dut['SEQ']['CLK_SR'  ][0:seq_loop_cnt-1] =  bitarray('1001 1001 1001 1001 1001 1001 1001 1001 1001 1001 1001 1001 1001 1001 1001 1001') 
dut['SEQ']['SAMPLE'  ][0:seq_loop_cnt-1] =  bitarray('1111 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000') 
dut['SEQ']['RST_B'   ][0:seq_loop_cnt-1] =  bitarray('1111 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000') 
dut['SEQ'].write()  # load sequencer memory

# select channel
dut.select_channel(c.SEL_ADC_CH0)

# start measurement
dut['SEQ'].start()  # start sequencer
dut['ADC_RX']['EN'] = 1  # enable ADC data receiver

dut['GPIO']['EN_RX_FIFO'] = 1
dut['GPIO'].write()
time.sleep(0.5)
dut['GPIO']['EN_RX_FIFO'] = 0
dut['GPIO'].write()

data = dut['DATA'].get_data() # read data

print("fifo size: " + str(dut['DATA']['FIFO_SIZE']))
print("data bytes received: " + str(len(data)))
print("data "+ bin(int.from_bytes(data[1:16], byteorder=sys.byteorder)))

input("Press Enter to stop...") # Wait for key

dut.switch_on_power_supply_voltages(0)  # switch off power supplies

dut.close()


