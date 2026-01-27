#!/bin/bash

echo "Installing TermiChat..."
pip install -r requirements.txt
chmod +x app/main.py
echo "Done! Run with: python app/main.py"
