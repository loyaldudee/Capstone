"""
Server Runner Alias
-------------------
Imports the FastAPI application instance from main.py and runs uvicorn.
Supports:
  - py .\server.py
  - uvicorn main:app --reload
  - uvicorn server:app --reload
"""

import sys
import os

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from main import app

if __name__ == "__main__":
    import uvicorn
    print("\n" + "=" * 65)
    print("  AEGIS INSURANCE CLAIMS INTELLIGENCE ASSISTANT")
    print("  Launching via server.py -> http://127.0.0.1:8000")
    print("=" * 65 + "\n")
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
