from gerrit import GerritClient
from yaml import load, dump
import json
from collections import Counter
import requests
from requests.auth import HTTPBasicAuth
from datetime import datetime

def get_projects(gerrit_client, adas_only=True, excl_interfaces=True):
       projects = gerrit_client.projects.list(limit=None)

       # Remove useless entries from the list
       project_names = [projName for projName in list(projects.keys()) if "All-Projects" not in projName and "All-Users" not in projName]

       if adas_only:
              adas_projects = [project for project in project_names if "adas/" in project]
              if excl_interfaces:
                     excl_intf = [adas_project for adas_project  in adas_projects  if not "interface " in adas_project]   #exclude interface repos
                     return excl_intf
              else:
                     return adas_projects
       elif excl_interfaces:
              excl_intf = [project for project  in project_names  if not "interface " in project]   #exclude interface repos
              return excl_intf
       else:
              return project_names                      


def get_log(client, project, branch='master'):
       """Get git reflog of the given project

       """       
       repo=client.projects.get(project)
             
       try:
              target=repo.branches.get('refs/heads/'+branch)            
       
       except Exception:
              print('{}'.format(project))

       else:
              try:
                     git_log = target.get_reflog()
                     return git_log
              
              except Exception:
                     print('Error retrieving reflog for {}'.format(project))
                     raise LogRetrieveException                     

       
       
def parse_log(log, verbose=False):
       """Parse the git reflog output of the given project and 
       report the frequency of its commits
       """
       dates=[]
       for commit in log:              
              dates.append(commit['who']['date'].split()[0])

       unique_dates = set(dates)
       freq = []
       for dd in sorted(unique_dates, reverse=True):
              occurances = Counter(dates)[dd]
              freq.append(occurances)
              if verbose:
                     print('{} commits issued on {}.'.format(occurances, dd))
                     
       min_freq = min(freq)
       max_freq = max(freq)
       avg_freq = sum(freq)/len(freq)

       return min_freq, max_freq, avg_freq


def extract_gerrit_stats(url,
                         start_time,
                         stop_time,
                         project,
                         branch,
                         status_list,
                         verbose=False,
                         debug=False):
       """Parse the gerrit change statistic and 
       report the frequency of its commits
       """       
       query='since:"{}" before:"{}" branch:"{}" project:"{}"'.format(
              start_time, stop_time, branch, project)

       submissions=[]   # initialize submission records
       for stat in status_list:
              query = stat+' ' + query
              parameters = {"q" : query,
                            "pp" : 'no-limit',
              }
                                          
              response = requests.get(url,
                                      auth=HTTPBasicAuth('ssoltan3', 'FH6I0MLxalupInnX6aX+2GwKI2cWVqxL5tH5jg8L4A'),
                                      params=parameters)
                            
              #if stat=='status:open':
              #       print(response.url)
              
              cleanContent=response.text.split("\n",1)[1]
              #print(cleanContent)
              for entry in json.loads(cleanContent):
                     #print(entry['created'])
                     submissions.append(entry['created'])
                                   
       dates=[]
       for item in submissions:              
              dates.append(item.split()[0])

       unique_dates = set(dates)
       freq = []
       for dd in sorted(unique_dates, reverse=True):
              occurances = Counter(dates)[dd]
              freq.append(occurances)
              if debug:
                     print('{} changes issued on {}.'.format(occurances, dd))

       dateFormat='%Y-%m-%d'
       startTstamp=datetime.strptime(start_time, dateFormat)
       stopTstamp=datetime.strptime(stop_time, dateFormat)
       numDays=(stopTstamp-startTstamp).days + 1
       if debug:
              print("Querying statistics over {} days...".format(numDays))

       if freq:
              min_freq = min(freq)
              max_freq = max(freq)
              avg_freq = sum(freq)/numDays
              return min_freq, max_freq, avg_freq
       else:
              if verbose:
                     print("Empty project: {}".format(proj))
              return None, None, None


if __name__ == "__main__":
       # Initialize gerrit client
       client = GerritClient(base_url="https://ad-adas-gerrit.volvocars.biz/",
                             username='ssoltan3',
                             password='FH6I0MLxalupInnX6aX+2GwKI2cWVqxL5tH5jg8L4A')
              
       projects=get_projects(client, adas_only=True, excl_interfaces=True)
       print('{} gerrit projects were discovered.'.format( len(projects) ))

       hits = 0
       miss = 0
       frequencies = {}       
       url="https://ad-adas-gerrit.volvocars.biz/changes/"

       start_time='2023-05-01'
       stop_time='2023-06-30'
       
       ###project=["adas/actuation-arbitration-manager-service", "adas/functions-status-interface"] DEBUG
       for proj in projects:              
              try:
                     # project_log=get_log(client, proj)
                     min_freq, max_freq, avg_freq = extract_gerrit_stats(url=url,
                                                                         start_time=start_time,
                                                                         stop_time=stop_time,
                                                                         project=proj,
                                                                         branch='master',
                                                                         status_list=['status:open','status:merged','status:abandoned'],
                                                                         verbose=True)
                     if min_freq and max_freq and avg_freq:
                            frequencies[proj] = [min_freq, max_freq, avg_freq]
                     #print(frequencies)
                     hits += 1
                            
              except Exception:
                     miss += 1

              else:
                     pass
                     #min_freq, max_freq, avg_freq = parse_log(project_log)
                     #min_freq, max_freq, avg_freq = parse_gerrit_stats(submissions, verbose=False)
                                                                                    
       print('{} logs successfully retrieved; {} repos failed.'.format(hits, miss))
       frequencies_sorted = sorted(frequencies.items(), key=lambda item: item[1], reverse=True)
       for item in frequencies_sorted:
              print('{} ==> min: {}, max: {}, mean: {}'.format(item[0], item[1][0], item[1][1], item[1][2]))
       

       # 'q' : 'all',              
       #TODO:make sure ALL dates were extracted
       #url="https://ad-adas-gerrit.volvocars.biz/changes/?q=project:adas%252Factuation-arbitration-manager-service&status:merged"            
       
       ##rest = GerritRestAPI(url="https://ad-adas-gerrit.volvocars.biz", auth=HTTPBasicAuth('ssoltan3', 'V7UHDsg86ECndxolpdl+gvEAOaBCEHS0+ZrKeFd+LQ'))
       ##changes = rest.get("changes/?q=is:open&o=DETAILED_ACCOUNTS&o=ALL_REVISIONS&o=ALL_COMMITS&o=ALL_FILES&o=MESSAGES", headers={'Content-Type': 'application/json'})
       
       ##with open('data.json', 'w') as f:
       ##       json.dump(jobs, f)
             
       
