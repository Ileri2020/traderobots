# Traderobots Platform

AI-driven forex and stock trading platform with social features and automated robot generation.

## How to Run Locally

### Prerequisites

- Python 3.10+
- Node.js 18+
- MongoDB (Local or Atlas)
- Metatrader 5 (For live trading integration)

### Setup & Launch

1. Ensure your `.env` file in the `backend/` directory is correctly configured (see `backend/.env.example`).
2. Run the automated startup script:
   ```bash
   ./start.bat
   ```
   _This will launch both the Django backend and Vite frontend in separate terminal windows._

## 🤖 Robot Creation Types

### 1. Indicator Win-Rate (Logic-Based)

This mode allows you to build a strategy using classic technical analysis.

- **Indicators**: RSI, Moving Averages, Bollinger Bands, and Stochastic Oscillators.
- **Process**:
  1. Select your symbol and timeframe (e.g., EURUSD, H1).
  2. Toggle indicators and adjust their parameters.
  3. The platform performs a **Real-Time Backtest** on historical data.
  4. Generates production-ready **MQL5 code** and a Python bridge for execution.

### 2. RNN Machine Learning (Neural/Deep Learning)

Leverages Recurrent Neural Networks (LSTM) to predict future price movements.

- **Architecture**: 3-Layer LSTM with Dropout regularization.
- **Process**:
  1. **Configuration**: Choose the depth of historical training data (1-10 years).
  2. **Generation**: The backend synthesizes a custom TensorFlow/Keras training script.
  3. **Training**: Copy the generated code to **Google Colab**.
  4. **Auto-Sync**: The script trains the model, saves it to Cloudinary, and automatically pings the Traderobots API with the model URL.
  5. **Activation**: Your robot becomes active on the dashboard, ready for deployment.

## 🚀 Key Features

- **Social Feed**: Share insights and copy trending strategies.
- **Dashboard**: Track performance across multiple MT5 accounts.
- **Auto-Deploy**: Launch orders directly to MetaTrader 5 from the UI.
- **Cloudinary Integration**: Secure storage for trained Neural models.

---

_Built with Django, React, Shadcn UI, and TensorFlow._
