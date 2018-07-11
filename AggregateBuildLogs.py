import subprocess
from io import StringIO
import json
from pandas.io.json import json_normalize
import requests
import os
import shutil


def get_builds():
    StringIO(subprocess.getoutput("oc get builds --output=json > allbuildsfromproject1.json"))
    with open("allbuildsfromproject1.json", "r") as read_file:
        data = json.load(read_file)
    tabular_data = json_normalize(data['items'])
    build_pod_names = (tabular_data['metadata.annotations.openshift.io/build.pod-name']).tolist()
    return build_pod_names


def get_logs():
    list_of_build_pods = get_builds()
    build_logs_endpoint_url = "http://user-api-thoth-test-core.cloud.paas.upshift.redhat.com/api/v1/ui/#!/Buildlogs/post_buildlog"
    build_logs_download_directory = os.path.dirname(os.path.realpath(__file__)) + "/BuildLogs"
    os.makedirs('BuildLogs')
    pod_list = [x for x in list_of_build_pods if str(x) != 'nan']
    for pod in pod_list:
        logs = str(subprocess.getoutput("oc logs "+pod))
        with open("BuildLogs/"+pod+".txt", "a+") as file:
            file.write(str(logs))
            file_content = file.read()
            requests.post(build_logs_endpoint_url, {'log': file_content})
    shutil.rmtree(build_logs_download_directory, ignore_errors=True)
    shutil.rmtree(os.path.dirname(os.path.realpath(__file__))+"allbuildsfromproject1.json", ignore_errors=True)
    return "success"


def retreive_build_logs():
    get_builds_endpoint_url="http://user-api-thoth-test-core.cloud.paas.upshift.redhat.com/api/v1/ui/#!/Buildlogs/get_buildlog"
    r = requests.get(get_builds_endpoint_url)
    return r


retreive_build_logs()