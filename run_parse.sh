#!/bin/bash

pwd
cd ./app
python2 ./parse_freelansim.py
python2 ./parse_freelance_com.py
python3 ./parse_freelancehunt.py
