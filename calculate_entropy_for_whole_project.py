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
    for i in collection_timeline.find({'$and':[{'created_at':{'$gt':startTime,'$lt':endTime}},{'$nor':[{"event":'commit-commented'},{"event":'line-commented'},{"user.type":'Bot'},{"actor.type":'Bot'}]}]}):
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
def lstToEntropy(lst):
    result = 0
    for i in lst:
        pi = i/sum(lst)
        result += -pi*log(pi,2)
    return result*sum(lst)

#entropy for each time
#input time2issuesEvent：{time:{issue_number:{event：count}}}
#output {x:y}
def dataToEntropy(time2issuesEvent):
    x = time2issuesEvent.keys()
    result = {}
    for i in x:
        issue2event2count = time2issuesEvent[i]
        if issue2event2count:
            tmpResult = 0
            for item in issue2event2count.values():
                tmpResult += lstToEntropy(list(item.values()) + [1])
            result[i] = tmpResult
            #result[i] = tmpResult/len(issue2event2count.values())
        else:
            result[i] = 0
    return result

def timelstToEntropy(timelst):
    time2issuesEvent = {}
    for i in range(len(timelst) - 1):
        time2issuesEvent[timelst[i]] = filterEvent(timelst[i],timelst[i+1])
    result = dataToEntropy(time2issuesEvent)
    return result

def calEntropy(repo,timelst):
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
np.save('entropy_for_whole_project.npy',lst)
