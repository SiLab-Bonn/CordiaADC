import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
import statistics


def eval(ADC_OUT,ADC_i,N,header_eval):
    # raw data evaluation (raw_data=ADC_OUT!)
    # ADC_i:  iterations per A/D conversion
    # N:  samples     
    
    # ***************************************************
    # ---------------------------------------------------
    # **************** Statistics ***********************
       
    X= np.zeros((N,1),dtype=float)  
    Ym= np.zeros(N,dtype=float)
    Ym_shift= np.zeros(N,dtype=float)
    Ystd= np.zeros(N,dtype=float)
    NL_Err=np.zeros(N,dtype=float)
    DNL_Err=np.zeros(N,dtype=float)
    DNL_hist=np.zeros(2048,dtype=int)
    hist_bin = np.arange(2048,dtype=int)
    raw_data=ADC_OUT.astype(float)
    
  
    for j in range(N): #  N=len(VIN_DIFF)
        #print(raw_data[j][2:])
        X[j][0]= (raw_data[j][1])/1000 # diff. input in [mV] ||||| the LinearRegression requires 2D array of X !!
        Ym[j]=statistics.mean(raw_data[j][2:])
        Ystd[j]=statistics.stdev(raw_data[j][2:])
        # -- DNL Histogram Method 
        q=round(Ym[j])
        Qq=DNL_hist[q]
        DNL_hist[q]=Qq+1
        # ----END 
    
    
    linear_model = LinearRegression()   # 
    linear_model.fit(X, Ym)  # perform linear regression 
    RS = linear_model.score(X, Ym) # coefficient of determination 
    A1=linear_model.coef_ 
    A0=linear_model.intercept_
    # the NonLinearity error    
    Y0 = linear_model.predict(X)  # 
    NL_Err=np.round(Ym-Y0,2)  
    
    # ----- DNL ----------------------- 
    #estimating the ideal step for DNL claculus
    STEP_ideal=A1*(X[N-1][0]-X[0][0])/(N-1)  # estimated ideal input step with respect to SMU (in LSB)
      
    # if STEP_ideal<1:
        # STEP_ideal=1  
            
    Ym_shift=np.roll(Ym, 1)
    DNL_Err=np.round( ((Ym-Ym_shift)-STEP_ideal), 2)
    #DNL_Err=np.round((Ym-Ym_shift), 2)
    DNL_Err[0]=0 # the first value is not valid !   
    
    
    
    
    # write the results to CSV file 
    calculus_out=['coefficient of determination (Rs^2) :' + str(RS),'fitting coefficient (A0 ; A1) :'+str(A0)+';'+str(A1), 'MAX/MIN INL : ' + str(max(NL_Err)) + '/' + str(min(NL_Err)), 'MAX/MIN DNL : ' + str(max(DNL_Err)) + '/' + str(min(DNL_Err)),'estimated ideal input step (in LSB) '+str(STEP_ideal)  ]
    with open('INL_DNL_eval.txt', 'w') as out_file:
        out_file.write(header_eval)
        out_file.write('\n')
        out_file.write('|*|'.join(calculus_out))
        out_file.write('\n')
        out_file.write('==================== ++++  ++  Histogramm ++ ++++ ===========================')
        out_file.write('\n')
        out_file.write('================= counts / ADC output (m=0 .. 2047) ===========================')
        out_file.write('\n')
        np.savetxt(out_file,DNL_hist,fmt='%d')
    out_file.close()
    
    plt.figure(1)
    plt.subplot(3,1,1)
    plt.title(header_eval)
    #plt.xlabel('Delta Vin [mV]')
    plt.ylabel('[LSB]')
    plt.scatter(X, Ym)
    plt.plot(X, Y0, color='red')
    plt.legend(('fitted','Actual'), loc='upper right')
    plt.grid(True)
    plt.subplot(3,1,2)
    plt.plot(X, NL_Err, color='red')
    #plt.title('INL ERROR')
    plt.legend(('nonlinearity Error',''), loc='upper right')
    plt.ylabel('[LSB]')
    plt.grid(True)
    plt.subplot(3,1,3)
    plt.plot(X, DNL_Err, color='blue')
    #plt.title('DNL ERROR')
    plt.legend(('DNL Error',''), loc='upper right')
    plt.xlabel('Delta Vin [mV]')
    plt.ylabel('[LSB]')
    plt.grid(True)
    #DNL ERROR (Histo. Method)
    plt.figure(2)
    plt.bar(hist_bin, DNL_hist)
    #plt.title('DNL ERROR (Histo. Method)')
    plt.title(header_eval)
    plt.legend(('DNL Error (Histo. Method)',''), loc='upper right')
    plt.xlabel('Code')
    plt.ylabel('[counts]')   
    # STD vs X  // makes sens only if size of samples is larg enough !!  
    plt.figure(3)
    plt.title(header_eval)
    plt.xlabel('Delta Vin [mV]')
    plt.ylabel('STD [LSB]')
    plt.plot(X, Ystd, color='red')
    plt.legend(('standard deviation/population size (Number of iterations / sample): ' +str(ADC_i),''), loc='upper right')
    plt.grid(True)
    plt.show()


