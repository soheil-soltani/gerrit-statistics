import json
from collections import Counter
import requests
from requests.auth import HTTPBasicAuth
from datetime import datetime


class GerritProject:
    def __init__(self, proj_id, url, username, password):
        self.pid = proj_id
        self.url = url
        self.username = username
        self.password = password
        self.branches = None
        self.has_more = False


    def get_changes(self, begin, end, status, branch='master'):
        Success = True
        changes_url = self.url+'changes/'
        query = 'since:"{}" before:"{}" branch:"{}" project:"{}"'.format(begin, end, branch, self.pid)
        query = status + ' ' + query
        parameters = {"q" : query, "pp" : 'no-limit'}
                                          
        response = requests.get(changes_url, auth=HTTPBasicAuth(self.username, self.password), params=parameters)
        _, clean_content = response.text.split("\n",1)

        changes = []  # initialize submission records
        try:
            for entry in json.loads(clean_content):
                changes.append(entry['id'])
                if '_more_changes' in entry.keys():
                    self.has_more = True
        except Exception:
            Success = False

        return changes, Success


    def count_plus_twos(self, change_details=None):
        if change_details:
            change_dict = json.loads(change_details)
        """
            plus_twos = 0
            for review in code_rev_all:
                if review["value"] == 2:
                    plus_twos += 1

            return plus_twos
        """
        return change_dict

    def get_change_details(self, change_id):
        change_url = self.url + 'changes/' + change_id + '/detail'
        ###change_url = self.url + 'changes/'+ change_id + '/comments' #'/detail?O=1916314'  #'https://ad-adas-gerrit.volvocars.biz/c/adas/domain-controller/+/19628'
        ###change_url = 'https://ad-adas-gerrit.volvocars.biz/c/adas/domain-controller/+/19628?tab=change-view-tab-header-zuul-results-summary'
        response = requests.get(change_url, auth=HTTPBasicAuth(self.username, self.password))
              
        _, clean_content = response.text.split("\n",1)

        return(clean_content)
                    
    
    def get_statistics(self, begin, end, status, branch='master'):
        """Parse the gerrit change statistic and 
        report the frequency of its commits
        thin of doing something like
        class Project()
            self.base_url
            self.branch
            ...
        """

        min_freq, max_freq, avg_freq = None, None, None

        url = self.url+'changes/'
        query='since:"{}" before:"{}" branch:"{}" project:"{}"'.format(
            begin, end, branch, self.pid)

        submissions=[]   # initialize submission records
        for stat in status:
            query = stat+' ' + query
            parameters = {"q" : query,
                          "pp" : 'no-limit',
            }
                                          
            response = requests.get(url, auth=HTTPBasicAuth(self.username, self.password),
                                    params=parameters)                            
              
            _, clean_content = response.text.split("\n",1)            
            
            for entry in json.loads(clean_content):                
                submissions.append(entry['created'])            
                if '_more_changes' in entry.keys():                    
                    self.has_more = True
                                   
        dates=[]
        for item in submissions:              
            dates.append(item.split()[0])   #TODO: make it cleaner

        unique_dates = set(dates)
        freq = []
        for dd in sorted(unique_dates, reverse=True):
            occurances = Counter(dates)[dd]
            freq.append(occurances)
            #if debug:
            #    print('{} changes issued on {}.'.format(occurances, dd))

        dateFormat='%Y-%m-%d'
        startTstamp=datetime.strptime(begin, dateFormat)
        stopTstamp=datetime.strptime(end, dateFormat)
        numDays=(stopTstamp-startTstamp).days + 1
        
        #if debug:
        #    print("Querying statistics over {} days...".format(numDays))
            
        if freq:
            min_freq = min(freq)
            max_freq = max(freq)
            avg_freq = sum(freq)/numDays

        return min_freq, max_freq, avg_freq
        #else:
            #if verbose:
            #    print("Empty project: {}".format(self.pid))
         
