#encoding:utf-8

import mysql.connector
import urllib.request
import socket
import re
import urllib
from bs4 import BeautifulSoup

#待爬取的类型，可以更改为其他关键词
tag = "C++"

user = 'root'
database = "resource"
passwd = "980306"

#由于rosette code网站有反爬虫机制，需要对访问请求进行伪装
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:23.0) Gecko/20100101 Firefox/23.0'}


def save_txt(title, no, text, desc):  #将代码文本存入mysql数据库
    #with open(title+'('+str(no)+')'+'.txt', 'w') as yfile:#代码预存入文本文件，如不需要可删去
    #    yfile.write(text)
    #    yfile.close()

    #对代码文本中的一些特殊字符进行预处理
    text = text.replace("\n", "\\n")
    text = text.replace("\\","\\\\")
    text = text.replace("'","\\'")
    text = text.replace('"','\\"')
    desc = desc.replace("\n", "\\n")
    desc = desc.replace("\\", "\\\\")
    desc = desc.replace("'", "\\'")
    desc = desc.replace('"', '\\"')
    #print(text)
    #链接生成指令
    instr = 'insert into rosseta(language, question, description, code) values("' + tag + '", "' + title + '", "' + desc + '", "' + text +'")'
    #print(instr)

    # 链接mysql数据库
    db = mysql.connector.connect(host='localhost', port=3306, user=user,
                                      passwd=passwd, database=database, charset='utf8')
    cursor = db.cursor()
    cursor.execute(instr)#执行命令将数据存入mysql数据库

    cursor.execute('SELECT language,question,code FROM rosseta LIMIT 100')#显示当前数据库中内容
    data = cursor.fetchall()
    for row in data:
        language, question, code = row
        print(language + ' ' + question + ' ' + code)
    print('\n')
    db.commit()     #注意！保存上述的更改（否则不会生效）
    cursor.close()
    db.close()


def segment(n, title, desc):  #将获取的代码文本分段（一系列正则语言操作都是用来解决爬取C代码时没有头文件的问题……）
    pattern = re.compile(r'<lang [\.\+\-\#\$\*0-9a-zA-Z]+>')#change all '<lang XXX>' into '$$lang XXX$$'
    res = pattern.findall(n)
    for r in res:
        m = r.lstrip('<')
        m = m.rstrip('>')
        n = re.sub(r, "$$"+m+"$$", n)

    pattern = re.compile(r'</lang>')#change all '</lang>' into '$$/lang$$'
    res = pattern.findall(n)
    for r in res:
        m = r.lstrip('<')
        m = m.rstrip('>')
        n = re.sub(r, "$$"+m+"$$", n)

    pattern = re.compile(r'<[\.\+\-\#\$\*0-9a-zA-Z]+>')#change all '<XXX>' into '@@XXX@@'（此时处理的都是C代码中的头文件）
    res = pattern.findall(n)
    for r in res:
        m = r.lstrip('<')
        m = m.rstrip('>')
        n = re.sub(r, "@@"+m+"@@", n)

    pattern = re.compile(r'\$\$lang [\.\+\-\#\$\*0-9a-zA-Z]+\$\$')#恢复为<lang XXX>
    res = pattern.findall(n)
    for r in res:
        m = r.lstrip('$')
        m = m.lstrip('$')
        m = m.rstrip('$')
        m = m.rstrip('$')
        n = n.replace(r, "<"+m+">")
        #n = re.sub(r, "<"+m+">", n)

    pattern = re.compile(r'\$\$/lang\$\$')#恢复为</lang>
    res = pattern.findall(n)
    for r in res:
        m = r.lstrip('$')
        m = m.lstrip('$')
        m = m.rstrip('$')
        m = m.rstrip('$')
        n = n.replace(r, "<"+m+">")
        #n = re.sub(r, "<" + m + ">", n)

    soup = BeautifulSoup(n, "html.parser")
    codes = soup.find_all("lang")   #利用<lang XXX>…</lang>标签进行html处理
    count = 1
    for code in codes:  #分段处理其中的代码
        print("Num: "+str(count))
        text = code.get_text()
        #print(text)
        pattern = re.compile(r'\@\@[\.\+\-\#\$\*0-9a-zA-Z]+\@\@')   #将'@@XXX@@'恢复为'<XXX>'头文件
        res = pattern.findall(text)
        for r in res:
            m = r.lstrip('@')
            m = m.lstrip('@')
            m = m.rstrip('@')
            m = m.rstrip('@')
            text = text.replace(r, "<" + m + ">")
            #print(text)
        save_txt(title, count, text, desc)  # 将代码存入mysql数据库
        count=count+1

