import os
from datetime import datetime

def consolidate_code(root_dir, output_file):
    # Directories to skip
    skip_dirs = {
        'node_modules', 'venv', 'env', '.venv', '__pycache__', 
        '.git', '.next', 'dist', 'build', '.vercel', 'public', 'assets',
        'migrations', 'staticfiles', 'forex_data', 'trading_data', '.vscode'
    }
    
    # Files to skip
    skip_files = {
        'package-lock.json', 'yarn.lock', 'pnpm-lock.yaml', 
        '.DS_Store', 'mql5.pdf', 'consolidate_code.py',
        '.gitignore', '.env', 'tsconfig.json', 'package.json',
        'postcss.config.js', 'tailwind.config.js', 'components.json',
        'eslint.config.js', 'vite.config.ts', 'tsconfig.app.json',
        'tsconfig.node.json', 'full_project_code.txt', 'seed_indicators.py',
        'test_mongo.py', 'hello.py', 'index.py', 'populate_db.py',
        'populate_extra.py', 'verify_prod.py', 'error_resp.html',
        'diagnose_mt5.py', 'test_fetch.py', 'test_login.py', 'test_yf.py',
        'test_yf_raw.py', 'test_data_api.py', 'verify_fixes_script.py',
        'test_mt5_connection.py', 'test_data_service_save.py'
    }
    
    # Extensions to include
    include_extensions = {
        '.py', '.js', '.ts', '.tsx', '.jsx', '.html', '.css', '.md'
    }

    file_count = 0
    
    with open(output_file, 'w', encoding='utf-8') as outfile:
        # Write comprehensive header
        outfile.write("=" * 80 + "\n")
        outfile.write("TRADEROBOTS PLATFORM - CONSOLIDATED CODE & DOCUMENTATION\n")
        outfile.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        outfile.write("=" * 80 + "\n\n")
        
        # Write project overview
        outfile.write("=" * 80 + "\n")
        outfile.write("PROJECT OVERVIEW\n")
        outfile.write("=" * 80 + "\n\n")
        
        outfile.write("""
## TRADEROBOTS - AI-Powered Trading Platform

### Architecture
- **Backend:** Django REST Framework + MongoDB (via Djongo)
- **Frontend:** React + TypeScript + Vite + Shadcn UI
- **Trading:** MetaTrader 5 Python API Integration
- **Data Sources:** MT5 + YFinance (fallback)

### Key Features
1. **Automated Robot Creation**
   - Logic-based strategies (RSI, MA, MACD, Bollinger Bands, Stochastic)
   - Neural network strategies (RNN/LSTM)
   - Backtesting engine
   - MQL5 & Python code generation

2. **MT5 Integration**
   - Auto-launch terminal
   - Connection health monitoring
   - EA deployment with confirmation
   - Watchdog service for auto-recovery
   - Per-user isolation support

3. **Social Features**
   - Community posts
   - Robot sharing
   - Performance leaderboards

4. **Account Management**
   - Multiple MT5 accounts per user
   - Encrypted credentials
   - Account guardrails
   - Emergency kill switch

### Database Structure (MongoDB)

**Collections:**
- `auth_user` - User accounts
- `api_tradingaccount` - MT5 account credentials
- `api_robot` - Trading robots
- `api_robotbuildtask` - Async build tasks
- `api_robotbuildreport` - Data fetching reports
- `api_strategyversion` - Robot version history
- `api_deploymentvalidation` - 3-phase deployment tracking
- `api_robotevent` - Robot lifecycle events
- `api_tradelog` - Trade execution logs
- `api_accountguardrail` - Risk management rules
- `api_emergencykillswitch` - Emergency stop mechanism
- `api_indicatortemplate` - Predefined indicator configs
- `social_post` - Community posts
- `social_comment` - Post comments
- `social_like` - Post likes

### API Endpoints

**Authentication:**
- POST /api/users/login/
- POST /api/users/logout/
- POST /api/users/register/

**Trading Accounts:**
- GET /api/accounts/
- POST /api/accounts/
- GET /api/accounts/mt5/status/
- POST /api/accounts/mt5/reconnect/
- POST /api/accounts/mt5/start-watchdog/
- GET /api/accounts/ea/status/{robot_id}/

**Robots:**
- GET /api/robots/
- POST /api/robots/create_winrate_robot/
- POST /api/robots/create_rnn_robot/
- POST /api/robots/{id}/deploy/
- POST /api/robots/{id}/start_trade/
- GET /api/robots/{id}/download_mql5/
- GET /api/robots/{id}/download_python/

**Social:**
- GET /api/social/posts/
- POST /api/social/posts/
- POST /api/social/posts/{id}/like/
- POST /api/social/posts/{id}/comment/

### File Structure

**Backend:**
- `backend/api/` - REST API views, serializers, models
- `backend/trading/` - MT5 integration, data services, robot generation
  - `mt5_connector.py` - Core MT5 connection manager
  - `mt5_watchdog.py` - Health monitoring & auto-recovery
  - `ea_manager.py` - EA deployment & confirmation
  - `user_mt5_manager.py` - Per-user isolation
  - `data_service.py` - Historical data fetching
  - `robot_generator.py` - MQL5/Python code generation
  - `backtester.py` - Strategy backtesting
- `backend/ml/` - Machine learning models
- `backend/social/` - Social features

**Frontend:**
- `frontend/src/pages/` - Main application pages
- `frontend/src/components/` - Reusable UI components
- `frontend/src/lib/` - Utilities and helpers

### Environment Variables Required

```env
# MT5 Configuration
MT5_LOGIN=your_account_number
MT5_PASSWORD=your_password
MT5_SERVER=your_broker_server
MT5_PATH=C:\\Program Files\\MetaTrader 5\\terminal64.exe

# Database
MONGO_URI=mongodb+srv://...

# Django
SECRET_KEY=your_secret_key
DEBUG=True

# OAuth (optional)
GOOGLE_OAUTH_CLIENT_ID=...
GOOGLE_OAUTH_CLIENT_SECRET=...
FACEBOOK_OAUTH_CLIENT_ID=...
FACEBOOK_OAUTH_CLIENT_SECRET=...

# Cloudinary (for RNN models)
CLOUDINARY_CLOUD_NAME=...
CLOUDINARY_API_KEY=...
CLOUDINARY_API_SECRET=...
```

### Production Features

1. **EA Injection Confirmation**
   - Verifies EA loaded via global variables
   - Monitors heartbeat files
   - Multi-stage deployment validation

2. **MT5 Watchdog**
   - Continuous health monitoring
   - Auto-recovery from crashes
   - IPC connection management

3. **Per-User Isolation**
   - Separate MT5 data directories
   - Isolated terminal instances
   - Safe multi-user trading

""")
        
        outfile.write("\n" + "=" * 80 + "\n")
        outfile.write("SOURCE CODE FILES\n")
        outfile.write("=" * 80 + "\n\n")
        
        for root, dirs, files in os.walk(root_dir):
            # Prune directories in-place to avoid walking into skipped dirs
            dirs[:] = [d for d in dirs if d not in skip_dirs]
            
            for file in files:
                if file in skip_files:
                    continue
                
                ext = os.path.splitext(file)[1].lower()
                if ext not in include_extensions:
                    continue
                
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, root_dir)
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as infile:
                        content = infile.read()
                    
                    # Skip very large files
                    if len(content) > 500000:  # 500KB limit
                        print(f"Skipped (too large): {relative_path}")
                        continue
                        
                    outfile.write("\n" + "=" * 80 + "\n")
                    outfile.write(f"FILE: {relative_path}\n")
                    outfile.write("=" * 80 + "\n\n")
                    outfile.write(content)
                    outfile.write("\n\n")
                    print(f"Added: {relative_path}")
                    file_count += 1
                except Exception as e:
                    print(f"Could not read {relative_path}: {e}")
        
        # Write footer
        outfile.write("\n" + "=" * 80 + "\n")
        outfile.write(f"TOTAL FILES CONSOLIDATED: {file_count}\n")
        outfile.write("=" * 80 + "\n")

if __name__ == "__main__":
    project_root = os.path.dirname(os.path.abspath(__file__))
    output_filename = "full_project_code.txt"
    print(f"Starting consolidation in {project_root}...")
    consolidate_code(project_root, output_filename)
    print(f"\nDone! All code consolidated into {output_filename}")
    print(f"Output file size: {os.path.getsize(output_filename) / 1024:.2f} KB")
