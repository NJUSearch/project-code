import mysql.connector
from py2neo import Graph, Node, Relationship
import re
import nltk
from nltk.corpus import stopwords

username = ""
passwd = ""	#此处填写数据库连接密码
buffer = {}

def Line():
    print("-----------------------------------------")

def color(str):
    print(str, end='')

def word_filter(input_str):
    #nltk.download('stopwords')  #初次执行的时候需运行此行（取消注释），以安装stopwords。之后执行不再需要运行此行。

    #删去文本中全部标点符号
    input_str = re.sub("[\s+\.\!\/_,$%^*(+\"\']+|[+——！，。？、~@#￥%……&*（）]+", " ",input_str)

    stop_words = stopwords.words('english')
    #print(stop_words)  #全部的英文停用词
    words = input_str.split()

    filtered_words = []
    for w in words:
        if w not in stop_words:
            filtered_words.append(w)

    #print(words)
    #print(filtered_words)
    return filtered_words


#tags
def get_desc(graph, key_word):
    Line()
    # print("(Input 'back' for return)")
    # key_word = input("Please input your key word: ")
    # if (key_word == 'back'):    #若输入‘back’，返回上一级
    #     order = ''
    #     return order

    instr = """
        MATCH (b:Tag) WHERE b.tag_name =~ '(?i).*""" + key_word + """.*'
        RETURN b.tag_name as name, b.tag_description as desc
    """     #在数据库中搜索包含关键字的tag
    data = graph.run(instr)
    tag_list = []
    desc_list = []
    weight = []
    count = 0
    for i in data:
        if(count>=10):  #如果匹配项过多，只显示前10个
            break
        #print(str(count)+": "+i['name'])
        tag_list.append(i['name'])
        desc_list.append(i['desc'])
        weight.append(1)
        count+=1


    if(len(tag_list)<=0): #如果输入的语句作为整体没有找到匹配
        word_list = word_filter(key_word)#key_word.split()#将输入语句拆分，
        for word in word_list:      #每个词分别搜索
            instr = """
                MATCH (b:Tag) WHERE b.tag_name =~ '(?i).*""" + word + """.*'
                RETURN b.tag_name as name, b.tag_description as desc
            """
            data = graph.run(instr)
            for i in data:
                t = i['name']
                if t in tag_list:   #如果匹配项已经在列表中
                    weight[tag_list.index(t)]+=1    #给其对应权值加一
                else:
                    tag_list.append(t)  #否则，将新的项加入列表
                    desc_list.append(i['desc'])
                    weight.append(1)

    #print(tag_list)
    #print(weight)
    tuple = []
    for n in range(0, len(tag_list)):   #将每个tag描述和其检索权值组合成序对
        tuple.append((tag_list[n], desc_list[n], weight[n]))
    tuple = sorted(tuple, key=lambda w: w[2], reverse=True) #按照权值降序排序
    return tuple[:5]

    #print(tuple)
    #print(tuple[0][0])
    # for n in range(0, len(tuple)):
    #     if (n >= 10):
    #         break
    #     color(str(n) + ": ")
    #     print(tuple[n][0])
    #
    # if(len(tuple)==0):
    #     color("Nothing found!")
    # else:
    #     while (1):
    #         Line()
    #         print("(Input 'back' for return)")
    #         num = input("Please choose a question num from 0 to " + str(min(9, len(tuple) - 1)) + ": ")
    #         if (num.isdigit() and int(num) in range(0, len(tuple))):
    #             break
    #         elif(num == 'back'):
    #             order = ''
    #             return order
    #
    #     instr = """
    #          MATCH (b:Tag) WHERE b.tag_name = '""" + tuple[int(num)][0] + """'
    #          RETURN b.tag_name as name, b.tag_description as desc
    #     """
    #     data = graph.run(instr)
    #     for i in data:
    #         color(i['name']+": ")
    #         print(i['desc'])
    #
    # order = '1'
    # return order

