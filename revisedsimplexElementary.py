# -*- coding: utf-8 -*-
"""
Created on Sun May 31 16:17:09 2020

@author: Amruta, Arun, Harshitha, Shruti, Preethi
"""

import numpy as np
import re
import time

def main():
    # A is array of coefficients of variables in costraints.
    # C is array of coeeficients of variables in objective function.
    # b is array of RHS values.
    # variables is list of variables in the input.
    A,C,b,variables=getFileInput()
    m,n=A.shape
    # BVindices are indices of columns in A put in initial Basic variable matrix.
    # NBVindices are the remaining non-basic variable columns' indices.
    BVindices,NBVindices=getInitialBVindicesAndNBVindices(A,n,m)
    B=A[:,BVindices] # Basic variable matrix 
    Binv=B # Inverse of B
    while(1):    
        CB=C[np.array(BVindices)] # C based on B matrix      
        X=np.matmul(Binv,b)
        Z=np.matmul(CB,X)
        # Calculating Zj-Cj for optimality test as well as for entering column.
        ZC=getZjMinusCj(A,NBVindices,CB,Binv,C) 
    
        if(checkOptimalAndFeasible(ZC,n,m)):
            break
        # Get index of column entering from A.    
        enteringindex=getEnteringIndex(ZC) 
        enteringcolumn=np.copy(A[:,NBVindices[int(enteringindex)]]) # Get entering column from A.
        # Get index of column leaving from B
        leavingindex=minimumRatioTest(Binv,enteringcolumn,X,m)
    
        # Swapping leaving column index with entering column index for BVindices and vice versa for NBVindices.
        BVindices[int(leavingindex)],NBVindices[int(enteringindex)]=NBVindices[int(enteringindex)],BVindices[int(leavingindex)]   
        NBVindices.sort()
    
        Binv=matinverse2(Binv,leavingindex,enteringcolumn) # Inverse of B    

    for i in range(0,m):
        print(variables[BVindices[i]]+"="+str(X[i]))    
    print("Maximum value is "+str(Z))

def getFileInput():
    file = open("sample_input.txt","r")
    C_line  = file.readline().split(' Z = ')
    C_line[1]=C_line[1].replace(" ","")
    # Store variables into list
    # Variables must be of the form x or s or e or R followed by a digit.
    var_list = re.findall('[xseR][0-9]',C_line[1])
    # Store coefficients of variables in objective function 
    coefficients = re.split('[xseR][0-9]',C_line[1])
    coefficients.pop() # pop \n
    Clist = []
    for i in coefficients:
        Clist.append(int(i))
    
    content = file.read().split("\n")
    counter = 0
    A = []
    b= []
    for line in content:
        b1 = []
        line=line.replace(" ","")
        counter+=1
        # Store coefficients of variables in constraints 
        coeff = re.split('[xseR][0-9]',line)
        if(counter  == 1):
            coeff[0] = coeff[0].replace("Subjectedto", "")
        # Get last element (RHS) 
        temp = coeff.pop() 
        temp = temp.replace('=', '')
        temp = temp.replace('-','') # If RHS input is negative, absolute value is stored
        b1.append(int(temp))
        b.append(b1)
        a = []
        for i in coeff:
            a.append(int(i))
        A.append(a)
    C=np.asarray(Clist) # Coefficients of variables in objective function
    A = np.asarray(A) # Coefficients of variables in constraints 
    b = np.asarray(b) # RHS values
    return A,C,b,var_list

def getInitialBVindicesAndNBVindices(A,n,m):
    BVindices=[] # Indices of columns in A to be put in intial B matrix
    NBVindices=[]  # Indices of columns of Non-basic variables.   
    for i in range(0,n):
        zeroes=0
        ones=0
        column=np.copy(A[:,[i]])
        for j in column:
            if(int(j)==0):
                zeroes+=1
            elif(int(j)==1):
                ones+=1;
        # If a column has zeroes = no. of rows-1 and only a single one, then the column's index is stored in BVindices.
        if(zeroes==m-1 and ones==1):
            BVindices.append(int(i)) 
        else:
            NBVindices.append(int(i))      
    # Doing an insertion sort on column indices so that Identity matrix is formed from BVindices.
    for i in range(0,m):
        finished=False
        current=i
        while(current>0 and not finished):
            # Getting two successive columns from B and comparing the indices where one is present in both the columns.
            column1=np.copy(A[:,BVindices[current]])                
            column2=np.copy(A[:,BVindices[current-1]])
            oneindex1=np.where(column1==1) # returns index of 1 in a column.
            oneindex2=np.where(column2==1)
            if(oneindex1<oneindex2):
                # Swapping the two columns in B
                BVindices[current],BVindices[current-1]=BVindices[current-1],BVindices[current]
                current-=1
            else:
                finished=True
    return BVindices,NBVindices 

# Inverse calculation using elementary matrix
def matinverse2(Binv,leavingindex,enteringcolumn):
    n,m=Binv.shape
    d=np.matmul(Binv,enteringcolumn)
    # E is elementary matrix. One column in Identity is replaced by d.
    #E=np.identity(n) 
    #for i in range(0,n):
        #E[i][leavingindex]=d[i] 
    # E inverse will be E0 
    E0=np.identity(n)
    for j in range(0,n):
        if(j!=leavingindex):
            E0[j][leavingindex]=(-1*d[j])/d[leavingindex]
        elif(j==leavingindex):
            E0[j][leavingindex]=1/d[leavingindex]
    inverse = np.matmul(E0,Binv)
    return inverse   

def getZjMinusCj(A,NBVindices,CB,Binv,C):
    ZClist=[]
    for j in NBVindices:
        p=np.copy(A[:,[j]])
        ZClist.append(np.matmul(np.matmul(CB,Binv),p)-C[j])
    ZC=np.array(ZClist)
    return ZC

def checkOptimalAndFeasible(ZC,n,m):
    flag=0
    for l in range(0,n-m):
        if(ZC[l]>=0):
            flag+=1
    if(flag==(n-m)):
        return True
    else:
        return False

def getEnteringIndex(ZC):
    enteringindex,data=np.where(ZC==min(ZC))
    return enteringindex
    
def minimumRatioTest(Binv,enteringcolumn,X,m):
    Binvecolumn=np.matmul(Binv,enteringcolumn)
    leave=[]
    for i in range(0,m):
        if(Binvecolumn[i]>0):
            leave.append(X[i]/Binvecolumn[i]) 
    leavearr=np.array(leave)
    leavingindex,data=np.where(leavearr==min(leavearr))
    return leavingindex


start=time.time()  
main()
end=time.time()
print("Time for execution: ")
print(((end-start)*1000))