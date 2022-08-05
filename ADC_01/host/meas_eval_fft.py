# FFT eval


from cProfile import label
from email import header
from re import S
import numpy as np 
import math
import matplotlib.pyplot as plt
from scipy.signal import blackmanharris, hamming, flattop, blackman, hann, find_peaks, argrelextrema
import csv


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

def compute_fft(ADC_OUT,Fs, F_SCALE):
    # Fs : ADC sampling frequency in [M sample/sec]
    Ts=1/Fs   # sampling time [us]
    # F_scale Scaling factor 
    # raw data evaluation (raw_data=ADC_OUT!)
    N=len(ADC_OUT) # N:  samples    
     #  time space  >>>>>>>>  windowing the signal / removing DC  / and re-scaling 
    Sn_win=np.empty(N)
    Sn_win[:]=ADC_OUT/F_SCALE  # Re-scaling the input 
    Sn_win -= np.mean(Sn_win)  # removing DC 
    SIG_WIN=[ 'hann', 'hamming', 'blackmanharris', 'blackman' , 'flattop']
    # !!! ************************************************************************** !!!
    # !! CPG : Coherent  power Gain  of Blackman-Harris --> Scaling Factor   due to windowing
    # !! we cannot have both a valid amplitude and correct energy correction at the same time !!!
    # use either  GPS_FACTOR_amp for correct amplitude and GPS_FACTOR_energy for correct energy  

    GPS_FACTOR_amp=[N/np.sum(hann(N)), N/np.sum(hamming(N)), N/np.sum(blackmanharris(N)), N/np.sum(blackman(N)), N/np.sum(flattop(N))] # !! amplitude corection 
    GPS_FACTOR_energy=[ np.sqrt(N/np.sum(hann(N)**2)) ,np.sqrt(N/np.sum(hamming(N)**2)),np.sqrt(N/np.sum(blackmanharris(N)**2)), np.sqrt(N/np.sum(blackman(N)**2)), np.sqrt(N/np.sum(flattop(N)**2))] # !! Energy corection !!
    GPS_FACTOR=GPS_FACTOR_energy 
    
    # select window
    i_win=2
    if i_win==0: Sn_win = Sn_win  * hann(N)  
    if i_win==1: Sn_win = Sn_win  * hamming(N)
    if i_win==2: Sn_win = Sn_win  * blackmanharris(N)
    if i_win==3: Sn_win = Sn_win  * blackman(N)
    if i_win==4: Sn_win = Sn_win  * flattop(N)
    # FFT computing
    Yf=np.fft.rfft(Sn_win) 
    N_fft=len(Yf)
    Xf=np.linspace(0,Fs/2,len(Yf))
     # Re-scaling FFT      
    Yf_amp=np.empty(len(Yf),float)
    Yf_amp[0]=(1/N) * np.abs(Yf[0]) *GPS_FACTOR[i_win]#  DC component
    Yf_amp[1:len(Yf)]=(2.0/N) * np.abs(Yf[1:len(Yf)]) *GPS_FACTOR[i_win] # 1 sided FFT and without DC component 

    # ***************************************************************** 
    # *********************** THD+N ***********************************
    # Measure the total rms-signal  after windowing (Time Spice)
    total_rms = np.sqrt(np.mean(np.absolute(Sn_win)**2)) # Return the root mean square of all elements 
    #  Find the Fundamental-companant
    i_fund = np.argmax(np.abs(Yf))
    # Measure the total rms-signal removing the Fundamental-companant from the spectrum !!
    lowermin, uppermin = find_range(np.abs(Yf), i_fund)
    Yf_DN=Yf*1   
    Yf_DN[lowermin: uppermin] = 0 # removing the Fundamental >>> noise + Harmonics
    Yt_DN=np.fft.irfft(Yf_DN) # reverse FFT --> time domain ! 
    THDN_rms = np.sqrt(np.mean(np.absolute(Yt_DN)**2)) # Measure the rms of noise + Harmonics   (Time Spice)
    THDN = THDN_rms /total_rms
    THDN_db=-20 * np.log10(THDN)
    # *****************************************************************
    
    # *****************************************************************
    # ************* SINAD calculus from frequency domain !   
    l0, m0 = find_range(Yf_amp, i_fund)
    Signal_power=np.sum((Yf_amp[l0:m0])**2)
    Total_power=np.sum((Yf_amp[1:])**2)  # without DC !
    DN_power = Total_power-Signal_power # distortion + noise power 
    SINAD=10 * np.log10(Signal_power/DN_power)
    ENOB=(SINAD-1.76)/6.02

    return(Yf_amp, N_fft,THDN, SINAD,i_fund, Signal_power, SIG_WIN[i_win], GPS_FACTOR[i_win])
         
                                                   
# load DATA from CSV 
print(" ++++++++ load DATA from CSV ++++++++ \n")
CSV_FILE="/faust/user/lhafiane/Desktop/untitled folder/meas_out_file_fft.csv" 
with open(CSV_FILE, newline='') as csvfile:
     DATA0 = list(csv.reader(csvfile, delimiter='\t'))
     # read the number of Samples   >>>>   N
     N=int(DATA0[4][1])
     # read the sampling and input freq. 
     Fs=float(DATA0[1][2])*1E6 #
     F0=float(DATA0[1][4]) #
     # read data data Integrity
     data_check=DATA0[3][0]
     # read DATA
     ADC_OUT=np.empty(N,dtype=int)
     for i in range(N):
      ADC_OUT[i]=int(DATA0[5][i])

     header_eval0=np.concatenate([DATA0[0][:], DATA0[1][:], DATA0[4][:]])
   
