from flask import Flask,render_template,request,flash,redirect
from functions import web_predict,config,parse_url,get_daily_news
from BertClass import BertClassifier
from config import APSchedulerJobConfig
from flask_sqlalchemy import SQLAlchemy
from flask_apscheduler import APScheduler

app = Flask(__name__)
app.config.from_object(APSchedulerJobConfig)
app.secret_key = 'why would I tell you my secret key?'
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///news.sqlite3"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
app.config["SQLALCHEMY_ECHO"] = True
db = SQLAlchemy(app)

class news(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50))
    URLs = db.Column(db.String(100))
    Mark = db.Column(db.String(10))
    Outlet = db.Column(db.String(10))
    Image = db.Column(db.String(150))
    MarkNumber = db.Column(db.Integer)

    def __init__(self, title, URLs, Mark,Outlet,Image,MarkNumber):
        self.title = title
        self.URLs = URLs
        self.Mark = Mark
        self.Outlet=Outlet
        self.MarkNumber=MarkNumber
        self.Image=Image

@app.route('/')
def home():
    #db.drop_all()
    #db.create_all()
    return render_template("home.html")

@app.route('/upload')
def upload():
    return render_template("upload.html")

@app.route('/uploadRes',methods = ['POST'])
def uploadRes():
    try:
        url = request.form['website']
        text,title,image = parse_url(url)
        score = web_predict(url,bert_model)
        score = round(score,4)
        if score>0.5:
            if url.startswith("https://www.cnn") or url.startswith("https://edition.cnn") or url.startswith(
                "http://www.cnn"):
                news_add = news(title, url, "Pos", "cnn", image, 0)
            elif url.startswith("https://www.bbc"):
                news_add = news(title, url, "Pos", "bbc", image, 0)
            elif url.startswith("https://abc"):
                news_add = news(title, url, "Pos", "abc", image, 0)
            elif url.startswith("https://www.cbc"):
                news_add = news(title, url, "Pos", "cbc", image, 0)
            elif "foxnews" in url:
                news_add = news(title, url, "Pos", "fox", image, 0)
            else:
                news_add = news(title, url, "Pos", "else", image, 0)
            db.session.add(news_add)
            db.session.commit()
            msg1 = "This news is positive. "
            msg2 = "This news has been uploaded."
        else:
            msg1 = "This news is negative. "
            msg2 = "Please double check this news. "
        res = {}
        res['text'] = text
        res['title'] = title
        if len(text)==0:
            res['text'] = "No text is captured"
        if len(title)==0:
            res['title'] = "No title is captured"
        if len(image)==0:
            res['img'] = "No image"
        else:
            res['img'] = image
        res['msg1'] = msg1
        res['msg2'] = msg2
    except:
        res = {}
        res['text'] = "No text is captured"
        res['title'] = "No title is captured"
        res['img'] = "No image"
        res['msg1'] = "Sorry but we cannot access this news website."
        res['msg2'] = "Please check the validity of the news or try it later."
    return render_template("upload.html", resultval=res)

@app.route('/predict')
def predict():
    return render_template("predict.html")


@app.route('/predictRes',methods = ['POST'])
def predictRes():
    try:
        url = request.form['website']
        text,title,image = parse_url(url)
        score = web_predict(url,bert_model)
        score = round(score,4)
        if score>0.5:
            msg1 = "This news is positive. "
        else:
            msg1 = "This news is negative. "
        msg2 = "The predicted score is "+ str(score)
        res = {}
        res['text'] = text
        res['title'] = title
        if len(text)==0:
            res['text'] = "No text is captured"
        if len(title)==0:
            res['title'] = "No title is captured"
        if len(image)==0:
            res['img'] = "No image"
        else:
            res['img'] = image
        res['msg1'] = msg1
        res['msg2'] = msg2
    except:
        res = {}
        res['text'] = "No text is captured"
        res['title'] = "No title is captured"
        res['img'] = "No image"
        res['msg1'] = "Sorry but we cannot access this news website."
        res['msg2'] = "Please check the validity of the news or try it later."
    return render_template("predict.html", resultval=res)

@app.route('/database')
def database():
    all_infor = news.query.all()
    length = len(all_infor)
    return render_template("database.html",news=all_infor,length=length)

@app.route('/database/bbc')
def databasebbc():
    all_infor = news.query.filter_by(Outlet='bbc').all()
    length = len(all_infor)
    return render_template("database.html",news=all_infor,length=length)

@app.route('/database/abc')
def databaseabc():
    all_infor = news.query.filter_by(Outlet='abc').all()
    length = len(all_infor)
    return render_template("database.html",news=all_infor,length=length)

@app.route('/database/cbc')
def databasecbc():
    all_infor = news.query.filter_by(Outlet='cbc').all()
    length = len(all_infor)
    return render_template("database.html",news=all_infor,length=length)

@app.route('/database/cnn')
def databasecnn():
    all_infor = news.query.filter_by(Outlet='cnn').all()
    length = len(all_infor)
    return render_template("database.html",news=all_infor,length=length)

@app.route('/database/fox')
def databasefox():
    all_infor = news.query.filter_by(Outlet='fox').all()
    length = len(all_infor)
    return render_template("database.html",news=all_infor,length=length)

@app.route('/database/else')
def databaseelse():
    all_infor = news.query.filter_by(Outlet='else').all()
    length = len(all_infor)
    return render_template("database.html",news=all_infor,length=length)

@app.route('/update/<id>',methods = ['GET','POST'])
def update(id):
    update_news=news.query.get(id)
    if update_news.Mark=="Pos":
        update_news.Mark="Neg"
    update_news.MarkNumber = update_news.MarkNumber+1
    db.session.commit()
    return redirect('/database')

if __name__ == '__main__':
    bert_model = config()
    app.run()

scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()