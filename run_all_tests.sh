#!/bin/bash

# For every directory in `tests`:
for d in "./modules/test/"/*; do

    # For every python file in a `test` subdirectory:
    for f in "$d"/*.py; do 

        # Run the test:
        python3 "$f"; 
    done
done