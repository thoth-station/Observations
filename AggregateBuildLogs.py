import os
import sys
import subprocess
import pandas as pd
from io import StringIO
import wget
import csv
import shutil


def get_builds():
    StringIO(subprocess.getoutput("oc get builds > allbuildsfromproject.csv"))
    df = pd.read_csv('allbuildsfromproject.csv', header=None, sep='\s\s+', skipinitialspace=True)
    df.to_csv('buildlist.csv', header=None, sep=',')
    builds = []
    with open('buildlist.csv', 'r') as f:
        dict_reader = csv.DictReader(f)
        for line in dict_reader:
            builds.append(line['NAME'])
    return builds


def get_build_config():
    build_values = get_builds()
    build_config = []
    for every_build in build_values:
        build_description = subprocess.getoutput("oc describe builds/" + every_build)
        build_desc = build_description.split('\n')
        build_dictionary = {}
        key_words = []
        for row in build_desc:
            if row:
                if row[0].isupper():
                    key, value = row.split(':', 1)
                    build_dictionary[key] = value
                    key_words.append(key)
                else:
                    build_dictionary[key_words[-1]] = build_dictionary[key_words[-1]]+row
        build_config.append(build_dictionary)
    build_data_frame = pd.DataFrame(build_config)
    build_data_frame.to_csv('random1.csv', quoting=csv.QUOTE_NONE, quotechar='', escapechar=',', sep=',')


def get_build_logs():
    build_config = get_build_config()
    system_path = os.path.dirname(os.path.realpath(__file__))
    download_directory = "/BuildLogs"
    source_location = system_path + download_directory
    shutil.rmtree(source_location, ignore_errors=True)
    os.makedirs("BuildLogs")
    for config in build_config:
        subprocess.getoutput("oc logs -f bc/"+config+"> BuildLogs/"+config+".csv")
    total_build_logs = []
    total_build_logs = os.listdir(source_location)
    for log in range(len(total_build_logs)):
        download_url = source_location + "/" + total_build_logs[log]
        wget.detect_filename(download_url, out=system_path)



def main():
    get_build_config()
    #get_build_logs()


main()