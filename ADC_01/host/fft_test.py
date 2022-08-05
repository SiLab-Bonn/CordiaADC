# fft test
from re import S
import numpy as np 
import math
import matplotlib.pyplot as plt
from scipy.signal import blackmanharris, hamming, flattop, blackman, hann

def find_range(f, x):
    """
    Find range between nearest local minima from peak at index x
    """
    for i in np.arange(x+1, len(f)):
        uppermin = i
        if i==len(f)-1: break 
        if f[i+1] >= f[i]: break
    for i in np.arange(x-1, 0, -1):
        lowermin = i + 1
        if i==0: break
        if f[i] <= f[i-1]:break
    
    return (lowermin, uppermin)



N=8192  # number of samples (or ADC iteration "called ADC_i in meas.py!!")
Fs=2.5E6 # Fs : ADC sampling frequency in [M sample/sec]  
Ts=1/Fs   # sampling time [us]
F0=9765      # actual frequency of the input signal

A=1024 # Amplitude  of the input signal [LSB]
NCM=1024 # Common mode (digital) 
F_scale=1 # input scaling factor

# Number of samples per period 
Ns_period=Fs/F0
N_period=((N+1)/Ns_period)

# generation of the time array  
#t = np.arange(tau, N*Ts+tau, Ts)
tau=np.random.randint(0,int(Ns_period))*Ts  # arbitrary time offset "only for simulation" 
t=np.linspace(tau, tau+N*Ts,N)

# generation of the signal  array 
Sn=np.empty(len(t),dtype=int)
Sn=np.round(NCM+F_scale*A*np.sin(2*np.pi*F0*t)+np.random.normal(0, np.sqrt(1/12), size=len(t))) # signal + quantization noise 


#  !!! !!! it doesn't work because the FFT  select 2^N point !!! use adjusted frequency instead  !!!!! 
#selecting an entire number of periodes from the set of data (usefull for  FFT calculation)  ! 
# this is usefull for lower frequency (input-signal) wher the signal windowing doesn't influence much the resluts   
""" N0=int(np.round(np.fix(N/(Ns_periode))*(Ns_periode)))
N_periode=np.round(N0/Ns_periode)
Sn_win=np.empty(N0)
if N0<N-2: Sn_win[:]=Sn[2:N0+2] # just to avoid the first point !!  
else: Sn_win[:]=Sn[0:N0] # 
 """     
 
# Without selecting an entire number of periods from the set of data (useful for  FFT calculation)  ! 
# N0=N
# Sn_win=np.empty(N0)
# Sn_win[:]=Sn[:] 
# N_periode=(N0/Ns_periode)
# end ---

# Get rid of DC and window the signal / time spice ! 
Sn_win=np.empty(N)
Sn_win[:]=Sn[:] 
Sn_win -= np.mean(Sn)
SIG_WIN=[ 'hann', 'hamming', 'blackmanharris', 'blackman' , 'flattop']

# !!! ************************************************************************** !!!
# !! CPG : Coherent  power Gain  of Blackman-Harris --> Scaling Factor   due to windowing
# !! we cannot have both a valid amplitude and correct energy correction at the same time !!!
# use either  GPS_FACTOR_amp for correct amplitude and GPS_FACTOR_energy for correct energy  

GPS_FACTOR_amp=[N/np.sum(hann(N)), N/np.sum(hamming(N)), N/np.sum(blackmanharris(N)), N/np.sum(blackman(N)), N/np.sum(flattop(N))] # !! amplitude corection 
GPS_FACTOR_energy=[ np.sqrt(N/np.sum(hann(N)**2)) ,np.sqrt(N/np.sum(hamming(N)**2)),np.sqrt(N/np.sum(blackmanharris(N)**2)), np.sqrt(N/np.sum(blackman(N)**2)), np.sqrt(N/np.sum(flattop(N)**2))] # !! Energy corection !!


GPS_FACTOR=GPS_FACTOR_energy 

