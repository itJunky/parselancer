#!/bin/bash

pwd
already_running=`ps aux | grep parse_.*py | grep -v grep | wc -l`
if [ $already_running -eq 0 ]
then
	python2 ./app/parse_freelansim.py
#	python2 ./app/parse_freelance_com.py  # doesn't work with anonymous access
  python3 ./app/parse_weblancer.py
	python3 ./app/parse_freelancehunt.py
else
	echo "Already running $already_running jobs"
fi
