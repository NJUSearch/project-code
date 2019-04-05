#encoding:utf-8
import sqlite3
import csv
import os
import re
import urllib.request
import urllib.error
import urllib
from bs4 import BeautifulSoup
from py2neo import Graph, Node, Relationship

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:23.0) Gecko/20100101 Firefox/23.0'}

def initialize_csv():   #初始化csv文件
    qfile = open('C:/Users/89597/.Neo4jDesktop/neo4jDatabases/database-4192cdaf-affe-4346-84aa-4250b1526a4b/installation-3.4.1/import/question.csv','w',newline='')
    writer = csv.writer(qfile)
    writer.writerow(('question_id','question_title','question_body','question_vote'))
    qfile.close()

    afile = open('C:/Users/89597/.Neo4jDesktop/neo4jDatabases/database-4192cdaf-affe-4346-84aa-4250b1526a4b/installation-3.4.1/import/answer.csv', 'w', newline='')
    writer = csv.writer(afile)
    writer.writerow(('answer_id', 'answer_body', 'answer_vote','question_id'))
    afile.close()

    tfile = open('C:/Users/89597/.Neo4jDesktop/neo4jDatabases/database-4192cdaf-affe-4346-84aa-4250b1526a4b/installation-3.4.1/import/tag.csv', 'w', newline='')
    writer = csv.writer(tfile)
    writer.writerow(('tag_name', 'tag_description', 'question_id'))
    tfile.close()

def analyze(html, question_id):
    #print(html)
    soup = BeautifulSoup(html, "html.parser")
    question_title = soup.find("meta", itemprop='name')#获取问题标题
    print("question title: "+question_title['content'])

    question_description = soup.find("div", itemprop='text')#获取问题描述
    al = re.compile(r'<pre><code>(.*?)</code></pre>', re.S)
    string_deletecode = al.sub('',str(question_description))
    question_body = BeautifulSoup(str(string_deletecode),"html.parser")
    print("question body: "+question_body.get_text())

    qvote = soup.find("div", itemprop="upvoteCount")#获取问题票数
    question_vote = qvote.get_text()
    print("question vote: "+str(question_vote)+'\n')

    with open("C:/Users/89597/.Neo4jDesktop/neo4jDatabases/database-4192cdaf-affe-4346-84aa-4250b1526a4b/installation-3.4.1/import/question.csv",'a',newline='',encoding="utf-8") as qfile:
        writer = csv.writer(qfile)
        writer.writerow([question_id,question_title['content'],question_body.get_text(),question_vote])

    answer_ids = soup.find_all("div", itemprop="acceptedAnswer")#获取回答号
    answer_ids.extend(soup.find_all("div", itemprop="suggestedAnswer"))

    answers = soup.find_all("div", itemprop='text')#获取回答描述
    del answers[0]
    answer_votes = soup.find_all("div", itemprop="upvoteCount")#获取回答票数
    del answer_votes[0]
    for answer, id, answer_vote in zip(answers, answer_ids, answer_votes):
        answer_deletecode = al.sub('',str(answer))
        answer_body = BeautifulSoup(str(answer_deletecode),"html.parser")
        answer_id = id['data-answerid']
        print("answer_id: "+str(answer_id)+"  vote: "+answer_vote.get_text())
        print(answer_body.get_text())
        with open("C:/Users/89597/.Neo4jDesktop/neo4jDatabases/database-4192cdaf-affe-4346-84aa-4250b1526a4b/installation-3.4.1/import/answer.csv",'a',newline='',encoding="utf-8") as afile:
            writer = csv.writer(afile)
            writer.writerow([answer_id, answer_body.get_text(), answer_vote.get_text(), question_id])

    question_tag = soup.find("div", class_='post-taglist')
    tag = BeautifulSoup(str(question_tag), "html.parser")
    st = tag.get_text()
    list = st.split()#获取tag标签
    for tag_name in list:
        print(tag_name)
        url_tag = 'https://stackoverflow.com/tags/'+tag_name+'/info'
        print(url_tag)
        html_tag = urllib.request.urlopen(url_tag, timeout=10).read().decode('utf-8')
        soup_tag = BeautifulSoup(html_tag, "html.parser")
        tag_description = soup_tag.find("div", attrs={'class':'welovestackoverflow'})
        #获取标签的维基简介
        print(tag_description.p.get_text())
        with open("C:/Users/89597/.Neo4jDesktop/neo4jDatabases/database-4192cdaf-affe-4346-84aa-4250b1526a4b/installation-3.4.1/import/tag.csv",'a',newline='',encoding="utf-8") as tfile:
            writer = csv.writer(tfile)
            writer.writerow([tag_name, tag_description.p.get_text(), question_id])

