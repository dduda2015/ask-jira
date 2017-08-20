from __future__ import print_function
from __future__ import unicode_literals

import unicodedata
from io import BytesIO
from jira.client import JIRA
from jira.exceptions import JIRAError


def exportprep_files(source_jira, conf):
    target_jira = JIRA({'server': conf.JIRA['server']},
                       basic_auth=(conf.JIRA['user'], conf.JIRA['password']))
    # _checktypes(source_jira, target_jira,conf)
    # _checkversions(source_jira, target_jira)
    # _checkcomponents(source_jira,target_jira)
    # _checkusermap(source_jira, target_jira)
    _getissuefields(source_jira)


def _checktypes(source, target, conf):
    sourcetypes=[]
    targettypes=[]
    results=[]
    maptypes= getattr(conf,'ISSUETYPE_MAP')
    for entry in source.issue_types():
        sourcetypes.append(getattr(entry, 'name'))
    for entry in target.issue_types():
        targettypes.append(getattr(entry, 'name'))
    for entry in sourcetypes:
        try:
            results.append(maptypes[entry])
        except KeyError:
            print("Type ",entry," doesn't exist in source map")
    for entry in results:
        if entry not in targettypes:
            print("Type ", entry, " doesn't exist in target map")


def _checkversions(source, target):
    return 0
def _checkcomponents(source, target):
    return 0
def _checkusermap(source_jira, target_jira):
    return 0

def _getissuefields(source):
    issue=source.issue('DEV-28181')
        print(issue.field.keys())

