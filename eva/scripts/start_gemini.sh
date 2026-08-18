#!/bin/bash
python3 -m venv myenv
source myenv/bin/activate || { echo "Activating virtual environment failed"; exit 1; }
pip install -U -r requirementsgemini.txt || { echo "Installing dependencies failed"; exit 1; }
python3 geminiapi_simple_generator.py || { echo "Running geminiapi.py failed"; exit 1; }