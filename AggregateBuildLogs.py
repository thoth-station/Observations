#!/usr/bin/env python3
# Kebechet
# Copyright(C) 2018 Sushmitha Nagarajan
#
# This program is free software: you can redistribute it and / or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

"""An OpenShift BuildLog Aggragator."""


import subprocess
import json
from pandas.io.json import json_normalize
import requests
import numpy as np
from nltk.tokenize import sent_tokenize


def get_builds():
    """Used to get the total list of builds from a openshift project."""
    subprocess.getoutput(
        "oc get builds --output=json > allbuildsfromproject1.json")
    with open("allbuildsfromproject1.json", "r") as read_file:
        data = json.load(read_file)
    tabular_data = json_normalize(data['items'])
    build_pod_names = (
        tabular_data['metadata.annotations.openshift.io/build.pod-name']).tolist()
    print(build_pod_names)
    api_version_list = []
    kind_list = []
    meta_data_list = []
    for i in data['items']:
        api_version = i['apiVersion']
        api_version_list.append(api_version)
        kind = i['kind']
        kind_list.append(kind)
        meta_data_list.append(i)
    return build_pod_names, api_version_list, kind_list, meta_data_list


def post_build_logs():
    """The method gets the list of log files of every build and posts them to the API."""
    get_build_info = get_builds()
    pod_list = get_build_info[0]
    api_version_list = get_build_info[1]
    kind_list = get_build_info[2]
    meta_data_list = get_build_info[3]
    build_logs_endpoint_url = "http://user-api-thoth-test-core.cloud.paas.upshift.redhat.com/api/v1/buildlog"
    clean_pod_list = ['N/A' if x is np.nan else x for x in pod_list]
    response_docid_list = []
    for index, pod in enumerate(clean_pod_list):
        logs = subprocess.getoutput("oc logs "+pod)
        log_info = {'log': logs}
        response = requests.post(build_logs_endpoint_url, json=log_info)
        print(response.json())
        response_docid_list.append(response.json())
    return response_docid_list
# 'apiVersion': api_version_list[index], 'kind': kind_list[index], 'metadata': meta_data_list[index]
# bad requests
# json.dumps on metadatalist


def get_build_logs():
    """The method gets the posted build logs based on the document ID."""
    doc_id_list = post_build_logs()
    get_build_logs_url = "http://user-api-thoth-test-core.cloud.paas.upshift.redhat.com/api/v1/buildlog/"
    total_logs = []
    for document in doc_id_list:
        for key, value in document.items():
            get_request_url = get_build_logs_url+value
            response = requests.get(get_request_url)
            total_logs.append(response.json())
    return total_logs


def normalise_build_logs():
    """The method is used to normalise logs and split them into multiple sections."""
    build_logs_list = get_build_logs()
    for log in build_logs_list:
        print(log)
        log_parser = log.get('log')
        # metadata_parser = log.get('metadata')
        # metadata_json_data = json.loads(metadata_parser)
        sent_tokenize_list = sent_tokenize(log_parser)
        print(sent_tokenize_list)


if __name__ == '__main__':
    normalise_build_logs()
