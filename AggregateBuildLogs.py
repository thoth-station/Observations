import subprocess
import json
from pandas.io.json import json_normalize
import requests
import numpy as np


def get_builds():
    subprocess.getoutput("oc get builds --output=json > allbuildsfromproject1.json")
    with open("allbuildsfromproject1.json", "r") as read_file:
        data = json.load(read_file)
    tabular_data = json_normalize(data['items'])
    build_pod_names = (tabular_data['metadata.annotations.openshift.io/build.pod-name'])
    pod_metadata = []
    for i in data['items']:
        meta_data = {}
        meta_data['apiVersion'] = i['apiVersion']
        meta_data['kind'] = "Buildlog"
        meta_data['name'] = i['metadata']['annotations']['openshift.io/build-config.name']
        if 'openshift.io/build.pod-name' in i['metadata']['annotations'].keys():
            meta_data['podname'] = i['metadata']['annotations']['openshift.io/build.pod-name']
        else:
            meta_data['podname'] = "N/A"
        meta_data['namespace'] = i['metadata']['namespace']
        meta_data['uid'] = i['metadata']['uid']
        pod_metadata.append(meta_data)
    return build_pod_names, pod_metadata


def get_logs():
    get_build_info = get_builds()
    pod_list = get_build_info[0]
    meta_data = get_build_info[1]
    build_logs_endpoint_url = "http://user-api-thoth-test-core.cloud.paas.upshift.redhat.com/api/v1/buildlog"
    clean_pod_list = ['N/A' if x is np.nan else x for x in pod_list]
    for ind, pod in enumerate(clean_pod_list):
        logs = subprocess.getoutput("oc logs "+pod)
        log_info= {'log': logs,'meta_data': meta_data[ind]}
        print(log_info)
        try:
            response = requests.post(build_logs_endpoint_url, json=log_info)

            print(response.status_code)
            m = response.json()
            print(m)
            break
        except requests.ConnectionError:
            print("failed to connect")
    print("over")
    # return "success"





get_logs()