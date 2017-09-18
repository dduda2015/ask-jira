#!/usr/bin/env python3
import pickle

_g_epic_map = {}
try:
    epic_map_file=open("epicmap","rb")
    _g_epic_map = pickle.loads(epic_map_file.read())
    epic_map_file.close()
except IOError:
    print('Epic Map not found')
with open("savedEpics.txt","r") as epfile:
    epics_to_add=epfile.readlines()
for line in epics_to_add:
    linepair=line.split()
    _g_epic_map[linepair[0]] = linepair[1]
for entry in _g_epic_map:
    print(entry,' ',_g_epic_map[entry])
epic_map_file=open("epicmap","wb+")
pickle.dump(_g_epic_map,epic_map_file)
epic_map_file.close()


