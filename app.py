# -*- coding:utf-8 -*-
from flask import Flask, request, render_template
from flask_bootstrap import Bootstrap
import json, sys
import requests
from py2neo import Graph, Node, Relationship
import pymysql
import re

import search



def rep(word):
    return '<span style="color:red">'+word.group(0)+'</span>'

def add_bold_tag(query, text):
    words = query.split(' ')
    words = [a for a in words if a != '']
    p = '|'.join(words)
    return re.sub(p,rep,text,flags=re.IGNORECASE)

app = Flask(__name__)
bootstrap = Bootstrap(app)
passwd = "123456"
graph = Graph("http://localhost:7474", username="neo4j", password=passwd)

db = pymysql.connect(host='localhost', port=3306, user='root',
                             passwd="980306", database='resource')
cursor = db.cursor()

@app.route('/')
def index():
    return render_template('index.html', name='index')


@app.route('/query/', methods=['GET'])
def query():
    if request.method == 'GET':
        has_result = 0
        error = 0
        key_word = request.args.get('q')
        offset = request.args.get('offset')
        #start_index = request.args.get('start')
        offset=request.args.get('offset')
        offset=int(offset)
        page_index=int(offset/10+1)

        #是否能往前翻
        if 1==page_index:
            has_previous=0
        else:
            has_previous=1

        # read engineID
        f = open('data/engine.json')
        s = json.load(f)

        for i in range(len(s['engine'])):
            sn = 'engine_' + str(i + 1)
            key = s['engine'][i][sn]['key']
            cx = s['engine'][i][sn]['cx']
            engine_name = s['engine'][i][sn]['name']

        results = []
        tags = []
        codes=[]
        #tags
        for item in search.get_desc(graph,key_word):
            tag = {"title": add_bold_tag(key_word,item[0]),
                      "link": 'https://stackoverflow.com/tags/'+str(item[0]),
                      "displayLink": 'https://stackoverflow.com/tags/'+str(item[0]),
                      "snippet": add_bold_tag(key_word,item[1][:100])
                      }
            tags.append(tag)

        # results

        for item in search.get_QA(graph,key_word,int(offset)):
              result = {"title": add_bold_tag(key_word,item[0]),
                       "link": 'https://stackoverflow.com/questions/'+str(item[2]),
                       "displayLink": 'https://stackoverflow.com/questions/'+str(item[2]),
                       "snippet":add_bold_tag(key_word,item[1][:400])
                       }
              results.append(result)

        #是否能往后翻
        length=len(results)
        has_next=1
        print(length)
        # codes
        for item in search.get_question(cursor, key_word):
            code = {"title": add_bold_tag(key_word,item[0]),
                      "link": 'http://rosettacode.org/wiki/'+str(item[0])+'#'+str(item[1]),
                      "displayLink": 'http://rosettacode.org/wiki/'+str(item[0])+'#'+str(item[1]),
                      "snippet": add_bold_tag(key_word,item[1])
                      }
            codes.append(code)

        return render_template('index.html', q=key_word, results=results,tags=tags,codes=codes,
                               error=error, engine_name=engine_name,
                               search_info='', has_previous=has_previous,has_next=has_next,
                               page_index=page_index,offset=offset)
        # else:
        # search_info = 'About ' + json_data['searchInformation']['formattedTotalResults'] + ' results (' + \
        #               json_data['searchInformation']['formattedSearchTime'] + ' seconds)'
        # return render_template('index.html', q=q, error=error, engine_name=engine_name, search_info=search_info)

        # search request
    # search.get_QA()
    # url = "https://www.googleapis.com/customsearch/v1"
    # if start_index :
    #     query_string = {"key":key,"cx":cx,"num":"10","q":q,"start":start_index}
    # else :
    #     query_string = {"key":key,"cx":cx,"num":"10","q":q}
    # response = requests.request("GET", url, params=query_string)
    # json_data = json.loads(response.text)

    # if has_result == 1 :
    #     # print "results"
    #     result = []
    #     results = []
    #     items = json_data['items']
    #     current_start_index = json_data['queries']['request'][0]['startIndex']
    #     page_index = (current_start_index-1)/10+1
    #     # print "page is : " + str(page_index)
    #     if current_start_index == 1 :
    #         has_previous = 0
    #         search_info =  'About ' + json_data['searchInformation']['formattedTotalResults'] + ' results (' + json_data['searchInformation']['formattedSearchTime'] + ' seconds)'
    #     else :
    #         has_previous = 1
    #         search_info =  "Page " + str(current_start_index/10+1) + ' of About ' + json_data['searchInformation']['formattedTotalResults'] + ' results (' + json_data['searchInformation']['formattedSearchTime'] + ' seconds)'



@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run(debug=True)
