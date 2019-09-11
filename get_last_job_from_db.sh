#!/bin/bash

sqlite3 jobs.db 'select * from job order by id DESC limit 1;'

