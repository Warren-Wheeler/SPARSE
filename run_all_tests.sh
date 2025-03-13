#!/bin/bash

for d in "./modules/test/"/*; do

    # For every directory in `tests`:
    if [ -d "$d" ]; then

        # For every python file in a `test` subdirectory:
        for f in "$d"/*.py; do 

            # Run the test:
            python3 "$f"; 
        done

    # For every python file in `tests`:
    elif [ "$d" == "*.py" ]; then

        # Run the test:
            python3 "$d"; 
    fi
done