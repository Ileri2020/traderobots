try:
    import tensorflow as tf
    from tensorflow.keras.models import Sequential
    from tensorflow.keras.layers import LSTM, Dense, Dropout
    HAS_TENSORFLOW = True
except ImportError:
    HAS_TENSORFLOW = False

import numpy as np

class RNNModel:
    @staticmethod
    def build_model(input_shape):
        if not HAS_TENSORFLOW:
            print("TensorFlow not available. Skipping RNN model build.")
            return None
            
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
        if not HAS_TENSORFLOW or model is None:
            return None
        model.fit(x_train, y_train, epochs=epochs, batch_size=batch_size)
        return model

    @staticmethod
    def predict(model, data):
        if not HAS_TENSORFLOW or model is None:
            return np.zeros((len(data), 1))
        return model.predict(data)
