#
# ------------------------------------------------------------
# Copyright (c) SILAB , Physics Institute of Bonn University
# ------------------------------------------------------------
#
# SVN revision information:
#  $Rev:: 418                   $:
#  $Author:: HK    $:
#  $Date:: 2015-01-04 10:56:36 #$:
#

from basil.dut import Dut
from pylab import *
import matplotlib.pyplot as plt
import numpy as np
import time as time

import ADC01_constants as c

class adc01(Dut):
	def init(self, init_conf=None, **kwargs):
		Dut.init(self, init_conf=init_conf, **kwargs)
		return
		
	def close(self):
		self.switch_on_power_supply_voltages(0)
		self['SEQ'].clear()
		Dut.close(self)		
		return


	def switch_on_power_supply_voltages(self,pwr_en):
		"""
		Switches on default supply voltages
		"""
		if(pwr_en):
			self['VDDIO'].set_current_limit(100, unit='mA')
		#Power
			self['VDDIO'].set_voltage(1.2, unit='V')
			self['VDDIO'].set_enable(pwr_en)
			self['VDDD'].set_voltage(1.2, unit='V')
			self['VDDD'].set_enable(pwr_en)
			self['VDDA'].set_voltage(1.2, unit='V')
			self['VDDA'].set_enable(pwr_en)

			time.sleep(0.01)
			print('')
			print('VDDIO:\t', format(self['VDDIO'].get_voltage(unit='V'), '.3f'), 'V\t', format(self['VDDIO'].get_current(), '.3f'), 'mA')
			print('VDDD:\t', format(self['VDDD'].get_voltage(unit='V'), '.3f'), 'V\t', format(self['VDDD'].get_current(), '.3f'), 'mA')
			print('VDDA:\t', format(self['VDDA'].get_voltage(unit='V'), '.3f'), 'V\t', format(self['VDDA'].get_current(), '.3f'), 'mA')
			print('')
		else:
			self['VDDIO'].set_enable(pwr_en)
			self['VDDD'].set_enable(pwr_en)
			self['VDDA'].set_enable(pwr_en)
		return
	
	def get_status(self):
		status = {}
		status['Time'] = time.strftime("%d %M %Y %H:%M:%S")
		status['VDDIO'] = {'voltage(V)':format(self['VDDIO'].get_voltage(unit='V'), '.3f'), 'current(mA)':  format(self['VDD'].get_current(), '.3f' )}
		status['VDDD'] = {'voltage(V)':format(self['VDDD'].get_voltage(unit='V'), '.3f'), 'current(mA)':  format(self['VDD'].get_current(), '.3f' )}
		status['VDDA'] = {'voltage(V)':format(self['VDDA'].get_voltage(unit='V'), '.3f'), 'current(mA)':  format(self['VDD'].get_current(), '.3f' )}
		return status
	
	def select_channel(self,ch):
		self['GPIO']['SEL'] = ch
		return
	

	

		
	



	

