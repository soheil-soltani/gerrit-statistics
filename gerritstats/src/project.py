"""
Implements the GerritProject class.

Author: Soheil Soltani
"""


import json
from collections import Counter
import requests
from requests.auth import HTTPBasicAuth
from datetime import datetime


class GerritProject:
    """
    Implements the GerritProject class containing the
    methods needed to retrieve project-specific details.
    """

    def __init__(self, proj_id, url, username, password):
        """
        Constructor

        Args:
            proj_id (str): Specific Gerrit project id
            url (str):  The base URL of the Gerrit repository
            username (str): Username for authentication to the Gerrit repository
            password (str): Password for authentication to the Gerrit repository

        Returns:
            None
        """
        self.pid = proj_id
        self.url = url
        self.username = username
        self.password = password
        self.branches = None
        self.has_more = False

    def get_changes(self, begin, end, status, branch='master'):
        """
        Retrieve all changes for a specific project on an optionally
        specified branch ('master' assumed otherwise).

        Args:
            begin (str): Exclude changes older than this date. Format: YY-MM-DD
            end (str): Exclude changes newer than this date. Format: YY-MM-DD
            status (list): Include changes currently in this status. Each element of
             the array should be a string of the following allowed values:
             'status:merged', 'status:open', 'status:abandoned'
            branch (str): Include changes listed on this branch (optional)

        Returns:
            list: List of changes retrieved (empty in case of errors)
            bool: Success flag
        """
        success = True
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
                    self.has_more = True   #TODO: act if true
        except Exception:
            success = False

        return changes, success

    def get_change_details(self, change_id):
        """
        Retrieve the details of the given change.

        Args:
            change_id (str): The change id

        Returns:
            dict: A json-formatted dictionary of the change details
        """
        change_url = self.url + 'changes/' + change_id + '/detail'
        response = requests.get(change_url, auth=HTTPBasicAuth(self.username, self.password))

        _, clean_content = response.text.split("\n",1)

        return clean_content
