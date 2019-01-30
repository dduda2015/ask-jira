from __future__ import print_function
from __future__ import unicode_literals

import unicodedata
from io import BytesIO
from jira.client import JIRA
from jira.exceptions import JIRAError


def export_import_issues(source_jira, conf, query):
    target_jira = JIRA({'server': conf.JIRA['server']},
                       basic_auth=(conf.JIRA['user'], conf.JIRA['password']))
    index = 0
    result = []
    issues = source_jira.search_issues(query, startAt=index, maxResults=False)
    total = issues.total
    counter = total
    while index < total:
        print('About to export/import', len(issues),'of',total,".\n",counter,'remaining issues')
        _make_new_issues(source_jira, target_jira, issues, conf, result, None)
        index += 50
        counter-=50
        issues = source_jira.search_issues(query, startAt=index, maxResults=False)
    return result


def _make_new_issues(source_jira, target_jira, issues, conf, result, parent):
    for issue in issues:
        if not parent:
            print('Exporting', issue.key, end=' ')
        # re-fetch to include comments and attachments
        issue = source_jira.issue(issue.key, expand='comments,attachments')
        fields = _get_new_issue_fields(issue.fields, conf)
        if parent:
            fields['parent'] = {'key': parent.key}
	#dduda - edit
	print("---- source fields ----")
	print (getattr(issue.fields,'assignee'))
	print (dir(issue.fields))
	print ("---- target fields use for creation ---")
	print (fields)
        new_issue = target_jira.create_issue(fields=fields)
        if not parent:
            print('to', new_issue.key, '...', end=' ')
        with open("savedates.csv",'a') as out:
            out.write(str(issue.key)+","+new_issue.key+","+str(issue.fields.created)+","+str(issue.fields.updated)+"\n")
        _set_epic_link(new_issue, issue, conf, source_jira, target_jira)
        _set_status(new_issue, issue, conf, target_jira)

        if issue.fields.comment.comments:
            _add_comments(new_issue, target_jira, issue.fields.comment.comments)
        if issue.fields.attachment:
            try:
                _add_attachments(new_issue, target_jira, issue.fields.attachment)
            except JIRAError as e:
                print('ERROR: attachment import failed with status',
                      e.status_code, '...', end=' ')
                target_jira.add_comment(new_issue, '*Failed to import attachments*')
        if issue.fields.subtasks:
            subtasks = [source_jira.issue(subtask.key) for subtask in
                        issue.fields.subtasks]
            print('with', len(subtasks), 'subtasks ...', end=' ')
            _make_new_issues(source_jira, target_jira, subtasks, conf, result, new_issue)

        comment = 'Imported from *[{1}|{0}/browse/{1}]*'.format(
            source_jira._options['server'], issue.key)
        target_jira.add_comment(new_issue, comment)
        if conf.ADD_COMMENT_TO_OLD_ISSUE:
            comment = 'Exported to *[{1}|{0}/browse/{1}]*'.format(
                target_jira._options['server'], new_issue.key)
            source_jira.add_comment(issue, comment)

        result.append(new_issue.key)
        if not parent:
            print('done')


def _get_new_issue_fields(fields, conf):
    result = {}
    result['project'] = conf.JIRA['project']
    for name in ('summary', 'description', 'labels'):
        value = getattr(fields, name)
        if value is not None:
            result[name] = value
    for name in ('priority','issuetype','reporter','assignee'):
        if hasattr(fields, name):
            field = getattr(fields, name)
	    print ("CHECKING for "+name)
	    print (getattr(field,'name'))
	    try:
		print (dict(field))
	    except:
		pass
            try:
                value = getattr(field,'name')
            except AttributeError:
                value = 'None'
            name_map = getattr(conf, name.upper() + '_MAP')
            try:
                result[name] = {'name': name_map[value]}
            except KeyError:
                if name == 'reporter':
                    #result[name] = {'name': conf.JIRA['user']}
		    #Create/manage name map
		    if getattr(conf,'ATTEMPT_ORIGINAL_USER_IF_NOT_IN_MAP') == True:
		      print ("Using source user information for reporter")
                      result[name] = {'name': value}
		    else:
	              result[name] = {'name': conf.JIRA['user']}
                elif name == 'priority':
                    result[name] = {'name': 'Minor'}
                elif name == 'assignee':
		    #print ("I AM THE ASSINGEE")
		    #print (fields.assignee)
		    if getattr(conf,'ATTEMPT_ORIGINAL_USER_IF_NOT_IN_MAP') == True:
		      print ("Using source user information for assignee")
                      result[name] = {'name': value}
		    else:
	              result[name] = {'name': conf.JIRA['user']}

    components=[]
    for component in fields.components:
        components.append({'name':getattr(component, 'name')})
    if len(components) == 0 :
        components.append({'name':'None'})
    result['components']=components

    versions=[]
    for version in fields.versions:
        versions.append({'name':getattr(version, 'name')})
    result['versions']=versions

    #fixversions=[]
    #for version in fields.fixVersions:
    #  fixversions.append({'name':getattr(version, 'name')})
    #result['fixversions']=fixversions

    if result['issuetype'] in conf.CUSTOM_FIELD_ISSUETYPES:
        timetracking={}
        for name in ['timeSpent','originalEstimate','remainingEstimate']:
            try:
                timetracking[name]=str(getattr(fields.timetracking,name))
            except (AttributeError,TypeError):
                a=None
        result['timetracking']=timetracking

