# Copy this file to exportimportconfig.py to use
from collections import namedtuple

JIRA = {
    'server': 'http://upg-jira.int.thomsonreuters.com',
    'user': 's_askjira.user',
    'password': 'askjiratest',
#    'source_project': 'gconfig'
    "source_project": "PSVR",
    "project": "TDNTEST"
}

PRIORITY_MAP = {
        'Blocker': 'Blocker',
        'Critical': 'Critical',
        'Major': 'Major',
        'Minor': 'Minor',
        'Trivial': 'Trivial',
}

ISSUETYPE_MAP = {
        'Epic': 'Epic',
        'Story': 'Story',
        'Improvement': 'Story',
        'New Feature': 'Story',
        'Change request': 'Story',
        'Task': 'Sub-task',
        'Bug': 'Bug',
        'Sub-task': 'Sub-task',
        'Development': 'Sub-task',
        'Design': 'Sub-task',
        'Technical task': 'Sub-task',
}

ASSIGNEE_MAP = {
#        'userb': 'user2',
}

REPORTER_MAP = ASSIGNEE_MAP

ATTEMPT_ORIGINAL_USER_IF_NOT_IN_MAP = True 

SOURCE_EPIC_LINK_FIELD_ID = 'customfield_14362'
SOURCE_EPIC_NAME_FIELD_ID = 'customfield_14364'
TARGET_EPIC_NAME_FIELD_ID = 'customfield_10237'

WithResolution = namedtuple('WithResolution', 'transition_name')

RESOLUTION_MAP = {
    'Fixed': 'Fixed',
    "Won't Fix": "Won't Fix",
    'Later': "Won't Fix",
    'Duplicate': 'Duplicate',
    'Incomplete': 'Incomplete',
    'Cannot Reproduce': 'Cannot Reproduce',
    'Fixed as is': 'Fixed',
    'Fixed with minor changes': 'Fixed',
    'Fixed with changes': 'Fixed',
    'Fixed quite differently': 'Fixed',
    'Released': 'Done',
    'Resolved': 'Done',
    'Verified': 'Done',
    'Unresolved': "Won't Fix",
    'Done': 'Done',
    'Cancelled': 'Cancelled',
}

#OLD/DEMO
#STATUS_TRANSITIONS = {
#    'Open': None,
#    'Reopened': None,
#    'In Progress': ('Start work',),
#    'In Testing': ('Start work', 'Work done', 'Review passed'),
#    'Resolved': ('Start work', 'Work done', 'Review passed',
#        WithResolution('Testing passed')),
#    'Closed': ('Start work', 'Work done', 'Review passed',
#        WithResolution('Testing passed')),
#}

STATUS_TRANSITIONS = {
    'Open': None,
    'Reopened': None,
    'In Progress': ('Start Coding'),
    'In Testing': ('Start Coding', 'Close'),
    'Resolved': ('Start Coding', WithResolution('Close')),
    'Closed': ('Start Coding', WithResolution('Close')),
}

ADD_COMMENT_TO_OLD_ISSUE = False 

# field types need to be aligned between systems in order to map custom fields
CUSTOM_FIELD_MAP = {
#    'customfield_sourcenum': 'customfield_targetnum',
#Environment Type: Environment Type
    'customfield_10463': 'customfield_12062',
}

# List Target Issue types that should map custom fields (usually just story or bug)
CUSTOM_FIELD_ISSUETYPES = ['Story','Bug']

#Set a custom field to a default value
#CUSTOM_FIELD = ('customfield_11086', {'value': 'Custom value'})
CUSTOM_FIELD = ()
