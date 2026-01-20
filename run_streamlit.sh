#!/bin/bash
cd /home/joaquim/Projects/Memorial-descritivo
source venv/bin/activate
export PYTHONPATH=/home/joaquim/Projects/Memorial-descritivo:$PYTHONPATH
streamlit run ui/app.py
