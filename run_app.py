import os
import sys
import subprocess
import webbrowser
from pathlib import Path
import time

def main():
    """
    Unified runner for the Traderobots application.
    Serves the Django backend which is configured to also serve the React frontend (dist).
    """
    ROOT_DIR = Path(__file__).resolve().parent
    BACKEND_DIR = ROOT_DIR / 'backend'
    FRONTEND_DIR = ROOT_DIR / 'frontend'
    DIST_DIR = FRONTEND_DIR / 'dist'

    print("[*] Traderobots Application Runner")
    print("=================================")

    # 1. Check if frontend build exists
    if not (DIST_DIR / 'index.html').exists():
        print(f"[!] Error: Frontend build not found in {DIST_DIR}")
        print("   Please run: cd frontend && npm run build")
        print("   Or use the build script if available.")
        
        choice = input("   Do you want to attempt building the frontend now? (y/n): ")
        if choice.lower() == 'y':
            print("   Building frontend... (this may take a minute)")
            try:
                subprocess.run(["npm", "run", "build"], cwd=FRONTEND_DIR, shell=True, check=True)
                print("   [+] Build successful!")
            except subprocess.CalledProcessError:
                print("   [!] Build failed. Please check node/npm setup.")
                sys.exit(1)
        else:
            sys.exit(1)

    # 2. Setup Environment
    print("[+] Frontend build detected.")
    
    # 3. Port check (optional, but good UX)
    # (Skipping for brevity, Django will complain if port is taken)

    # 4. Run Server
    print("[*] Starting Django Server on http://localhost:8000")
    print("   The app will automatically serve the React frontend.")
    print("   Press Ctrl+C to stop.")
    
    # Open browser after a short delay
    def open_browser():
        time.sleep(3)
        webbrowser.open("http://localhost:8000")
        
    import threading
    threading.Thread(target=open_browser, daemon=True).start()

    # Run Django
    # We use sys.executable to ensure we use the same python interpreter
    try:
        subprocess.run([sys.executable, "manage.py", "runserver", "0.0.0.0:8000"], cwd=BACKEND_DIR)
    except KeyboardInterrupt:
        print("\n[!] Server stopped.")

if __name__ == "__main__":
    main()
