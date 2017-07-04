# -*- coding: utf-8 -*-

from github import Github
import config
import time
import requests
from bs4 import BeautifulSoup
import datetime
import pandas as pd


current_time = time.time()

user = config.github_user
assert user == "sara-02"
password = config.github_psswd
g = Github(user, password)
reset_time = g.rate_limiting_resettime


def get_rate_remaining():
    return g.get_rate_limit().rate.remaining


def get_requested_file(complete_path):
    return requests.get(complete_path, auth=(user, password))


start_time = datetime.datetime.now()
flag = True
while flag:
    try:
        results = g.search_code("filename:package_json")
        flag = False
    except Exception as e:
        print(e)
        time.sleep(5)
        flag = True
print("Time for search = %s" % (datetime.datetime.now() - start_time))
print(results.totalCount)

start_time = datetime.datetime.now()
flag = True
while flag:
    try:
        time.sleep(5)
        repos = [result.repository for result in results[:1021]]
        flag = False
    except Exception as e:
        print(e)
        time.sleep(10)
        flag = True
print("Time for repo collection = %s" % (datetime.datetime.now() - start_time))
print(len(repos))

try:
    collected_count = 0
    result_count = len(repos) - 1

    prefix = "https://github.com/"
    midfix = "/blob/master/"
    postfix = "requirements.txt"


    data = []
    while collected_count != result_count:
        rate_remain = get_rate_remaining()
        if rate_remain == 0:
            time.time.sleep(reset_time - current_time)
        current_time = reset_time
        reset_time = g.rate_limiting_resettime

        repo_name = repos[collected_count].full_name
        file_path = results[collected_count].path
        complete_path = prefix + repo_name + midfix + file_path
        # start_time = datetime.datetime.now()
        r = get_requested_file(complete_path)
        time.sleep(1)
        # print("request for file done in %s" %
        # (datetime.datetime.now() - start_time))
        if r.status_code == 200:
            soup_obj = BeautifulSoup(r.content, "lxml")
            save_file_name = repo_name.split("/")[-1] + "_" + postfix
            tables = soup_obj.find_all('table', {"class": "highlight tab-size js-file-line-container"})
            for t in tables:
                tds = t.find_all('td', {'class': 'blob-code blob-code-inner js-file-line'})
                d = {}
                c = 1
                d[0] = save_file_name
                for each in tds:
                    d[c] = each.get_text().encode('utf-8')
                    c = c + 1
            data.append(d)

        collected_count = collected_count + 1
        print (collected_count)
        time.sleep(1)
    cols = list(range(1001))
    df = pd.DataFrame(data, columns=cols)
    df.to_csv("python_dump.csv", index=False)
except Exception as e:
    print("Exception at Try: %s" % e)
    cols = list(range(1001))
    df = pd.DataFrame(data, columns=cols)
    df.to_csv("python_dump_partial.csv", index=False)
