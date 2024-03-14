import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import tensorflow as tf
from tensorflow import keras
import seaborn as sns
import os
from datetime import datetime
import yfinance as yf

import warnings
warnings.filterwarnings("ignore")

end_date = str(datetime.now().date())
data = yf.download('AAPL', start='2013-01-01', end=end_date)
print(data.shape)
print(data.sample(7))
print(data.info())

# index
data['date'] = data.index
data.info()

data['date'] = pd.to_datetime(data['date'])
# date vs open
# date vs close
# plt.figure(figsize=(15, 8))
# for index, company in enumerate(companies, 1):
# 	plt.subplot(3, 3, index)
# 	c = data[data['Name'] == company]
# 	plt.plot(c['date'], c['close'], c="r", label="close", marker="+")
# 	plt.plot(c['date'], c['open'], c="g", label="open", marker="^")
# 	plt.title(company)
# 	plt.legend()
# 	plt.tight_layout()
# plt.show()

# date vs high
# date vs low
# plt.figure(figsize=(15, 8))
# for index, company in enumerate(companies, 1):
#     plt.subplot(3, 3, index)
#     c = data[data['Name'] == company]
#     plt.plot(c['date'], c['high'], c="r", label="high", marker="+")
#     plt.plot(c['date'], c['low'], c="g", label="low", marker="^")
#     plt.title(company)
#     plt.legend()
#     plt.tight_layout()
# plt.show()

# date vs volume
# plt.figure(figsize=(15, 8))
# for index, company in enumerate(companies, 1):
#     plt.subplot(3, 3, index)
#     c = data[data['Name'] == company]
#     plt.plot(c['date'], c['volume'], c="r", label="volume", marker="+")
#     plt.title(company)
#     plt.legend()
#     plt.tight_layout()
# plt.show()


# plt.figure(figsize=(15, 8))
# for index, company in enumerate(companies, 1):
# 	plt.subplot(3, 3, index)
# 	c = data[data['Name'] == company]
# 	plt.plot(c['date'], c['volume'], c='purple', marker='*')
# 	plt.title(f"{company} Volume")
# 	plt.tight_layout()
# plt.show()

apple = data
prediction_range = apple.loc[(apple['date'] > datetime(2013, 1, 1)) & (apple['date'] < datetime(2018, 1, 1))]
plt.plot(apple['date'], apple['Close'])
plt.xlabel("Date")
plt.ylabel("Close")
plt.title("Apple Stock Prices")
plt.show()


close_data = apple.filter(['close'])
dataset = close_data.values
training = int(np.ceil(len(dataset) * .95))
print(training)

from sklearn.preprocessing import MinMaxScaler

scaler = MinMaxScaler()
scaled_data = scaler.fit_transform(dataset)

train_data = scaled_data[0:int(training), :]
# prepare feature and labels
x_train = []
y_train = []

for i in range(60, len(train_data)):
	x_train.append(train_data[i-60:i, 0])
	y_train.append(train_data[i, 0])

x_train, y_train = np.array(x_train), np.array(y_train)
x_train = np.reshape(x_train, (x_train.shape[0], x_train.shape[1], 1))

model = keras.models.Sequential()
model.add(keras.layers.LSTM(units=64,
							return_sequences=True,
							input_shape=(x_train.shape[1], 1)))
model.add(keras.layers.LSTM(units=64))
model.add(keras.layers.Dense(32))
model.add(keras.layers.Dropout(0.5))
model.add(keras.layers.Dense(1))
model.summary

model.compile(optimizer='adam',
			loss='mean_squared_error')
history = model.fit(x_train,
					y_train,
					epochs=10)

test_data = scaled_data[training - 60:, :]
x_test = []
y_test = dataset[training:, :]
for i in range(60, len(test_data)):
	x_test.append(test_data[i-60:i, 0])

x_test = np.array(x_test)
x_test = np.reshape(x_test, (x_test.shape[0], x_test.shape[1], 1))

# predict the testing data
predictions = model.predict(x_test)
predictions = scaler.inverse_transform(predictions)

# evaluation metrics
mse = np.mean(((predictions - y_test) ** 2))
print("MSE", mse)
print("RMSE", np.sqrt(mse))

train = apple[:training]
test = apple[training:]
test['Predictions'] = predictions

plt.figure(figsize=(10, 8))
plt.plot(train['Date'], train['Close'])
plt.plot(test['Date'], test[['Close', 'Predictions']])
plt.title('Apple Stock Close Price')
plt.xlabel('Date')
plt.ylabel("Close")
plt.legend(['Train', 'Test', 'Predictions'])
plt.show()

# predict the future 30 days
future = apple.filter(['Close'])
future = future[-60:].values
future = scaler.transform(future)
x_future = []
x_future.append(future)
x_future = np.array(x_future)
x_future = np.reshape(x_future, (x_future.shape[0], x_future.shape[1], 1))
future_predictions = model.predict(x_future)
future_predictions = scaler.inverse_transform(future_predictions)
print(future_predictions)
print(future_predictions[0][0])
