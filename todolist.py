from fastapi import FastAPI, Depends,Body, HTTPException,Query
from jose import jwt
from jose.exceptions import*
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import Column,create_engine,Integer,String, ForeignKey
from sqlalchemy.orm import DeclarativeBase, sessionmaker,relationship
import os
from datetime import datetime,timedelta
from fastapi.responses import Response,FileResponse,RedirectResponse
import sqlite3
#uvicorn todolist:app --reload
app=FastAPI()
SECRET='arv@h2so4'
ALGORITHM='HS256'
oauth2=OAuth2PasswordBearer(tokenUrl='reglog')
DATABASE_URL=os.getenv('DATABASE_URL', 'sqlite:///todolist.db')
engine=create_engine(DATABASE_URL)

def create(username:str):
    payload={
        'sub':username,
        'exp':datetime.now()+timedelta(hours=1)
    }
    token=jwt.encode(payload,SECRET,ALGORITHM)
    return token

def get(token=Depends(oauth2)):
    try:
        data=jwt.decode(token,SECRET,algorithms=[ALGORITHM])
        return data['sub']
    except ExpiredSignatureError:
        print('токен просрочен')
        raise HTTPException(400)
    except:
        raise HTTPException(400)
    
class Base(DeclarativeBase):pass

class User(Base):
    __tablename__='users'
    id=Column(Integer,primary_key=True,index=True)
    name=Column(String)
    password=Column(String)
    tasks=relationship('Task', back_populates='user')

class Task(Base):
    __tablename__='task'
    id=Column(Integer,primary_key=True,index=True)
    name=Column(String)
    user_id=Column(Integer, ForeignKey('users.id'))
    user=relationship('User', back_populates='tasks')

Base.metadata.create_all(bind=engine)

@app.get('/')
def root():
    return FileResponse('mainpage.html')

@app.post('/reglog')
def reglog(data=Body()):
    try:
        Session=sessionmaker(autoflush=False, bind=engine)
        with Session() as db:
            name=data['name']
            password=data['age']
            user=db.query(User).filter(User.name==name).first()
            if not user:
                dummy=User(name=name, password=password)
                db.add(dummy)
                db.commit()
            elif password!=user.password:
                raise HTTPException(401)
            token=create(name)
            return {'status':'ok', 'redirect_url':f'/account?token={token}'}
    except Exception as e:
        print(e)
    
@app.get('/account')
def account(token:str=Query(...)):
    try:
        data=jwt.decode(token,SECRET,algorithms=[ALGORITHM])
        return FileResponse('account.html')
    except ExpiredSignatureError:
        print('токен просрочен')
        raise HTTPException(401)
    except:
        raise HTTPException(401)
    
@app.post('/add')
def add(token=Body()):
    print(token['token'])
    return {'status':'ok', 'redirect_url':f'/addingmenu?token={token['token']}'}

@app.post('/delete')
def delete(token=Body()):
    return {'status':'ok', 'redirect_url':f'/deletemenu?token={token['token']}'}

@app.get('/addingmenu')
def addingmenu(token:str=Query(...)):
    try:
        data=jwt.decode(token,SECRET,algorithms=[ALGORITHM])
        return FileResponse('addmenu.html')
    except ExpiredSignatureError:
        print('токен протух')
        raise HTTPException(401)
    except:
        raise HTTPException(401)
    
@app.post('/dobav')
def dobav(data=Body(), user=Depends(get)):
    try:
        print(user)
        name=data['name']
        print(name,'-name')
        Session=sessionmaker(autoflush=False,bind=engine)
        with Session() as db:
            us=db.query(User).filter(User.name==user).first()
            new=Task(name=name)
            us.tasks.extend([new])
            db.commit()
    except ExpiredSignatureError:
        print('токен протух')
        raise HTTPException(401)
    except Exception as e:
        print(e)

@app.get('/deletemenu')
def deletemenu(token:str=Query(...)):
    try:
        data=jwt.decode(token,SECRET,algorithms=[ALGORITHM])
        return FileResponse('deletemenu.html')
    except ExpiredSignatureError:
        print('токен протух')
        raise HTTPException(401)
    except Exception as e:
        print(e)
        raise HTTPException(401)
    
@app.post('/deleting')
def deleting(data=Body(), user=Depends(get)):
    try:
        print(user)
        name=data['name']
        print(name,'-name')
        Session=sessionmaker(autoflush=False,bind=engine)
        with Session() as db:
            us=db.query(User).filter(User.name==user).first()
            print(us.id)
            task=db.query(Task).filter(Task.name==name).all()
            for i in task:
                print(i.id)
                if i.user_id==us.id:
                    target=i
                    break
            us.tasks.remove(target)
            db.delete(target)
            db.commit()
    except ExpiredSignatureError:
        print('токен протух')
        raise HTTPException(401)
    except Exception as e:
        print(e)

@app.post('/list')
def list(token=Body()):
    return {'status':'ok', 'redirect_url':f'/userlist?token={token['token']}'}

@app.get('/userlist')
def userslist(token:str=Query(...)):
    try:
        text='Ваш список задач:\n'
        data=jwt.decode(token,SECRET,algorithms=[ALGORITHM])
        name=data['sub']
        Session=sessionmaker(autoflush=False,bind=engine)
        with Session() as db:
            user=db.query(User).filter(User.name==name).first()
            for i in user.tasks:
                text+=str(i.name)+'\n'
        if text!='Ваш список задач:\n':
            return Response(content=text, media_type='text/plain')    
        else:
            return Response(content='<h2>У вас нету задач :(<h2>', media_type='text/html')
    except Exception as e:
        print(e)
        raise HTTPException(401)
    
@app.post('/update')
def update(token=Body()):
    return {'status':'ok', 'redirect_url':f'/updatemenu?token={token['token']}'}

@app.get('/updatemenu')
def updatemenu(token:str=Query(...)):
    try:
        data=jwt.decode(token,SECRET,algorithms=[ALGORITHM])
        return FileResponse('updatemenu.html')
    except Exception as e:
        print(e)

@app.post('/updating')
def updating(data=Body(), user=Depends(get)):
    try:
        print(user)
        name=data['name']
        new=data['new']
        print(name,'-name\tnew - ', new)
        Session=sessionmaker(autoflush=False,bind=engine)
        with Session() as db:
            us=db.query(User).filter(User.name==user).first()
            print(us.id)
            task=db.query(Task).filter(Task.name==name).all()
            for i in task:
                print(i.id)
                if i.user_id==us.id:
                    target=i
                    break
            target.name=new
            db.commit()
    except ExpiredSignatureError:
        print('токен протух')
        raise HTTPException(401)
    except Exception as e:
        print(e)