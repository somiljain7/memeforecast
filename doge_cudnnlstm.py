# -*- coding: utf-8 -*-
"""DOGE-CuDNNLSTM.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/16jP_QJ_aiG_yle3CCsG6ZlGd5UFwrIG7
"""

!pip install tensorflow

# Commented out IPython magic to ensure Python compatibility.
import os 
import numpy as np
import tensorflow as tf
from tensorflow import keras
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib import rc
from pylab import rcParams
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.layers import Bidirectional, Dropout ,Activation , Dense , LSTM
from tensorflow.python.keras.layers import CuDNNLSTM
from tensorflow.keras.models import Sequential
# %matplotlib inline

sns.set(style='whitegrid',palette='muted',font_scale=1.5)
rcParams['figure.figsize']=14,8
RANDOM_SEED = 42
np.random.seed(RANDOM_SEED)

from google.colab import files
uploaded = files.upload()

df = pd.read_csv('DOGE-USD-late.csv', parse_dates=['Date'])

df=df.sort_values('Date')

df

px = df.plot(x='Date',y='Close');
px.set_xlabel("Date")
px.set_ylabel("close_price(USD)");

"""YOU CAN SEE THAT PRICE OF DOGECOIN HAS PROGRESSED VERY UP AND UNTIL ELON MUSK **HOSTED** SNL

***DATA PREPERATION***
"""

#NORMALIZATION
scaler=MinMaxScaler()
close_price = df.Close.values.reshape(-1,1)
scaled_close = scaler.fit_transform(close_price)

scaled_close.shape

#to check whether any value is nan or not funct will return false or true
np.isnan(scaled_close).any()

df.dropna()

"""PREPROCESSING"""

SEQ_LEN=100
def to_sequences(data, seq_len):
  d=[]
  for index in range(len(data)-seq_len):
    d.append(data[index: index + seq_len])

  return np.array(d)

def preprocess(data_raw, seq_len,train_split):
  data = to_sequences(data_raw, seq_len) 
  num_train = int(train_split*data.shape[0])
  
  X_train = data[:num_train,:-1,:] 
  y_train  = data[:num_train,-1,:]
  X_test  = data[num_train:,:-1,:]
  y_test  = data[num_train:,-1,:]
  return X_train ,y_train, X_test, y_test

X_train ,y_train, X_test, y_test=preprocess(scaled_close, SEQ_LEN,train_split=0.95)

X_train.shape

y_train.shape

X_test.shape

"""MODEL"""

DROPOUT=0.2
WINDOW_SIZE= SEQ_LEN-1
model = keras.Sequential()
model.add(Bidirectional(CuDNNLSTM(WINDOW_SIZE,return_sequences=True),input_shape=(WINDOW_SIZE,X_train.shape[-1])))
model.add(Dropout(rate=DROPOUT))
model.add(Bidirectional(CuDNNLSTM((WINDOW_SIZE*2),return_sequences=True)))
model.add(Dropout(rate=DROPOUT))
model.add(Bidirectional(CuDNNLSTM(WINDOW_SIZE,return_sequences=False)))
model.add(Dense(units=1))
model.add(Activation('linear'))

#TRAINING
model.compile(
    loss='mean_squared_error',
    optimizer='adam'
)

BATCH_SIZE = 64
history = model.fit(
    X_train,
    y_train,
    epochs=50,
    batch_size=BATCH_SIZE,
    shuffle=False,
    validation_split=0.1
)

model.evaluate(X_test,y_test)

plt.plot(history.history['loss'])
plt.plot(history.history['val_loss'])
plt.title('model loss')
plt.ylabel('loss')
plt.xlabel('epoch')
plt.legend(['train','test'],loc = 'upper left')
plt.show()

#PREDICTION
y_hat=model.predict(X_test)
y_test_inv=scaler.inverse_transform(y_test)
y_hat_inv= scaler.inverse_transform(y_hat)
plt.plot(y_test_inv,label="Actual p",color='blue')
plt.plot(y_hat_inv,label="predicted p",color='red')
plt.title('DOGE COIN P PREDICTION')
plt.xlabel('[days]')
plt.ylabel('price')
plt.legend(loc='best')
plt.show();