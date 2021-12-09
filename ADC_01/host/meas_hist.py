import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
import statistics


def eval_hist(ADC_OUT,ADC_i,N,header_hist):
    # raw data evaluation (raw_data=ADC_OUT!)
    # ADC_i:  iterations per A/D conversion
    # N:  samples     
    
    # ***************************************************
    # ---------------------------------------------------
    # **************** Statistics ***********************

    #  --- check the data size -------
    # ---- the number of samples should not be greater thean 10 !!! 

    if N>10:
        print("Too much data to plot !!!!! N samples should be less than 10")
        print("cannot evalute Histogram ... Exit the prorgamm")
        return None
    else: 
        X= np.zeros((N,1),dtype=float)  
        Ym= np.zeros(N,dtype=float)
        Y=np.zeros(ADC_i,dtype=int)
        Ystd= np.zeros(N,dtype=float)
        calculus_out=np.zeros((N,5),dtype=float) # VDIFF |  MIN|MAX|Sigma|MEAN
        plt.subplot(N,1,1)
        plt.title(header_hist)        
        raw_data=ADC_OUT.astype(float)
        for j in range(N): #  N=len(VIN_DIFF)
            #print(raw_data[j][2:])
            X[j]= (raw_data[j][1])/1000 # diff. input in [mV] ||||| the LinearRegression requires 2D array of X !!
            Y[:]=raw_data[j][2:]
            Ym[j]=np.round(statistics.mean(raw_data[j][2:]),2)
            Ystd[j]=np.round(statistics.stdev(raw_data[j][2:]),2)
            calculus_out[j][0]=X[j]
            calculus_out[j][1]=min(Y)
            calculus_out[j][2]=max(Y)
            calculus_out[j][3]=Ym[j]
            calculus_out[j][4]=Ystd[j]                                                            
            bins0=np.arange(min(Y)-4, max(Y)+4, 1)  #  
            plt.subplot(N,1,j+1)
            n, bins, patches =plt.hist(Y,bins0,align='left',rwidth=0.8) #density=True
            plt.grid(True)
            plt.legend(('input ='+str(X[j])+'[mV]'+'||'+'[u,s]='+str(Ym[j])+','+str(Ystd[j]),''), loc='upper right')
        # write the results to TEXT file 
        header_0=' VDIFF [mV] | MIN [LSB] | MAX [LSB] | Sigma [LSB] | MEAN [LSB]'
        with open('Stat.txt', 'w') as out_file:
            out_file.write(header_hist)
            out_file.write('\n')
            out_file.write(header_0)
            out_file.write('\n')
            out_file.write(str(calculus_out))
        out_file.close()
    #print(Y)
    #print(Ystd)
    plt.show()           
                                                                                                                                     