# choose window
i_win=4
if i_win==0: Sn_win = Sn_win  * hann(N)  
if i_win==1: Sn_win = Sn_win  * hamming(N)
if i_win==2: Sn_win = Sn_win  * blackmanharris(N)
if i_win==3: Sn_win = Sn_win  * blackman(N)
if i_win==4: Sn_win = Sn_win  * flattop(N)

# FFT computing 

Yf=np.fft.rfft(Sn_win)
Xf=np.linspace(0,Fs/2,len(Yf))
# Re-scaling FFT  
 
Yf_amp=np.empty(len(Yf))
Yf_amp[0]=(1/N) * np.abs(Yf[0]) #  DC component
Yf_amp[1:len(Yf)]=(2.0/N) * np.abs(Yf[1:len(Yf)])*GPS_FACTOR[i_win]  # 1 sided FFT and without DC component 
Yf_amp_DBFS= 20*np.log10(Yf_amp/(1024*F_scale))
#  Find the Fundamental-companant
i_fund = np.argmax(np.abs(Yf))


# SINAD calculus in time domain 
# Measure the total rms-signal before filtering but after windowing
total_rms = np.sqrt(np.mean(np.absolute(Sn_win)**2)) # Return the root mean square of all the elements 
# Measure the total rms-signal after filtering 
# Filtering : removing the Fundamental-companant from the spectrum !!
lowermin, uppermin = find_range(np.abs(Yf), i_fund)
Yf_DN=Yf*1   # distoration + noise 
Yf_DN[lowermin: uppermin] = 0 # noise + Harmonics
Yt_DN=np.fft.irfft(Yf_DN) # reverse FFT --> time domain ! 
THDN_rms = np.sqrt(np.mean(np.absolute(Yt_DN)**2)) # 
THDN = THDN_rms /total_rms
THDN_db=-20 * np.log10(THDN)

# SINAD calculus from frequency domain ! 

l0, m0 = find_range(Yf_amp, i_fund)
print("Fund range: " +str(l0) + "..." + str(m0))
Signal_power=np.sum((Yf_amp[l0:m0])**2)
Total_power=np.sum((Yf_amp[1:])**2)  # without DC !
DN_power = Total_power-Signal_power # distortion + noise power 
SINAD=10 * np.log10(Signal_power/DN_power)

# print('signal_power'+str(Signal_power))
# print('Total_power'+str(Total_power))
# print('DN_power'+str(DN_power))

print('FFT size :'+str(len(Yf)))
print('number of the sampled periods (after windowing)='+str(N_period)) 
print('actual frequency of the input signal=' +str(F0)) # actual frequency (applied to the input)
print('fundamental index: %d' % (i_fund )+' >> fundamental frequency: %f Hz' % (Xf[i_fund])) # fundamental frequency 
print('peak Amplitude @ fundamental frequency: %f LSB' % (Yf_amp[i_fund])) # fundamental frequency 
print('Energy around fundamental frequency: %f LSB' % (np.sqrt(Signal_power))) # fundamental frequency 
print('applied window: '+ str(SIG_WIN[i_win]) + ' >> Coherent  power Gain (correction factor)='+ str(GPS_FACTOR[i_win]))
print("THD+N:     %.4f%% or %.1f dB" % (THDN * 100, THDN_db))
print("SINAD:     %.1f dB " % (SINAD)+ "  >>  ENOB:     %.2f " % ((SINAD-1.76)/6.02))


plt.figure(1)
plt.ylabel('[LSB]')
plt.xlabel('Sample')
plt.plot(Sn_win)
plt.grid(True)
plt.figure(2)
plt.plot(Xf[1:], Yf_amp_DBFS[1:])
plt.xlabel('Freq[Hz]')
plt.ylabel('dBFS')
plt.grid(True)
# plt.figure(3)
# plt.plot(np.abs(Yf))
# plt.grid(True)
# plt.figure(4)
# plt.plot(np.abs(Yf_noise))
# plt.grid(True)
plt.show()



