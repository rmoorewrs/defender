#!/bin/bash
if test -f /usr/bin/python3; then
    PYTHON=python3
else
    if test -f /usr/bin/python; then
        PYTHON=python
    else
        echo Python not found, please install
        exit -1
    fi
fi
$PYTHON -m http.server 5001
