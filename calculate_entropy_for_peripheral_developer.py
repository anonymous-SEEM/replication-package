import numpy as np
import pandas as pd
import pymongo
import time 
import sys
from math import *
from collections import Counter
from calendar import Calendar
from pyecharts import options as opts
from pyecharts.charts import Bar,Grid,Line
import statsmodels.api as sm
from matplotlib import pyplot as plt
from statsmodels.tsa.seasonal import STL

def filterEvent(startTime,endTime):
    eventLst = []
    for i in collection_timeline.find({'$and':[{'created_at':{'$gt':startTime,'$lt':endTime}},
                                            {'$nor':[{"event":'unlabeled'},{"event":'labeled'},{"event":'commit-commented'},
                                                {"event":'line-commented'},{"user.type":'Bot'},{"actor.type":'Bot'}]}]}):
        if i.get('actor'):
            if i['actor']['login'] in special_user_dic.keys():
                if i['created_at'] > special_user_dic[i['actor']['login']]['min'] and i['created_at'] < special_user_dic[i['actor']['login']]['max']:
                    continue
        if i.get('user'):
            if i['user']['login'] in special_user_dic.keys():
                if i['created_at'] > special_user_dic[i['user']['login']]['min'] and i['created_at'] < special_user_dic[i['user']['login']]['max']:
                    continue
        eventLst.append(i)
    issue2eventCount = {}
    for i in eventLst:
        if issue2eventCount.get(i['issue_number']):
            if issue2eventCount[i['issue_number']].get(i['event']):
                issue2eventCount[i['issue_number']][i['event']] += 1
            else:
                issue2eventCount[i['issue_number']][i['event']] = 1
        else:
            issue2eventCount[i['issue_number']]={i['event']:1}
    return issue2eventCount


def filterEventAll(startTime,endTime):
    eventLst = []
    for i in collection_timeline.find({'$and':[{'created_at':{'$gt':startTime,'$lt':endTime}},
                                            {'$nor':[{"event":'unlabeled'},{"event":'labeled'},{"event":'commit-commented'},
                                                {"event":'line-commented'},{"user.type":'Bot'},{"actor.type":'Bot'}]}]}):
        eventLst.append(i)
    issue2eventCount = {}
    for i in eventLst:
        if issue2eventCount.get(i['issue_number']):
            if issue2eventCount[i['issue_number']].get(i['event']):
                issue2eventCount[i['issue_number']][i['event']] += 1
            else:
                issue2eventCount[i['issue_number']][i['event']] = 1
        else:
            issue2eventCount[i['issue_number']]={i['event']:1}
    return issue2eventCount

#Change the format of time
def day2timeStamp(string):
    if len(string) == 10:
        return int(time.mktime(time.strptime(string,"%Y-%m-%d")))
    elif len(string) == 20:
        return int(time.mktime(time.strptime(string,"%Y-%m-%dT%H:%M:%SZ")))
    else:
        return -1

      
#entropy formula
def lstToEntropy(lst,sm):
    result = 0
    for i in lst:
        pi = i/sum(lst)
        result += -pi*log(pi,2)
    return result*sm

#entropy for each time
#input time2issuesEvent：{time:{issue_number:{event：count}}}
#output {x:y}
def dataToEntropy(time2issuesEvent,time2issuesEventAll):
    x = time2issuesEvent.keys()
    result = {}
    for i in x:
        issue2event2count = time2issuesEvent[i]
        issue2event2countAll = time2issuesEventAll[i]
        if issue2event2count and issue2event2countAll:
            tmpResult = 0
            for issue in issue2event2countAll.keys():
                if issue2event2count.get(issue):
                    sm = sum(list(issue2event2count[issue].values()))
                else:
                    sm = 0
                tmpResult += lstToEntropy(list(issue2event2countAll[issue].values()) + [1],sm)
            result[i] = tmpResult
            #result[i] = tmpResult/len(issue2event2count.values())
        else:
            result[i] = 0
    return result


def timelstToEntropy(timelst):
    time2issuesEvent = {}
    time2issuesEventAll = {}
    for i in range(len(timelst) - 1):
        time2issuesEvent[timelst[i]] = filterEvent(timelst[i],timelst[i+1])
        time2issuesEventAll[timelst[i]] = filterEventAll(timelst[i],timelst[i+1])
    result = dataToEntropy(time2issuesEvent,time2issuesEventAll)
    return result


def calEntropy(repo,timelst):
    global special_permissions
    global divide_permissions
    special_permissions,divide_permissions = getAccess()
    global special_user_dic
    special_user_dic = get_special_user(repo)
    global collection_issues
    global collection_timeline
    collection_issues,collection_timeline = getCollection(repo)
    result = timelstToEntropy(timelst)
    x = list(result.keys())
    y = list(result.values())
    return (x,y)


#set mongodb
def getCollection(repo):
    client = pymongo.MongoClient(host='localhost',port=27017)
    db = client[repo]
    collection_timeline = db.timeline   
    collection_issues = db.issues
    return (collection_issues,collection_timeline)


