import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
import numpy as np

class RNNModel:
    @staticmethod
    def build_model(input_shape):
        model = Sequential([
            LSTM(units=50, return_sequences=True, input_shape=input_shape),
            Dropout(0.2),
            LSTM(units=50, return_sequences=False),
            Dropout(0.2),
            Dense(units=25),
            Dense(units=1)
        ])
        model.compile(optimizer='adam', loss='mean_squared_error')
        return model

    @staticmethod
    def train_model(model, x_train, y_train, epochs=25, batch_size=32):
        model.fit(x_train, y_train, epochs=epochs, batch_size=batch_size)
        return model

    @staticmethod
    def predict(model, data):
        return model.predict(data)
