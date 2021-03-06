# -*- coding: utf-8 -*-
"""HW3_Classification_AvgSamples.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1S9uDNPVbC8DM8yblqlOF87sNLi7JOAx8
"""



pip install skorch

from sklearn.datasets import make_classification
from sklearn.metrics import accuracy_score
from sklearn.metrics import confusion_matrix
from skorch import NeuralNetClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn import preprocessing
from sklearn.model_selection import cross_val_predict
from sklearn.model_selection import GroupShuffleSplit
from skorch import NeuralNetRegressor
from sklearn.metrics import mean_squared_error
import seaborn as sns; sns.set()
import matplotlib as plt
import statistics 
import numpy as np
import re
import os
import pandas as pd
import librosa
import torch
from torch import nn
import pickle


# ==========================Define the required variables======================
Mean=[]
STD=[]
labels=[]
file_names_class=[]
file_names_regr=[]
All_mfccs=[]
noise_Values=[]
accuracy_classification=[]
accuracy_classification_Mean=[]
accuracy_classification_total=[]
accuracy_regression=[]
accuracy_regression_Mean=[]
accuracy_regression_total=[]
# ========================Store all .webm files in a list======================
path_to_webm=r'/content/Sounds'
webm_files = [pos_webm for pos_webm in os.listdir(path_to_webm) if pos_webm.endswith('.webm')] 

# ==============================Load the files=================================
n_mfcc=15
for k in webm_files:
        ff,sr = librosa.load(path_to_webm +  '//' + k) #load the files via librosa
        mfcc = librosa.feature.mfcc(y=ff, sr=sr, n_mfcc=n_mfcc) #Extract mfcc coefficients 
        
      # Append the Mean values of all coefficients into a list as Mean
        
     
        file_names_class.append('_'.join(k.split('_')[:1]))# Split the file names and get the class names for classification
                                                           #(e.g.'autos_JamshidiAvanaki_48dBA_1590939394506.webm'-->'autos')
                                                           
        file_names_regr.append('_'.join(k.split('_')[2:3]))# Split the file names and get the noise level for regression
                                                           #(e.g.'autos_JamshidiAvanaki_48dBA_1590939394506.webm'-->'48')
        mfcc_T=np.transpose(mfcc)
# =============================================================================
        mfcc_Mean=np.mean(mfcc_T, axis=0) 
        Mean.append(mfcc_Mean)
        labels.append(file_names_class[-1])
        #for i in range (0,np.shape(mfcc_T)[0]):
             #mfcc_Mean=mfcc_T[i]

             #mfcc_Mean=np.mean(mfcc_T[i:i+17] , axis=0)
             #mfcc_STD=np.std(mfcc_T[i:i+17] , axis=0)
             #Mean.append(mfcc_Mean)
             #STD.append(mfcc_STD)
             #labels.append(file_names_class[-1])

             #labels.append(file_names_class[-1])
# =============================================================================
for k in file_names_regr:
    noise_Values.append(int(re.search(r'\d+', k).group()))# Store all noise values as int at noise_Values list 

     
df_class_names = pd.DataFrame(labels)# Convert list to DataFrame
df_noise_Values = pd.DataFrame(noise_Values)# Convert list to DataFrame
df_mfcc_Mean = pd.DataFrame(Mean)# Convert list to DataFrame
#df_mfcc_Mean = pd.DataFrame(df_Mean)# Convert list to DataFrame

# ============================Encode the class labels===========================  
labelencoder = LabelEncoder()# Create instance of labelencoder
df_class_names = labelencoder.fit_transform(df_class_names) # Assign numerical values for df_class_names

# ========Define the Features and Labels for Classification and Regression=====

# Define X as features and y as lable for Classification part
X=(df_mfcc_Mean).to_numpy()
y=df_class_names
X = X.astype(np.float32) # Change the type of X to float32
y = y.astype(np.int64) # Change the type of y to int64 
  
# Define X_regr as features and y_regr as lable for Regression part
X_regr = X
y_regr=(df_noise_Values).to_numpy()
y_regr = y_regr.astype(np.float32)/100
y_regr = y_regr.reshape(-1, 1)   

# ===============Preprocessing the features using StandardScaler===============
scaler = preprocessing.StandardScaler()
X = scaler.fit_transform(X) # Transform the feature
X_regr = scaler.fit_transform(X_regr)

# ========================Neural Network for Classification====================
class Net(torch.nn.Module):
     def __init__(self):
         '''
         A feedForward neural network.
         Argurmets:
             n_feature: How many of features in your data
             n_hidden:  How many of neurons in the hidden layer
             n_output:  How many of neuros in the output leyar (defaut=1)
         '''
         super(Net, self).__init__()
         self.hidden = torch.nn.Linear(n_mfcc, 100, bias=True) # hidden layer
         self.predict = torch.nn.Linear(100, 9, bias=True) # output layer
     def forward(self, x,**kwargs):
         '''
         Argurmets:
             x: Features to predict
         '''
         torch.nn.init.constant_(self.hidden.bias.data,1)
         torch.nn.init.constant_(self.predict.bias.data,1)
         x = torch.sigmoid(self.hidden(x))  # activation function for hidden layer
         x = torch.sigmoid(self.predict(x)) # linear output
         return x
 
# ====================== Define the Classification Network=====================
net_class = NeuralNetClassifier(
    Net,
    max_epochs=10,
    lr=0.1,
    verbose=1,
)   

# =================Split the dataset using GroupShuffleSplit===================
gss= GroupShuffleSplit(n_splits=10,test_size=0.15, random_state=None) 
gss.get_n_splits(X,y,groups=y)
for train_index, test_index in (gss.split(X,y, groups=y)):
    print("TRAIN:", train_index, "TEST:", test_index)
    X_train,X_test = X[train_index],X[test_index]
    y_train,y_test = y[train_index],y[test_index]
    
# ==============================Train the model================================
    net_class.fit(X_train, y_train)
    
# ================Test/Validate the model via 10fold crossValidation===========
    y_class_pred=cross_val_predict(net_class, X_test, y_test, cv=10)
    
# ============================ Evaluate the model =============================
    score=accuracy_score(y_class_pred, y_test)
    accuracy_classification.append(score)
#accuracy_classification_Mean = statistics.mean(accuracy_classification)
#accuracy_classification_total.append(accuracy_classification_Mean)

from matplotlib import pyplot as plt
from sklearn.metrics import plot_confusion_matrix
plot_confusion_matrix(net_class, X_train, y_train)  # doctest: +SKIP

plot_confusion_matrix(net_class, X_test, y_test)  # doctest: +SKIP

plt.show() 
plt.savefig('all_samples.png')