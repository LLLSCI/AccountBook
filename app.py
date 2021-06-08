import datetime

from flask import Flask,render_template,request,url_for,redirect
from flask_sqlalchemy import SQLAlchemy
import time


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']='mysql://root:@localhost/accountbook'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
db=SQLAlchemy(app)

#创建模型
class User(db.Model):
    __tablename__='user'
    user_id=db.Column(db.Integer,primary_key=True)
    username=db.Column(db.String(18),unique=True)
    password=db.Column(db.String(18))
    accounts=db.relationship('Account',backref='user')

class Account(db.Model):
    __tablename__='acoount'
    id=db.Column(db.Integer,primary_key=True)
    date=db.Column(db.Date)
    typeId=db.Column(db.Integer)
    money=db.Column(db.Float)
    fk_user_id=db.Column(db.Integer,db.ForeignKey('user.user_id'))


#登录
@app.route('/',methods=['POST','GET'])
def login():
    if request.method=='GET':
        return render_template('login.html',labbel='')
    if request.method=='POST':
        username=request.form.get('username')
        password=request.form.get('password')
        user=User.query.filter_by(username=username).first()
        users=User.query.all()
        if user:
            if user.password==password:
                #重定向，进入展示页面
               return redirect(url_for('interface',username=username))
            else:
                return render_template('login.html',label='账号密码错误')
        else:
            return render_template('login.html',label='账号密码错误')

#注册
@app.route('/register',methods=['POST','GET'])
def register():
    if request.method=='GET':
        return render_template('register.html',label='')
    else:
        username=request.form.get('username')
        password=request.form.get('password')
        user=User.query.filter_by(user_id=username).first()
        if username=='' or password=='':
            return render_template('register.html',label='输入不能为空')
        elif len(username)>18 or len(password)>18:
            return render_template('register.html',label='输出超过最大长度')
        elif user:
            return render_template('register.html',label='已存在相同用户名')
        else:
            try:
                new_add_user = User(username=username, password=password)
                db.session.add(new_add_user)
                db.session.commit()
                return render_template('register.html', label='注册成功')
            except Exception as e:
                print(e)


@app.route('/interface/<username>')
def interface(username):
    return render_template('index.html',username=username)


@app.route('/jiyibi/<username>')
def jiyibi(username):
    return render_template('views/记一笔.html',username=username)

@app.route('/xiaofeiyilan/<username>')
def xiaofeiyilan(username):
    totalConsumption,monthConsumption,dayConsumption=xiaofeiyilanFunction(username)
    return render_template('views/消费一览.html',username=username,totalConsumption=totalConsumption,monthConsumption=monthConsumption,dayConsumption=dayConsumption)

@app.route('/xiaofeichakan/<username>')
def xiaofeichakan(username):
    accounts,index=xiaofeichakanFunciton(username)
    return render_template('views/消费查看.html',username=username,accounts=accounts,index=index)

@app.route('/zhuzhuangtu/<username>')
def zhuzhuangtu(username):
    ConsumeList=zhuzhuangtuFunction(username)
    return render_template('views/柱状图.html',username=username,ConsumeList=ConsumeList)


def zhuzhuangtuFunction(username):
    ConsumeList=[0,0,0,0,0,0,0,0,0,0]
    user_id=User.query.filter_by(username=username).first().user_id
    accounts=Account.query.filter_by(fk_user_id=user_id)
    for account in  accounts:
        ConsumeList[account.typeId]=ConsumeList[account.typeId]+account.money
    return  ConsumeList


@app.route('/add/<username>/<money>/<typeId>/<date>')
def add(money,typeId,date,username):
    try:
        user_id = User.query.filter_by(username=username).first().user_id
        new_account = Account(money=money, typeId=typeId, date=date, fk_user_id=user_id)
        db.session.add(new_account)
        db.session.commit()
    except Exception as  e:
        print(e)
    return  redirect(url_for("jiyibi",username=username));



#删除消费记录
@app.route('/delete/<account_id>/<username>')
def deleteAccount(account_id,username):
    try:
        account=Account.query.filter_by(id=account_id).first()
        db.session.delete(account)
        db.session.commit()
    except Exception as e:
        print(e)
    return redirect(url_for("xiaofeichakan",username=username))


def xiaofeiyilanFunction(username):
    totalConsumption=0
    monthConsumption=0
    dayConsumption=0
    user_id=User.query.filter_by(username=username).first().user_id
    accounts=Account.query.filter_by(fk_user_id=user_id)


    cur = datetime.datetime.now()
    if cur.month>=10:
        month=str(cur.month)
    else:
        month='0'+str(cur.month)

    if cur.day>=10:
        day=str(cur.day)
    else:
        day='0'+str(cur.day)

    for accout in  accounts:
        print(type(accout.date))
        totalConsumption=totalConsumption+accout.money
        if str(accout.date).split('-')[1]==month:
            monthConsumption=monthConsumption+accout.money
        if str(accout.date).split('-')[2]==day:
            dayConsumption=dayConsumption+accout.money

    return totalConsumption,monthConsumption,dayConsumption

def xiaofeichakanFunciton(username):
    user_id=User.query.filter_by(username=username).first().user_id
    accounts=Account.query.filter_by(fk_user_id=user_id)
    num=Account.query.filter_by(fk_user_id=user_id).count()
    index=[]
    for i in range(0,num):
        index.append(i)

    for i in range(0,num-1):
        for j in range(i+1,num):
            if str(accounts[index[i]].date)<str(accounts[index[j]].date):
                temp=index[i]
                index[i]=index[j]
                index[j]=temp



    for i in range(0,num):
        print(accounts[index[i]].date)

    return accounts,index






# db.drop_all()
# db.create_all()


if __name__ == '__main__':
    app.run()
