# Traderobots Enhancement Implementation Plan

## Cloudinary Configuration
- Cloud name: `drgpl4vsj`
- API key: `981145687422755`
- API secret: `FaMr1QHVULEUPsb7eMMHkiXDChQ`

## Phase 1: UI Enhancements ✅
### 1.1 Add Button Descriptions (Tooltips)
- Install/use ShadCN Tooltip component
- Add tooltips to all buttons across:
  - Dashboard (Sync MT5, Stop Robot, Open Controller, etc.)
  - RobotCreation (Generate AI Strategy, Deploy, Copy Code, etc.)
  - Robots page
  - Social page

### 1.2 Expand Currency Pairs
**Current pairs:** EURUSD, GBPUSD, USDJPY, AUDUSD, USDCAD, USDCHF, NZDUSD, BTCUSD, XAUUSD, XAGUSD

**Add:**
- **Forex:** EURGBP, EURJPY, GBPJPY, AUDJPY, NZDCAD, CADCHF, EURCHF, GBPCHF, EURAUD, GBPAUD
- **Crypto:** ETHUSD, LTCUSD, XRPUSD, ADAUSD, DOTUSD, SOLUSD, MATICUSD, AVAXUSD
- **Stocks:** AAPL, GOOGL, MSFT, AMZN, TSLA, NVDA, META, NFLX, SPY, QQQ

## Phase 2: Dashboard Enhancements ✅
### 2.1 Robot Deletion Functionality
- Add "Delete" button to each robot row
- Add "Delete All Robots" button at the top
- Implement confirmation dialogs
- Backend API endpoint: DELETE `/api/robots/{id}/`
- Backend API endpoint: DELETE `/api/robots/delete_all/`

### 2.2 Robot Selection During Sync
- Add dropdown in sync modal to select specific robot
- Update sync logic to use selected robot
- Store last used robot in localStorage

## Phase 3: Model Performance Visualizations 📊
### 3.1 Add Performance Charts
- Install recharts or chart.js
- Create performance visualization component
- Show metrics:
  - Win rate over time
  - Profit/Loss curve
  - Trade distribution
  - Account-specific performance
- Display per MT5 account device

### 3.2 Trade History Visualization
- Line chart for balance growth
- Bar chart for wins vs losses
- Pie chart for trade distribution by symbol

## Phase 4: RNN Robot Creation 🤖
### 4.1 UI Updates
- Add "RNN Model" option in robot creation
- Add years of data selector (1-10 years)
- Add training parameters:
  - Epochs
  - Batch size
  - Learning rate
  - LSTM units
  - Dropout rate

### 4.2 TensorFlow Code Generation
Create complete Google Colab-ready code that includes:
```python
# 1. Data fetching from Yahoo Finance/Alpha Vantage
# 2. Data preprocessing (normalization, windowing)
# 3. LSTM/RNN model architecture
# 4. Training loop with validation
# 5. Model evaluation
# 6. Cloudinary upload
# 7. Database update with model URL
```

### 4.3 Code Copy Button
- Generate full TensorFlow training script
- Add "Copy to Clipboard" button
- Add "Download as .ipynb" button
- Include all dependencies in requirements

## Phase 5: Cloudinary Integration ☁️
### 5.1 Backend Setup
```python
# Install cloudinary SDK
pip install cloudinary

# Configure in Django settings
import cloudinary
cloudinary.config(
    cloud_name='drgpl4vsj',
    api_key='981145687422755',
    api_secret='FaMr1QHVULEUPsb7eMMHkiXDChQ'
)
```

### 5.2 Model Upload Flow
1. User trains model in Google Colab
2. Colab script uploads .h5 file to Cloudinary
3. Colab script sends model URL to backend API
4. Backend stores URL in database
5. Local machine downloads model from Cloudinary
6. Model saved to `backend/ml/trained_models/{robot_id}.h5`
7. Push to GitHub

### 5.3 API Endpoints
- POST `/api/robots/rnn/upload_model/` - Receive model URL from Colab
- GET `/api/robots/rnn/{id}/download_model/` - Download model locally
- POST `/api/robots/rnn/create/` - Create RNN robot entry

## Phase 6: Database Schema Updates
```python
# Add to Robot model
class Robot(models.Model):
    # ... existing fields ...
    model_type = models.CharField(max_length=20, default='indicator')  # 'indicator' or 'rnn'
    model_url = models.URLField(null=True, blank=True)  # Cloudinary URL
    training_years = models.IntegerField(null=True, blank=True)
    model_params = models.JSONField(null=True, blank=True)  # epochs, batch_size, etc.
    model_performance = models.JSONField(null=True, blank=True)  # accuracy, loss, etc.
```

## Implementation Order
1. ✅ Add tooltips to all buttons
2. ✅ Expand currency pairs
3. ✅ Add robot deletion functionality
4. 🔄 Add RNN robot creation UI
5. 🔄 Generate TensorFlow training code
6. 🔄 Implement Cloudinary integration
7. 🔄 Add performance visualizations
8. 🔄 Test end-to-end flow
9. 🔄 Build and deploy to GitHub

## Testing Checklist
- [ ] All tooltips display correctly
- [ ] New currency pairs work in robot creation
- [ ] Robot deletion works (single and bulk)
- [ ] RNN code generation produces valid Python
- [ ] Cloudinary upload works from Colab
- [ ] Model download works on local machine
- [ ] Performance charts display correctly
- [ ] All type errors resolved
- [ ] Build succeeds
- [ ] GitHub push successful
