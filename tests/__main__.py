"""Command line script
Usage:
    __main__.py --username=<username>  --password=<password>

Options:
    --username=<username>   Your Gerrit username (required)
    --password=<password>   Your Gerrit password (required)
"""

import json
from gerritstats import GerritStats
from datetime import date, timedelta
from docopt import docopt

def get_cumulative(begin, end, projects, status):
    delta = timedelta(days=1)  # checking daily gate job activation
    today = begin
    cumulative = {}
    while today != end + delta:  # inclusive end
        tomorrow = today + delta
        today_str = today.strftime('%Y-%m-%d')
        cumulative[today_str] = 0
        gate_jobs = 0

        for proj in projects:
            for stat in status:
                proj_changes, success = gerrit.get_project_changes(project_id=proj, begin=today, end=tomorrow,
                                                                   status=stat)
                if success:
                    # Count the number of gate jobs
                    if proj_changes:
                        for change in proj_changes:
                            change_details = gerrit.get_change(project_id=proj, change_id=change)
                            if change_details:
                                change_dict = json.loads(change_details)
                                for msg in change_dict["messages"]:
                                    if "Starting gate jobs" in msg["message"]:
                                        gate_jobs += 1
                            else:
                                print("\t\tFailed to fetch details for change {}".format(change))
                else:
                    print("\t\tError fetching changes. Project-->{}, status-->{}".format(proj, stat))

        if gate_jobs > 0:
            cumulative[today_str] += gate_jobs
        today += delta

    return cumulative

if __name__=="__main__":
    arguments = docopt(__doc__)
    uname = arguments['--username']
    passw = arguments['--password']
#'FH6I0MLxalupInnX6aX+2GwKI2cWVqxL5tH5jg8L4A'
    gerrit = GerritStats(username=uname, password=passw, url="https://ad-adas-gerrit.volvocars.biz/")

    gerrit.set_projects(include=['adas/'], exclude=['interface'])
    projects = gerrit.get_projects()
    print('{} gerrit projects were discovered.'.format( len(projects) ))

    #for proj in projects:
    #    print(proj)

    status = ['status:merged', 'status:open', 'status:abandoned']   #stats to query

    #projects = ["adas/domain-controller"]
    begin = date(year=2023, month=5, day=1)
    end = date(year=2023, month=7, day=15)
    delta = timedelta(days=1)  # checking daily gate job activation

    print("Collecting cumulative statistics...")
    cum_changes = get_cumulative(begin=begin, end=end, projects=projects, status=status)
    for key in cum_changes.keys():
        print("{}--> {} gate jobs trigerred".format(key, cum_changes[key]))
        
    """    
    for proj in projects:
        print("Module: {}".format(proj))
        for stat in status:
            print("\tStatus: {}".format(stat))
            today = begin
            while today != end+delta:   # inclusive end
                tomorrow = today+delta
                proj_changes, success = gerrit.get_project_changes(project_id=proj, begin=today, end=tomorrow,
                                                                   status=stat)
                if success:
                    # Count the number of gate jobs
                    if proj_changes:
                        gate_jobs = 0
                        for change in proj_changes:
                            change_details = gerrit.get_change(project_id=proj, change_id=change)
                            if change_details:
                                change_dict = json.loads(change_details)
                                for msg in change_dict["messages"]:
                                    if "Starting gate jobs" in msg["message"]:
                                        gate_jobs += 1
                            else:
                                print("\t\tFailed to fetch details for change {}".format(change))
                        if gate_jobs > 0:                            
                            print("\t\tOn {}, {} gate jobs activated".format(today, gate_jobs))
                else:
                    print("\t\tError fetching changes")
                today += delta
    """