#results
def get_QA(graph,key_word,offset):
    Line()
    print("(Input 'back' for return)")
    # key_word = input("Please input your key word: ")
    # if (key_word == 'back'):
    #     order = ''
    #     return order
    if key_word in buffer:
        return buffer[key_word][min(offset,len(buffer[key_word])):min(offset+10,len(buffer[key_word]))]
    else:
        instr = """
                MATCH (b:Question) WHERE b.question_title =~ '(?i).*""" + key_word + """.*'
                RETURN b.question_title as title, b.question_body as body, b.question_id as id
            """
        data = graph.run(instr)
        title_list = []
        body_list = []
        id_list = []
        weight = []
        for i in data:
            # print(str(count) + ': ')
            # print(i['title'])
            title_list.append(i['title'])
            body_list.append(i['body'])
            id_list.append(i['id'])
            weight.append(1)

        if (len(title_list) <= 0):
            word_list = word_filter(key_word)  # .split()  # 将输入语句拆分，
            for word in word_list:  # 每个词分别搜索
                instr = """
                        MATCH (b:Question) WHERE b.question_title =~ '(?i).*""" + word + """.*'
                        RETURN b.question_title as title, b.question_body as body, b.question_id as id
                    """
                data = graph.run(instr)
                for i in data:
                    t = i['title']
                    if t in title_list:  # 如果匹配项已经在列表中
                        weight[title_list.index(t)] += 1  # 给其对应权值加一
                    else:
                        title_list.append(t)  # 否则，将新的项加入列表
                        body_list.append(i['body'])
                        id_list.append(i['id'])
                        weight.append(1)

        # print(title_list)
        # print(body_list)
        # print(weight)
        tuple = []
        print(len(title_list))
        print(len(body_list))
        print(len(id_list))
        for n in range(0, len(title_list)):
            tuple.append((title_list[n], body_list[n], id_list[n], weight[n]))
        tuple = sorted(tuple, key=lambda w: w[3], reverse=True)  # 按照权值降序排序
        buffer[key_word] = tuple
        return tuple[min(offset,len(buffer[key_word])):min(offset+10,len(buffer[key_word]))]


    # for n in range(0, len(tuple)):
    #     if (n >= 10):
    #         break
    #     color(str(n)+": ")
    #     print(tuple[n][0])
    #
    # if(len(tuple)==0):
    #     color("Nothing found!")
    # else:
    #     while(1):
    #         Line()
    #         print("(Input 'back' for return)")
    #         num = input("Please choose a question num from 0 to " + str(min(9, len(tuple) - 1)) + ": ")
    #         if (num.isdigit() and int(num) in range(0, len(tuple))):
    #             break
    #         elif (num=='back'):
    #             order = ''
    #             return order
    #
    #     color("Question title: ")
    #     print(tuple[int(num)][0])
    #     color("Question desc: ")
    #     print(tuple[int(num)][1])
    #
    #     m = ''
    #     while (m != 'back'):
    #         Line()
    #         print("(Input 'back' for return)")
    #         m = input("""
    #             1:show answers
    #             2:show linked tags
    #         """)
    #         if (m == '1'):
    #             instr = """
    #                 MATCH (a:Question)-->(b:Answer) WHERE a.question_title='""" + tuple[int(num)][0].replace("\'","\\'") + """'
    #                 RETURN b.answer_body as body, b.answer_vote as vote
    #             """
    #             data = graph.run(instr)
    #             answer_no = 1
    #             for i in data:
    #                 color("Answer " + str(answer_no) + "  ")
    #                 color("Vote: ")
    #                 color(i['vote'])
    #                 print(i['body'])
    #                 answer_no = answer_no + 1
    #
    #         elif (m == '2'):
    #             instr = """
    #                 MATCH (a:Question)-->(b:Tag) WHERE a.question_title='""" + tuple[int(num)][0].replace("\'","\\'") + """'
    #                 RETURN b.tag_name as name
    #             """
    #             data = graph.run(instr)
    #             tag_no = 1
    #             for i in data:
    #                 color("Tag " + str(tag_no) + ": ")
    #                 print(i['name'])
    #                 tag_no = tag_no + 1
    #
    # order = '2'
    # return order

