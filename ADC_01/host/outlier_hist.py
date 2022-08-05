import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
import statistics
import csv


# ----------------------------
# **** Read DATA from CSV ****
# this program is only to analyse the outliers   
# ----------------------------



# -------------------------------------------
# this procedure is copied from meas_hist.py 
# -------------------------------------------

def eval_hist(ADC_OUT,ADC_i,N,header_hist,STD_th):
    # raw data evaluation (raw_data=ADC_OUT!)
    # ADC_i:  iterations per A/D conversion
    # N:  samples     
    #  !!! for  STD > STD_th (threshold) the coresponding data-set will be ploted !!!   
    # ***************************************************
    # ---------------------------------------------------
    # **************** Statistics ***********************
    
    X= np.zeros((N,1),dtype=float)  
    Xn= np.zeros(10,dtype=float) # max data to be ploted 10 !!
    Ym= np.zeros(N,dtype=float)
    Ym_n= np.zeros(10,dtype=float)
    Ystd= np.zeros(N,dtype=float)
    Ystd_n= np.zeros(10,dtype=float)
    raw_data=ADC_OUT.astype(float)
    Yn=np.empty((1,ADC_i),dtype=int)

    M=0
    # computing STD  
    for j in range(N): #  N=len(VIN_DIFF)
        #print(raw_data[j][2:])
        X[j][0]= (raw_data[j][1])/1000 # diff. input in [mV] ||||| the LinearRegression requires 2D array of X !!
        Ym[j]=statistics.mean(raw_data[j][2:])
        Ystd[j]=statistics.stdev(raw_data[j][2:])
        if Ystd[j]>STD_th:  # select points of interest from 4095 samples / to be evaluated based on probability density function 
            if M==0:
                Yn[0][:]= ADC_OUT[j][2:]                
            else:
                Yn = np.append(Yn, [ADC_OUT[j][2:]], axis=0)
                
            Ystd_n[M]=Ystd[j]
            Ym_n[M]=Ym[j]
            Xn[M]=X[j][0]
            M=M+1
    print("the number of data-set to be ploted is: "+str(M))
    
    #  --- check the data size -------
    # ---- the number of samples should not be greater thean 10 !!! 

    if M>10:
        print("Too much data to plot !!!!! M samples should be less than 10")
        print("cannot evalute Histogram ... Exit prorgamm")
        return None
    else: 
        Y=np.zeros(ADC_i,dtype=int)
        calculus_out=np.zeros(5,dtype=float) # VDIFF |  MIN|MAX|Sigma|MEAN

        for n in range(M): # 
                      
            #print(Yn[n][:])
            #print("********************************************")
            
            Y[:]=Yn[n][:]
            calculus_out[0]=Xn[n] # diff. input in [mV] ||||| the LinearRegression requires 2D array of X !!
            calculus_out[1]=min(Y)
            calculus_out[2]=max(Y)
            calculus_out[3]=np.round(Ym_n[n],2)
            calculus_out[4]=np.round(Ystd_n[n],2)

            print(calculus_out)

            bins0=np.arange(min(Y)-4, max(Y)+4, 1)  #  
            plt.figure(n+1) # plt.subplot(N,1,j+1)
            n, bins, patches =plt.hist(Y,bins0,align='left',rwidth=0.8) #density=True
            plt.grid(True)
            plt.xlabel('[LSB]')
            plt.ylabel('[Count]')
            plt.legend(('sample set = '+str(ADC_i)+' |*| '+'VDIFF ='+str(calculus_out[0])+'[mV]'+' |*| '+'[MAX,MIN]='+str(calculus_out[2])+','+str(calculus_out[1])+' |*| '+'[u,s]='+str(calculus_out[3])+','+str(calculus_out[4]),''), loc='upper right')
        
        plt.show()           

# -------------------------------------------
# this procedure is copied from meas_hist.py 
# -------------------------------------------
    


print(" ++++++++ load data from CSV files ++++++++ \n")

ADC_i=128
N=4095 
ADC_OUT= np.zeros((N,ADC_i+2),dtype=int)  


# typical data size ! N sample =4096 / 128 iterations pro point  
# "ADC_i+2" --> to add VDIF and Number of sample to the result matrix

# ------------------------------------

CSV_FILE="../meas_results/20220518_re-test_updated_timimg/CH00/meas_out_file.csv" 

with open(CSV_FILE, newline='') as csvfile:
        DATA0 = list(csv.reader(csvfile, delimiter='\t'))
        header_0=DATA0[0][:]   # row 1 
        header_1=DATA0[1][:]   # row 2
        header_2=DATA0[2][:]   # row 3
        header_2_1=DATA0[3][:] # row 4
        header_3=DATA0[4][:]   # row 5

        #ADC_OUT=np.concatenate((np.int_(DATA0[20][:]),np.int_(DATA0[50][:])), axis=0) 
        ADC_OUT=np.int_(DATA0[5:][:])
               
        header_hist="header_0"

        # select points of interest from 4095 samples / to be evaluated based on probability density function 
        #  !! for  STD > STD_th (threshold) the coresponding data-set will be ploted !!  
        STD_th=1.2
        # ------------------------------------------------------

        eval_hist(ADC_OUT,ADC_i,N,header_hist,STD_th)
                
        
csvfile.close() # close the file


