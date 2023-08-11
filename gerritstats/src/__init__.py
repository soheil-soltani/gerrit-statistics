from gerrit import GerritClient
from gerritstats.src.project import GerritProject


class GerritStats:
    def __init__(self,username, password, url):
        self.uname = username
        self.pw = password
        self.url = url
        self.projects = None

    @property
    def client(self):
        return GerritClient(self.url, self.uname, self.pw)
        

    def set_projects(self, include=None, exclude=None):
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

                     
    def get_projects(self):
        return self.projects


    def get_project_stats(self, project_id, begin, end, status, branch='master'):
        project = GerritProject(proj_id=project_id, url=self.url, username=self.uname,
                                password=self.pw)
        
        min_rate, max_rate, avg_rate = project.get_statistics(begin=begin,
                                                              end=end,
                                                              status=status,
                                                              branch=branch)
        return min_rate, max_rate, avg_rate


    def get_project_changes(self, project_id, begin, end, status, branch='master'):
        project = GerritProject(proj_id=project_id, url=self.url, username=self.uname,
                                password=self.pw)
         
        changes = project.get_changes(begin=begin, end=end, status=status, branch=branch)

        return changes


    def get_change(self, project_id, change_id):
        project = GerritProject(proj_id=project_id, url=self.url, username=self.uname,
                                password=self.pw)
        change_details = project.get_change_details(change_id=change_id)

        return change_details


"""
    def get_plus_twos(self, project_id, change_details):
        project = GerritProject(proj_id=project_id, url=self.url, username=self.uname, password=self.pw)
        plus_twos = project.count_plus_twos(change_details=change_details)

        return plus_twos

"""
    #def to_be_testes():
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