#codes
def get_question(cursor, key_word):
    Line()
    print("(Input 'back' for return)")
    # key_word = input("Please input your key word: ")
    # if (key_word == 'back'):
    #     order = ''
    #     return order

    cursor.execute("SELECT DISTINCT language,question FROM rosseta WHERE question like '%" + key_word + "%' LIMIT 10")
    data = cursor.fetchall()
    language_list = []
    question_list = []
    weight = []
    for row in data:
        language, question = row
        #print("Num " + str(count) + ": " + language + ' ' + question)
        question_list.append(question)
        language_list.append(language)
        weight.append(1)

    if(len(question_list)<=0):
        word_list = word_filter(key_word)#key_word.split()  # 将输入语句拆分，
        for word in word_list:  # 每个词分别搜索
            cursor.execute("SELECT DISTINCT language,question FROM rosseta WHERE question like '%" + word + "%' LIMIT 10")
            data = cursor.fetchall()
            for row in data:
                language, question = row
                if question in question_list:   #如果匹配项已经在列表中
                    weight[question_list.index(question)]+=1    #给其对应权值加一
                else:
                    question_list.append(question)  #否则，将新的项加入列表
                    language_list.append(language)
                    weight.append(1)

    tuple = []
    for n in range(0, len(question_list)):
        tuple.append((question_list[n], language_list[n], weight[n]))
    tuple = sorted(tuple, key=lambda w: w[2], reverse=True)  # 按照权值降序排序
    return tuple[:5]

    # for n in range(0, len(tuple)):
    #     if (n >= 10):
    #         break
    #     color(str(n) + ": ")
    #     print(tuple[n][0])
    #
    # if (len(tuple) == 0):
    #     color("Nothing found!")
    # else:
    #     while (1):
    #         Line()
    #         print("(Input 'back' for return)")
    #         num = input("Please choose a question num from 0 to " + str(min(9, len(tuple) - 1)) + ": ")
    #         if (num.isdigit() and int(num) in range(0, len(tuple))):
    #             break
    #         elif (num=='back'):
    #             order = ''
    #             return order
    #
    #     question = tuple[int(num)][0]
    #     cursor.execute(
    #         "SELECT DISTINCT language, description FROM rosseta WHERE question='" + question + "' LIMIT 10")
    #     data = cursor.fetchall()
    #     language_list = []
    #     for row in data:
    #         language, description = row
    #         if language in language_list:
    #             continue
    #         else:
    #             language_list.append(language)
    #
    #     description= description.replace("\\n", "\n")
    #     color("Question Description: ")
    #     print(description)
    #     color("Language list: "+"\n")
    #     count = 0
    #     for language in language_list:
    #         color(str(count) + ": ")
    #         print(language)
    #         count = count + 1
    #
    #     while (1):
    #         Line()
    #         num = input("Please choose a language num from 0 to " + str(min(9, len(language_list) - 1)) + ": ")
    #         Line()
    #         if (num.isdigit() and int(num) in range(0, len(language_list))):
    #             break
    #
    #     cursor.execute(
    #         "SELECT DISTINCT code FROM rosseta WHERE question='" + question + "' and language ='" + language_list[int(num)] + "' LIMIT 10")
    #     data = cursor.fetchall()
    #     count = 0
    #     for row in data:
    #         code, = row
    #         code = code.replace("\\n", "\n")
    #         color("Code" + str(count) + ": ")
    #         print(code+"\n")
    #         count += 1
    #
    # order = '3'
    # return order

def search():
    # 链接本地数据库
    # graph = Graph("http://localhost:7474", username="neo4j", password=passwd)
    #
    # db = mysql.connector.connect(host='localhost', port=3306, user='root',
    #                              passwd=passwd, database='cjy', charset='utf8')
    # cursor = db.cursor()

    # while (1):
         Line()
    #     order = input("""
    #         1：查看名词释义
    #         2：查看相关问答
    #         3：查看相关习题
    #         4：结束
    #
    #     请输入数字指令: """)
    #
    #     while(order == '1'):
    #         order = get_desc(graph)
    #
    #     while (order == '2'):
    #         order = get_QA(graph)
    #
    #     while (order == '3'):
    #         order =get_question(cursor)
    #
    #     if(order == '4'):
    #         break


if __name__ == '__main__':
    # search()
    # graph = Graph("http://localhost:7474", username=username, password=passwd)
    # print(get_QA(graph,'test'))
    input_str = "How to sort an array."
    print(word_filter(input_str))