def get_code(html, title):
    soup = BeautifulSoup(html, "html.parser")
    #print(soup)

    content = soup.find("div", class_="mw-content-ltr")
    mm = content.find_all("p")
    desc = ''
    for m in mm:
        desc += m.get_text()
    #print(desc)

    edit = soup.find("a", title="Edit section: "+tag )  #找到问题页面下的一个"edit"链接（其中存放有代码的文本信息）
    site = "http://rosettacode.org"+edit['href']
    print(site)
    req = urllib.request.Request(url=site, headers=headers)
    try:
        html = urllib.request.urlopen(req, timeout=15).read()
    except urllib.error.HTTPError:
        print('【HTTP ERROR】')
    except urllib.error.URLError:
        print('【URL ERROR】')
    except socket.timeout:
        print('【TIMEOUT ERROR】')
    except Exception:
        print('【Unknown ERROR】')

    soup = BeautifulSoup(html, "html.parser")
    #print(soup)

    text = soup.find("textarea", id="wpTextbox1")
    n = text.get_text()
    #print(n)
    segment(n, title, desc)

def save_csv(): #将mysql导出的文件转存为csv格式
    instr = """
    select * from rosseta into outfile 'C:/Users/89597/Documents/test.txt' 
    fields terminated by ',' enclosed by '"' 
    lines terminated by '\r\n';
    """
    db = mysql.connector.connect(host='localhost', port=3306, user=user,
                                 passwd=passwd, database=database, charset='utf8')
    cursor = db.cursor()
    cursor.execute(instr)  # 执行命令将数据存入mysql数据库
    cursor.close()
    db.close()

    rfile = open('C:/Users/89597/Documents/test.txt', 'r', encoding='utf-8')
    text = rfile.read()
    rfile.close()
    text = text.replace("\\\"", "\\\"\"")   #注意，将单个"替换为""（以免csv中格式出错）
    print(text)

    with open('C:/Users/89597/Documents/test1.csv', 'w') as f:
        f.write(text)

if __name__=='__main__':
    #"""
    url = 'http://rosettacode.org/wiki/Category:'+tag   #起始网址
    req = urllib.request.Request(url=url, headers=headers)  #对访问请求进行伪装
    html = urllib.request.urlopen(req).read()

    soup = BeautifulSoup(html, "html.parser")
    #print(soup)

    lists = soup.find_all("div", attrs={'class':'mw-category'})
    #print(list)

    for list in lists:
        questions = list.find_all("a")  #获取到当前关键词（例子中是C++）下的所有问题（可能存在一些无效词，在下方会自动报错返回，不影响代码运行）
        for question in questions:
            t = question['title']
            print(t)
            title = t.replace(" ", "_") #由于网址中的问题文本用'_'而非空格隔开，需要进行一下替换
            print(title)
            question_url = 'http://rosettacode.org/wiki/' + title   #组合得到待爬取问题的网址
            print('Question: '+question_url+'\n')
            req = urllib.request.Request(url=question_url, headers=headers) #同样进行伪装

            try:
                html = urllib.request.urlopen(req, timeout=15).read().decode('utf-8')
                get_code(html, title)
            # except urllib.error.HTTPError:
            #     print('【HTTP ERROR】')
            # except urllib.error.URLError:
            #     print('【URL ERROR】')
            # except socket.timeout:
            #     print('【TIMEOUT ERROR】')
            except Exception as e:
                print(e)
    #"""

    save_csv()
