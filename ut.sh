#!/usr/bin/bash

set -e
set -u

#python3 -m unittest test.epub test.gb_de

python3 -m unittest \
  discover --start-directory test --pattern '*.py' --top-level-directory .