#Not sure if statement below is needed?  result['issuetype'] is name -> value, not value, so if statement should be corrected if valid
    #if result['issuetype'] in conf.CUSTOM_FIELD_ISSUETYPES:
    print ("---- hi, trying match fields based on issue types ----")
    for name in conf.CUSTOM_FIELD_MAP:
        if hasattr(fields, name):
            field = getattr(fields, name)

            if hasattr(field, 'value'):
                result[conf.CUSTOM_FIELD_MAP[name]] = {'value': field.value}
            elif hasattr(field, 'name'):
                try:
                    result[conf.CUSTOM_FIELD_MAP[name]] = {'name': conf.ASSIGNEE_MAP[field.name]}
                except KeyError:
                    result[conf.CUSTOM_FIELD_MAP[name]] = {'name': None}
            else:
                result[conf.CUSTOM_FIELD_MAP[name]] = field

#    print ("--- Custom field map: "+str(getattr(conf,'CUSTOM_FIELD_MAP')))
    print ("--- Custom field map: "+str(conf.CUSTOM_FIELD_MAP))
    if conf.CUSTOM_FIELD:
        result[conf.CUSTOM_FIELD[0]] = conf.CUSTOM_FIELD[1]
    return result


_g_epic_map = {}
try:
    epic_map_file=open("epicmap.txt","a")
    epics_to_add = epic_map_file.readlines()
    for line in epics_to_add:
        linepair = line.split()
        _g_epic_map[linepair[0]] = linepair[1]
    epic_map_file.close()
except IOError:
    print('Epic Map not found')


def _set_epic_link(new_issue, old_issue, conf, source_jira, target_jira):
    source_epic_key = getattr(old_issue.fields, conf.SOURCE_EPIC_LINK_FIELD_ID)
    if not source_epic_key:
        return
    global _g_epic_map
    if source_epic_key not in _g_epic_map:
        try:
            source_epic = source_jira.issue(source_epic_key)
        except JIRAError as e:
            print('ERROR: Source Link Invalid, cannot link issue',
                  e.status_code, '...', end=' ')
            return
        epic_fields = _get_new_issue_fields(source_epic.fields, conf)
        epic_fields[conf.TARGET_EPIC_NAME_FIELD_ID] = getattr(
            source_epic.fields, conf.SOURCE_EPIC_NAME_FIELD_ID)
        target_epic = target_jira.create_issue(fields=epic_fields)
        _set_status(target_epic,source_epic, conf, target_jira)
        _g_epic_map[source_epic_key] = str(target_epic)
        with open("epicsave.txt",'a') as out:
            out.write(str(source_epic_key)+" "+str(target_epic)+"\n")
    target_epic = _g_epic_map[source_epic_key]
    target_jira.add_issues_to_epic(target_epic, [new_issue.key])
    print('linked to epic', target_epic, '...', end=' ')


def _set_status(new_issue, old_issue, conf, target_jira):
    status_name = old_issue.fields.status.name
    try:
        transitions = conf.STATUS_TRANSITIONS[status_name]
    except KeyError as e:
        print('ERROR: Issue transition invalid, cant transition issue',
               '...', end=' ')
        return
    if not transitions:
        return
    for transition_name in transitions:
        if isinstance(transition_name, conf.WithResolution):
            resolution = conf.RESOLUTION_MAP[old_issue.fields.resolution.name]
            print(transition_name.transition_name, " ", resolution)
            target_jira.transition_issue(new_issue, transition_name.transition_name,
                                         fields={'resolution': {'name': resolution}})
        else:
            target_jira.transition_issue(new_issue, transition_name)


def _add_comments(issue, jira, comments):
    for comment in comments:
        try:
            jira.add_comment(issue, u"*Comment by {0}*:\n{1}"
                             .format(comment.author.displayName, comment.body))
        except JIRAError as e:
            print('ERROR: Source Link Invalid, cannot link issue',
                  e.status_code, '...', end=' ')

def _add_attachments(issue, jira, attachments):
    for attachment in attachments:
        with BytesIO() as buf:
            for chunk in attachment.iter_content():
                buf.write(chunk)
            jira.add_attachment(issue,
                                filename=_normalize_filename(attachment.filename),
                                attachment=buf)


def _normalize_filename(value):
    return unicodedata.normalize('NFKD', value).encode('ascii',
                                                       'ignore').decode('ascii')

# -------------------------------------
# TODO:
# - more mappings from http://stackoverflow.com/a/26043914/258772
# - components, fixVersions (use create_version())
# - estimates and timelogs
#   - tried, no luck, even though seems to have been working:
#     https://answers.atlassian.com/questions/211138/defining-original-estimation-value-via-api

# Not doing:
# - keep original key: JIRA does not support this
# - comment authors map -- cannot change comment authors easily, Google for
#   reasons
