#!/usr/bin/env bash
IFS=$'\n'
for I in $(cat ./fields.txt)
do
    grep -i "\'$I\'" ./redijira.flds | tr -d '\n'
    grep -i "\'$I\'" ./upgjira.flds
done