#!/bin/bash

echo "Testing 'organization create'..."
./restya-cli.py organization create -o "Organization #1"
./restya-cli.py organization create -o "Organization #2"
./restya-cli.py organization create -o "Organization #3"
echo
echo "Checking..."
./restya-cli.py organization list

echo
echo "Testing 'organization delete'..."
./restya-cli.py organization delete -o "Organization #2"
./restya-cli.py organization delete -o "Organization #3"
./restya-cli.py organization list

echo
echo "Checking..."
./restya-cli.py organization list

echo
echo "Testing 'organization list-boards'..."
./restya-cli.py organization list-boards -o "Organization #1"

echo
echo "Testing 'organization create-board'..."
./restya-cli.py organization create-board -b "Board 1" -o "Organization #1"
./restya-cli.py organization create-board -b "Board 2" -o "Organization #1"
./restya-cli.py organization create-board -b "Board 3" -o "Organization #1"

echo
echo "Checking..."
./restya-cli.py organization list-boards -o "Organization #1"

echo
echo "Testing 'organization close-board'..."
./restya-cli.py organization close-board -b "Board 2" -o "Organization #1"
./restya-cli.py organization close-board -b "Board 3" -o "Organization #1"

echo
echo "Testing 'organization delete-board'..."
./restya-cli.py organization delete-board -b "Board 2" -o "Organization #1"
./restya-cli.py organization delete-board -b "Board 3" -o "Organization #1"

echo
echo "Checking..."
./restya-cli.py organization list-boards -o "Organization #1"

echo
echo "Testing 'board list-lists'..."
./restya-cli.py board list-lists -o "Organization #1" -b "Board 1"

echo
echo "Testing 'board list-lists'..."
./restya-cli.py board add-list -o "Organization #1" -b "Board 1" -l "Todo"

echo
echo "Checking..."
./restya-cli.py board list-lists -o "Organization #1" -b "Board 1"

# Clean
#./restya-cli.py organization delete-board -b "Board 1" -o "Organization #1"
#./restya-cli.py organization delete -o "Organization #1"