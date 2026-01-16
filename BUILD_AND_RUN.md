# Build and Run Guide (Production Mode)

This guide explains how to build the frontend and run the application in "production-like" mode locally, serving the built files and avoiding CORS issues.

## 1. Build the Frontend

First, compile the React application into static files:

```bash
cd frontend
npm run build
```

This creates a `dist` directory containing:

- `index.html`
- `assets/` (bundled JS, CSS)

## 2. Running the Application

There are three ways to run the built app.

### Option A: Serve via Django (Recommended for full integration)

The backend is configured to serve the frontend static files automatically if `DEBUG=False` or via Whitenoise.

1.  **Ensure Environment Variables**:
    Make sure your `backend/.env` has:

    ```
    DEBUG=True
    MONGO_URI=mongodb://localhost:27017/
    ```

    _Note: In development (DEBUG=True), Django typically doesn't serve static files from `dist` without extra config, but we have configured `STATICFILES_DIRS` to point to `frontend/dist`. You might need to run `collectstatic` if using Whitenoise._

2.  **Run Django**:

    ```bash
    cd backend
    python manage.py runserver 0.0.0.0:8000
    ```

3.  **Access**: Open `http://localhost:8000/`. You should see the React app served by Django. This avoids CORS completely as they are on the same origin.

### Option B: Serve Dist Separately (The "Dist Directory" Request)

If you want to explicitly verify the `dist` build works on its own server:

1.  **Run Backend**:

    ```bash
    cd backend
    python manage.py runserver 0.0.0.0:8000
    ```

2.  **Serve Frontend**:
    You can use `serve` (Node.js) or `python http.server`.

    **Using Node:**

    ```bash
    cd frontend
    npx serve -s dist -p 3000
    ```

    **Using Python:**

    ```bash
    cd frontend/dist
    python -m http.server 3000
    ```

3.  **Access**: Open `http://localhost:3000/`.

### 3. Avoiding CORS Errors

When using Option B (Frontend on 3000, Backend on 8000), Cross-Origin Resource Sharing (CORS) is enforced by the browser.

We have already configured the Backend to allow this.
File: `backend/traderobots/settings.py`

```python
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:5173",
]
CORS_ALLOW_CREDENTIALS = True
```

**Troubleshooting CORS:**

- **Credentials**: If you see "Credential is not supported if the CORS header 'Access-Control-Allow-Origin' is '\*'", ensure you are accessing `http://localhost:3000` and NOT an IP address unless that IP is in the allowed list.
- **Slash**: Ensure your API calls end with a slash (e.g., `/api/robots/`) as Django redirects can sometimes drop CORS headers.
- **Browser Cache**: Disable cache if testing changes.

## 4. Run the Consolidation Script

To capture all changes into a single file for analysis:

```bash
cd to/project/root
python consolidate_code.py
```

This generates `full_project_code.txt`.

## Summary of Recent Architectural Changes

We have implemented the "Historical-Data-Driven Conditional Execution" architecture.

1.  **Backend**: `StrategyAnalyzer` now computes probability-weighted entry zones instead of immediate execution.
2.  **Frontend**: Robot Creation Wizard now includes "Historical Training Configuration" (Lookback, Recency Bias, etc.).
3.  **API**: New endpoints `/preview_analysis/` and `/start_trade/` support the breakdown of "Signal" vs "Execution".

You can now test this flow in the app.