def getAccess():
    df = pd.read_excel('data/event_type/event_type.xlsx',sheet_name= "event_type")
    dic = dict(zip(df['event_type'],df['access']))
    special_permissions = []
    divide_permissions = []
    for key in dic.keys():
        if dic[key] in ['maintain access','write access','triage access','onwer access']:
            special_permissions.append(key)
        elif dic[key] in ['triage access(read access when they opened)','triage access(read access they opened themselves)']:
            divide_permissions.append(key)
        else:
            continue
    return (special_permissions,divide_permissions)

def get_eventLst(repo):
    collection_issues,collection_timeline = getCollection(repo)
    eventLst = []
    for i in collection_timeline.find({'$and':[{'$nor':[{"event":'labeled'},{"event":'unlabeled'},{"event":'commit-commented'},{"event":'line-commented'},{"user.type":'Bot'},{"actor.type":'Bot'}]}]}):
        eventLst.append(i)
    return eventLst
###return special_user:(userLogin,created_at)

def get_special_user(repo):
    eventLst = get_eventLst(repo)
    core_user = []   
    special_permissions_user_dic = {}
    divide_permissions_user_dic = {}
    count = 0    
    
    for i in eventLst:
        if i['event'] in divide_permissions:
            if i.get('user'):
                if(i['user']['login'] != i['issue_founder']):
                    if divide_permissions_user_dic.get(i['user']['login']):
                        divide_permissions_user_dic[i['user']['login']]['min'] = min(divide_permissions_user_dic[i['user']['login']]['min'],i['created_at'])
                        divide_permissions_user_dic[i['user']['login']]['max'] = max(divide_permissions_user_dic[i['user']['login']]['max'],i['created_at'])
                    else:
                        divide_permissions_user_dic[i['user']['login']] = {'min':i['created_at'],'max':i['created_at']}
            elif i.get('actor'):
                if(i['actor']['login'] != i['issue_founder']):
                    if divide_permissions_user_dic.get(i['actor']['login']):
                        divide_permissions_user_dic[i['actor']['login']]['min'] = min(divide_permissions_user_dic[i['actor']['login']]['min'],i['created_at'])
                        divide_permissions_user_dic[i['actor']['login']]['max'] = max(divide_permissions_user_dic[i['actor']['login']]['max'],i['created_at'])
                    else:
                        divide_permissions_user_dic[i['actor']['login']] = {'min':i['created_at'],'max':i['created_at']}
            else:
                pass
                #print(i)
        if i['event'] in special_permissions:
            if i.get('user'):
                if special_permissions_user_dic.get(i['user']['login']):
                    special_permissions_user_dic[i['user']['login']]['min'] = min(special_permissions_user_dic[i['user']['login']]['min'],i['created_at'])
                    special_permissions_user_dic[i['user']['login']]['max'] = max(special_permissions_user_dic[i['user']['login']]['max'],i['created_at'])
                else:
                    special_permissions_user_dic[i['user']['login']] = {'min':i['created_at'],'max':i['created_at']}
            elif i.get('actor'):
                if special_permissions_user_dic.get(i['actor']['login']):
                    special_permissions_user_dic[i['actor']['login']]['min'] = min(special_permissions_user_dic[i['actor']['login']]['min'],i['created_at'])
                    special_permissions_user_dic[i['actor']['login']]['max'] = max(special_permissions_user_dic[i['actor']['login']]['max'],i['created_at'])
                else:
                    special_permissions_user_dic[i['actor']['login']] = {'min':i['created_at'],'max':i['created_at']}
            else:
                pass
                #print(i)
    special_user_dic = {}
    a = divide_permissions_user_dic
    b = special_permissions_user_dic
    for i in list(a.keys())+list(b.keys()):
        if i in a.keys() and i in b.keys():
            special_user_dic[i] = {}
            special_user_dic[i]['min'] = min(a[i]['min'],b[i]['min'])
            special_user_dic[i]['max'] = min(a[i]['max'],b[i]['max'])
        elif i in a.keys() and i not in b.keys():
            special_user_dic[i] = a[i]
        elif i in b.keys() and i not in a.keys():
            special_user_dic[i] = b[i]
    return special_user_dic


def get_date():
    c = Calendar()
    dateLst = []
    for year in range(2007,2022):
        for month in range(1,13):
            dateLst += [str(date) for date in c.itermonthdates(year,month)]
    dateLst = list(set(dateLst))
    dateLst.sort()
    return dateLst




dateLst = get_date()
timelst = []
for i in range(len(dateLst)):
    timelst.append(dateLst[i])

timelst = timelst[1044:1047]
#company project
xgo,ygo = calEntropy('go',timelst)
xbootstrap,ybootstrap = calEntropy('bootstrap',timelst)
xreact,yreact = calEntropy('react',timelst)
xtensorflow,ytensorflow = calEntropy('tensorflow',timelst)
#non-company project
xrails,yrails = calEntropy('rails',timelst)
xvue,yvue = calEntropy('vue',timelst)
xelectron,yelectron = calEntropy('electron',timelst)
xrust,yrust = calEntropy('rust',timelst)

lst = []
lst.append((xgo,ygo))
lst.append((xbootstrap,ybootstrap))
lst.append((xreact,yreact))
lst.append((xtensorflow,ytensorflow))
lst.append((xrails,yrails))
lst.append((xvue,yvue))
lst.append((xelectron,yelectron))
lst.append((xrust,yrust))
np.save('entropy_for_peripheral_developer.npy',lst)
