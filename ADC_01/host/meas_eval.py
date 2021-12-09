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
    raw_data=ADC_OUT.astype(float)
  
    for j in range(N): #  N=len(VIN_DIFF)
        #print(raw_data[j][2:])
        X[j][0]= (raw_data[j][1])/1000 # diff. input in [mV] ||||| the LinearRegression requires 2D array of X !!
        
        Ym[j]=statistics.mean(raw_data[j][2:])
        Ystd[j]=statistics.stdev(raw_data[j][2:])
        
    
    
    
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
    LSB_ideal=A1*(X[N-1][0]-X[0][0])/(N-1) 
    Ym_shift=np.roll(Ym, 1)
    DNL_Err=np.round( (((Ym-Ym_shift)/LSB_ideal)-1), 2)
    DNL_Err[0]=0 # the first value is not valid !   
    
    # write the results to CSV file 
    calculus_out=['coefficient of determination (Rs^2) :' + str(RS),'fitting coefficient (A0 ; A1) :'+str(A0)+';'+str(A1), 'MAX/MIN INL : ' + str(max(NL_Err)) + '/' + str(min(NL_Err)), 'MAX/MIN DNL : ' + str(max(DNL_Err)) + '/' + str(min(DNL_Err)) ]
    with open('INL_DNL_eval.txt', 'w') as out_file:
        out_file.write(header_eval)
        out_file.write('\n')
        out_file.write('|*|'.join(calculus_out))
    out_file.close()

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
    #plt.title('INL ERROR')
    plt.legend(('DNL Error',''), loc='upper right')
    plt.xlabel('Delta Vin [mV]')
    plt.ylabel('[LSB]')
    plt.grid(True)
    plt.show()


