import os
import sys
import webbrowser
import uvicorn

def main():
    print("=" * 70)
    print("  RAZORGUARD AI - AI RISK MANAGER & CHARGEBACK SENTINEL")
    print("  Razorpay AI Builder Internship 2026 (Track 02: AI Risk Manager)")
    print("=" * 70)
    print("Initializing Autonomous Defense Engine...")

    # Ensure artifacts exist
    if not os.path.exists("ml/artifacts/razorguard_model.joblib"):
        print("[Setup] Training machine learning risk classifier on benchmark dataset...")
        from ml.train_and_eval import train_and_evaluate
        train_and_evaluate(save_artifacts=True)
    else:
        print("[Setup] Verified ML model weights and benchmark metrics.")

    host = "127.0.0.1"
    port = 8000
    url = f"http://{host}:{port}"
    print(f"\n>> Starting Web Dashboard at {url}")
    print(">> Press Ctrl+C in terminal to stop server.")
    print("=" * 70)

    try:
        # Open browser automatically after 1 second
        import threading
        import time
        def open_browser():
            time.sleep(1.5)
            webbrowser.open(url)
        threading.Thread(target=open_browser, daemon=True).start()
    except Exception:
        pass

    uvicorn.run("app.main:app", host=host, port=port, reload=False)

if __name__ == "__main__":
    main()
