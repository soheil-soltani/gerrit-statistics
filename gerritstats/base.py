from gerrit import GerritClient
import json
from collections import Counter
import requests
from requests.auth import HTTPBasicAuth
from datetime import datetime
###from projects import GerritProjects


class GerritStats:
       def __init__(self,username, password, url):
              self.uname = username
              self.pw = password
              self.url = url
              self.client = GerritClient(self.url, self.uname, self.pw)
              self.projects = None
       

       def get_projects(self, include=None, exclude=None):
              projects_dict = self.client.projects.list(limit=None)
              projects_list = list(projects_dict.keys())  #TODO: set()?
              
              if include:
                     new_projects = [proj for proj in projects_list if
                                     any(phrase in proj for phrase in include)]
                     
                     projects_list = new_projects
              
              if exclude:
                     new_projects = [proj for proj in projects_list if
                                     any(phrase not in proj for phrase in exclude)]
                     
                     projects_list = new_projects

              self.projects = projects_list

                     
       def print_projects(self):
              if self.projects:
                     for item in self.projects:
                            print(item)
              else:
                     print("No projects found.")


       # These methods are not yet tested
       # def get_log(client, project, branch='master'):
       #        """Get git reflog of the given project
       #        """
              
       #        repo=client.projects.get(project)
              
       #        try:
       #               target=repo.branches.get('refs/heads/'+branch)            
       
       #        except Exception:
       #               print('{}'.format(project))

       #        else:
       #               try:
       #                      git_log = target.get_reflog()
       #                      return git_log
              
       #               except Exception:
       #                      print('Error retrieving reflog for {}'.format(project))
       #                      raise LogRetrieveException                     

              
       # def parse_log(log, verbose=False):
       #        """Parse the git reflog output of the given project and 
       #        report the frequency of its commits
       #        """
                            
       #        dates=[]
       #        for commit in log:              
       #               dates.append(commit['who']['date'].split()[0])

       #        unique_dates = set(dates)
       #        freq = []
       #        for dd in sorted(unique_dates, reverse=True):
       #               occurances = Counter(dates)[dd]
       #               freq.append(occurances)
       #               if verbose:
       #                      print('{} commits issued on {}.'.format(occurances, dd))
                     
       #        min_freq = min(freq)
       #        max_freq = max(freq)
       #        avg_freq = sum(freq)/len(freq)

       #        return min_freq, max_freq, avg_freq


       def extract_stats(self,                                
                         start_time,
                         stop_time,
                         project,
                         branch,
                         status,
                         verbose=False,
                         debug=False):
              """Parse the gerrit change statistic and 
              report the frequency of its commits
              thin of doing something like
              class Project()
                  self.base_url
                  self.branch
                  ...
              """
              
              query='since:"{}" before:"{}" branch:"{}" project:"{}"'.format(
                     start_time, stop_time, branch, project)

              change_url = self.url+'changes/'
              submissions=[]   # initialize submission records
              for stat in status:
                     query = stat+' ' + query
                     parameters = {"q" : query,
                                   "pp" : 'no-limit',
                     }
                                          
                     response = requests.get(change_url, auth=HTTPBasicAuth(self.uname, self.pw),
                                             params=parameters)
                            
                     #if stat=='status:open':
                     #       print(response.url)
              
                     clean_content = response.text.split("\n",1)[1]
                     #print(cleanContent)
                     for entry in json.loads(clean_content):
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
                            print("Empty project: {}".format(project))
                     return None, None, None      


if __name__ == "__main__":
       testob = GerritStats()
