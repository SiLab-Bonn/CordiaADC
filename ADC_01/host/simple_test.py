
import time
import _thread
import yaml
import sys
import pyvisa as visa

from basil.dut import Dut
import serial


#rm=visa.ResourceManager()
#print(rm.list_resources())
#dev=rm.open_resource('ASRL/dev/ttyUSB0')
#print(dev.query('*IDN?'))
#dut_AWG = Dut("agilent_33250a.yaml") # AWG Arbitrary Waveform Generator
#dut_AWG.init()
#dut_AWG['Pulser'].set_voltage_high(1.0)
#


# rm=visa.ResourceManager()
# print(rm.list_resources())
# dev=rm.open_resource('ASRL5::INSTR')
# dev.timeout=1
# dev.send_end=False
# dev.baud_rate = 57600
# dev.read_termination = '\n'
# dev.write_termination = '\n'
# dev.write('APPL:SIN 5 KHZ, 3.0 VPP, -2.5 V')
#dev.read_bytes(1)
#print(dev.query('*IDN?'))
#print(dev.query("*IDN?"))


ser = serial.Serial('COM5', 57600, timeout=3, dsrdtr=False)  # open serial port
print(ser)
#print(ser.port)         # check which port was really used
#print(ser.baudrate)
#print(ser.parity)
print(ser.readline())   # read a '\n' terminated line
ser.write(b'APPL:SIN 5 KHZ, 3.0 VPP, -2.5 V')     # write a string
print(ser.readline())   # read a '\n' terminated line
ser.close()             # close port






# dut_SMU = Dut("keithley_2602a.yaml")
# dut_SMU.init()
# dut_SMU['SMU'].on(channel=1)
# dut_SMU['SMU'].on(channel=2)
# dut_SMU['SMU'].source_volt(channel=1)
# dut_SMU['SMU'].source_volt(channel=2)
# dut_SMU['SMU'].set_current_limit(0.005, channel=1)
# dut_SMU['SMU'].set_current_limit(0.005, channel=2)
# dut_SMU['SMU'].set_voltage_limit(1.4, channel=1)
# dut_SMU['SMU'].set_voltage_limit(1.4, channel=2)
# dut_SMU['SMU'].set_voltage_range(1.2,channel=1)
# dut_SMU['SMU'].set_voltage_range(1.2,channel=2)
# 

# dut_SMU['SMU'].set_voltage(0.6, channel=1)
# dut_SMU['SMU'].set_voltage(0.6, channel=2)
# print(dut_SMU['SMU'].get_voltage() 




# 


















