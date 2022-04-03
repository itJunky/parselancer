#!/bin/bash

#pwd
already_running=`ps aux | grep parse_.*py | grep -v grep | wc -l`
if [ $already_running -eq 0 ]
then
	python3 ./app/parse_freelance_habr.py
	python3 ./app/parse_weblancer.py
	python3 ./app/parse_freelancehunt.py
else
	echo "Already running $already_running jobs"
fi
