#!/usr/bin/env python3
"""
ExploreIndonesia - Complete Application Launcher
Menjalankan FastAPI backend dan Streamlit frontend secara bersamaan
"""

import subprocess
import sys
import time
import os
from pathlib import Path

def run_api_server():
    """Run FastAPI server"""
    api_path = Path(__file__).parent / "api"
    os.chdir(api_path)
    
    print("🚀 Starting FastAPI server...")
    api_process = subprocess.Popen([
        sys.executable, "api.py"
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    return api_process

def run_streamlit_app():
    """Run Streamlit app"""
    website_path = Path(__file__).parent / "website"
    os.chdir(website_path)
    
    print("🌟 Starting Streamlit app...")
    streamlit_process = subprocess.Popen([
        sys.executable, "-m", "streamlit", "run", "app.py", 
        "--server.port=8501", 
        "--server.address=0.0.0.0",
        "--server.headless=true"
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    return streamlit_process

def main():
    print("="*60)
    print("🏝️  EXPLOREindonesia - AI Tourism Recommendations")
    print("="*60)
    print("Starting complete application stack...")
    print()
    
    try:
        # Start API server
        api_process = run_api_server()
        time.sleep(3)  # Wait for API to start
        
        # Check if API started successfully
        if api_process.poll() is None:
            print("✅ FastAPI server started successfully")
            print("   📡 API available at: http://localhost:8000")
            print("   📚 API docs at: http://localhost:8000/docs")
        else:
            print("❌ Failed to start API server")
            return
        
        print()
        
        # Start Streamlit app
        streamlit_process = run_streamlit_app()
        time.sleep(5)  # Wait for Streamlit to start
        
        # Check if Streamlit started successfully
        if streamlit_process.poll() is None:
            print("✅ Streamlit app started successfully")
            print("   🌐 Website available at: http://localhost:8501")
        else:
            print("❌ Failed to start Streamlit app")
            api_process.terminate()
            return
        
        print()
        print("="*60)
        print("🎉 Application is running!")
        print("="*60)
        print("🌐 Open your browser and go to: http://localhost:8501")
        print("📡 API documentation: http://localhost:8000/docs")
        print()
        print("Press Ctrl+C to stop both servers...")
        print("="*60)
        
        # Wait for user to stop
        try:
            while True:
                time.sleep(1)
                # Check if processes are still running
                if api_process.poll() is not None:
                    print("⚠️  API server stopped unexpectedly")
                    break
                if streamlit_process.poll() is not None:
                    print("⚠️  Streamlit app stopped unexpectedly")
                    break
        except KeyboardInterrupt:
            print("\n🛑 Stopping servers...")
            
    except Exception as e:
        print(f"❌ Error starting application: {e}")
    finally:
        # Clean up processes
        try:
            print("🧹 Cleaning up processes...")
            if 'api_process' in locals():
                api_process.terminate()
                api_process.wait(timeout=5)
            if 'streamlit_process' in locals():
                streamlit_process.terminate()
                streamlit_process.wait(timeout=5)
            print("✅ All processes stopped successfully")
        except Exception as e:
            print(f"⚠️  Error during cleanup: {e}")

if __name__ == "__main__":
    main()