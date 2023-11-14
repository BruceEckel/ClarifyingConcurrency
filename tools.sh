#!/bin/bash

# tools.sh

if [ "$1" ]; then
    # If an argument is provided, run tools.py with the argument
    clear; rye run tools "$1"
else
    # If no argument is provided, display the help for tools.py
    clear; rye run tools --help
fi
