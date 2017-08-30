from __future__ import print_function
from __future__ import unicode_literals

import inspect
import unicodedata
from io import BytesIO
from jira.client import JIRA
from jira.exceptions import JIRAError


def exportprep_files(source_jira, conf):
    target_jira = JIRA({'server': conf.JIRA['server']},
                       basic_auth=(conf.JIRA['user'], conf.JIRA['password']))
    source_project=conf.JIRA['source_project']

    if _checkcustomfieldmap(source_jira, target_jira, conf):
        print("Custome field map check complete")

    if _checktypes(source_jira, target_jira,conf):
        print("Issuetype map verified.")
    else:
        print("Issuetype map check failed.")

    if _checkversions(source_jira, target_jira, conf):
        print("Versions check complete")

    if _checkcomponents(source_jira,target_jira, conf):
        print("Component check complete")

    if _checkusermap(source_jira, target_jira,conf):
        print("User map check complete")



def _checktypes(source, target, conf):
    sourcetypes=[]
    targettypes=[]
    success = True
    maptypes= getattr(conf,'ISSUETYPE_MAP')
    for entry in source.issue_types():
        sourcetypes.append(getattr(entry, 'name'))
    for entry in target.issue_types():
        targettypes.append(getattr(entry, 'name'))
    for entry in maptypes:
        if entry not in sourcetypes:
            print(entry, " issue type doesn't exist in source jira system")
            success=False
        if maptypes[entry] not in targettypes:
            print(maptypes[entry]," issue type doesn't exist in target jira system")
            success=False
    return success

def _checkversions(source, target, conf):
    source_project=source.project(conf.JIRA['source_project'])
    target_project=target.project(conf.JIRA['project'])
    target_versions=target.project_versions(target_project)
    target_version_names=[]
    for target_version in target_versions:
        target_version_names.append(target_version.name)
    source_versions=source.project_versions(source_project)
    for fixVersion in source_versions:
        if fixVersion.name not in target_version_names:
            target.create_version(name=fixVersion.name, project=conf.JIRA['project'],\
                                  archived=fixVersion.archived, released=fixVersion.released)
            print(fixVersion.name, " created in ",conf.JIRA['project'])
    return True

def _checkcomponents(source, target,conf):
    source_project = source.project(conf.JIRA['source_project'])
    target_project = target.project(conf.JIRA['project'])
    target_components=target.project_components(target_project)
    target_component_names = []
    for target_component in target_components:
        target_component_names.append(target_component.name)
    source_components=source.project_components(source_project)
    for component in source_components:
        if component.name not in target_component_names:
            target.create_component(name=component.name, project=conf.JIRA['project'])
            print(component.name, " created in project ",conf.JIRA['project'])

    return True


def _checkusermap(source, target,conf):
    success=True
    for entry in conf.ASSIGNEE_MAP:
        try:
            user=source.user(entry)
        except JIRAError:
            print(entry, " does not exist in source jira")
            success=False
        try:
            user=target.user(conf.ASSIGNEE_MAP[entry])
        except JIRAError:
            print(conf.ASSIGNEE_MAP[entry], " does not exist in target jira")
            success = False
    return success

def _compareusers(source, target, conf):
    #Utility to compare users between two jira systems and try to map by display name

    source_users = source.group_members(conf.JIRA['source_group'])
    for source_user in source_users:
        user = source.user(source_user)
        target_users = target.search_users(user=user.displayName)
        if len(target_users) == 0:
            print("Source User: ", user.displayName, "Not found")
        elif len(target_users) > 1:
            print("Source User: ", user.displayName, "Multiple Matches")
        else:
            users = user.key.strip(' ')
            usert = target_users[0].key.strip(' ')
            print("'", users, "'", ": ", "'", usert, "'")

def _checkcustomfieldmap(source, target,conf):
    source_fieldids=[]
    source_fieldnames=[]
    target_fieldids=[]
    target_fieldnames=[]
    success=True

    for field in source.fields():
        source_fieldids.append(field['id'])
        source_fieldnames.append(field['name'])
    for field in target.fields():
        target_fieldids.append(field['id'])
        target_fieldnames.append(field['name'])
    for entry in conf.CUSTOM_FIELD_MAP:
        if not entry in source_fieldids:
            print(entry,"not present in source jira")
            success=False
        else:
            print (entry,":",source_fieldnames[source_fieldids.index(entry)])
        if not conf.CUSTOM_FIELD_MAP[entry] in target_fieldids:
            print(entry,"not present in target jira")
            success=False
        else:
            print (conf.CUSTOM_FIELD_MAP[entry],":",target_fieldnames[target_fieldids.index(conf.CUSTOM_FIELD_MAP[entry])])