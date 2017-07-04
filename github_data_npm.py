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


def get_dep_name(span_data):
    return span_data.get_text().encode('utf-8')[1:-1]


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
    collected_count = 400
    result_count = len(repos) - 1

    prefix = "https://github.com/"
    midfix = "/blob/master/"
    postfix = "package.json"
    
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
        r = get_requested_file(complete_path)
        time.sleep(1)
        if r.status_code == 200:
            save_file_name = repo_name.split("/")[-1] + "_" + postfix
            soup_obj = BeautifulSoup(r.content,"lxml")
            tables = soup_obj.find_all('table', {"class":"highlight tab-size js-file-line-container"})
            if tables is None:
                continue
            table = tables[0]
            trs = table.find_all('tr')
            dep = False
            d = {}
            c = 1
            d[0] = save_file_name
            for each_tr in trs:
                each_td = each_tr.find('td', {'class': 'blob-code blob-code-inner js-file-line'})
                if each_td is None:
                    continue
                check_end = each_td.get_text().encode('utf-8').strip()
                if (check_end =='},' or check_end == '}') and dep:
                    break
                if dep:
                    all_inner_span = each_td.find_all('span', {'class': 'pl-s'})
                    if len(all_inner_span) == 1:
                        d[c] = get_dep_name(all_inner_span[0])
                        c = c + 1
                    elif len(all_inner_span) == 2:
                        d[c] = get_dep_name(all_inner_span[0])+":"+get_dep_name(all_inner_span[1])
                        c = c + 1     
                each_span = each_td.find('span', {'class': 'pl-s'})
                if each_span is None:
                    continue
                if each_span.get_text().encode('utf-8') =='"dependencies"':
                    dep = True

            data.append(d)    
            collected_count = collected_count + 1
            print (collected_count)
        time.sleep(1)
    
    cols = list(range(1001))
    df = pd.DataFrame(data, columns=cols)
    df.to_csv("npm_dump.csv", index=False)
    
except Exception as e:
    print("Exception at Try: %s" % e)
    cols = list(range(1001))
    df = pd.DataFrame(data, columns=cols)
    df.to_csv("npm_dump_partial.csv", index=False)