def save_data():
    graph = Graph(
        "http://localhost:7474",
        username="neo4j",
        password="123456"
    )
    instr = "MATCH (n)-[r]-(m) DELETE r"  # 删除所有关系
    graph.run(instr)  # 直接调用Cypher命令对数据库进行操作
    instr = "MATCH (n) DELETE n"  # 删除所有节点
    graph.run(instr)

    f = open('C:/Users/89597/.Neo4jDesktop/neo4jDatabases/database-4192cdaf-affe-4346-84aa-4250b1526a4b/installation-3.4.1/import/question.csv', 'r', encoding='utf-8')
    csv_reader_lines = csv.reader(f)
    next(csv_reader_lines)
    count = 1
    for line in csv_reader_lines:
        print(str(count) + str(line))
        node = Node("Question", question_id=line[0], question_title=line[1], question_body=line[2],
                    question_vote=line[3])
        graph.create(node)
        count = count + 1

    f = open('C:/Users/89597/.Neo4jDesktop/neo4jDatabases/database-4192cdaf-affe-4346-84aa-4250b1526a4b/installation-3.4.1/import/answer.csv', 'r', encoding='utf-8')
    csv_reader_lines = csv.reader(f)
    next(csv_reader_lines)
    count = 1
    for line in csv_reader_lines:
        print(str(count) + str(line))
        node = Node("Answer", answer_id=line[0], answer_body=line[1], answer_vote=line[2])
        graph.create(node)
        count = count + 1

    tag_list = []
    f = open('C:/Users/89597/.Neo4jDesktop/neo4jDatabases/database-4192cdaf-affe-4346-84aa-4250b1526a4b/installation-3.4.1/import/tag.csv', 'r', encoding='utf-8')
    csv_reader_lines = csv.reader(f)
    next(csv_reader_lines)
    count = 1
    for line in csv_reader_lines:
        if line[0] in tag_list:
            continue
        else:
            print(str(count) + str(line))
            tag_list.append(line[0])
            node = Node("Tag", tag_name=line[0], tag_description=line[1])
            graph.create(node)
            count = count + 1

    f = open('C:/Users/89597/.Neo4jDesktop/neo4jDatabases/database-4192cdaf-affe-4346-84aa-4250b1526a4b/installation-3.4.1/import/answer.csv', 'r', encoding='utf-8')
    csv_reader_lines = csv.reader(f)
    next(csv_reader_lines)
    count = 1
    for line in csv_reader_lines:
        print(str(count) + " Relation: Question-->Answer" + str(line))
        count = count + 1
        answer_id = line[0]
        question_id = line[3]
        instr = """
                match (a:Question),(b:Answer)
                where a.question_id = '""" + question_id + """' and b.answer_id = '""" + answer_id + """' 
                create (a)-[r:has_answer]->(b)
            """
        graph.run(instr)

    f = open('C:/Users/89597/.Neo4jDesktop/neo4jDatabases/database-4192cdaf-affe-4346-84aa-4250b1526a4b/installation-3.4.1/import/tag.csv', 'r', encoding='utf-8')
    csv_reader_lines = csv.reader(f)
    next(csv_reader_lines)
    count = 1
    for line in csv_reader_lines:
        print(str(count) + " Relation: Question-->Tag" + str(line))
        count = count + 1
        tag_name = line[0]
        question_id = line[2]
        instr = """
                match (a:Question),(b:Tag)
                where a.question_id = '""" + question_id + """' and b.tag_name = '""" + tag_name + """' 
                create (a)-[r:has_tag]->(b)
            """
        graph.run(instr)


if __name__=='__main__':
    '''
    initialize_csv()

    # db1.db : questions tagged [c++] , totally 577,258 questions
    # db2.db : questions tagged [c++ && (sorting || search || tree || graph || linked-list) ], totally 9,496 questions
    DB_NAME = 'db2.db'
    URL_HEAD = 'https://stackoverflow.com/questions/'

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    print('Connect to database %s successfully!' %DB_NAME)
    data = cursor.execute("SELECT ID FROM QUESTION")
    count = 0
    for row in data:
        question_id = row[0]
        url = URL_HEAD + str(question_id)
        print(url)
        req = urllib.request.Request(url=url, headers=headers)  # 同样进行伪装

        #using url here
        try:
            html = urllib.request.urlopen(req, timeout=15).read().decode('utf-8')
            analyze(html, question_id)
        except urllib.error.HTTPError:
            print('【HTTP ERROR】')
        except urllib.error.URLError:
            print('【URL ERROR】')
        except socket.timeout:
            print('【TIMEOUT ERROR】')
        except Exception:
            print('【Unknown ERROR】')
        count = count + 1
        if (count == 10):
            time.sleep(1)
            count = 0
    conn.close()
    print('Connect close successfully.')
    '''
    save_data()    #将获取的信息存入neo4j
