#!/bin/bash

ssh -f -N -g -L 127.0.0.1:3306:127.0.0.1:3306 pythonitj@hosting.itjunky.ml
