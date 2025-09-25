#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(__file__))

from main import app
import uvicorn

if __name__ == "__main__":
    print("Starting URL Shortener backend on port 8001...")
    uvicorn.run(app, host="0.0.0.0", port=8001, log_level="info")