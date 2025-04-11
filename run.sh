#!/bin/bash
echo "Activating virtual environment..."
cd /opt/projects/Ain_RaqimAiServices/ || cd /opt/Ain_RaqimAiServices/ || exit
source env/bin/activate
echo "Running raqim..."
python3 runServices.py
