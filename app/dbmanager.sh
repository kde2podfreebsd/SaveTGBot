#!/bin/bash

if [ "$1" == "init" ]; then
    cd database
    python3 dbCreate.py
    echo "Database created"
    ls

elif [ "$1" == "delete" ]; then
    cd database
    rm db.sqlite
    echo "Database deleted"
    ls

elif [ "$1" == "rebuild" ]; then
    cd database
    rm db.sqlite
    echo "Database deleted"
    ls
    python3 dbCreate.py
    echo "Database created"
    ls
fi
