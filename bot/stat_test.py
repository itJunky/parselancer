# -*- coding: utf-8 -*-

from bot import get_stats

stats = get_stats('webdev')
for stat in stats:
    print('Count:',len(stat.all()))
    jobs = stat.all()
    length = len(jobs)
    # if length > 0:
    #     print(jobs[length-1].parse_date)
    #     # print(jobs[length-2].parse_date)
    #     # print(jobs[length-3].parse_date)
    #     # print(jobs[3].parse_date)
    #     # print(jobs[2].parse_date)
    #     print(jobs[0].parse_date)

    print(' ')
    # for job in jobs:
    #     print(job.parse_date)