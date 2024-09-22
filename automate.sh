#!/bin/bash

# Upgrading pip and other dependencies
pip install --upgrade pip setuptools wheel

echo "Installing requirements..."
pip install -r requirements.txt

# Change to test directory
cd test

echo "****************************************************************"
echo "****************************************************************"
echo "Running test_pub_sub.py..."
python test_pub_sub.py

echo "****************************************************************"
echo "****************************************************************"
echo "Running test_multi_pub_sub.py..."
python test_multi_pub_sub.py

echo "****************************************************************"
echo "****************************************************************"
echo "Running test_ping_pong.py..."
python test_ping_pong.py

echo "****************************************************************"
echo "****************************************************************"
echo "Running benchmark_pub_sub.py..."
python benchmark_pub_sub.py

echo "****************************************************************"
echo "****************************************************************"
echo "Running benchmark_ping_pong.py..."
python benchmark_ping_pong.py

echo "All scripts executed successfully!"