csvfile.close() # close the file

#  **************** only for test  **************************
#ADC_OUT[0,:]=ADC_OUT[0,:]+ np.random.normal(0, 10, size=N) #  adding noise to the data 
# ***********************************************************

# Number of samples per period 
Ns_period=Fs/F0
N_period=((N)/Ns_period)


# calculating the scale factor 
OUTPUT_mean= round(np.mean(ADC_OUT),3)  # the DC component  
OUTPUT_max= np.max(ADC_OUT)
OUTPUT_min= np.min(ADC_OUT)
OUTPUT_peak2peak=OUTPUT_max-OUTPUT_min
# estimating the amplitude based on RMS (to filter outlayers) 
X=ADC_OUT-OUTPUT_mean
OUTPUT_ac_rms= round(np.sqrt(np.mean(np.absolute(X)**2)),5)
OUTPUT_amp=round(OUTPUT_ac_rms*np.sqrt(2),5)
F_scale=round(OUTPUT_amp/1024,5)

print(data_check)
print("FFT-input DATA size : "+str(N))
print("Fs= "+str(Fs))
print("actual frequency of the input signal (F0)= "+str(F0))
print('number of the sampled periods (after windowing)='+str(N_period))
print("OUTPUT_mean= "+str(OUTPUT_mean))
print("OUTPUT_max= "+str(OUTPUT_max))
print("OUTPUT_min= "+str(OUTPUT_min))
print("OUTPUT_peak2peak= "+str(OUTPUT_peak2peak))
print("OUTPUT_ac_rms= "+str(OUTPUT_ac_rms))
print("OUTPUT_amp= "+str(OUTPUT_amp))
print("F_scale= "+str(F_scale))

header_eval=" ".join(header_eval0)


plt.figure(1)
plt.ylabel('[LSB]')
plt.xlabel('Samples')
plt.plot(ADC_OUT,label="data set")
plt.grid(True)
plt.title(header_eval)
plt.legend(loc="upper right")
plt.show()

# computing FFT for each individual set (M times !) 
N_FFT=(N//2)+1 # expected FFT size 

Xf=np.linspace(0,Fs/2,N_FFT)
 
Yf_amp, n_fft, THDN , SINAD, i_fund, Signal_power, SIG_WIN, GPS_FACTOR=compute_fft(ADC_OUT,Fs, F_scale)
Yf_amp_dBFS= 20*np.log10(Yf_amp/1024)
F_Fund=Xf[i_fund]



# THDN [%] -->  THDN [dB] SINAD[dB] -->  ENOB[BITs]
THDN_db=round(-20 * np.log10(THDN),3)
ENOB=round((SINAD-1.76)/6.02,3)
  

print(" **************** FFT output  *************************** ")    
if n_fft != N_FFT: print("FFT size matching error ! actual size not equal to the expected one")
else: print(" ***** expected FFT size OK  !! ***** ")
print("FFT size  : " + str(n_fft) )  
print("fundamental frequency [Hz]: " + str(F_Fund) + "|| index :" + str(i_fund))  # fundamental frequency
print("estimated power around the fundamental [dBc] / [LSB]  : " + str(round(20*np.log10((np.sqrt(Signal_power)/1024)),3)    )  + " / "  + str(round((np.sqrt(Signal_power)),2)) )  # estimated fundamental Power  
print("estimated power around the fundamental after scaling the back [LSB]  : " + str(round(np.sqrt(Signal_power)*F_scale, 2) )) 
print('applied window: '+ str(SIG_WIN) + ' >> Coherent  power Gain (Energy correction factor) ='+ str(round(GPS_FACTOR,5)))
print("THD+N [%]:"+str(round(100*THDN,5))+"  ||  THD+N [dB]:"+str(round(THDN_db,3) ) )   
print("SINAD [dB]:"+str(round(SINAD,3))+" >>>   ENOB[BITs] : "+str(ENOB)  )

# plot FFT data
plt.figure(2)
plt.plot(Xf[1:], Yf_amp_dBFS[1:],label="FFT")
plt.xlabel('Freq[Hz]') 
plt.ylabel('dBFS') 
plt.grid(True) 
plt.legend(loc="upper right")
plt.title(header_eval)   
plt.legend(loc="upper right")
plt.show()


# Write the DATA to CSV

print("  ==== ****** ====  writing data to csv file  ==== ***** ==== ")



with open('fft_eval.csv', 'w', newline='') as csv_out_file:
    writer = csv.writer(csv_out_file, delimiter='\t')
    writer.writerow(["F0 <Hz>","F_Fund <Hz>","F_scale","Signal_power [dBc]","ENOB [Bits]"])
    writer.writerow( [F0 , F_Fund, F_scale, 20*np.log10((np.sqrt(Signal_power)/1024)), ENOB ] )



csv_out_file.close()





   
