import json
from gerritstats import GerritStats
from datetime import date, timedelta

if __name__=="__main__":
    gerrit = GerritStats(username='ssoltan3',
                         password='FH6I0MLxalupInnX6aX+2GwKI2cWVqxL5tH5jg8L4A',
                         url="https://ad-adas-gerrit.volvocars.biz/")

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



"""     for proj in projects:
        #try:
        min_freq, max_freq, avg_freq = gerrit.get_project_stats(project_id=proj,
                                                                begin='2023-07-01',
                                                                end='2023-07-30',
                                                                status=status,
                                                                branch='master')
            #if min_freq and max_freq and avg_freq:
            #    frequencies[proj] = [min_freq, max_freq, avg_freq]
            #    ###print(frequencies)
            #    hits += 1

        #except Exception:
        #    miss += 1

# # #        min_freq, max_freq, avg_freq = parse_log(project_log)
# # #        min_freq, max_freq, avg_freq = parse_gerrit_stats(submissions, verbose=False)

 """
"""     print('{} logs successfully retrieved; {} repos failed.'.format(hits, miss))
    frequencies_sorted = sorted(frequencies.items(),
                                key=lambda item: item[1], reverse=True)
    for item in frequencies_sorted:
        print('{} ==> min: {}, max: {}, mean: {}'.format(
            item[0], item[1][0], item[1][1], item[1][2]))
 """