#!/bin/bash

#pwd
already_running=`ps aux | grep parse_.*py | grep -v grep | wc -l`
if [ $already_running -eq 0 ]
then
	nice -n 10 python3 ./app/parse_freelance_habr.py
	nice -n 10 python3 ./app/parse_weblancer.py
	nice -n 10 python3 ./app/parse_freelancehunt.py
#else
#	echo "Already running $already_running jobs"
fi
