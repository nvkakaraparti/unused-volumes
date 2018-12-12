#==================================================================================================================
# Script:       unused-volumes.py
# Date:         6/29/2017
# Author:       (Naveen vishnu Kakaraparti)
# Description:  To query the list of all volumes whose 'State' is 'Available'and represent the volumes and their information in a csv file Also, to delete those available volumes.
#==================================================================================================================

#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Purpose: To query the list of all volumes whose 'State' is 'Available',
         and represent the volumes and their information in a csv file
         Also, to delete those available volumes.

SYNTAX: unused-volumes.py <action>

EX:     unused-volumes.py list
"""
import sys
import os
import pdb
from boto3 import Session
from csv import DictWriter

global setFields
global volumesWithTags
global availableVolumesCount

setFields = 0
volumesWithTags = 0
availableVolumesCount = 0

profileList = [
  
]
regionList = [
    'us-east-1',
    'us-east-2',
    'us-west-1',
    'us-west-2',
    'ca-central-1',
    'ap-south-1',
    'ap-northeast-2',
    'ap-southeast-1',
    'ap-southeast-2',
    'ap-northeast-1',
    'eu-central-1',
    'eu-west-1',
    'eu-west-2',
    'sa-east-1'
]

def getAvailableVolumes(ses, region, profile):
    global fieldNamesD
    global setFields
    global availableVolumesCount
    global volumesWithTags

    response = ses.client('ec2', region_name=region).describe_volumes()
    AvailableVolumes = []
    for vol in response['Volumes']:
        if vol['State'] == 'available':
            AvailableVolumes.append(vol)
    availableVolumesCount += len(AvailableVolumes)
    with open('AvailableVolumes.csv', 'ab+') as fileHandler:
        if not setFields:
            for aVol in AvailableVolumes:
                if len(aVol) == max([len(i) for i in AvailableVolumes]):
                    fieldNamesD = ['profileName'] + aVol.keys()
                    setFields = 1
                    break
        if AvailableVolumes:
            writer = DictWriter(fileHandler, fieldnames=fieldNamesD)
            writer.writeheader()
            for aVol in AvailableVolumes:
                try:
                   del aVol['Tags']
                   volumesWithTags += 1
                except KeyError:
                   pass
                aVol['profileName'] = profile
                try:
                    writer.writerow(aVol)
                except Exception as ex:
                    print "error"
                    print aVol,'\n',ex


def deleteAvailableVolumes(ses, region):
    ec2 = ses.resource('ec2', region_name=region)
    print "Trying to delete the below volumes:"
    for vol in ec2.volumes.all():
        try:
            if vol.state == 'available':
                v = ec2.Volume(vol.id)
                print vol.id
                v.delete()
        except Exception as ex1:
            print ex1


if __name__ == '__main__':
    try:
        if len(sys.argv) == 2:
            action = sys.argv[1]
            # Removing existing AvailableVolumes.csv file
            if os.path.exists('./AvailableVolumes.csv'):
                os.remove('./AvailableVolumes.csv')
            for profile in profileList:
                print "processing for profile:", profile
                ses = Session(profile_name=profile)
                for region in regionList:
                    if action == 'list':
                        getAvailableVolumes(ses, region, profile)
                    elif action == 'delete':
                        deleteAvailableVolumes(ses, region)
                    else:
                        print "INVALID ACTION:", action
                        print "<action> should be either list or delete"
                        sys.exit(1)
            if volumesWithTags:
                print "No. of volumes with Tags:", volumesWithTags
            if availableVolumesCount:
                print "Total Number of available volumes :", availableVolumesCount
        else:
            print __file__, "<action>"
            print "Ex:\n", __file__, "list"
    except Exception as ex:
        print "Exception Occurred: %s" % ex
