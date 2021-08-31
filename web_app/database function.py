import sqlite3
from newspaper import Article
from functions import parse_url,get_daily_news
def get_title(url):
    news = Article(url)
    news.download()
    news.parse()
    return news.title

def insert_news(url):
    db = 'news.sqlite3'
    con = sqlite3.connect(db)
    cur = con.cursor()
    text,title,image=parse_url(url)
    title = list(title)
    for item in title:
        if item == '"' or item == "'":
            title.remove(item)
    title = "".join(title)
    outlet='cnn'
    insert_sql = "insert into news (title,URLs,Mark,Outlet,Image,MarkNumber) values ('{title}','{url}','Pos','{outlet}','{image}',0)".format(url=url,title=title,outlet=outlet,image=image)
    cur.execute(insert_sql)
    con.commit()
    cur.close()
    cur = con.cursor()
    select_sql = "select title,URLs,Mark,Outlet,Image,MarkNumber from news"
    cur.execute(select_sql)
    date_set = cur.fetchall()
    print(date_set)
    cur.close()

def delete_news():
    db = 'news.sqlite3'
    con = sqlite3.connect(db)
    cur = con.cursor()
    insert_sql = "delete from news where Outlet = 'fox'"
    cur.execute(insert_sql)
    con.commit()
    cur.close()
    cur = con.cursor()
    select_sql = "select title,URLs,Mark,Outlet,Image,MarkNumber from news"
    cur.execute(select_sql)
    date_set = cur.fetchall()
    print(date_set)
    cur.close()
def get():
    url="https://edition.cnn.com/travel/article/nara-deer-plastic-bags-scli-intl-scn/index.html"
    text,title,image = parse_url(url)
    title = list(title)
    for item in title:
        if item =='"' or item =="'":
            title.remove(item)
    title = "".join(title)
    #print(text)
    print(title)
    print(image)
#url="https://edition.cnn.com/travel/article/nara-deer-plastic-bags-scli-intl-scn/index.html"
#insert_news(url)
#delete_news()
db = 'news.sqlite3'
con = sqlite3.connect(db)
cur = con.cursor()
select_sql = "select title,URLs,Mark,Outlet,Image,MarkNumber from news"
cur.execute(select_sql)
date_set = cur.fetchall()
print(date_set)
cur.close()