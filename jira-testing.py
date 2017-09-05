#!/usr/bin/env python3

import sys
import pprint
import argparse
import inspect
from jira.client import JIRA, CustomFieldOption
import exportimportconfig

from lib import timetracking
from lib import subissues
from lib import export_import
from lib import google_calendar
from lib import exportprep
from utils.smart_argparse_formatter import SmartFormatter

tab='\t'
CONF = {
    "server": "http://upg-jira.int.thomsonreuters.com",
    "user": "steven.schiff",
    "password":"St3v3Sch1ff%",
    "project":"REDITEMP",
    "user_group":"xact-users",
}
CONF_REDI ={
    "server": "http://jira.redi.com",
    "user": "schiffs",
    "password": "St3v3Sch1ff%",
    "project": "DEV",
    "user_group": "jira-users",
}

def _getProjects(jira):
    projects=jira.projects()
    for project in projects:
        full_project=jira.project(project.key)
        try:
            print(full_project.id,tab,full_project.name,tab,full_project.projectCategory,tab,full_project.lead.name)
        except AttributeError:
            print(full_project.id,tab,full_project.name)

def _searchIssues(jira, search_string,field_list):
    index=0
    issue_list=jira.search_issues(search_string,startAt=index,maxResults=False,fields=field_list)
    total=issue_list.total
    while index < total:
        for issue in issue_list:
            print(issue.fields.customfield_12544)
        index+=50
        issue_list=jira.search_issues(search_string,startAt=index,maxResults=False,fields=field_list)

def _getUsers(jira,CONF):
    jira_users=jira.group_members(CONF["user_group"])
    for jira_user in jira_users:
        print(jira_user)

def _getfields(jira,redijira):
    jira_fields=jira.fields()
    redijira_fields=redijira.fields()

    for field in jira_fields:
        try:
            print(field["name"], field["id"], tab, field['schema']['type'],tab,"UPG")
        except KeyError:
            print(field["name"], tab, field["id"],tab,"UPG" )
    for field in redijira_fields:
        try:
            print(field["name"], field["id"], tab, field['schema']['type'], tab, "REDI")
        except KeyError:
            print(field["name"], tab, field["id"], tab, "REDI")

def _create_issue(jira, issue_dict):
    new_issue=jira.create_issue(fields=issue_dict)
    return new_issue

def _print_issuefields(jira,issuekey,conf):
    issue=jira.issue(issuekey)
    fields=issue.fields
    #print(fields.timeoriginalestimate)
    for field in (vars(fields)):
        if not field == '__dict__':
            a=None
            #print(field," : ",getattr(fields,field))
        if field =='timetracking' :
            timetracking={}
            for name in ['timeSpent', 'originalEstimate', 'remainingEstimate']:
                try:
                    timetracking[name] = str(getattr(fields.timetracking, name))
                except AttributeError:
                    a = None
            print(timetracking)
    result={}
    print('-----------------------------------------------------------')
    for name in conf.CUSTOM_FIELD_MAP:
        if hasattr(fields,name):
            field = getattr(fields, name)
            if hasattr(field, 'value'):
                result[conf.CUSTOM_FIELD_MAP[name]]={'value': field.value}
            elif hasattr(field,'name'):
                try:
                    result[conf.CUSTOM_FIELD_MAP[name]]={'name': conf.ASSIGNEE_MAP[field.name]}
                except KeyError:
                    result[conf.CUSTOM_FIELD_MAP[name]] = {'name': None}
            else:
                result[conf.CUSTOM_FIELD_MAP[name]] = field
#    print(result)

issue_dict= {
    'project': 'REDITEMP',
    'summary': 'Test Issue',
    'description':'Testing testing 123',
    'issuetype': {'name':'Story'},
    'fixVersions': [{'name':'ToolsDepot-7.0.0'},{'name':'CL52208'}],
    'components':[{'name':'CET'},{'name':'API'}],
    'reporter':{'name':'adam.cardarelli'},
    'assignee':{'name':'steven.schiff'},
    'customfield_11761':'Defect',
    'timetracking':{
        'remainingEstimate':'4d',
        'originalEstimate':'5d',
    }
}
jira = JIRA({'server': CONF['server']},
                basic_auth=(CONF['user'], CONF['password']))

redijira=JIRA({'server': CONF_REDI['server']},
                basic_auth=(CONF_REDI['user'], CONF_REDI['password']))
#_create_issue(jira, issue_dict)
#_getProjects(jira)
#_getUsers(jira,CONF)
#_searchIssues(jira,"project=REDITEMP and issuetype='Story'","customfield_12544")
#_getfields(jira,redijira)
_print_issuefields(jira,'ATS-550',exportimportconfig)