#!/bin/bash

echo "=== Parser started at $(date '+%Y-%m-%d %H:%M:%S') ==="

python ./app/parse_freelancehunt.py -q
python ./app/parse_flru.py -q
python ./app/parse_weblancer.py -q
python ./app/parse_prozcom.py -q
