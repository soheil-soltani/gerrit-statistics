"""
This module provides the API through the GerritStats class.

Author: Soheil Soltani
"""

# Third-party imports
from gerrit import GerritClient
# Local imports
from gerritstats.src.project import GerritProject


class GerritStats:
    """
    Implement the API.

    This class implements the outward facing API, which
    can be used by the user application.
    """

    def __init__(self, username, password, url):
        """
        Constructor

        Args:
            username (str): Username for authenticating to Gerrit
            password (str): Password for authenticating to Gerrit
            url (str): The base URL of the Gerrit repository
        Returns:
            None
        """
        self.uname = username
        self.pw = password
        self.url = url
        self.projects = None

    @property
    def client(self):
        """
        Compute property to get the gerrit client

        Returns:
            A GerritClient object to be used for communicating with
            the Gerrit API
        """
        return GerritClient(self.url, self.uname, self.pw)

    def set_projects(self, include=None, exclude=None):
        """
        Create a list of Gerrit projects

        This method creates a list of Gerrit projects by querying
        the Gerrit repository represented using the base URL. It
        then assigns this list to the attribute projects
        It allows some filtering by only including those projects
        that contain the include strings. It also excludes from the
        list all those project that contain any of the exclude
        strings in the project name.

        Args:
             include (list): List of strings (optional)
             exclude (list): List of strings (optional)

        Returns:
            None
        """
        projects_dict = self.client.projects.list(limit=None)
        projects_list = list(projects_dict.keys())  # TODO: set()?

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
        """
        Get the list of Gerrit projects

        This method gets the list of Gerrit projects specified
        using the set_projects() method

        Returns:
            project (list of strings): List of project names
        """
        return self.projects

    def get_project_changes(self, project_id, begin, end, status, branch='master'):
        """
        Retrieve the changes for a specific project

        This method queries the Gerrit API for the changes using the specific
        project, branch, and the status of the change

        Args:
            project_id (str): Gerrit Project ID contained in self.project
            begin (str): Exclude changes older than this date (Format: YY-MM-DD)
            end (str): Exclude changes newer than this date (Format: YY-MM-DD)
            status (list): Include changes currently in this status. Each element of
             the array should be a string of the following allowed values:
             'status:merged', 'status:open', 'status:abandoned'
            branch (str): Include changes listed on this branch (optional)

        Returns:
            list: List of retrieved changes
            bool: Success flag
        """
        project = GerritProject(proj_id=project_id, url=self.url, username=self.uname, password=self.pw)
        changes, success = project.get_changes(begin=begin, end=end, status=status, branch=branch)

        return changes, success

    def get_change(self, project_id, change_id):
        """
        Get details of a specific change

        This method retrieves the change details using the Gerrit API

        Args:
            project_id (str): Gerrit Project ID contained in self.project
            change_id (str): Change ID returned by get_project_changes()

        Returns:
            dict: A json-formatted dictionary of the change details
        """
        project = GerritProject(proj_id=project_id, url=self.url, username=self.uname, password=self.pw)
        change_details = project.get_change_details(change_id=change_id)

        return change_details
