from flask import Flask, request, session, make_response, jsonify, send_file
from flask_cors import CORS
import random
import os
import sys
import time
import json
from docx import Document
from sqlalchemy.orm import sessionmaker
from user import *
engine = create_engine('sqlite:///third_eye.db', echo=True)

sys.path.append("utils")
from common_utils import *

app=Flask(__name__)
RESULT_FOLDER=os.path.join(os.path.abspath(os.getcwd()),"documents")

app.config['RESULT_FOLDER']=RESULT_FOLDER

CORS(app)

@app.route("/login",methods=['POST'])
def login():
    username=request.form['username']
    password=request.form['password']


    try:
        Session = sessionmaker(bind=engine)
        session = Session()

        query = session.query(User).filter(User.username.in_([username]), User.password.in_([password]) )
        result = query.first()

        if result:
            res={
                "status":"success",
                "name":result.name
            }
            response=make_response(jsonify(data=res))
            response.headers['X-Token']=create_jwt(result.id)
            return response
        else:
            res={
                "status":"failed"
            }
            response=make_response(jsonify(data=res))
            return response
    except Exception as e:
        print(e)
    

@app.route("/register",methods=['POST'])
def register():
    name=request.form['name']
    username=request.form['email']
    password=request.form['password']

    try:
        Session = sessionmaker(bind=engine)
        session = Session()

        query = session.query(User).filter(User.username.in_([username]) )
        result = query.first()

        if result:
            return "User Already Exists!"
        else:
            user = User(name,username,password)
            session.add(user)
            session.commit()
            return "User Created!"
    except Exception as e:
        print(e)


@app.route("/getDoc", methods=['GET'])
def get_doc():
    data=request.get_json()
    token=request.headers['Authorization']
    if verify_token(token) is True:
        document = Document()
        document.add_paragraph(data['data'])
        doc_name=str(get_id(token))+"_"+str(round(time.time() * 1000))+".docx"
        document.save(os.path.join(app.config['RESULT_FOLDER'],doc_name))
        return send_file(os.path.join(app.config['RESULT_FOLDER'],doc_name),download_name=doc_name,as_attachment=True)
    else:
        return "Invalid User!"

@app.route("/chat", methods=['GET'])
def chat():
    connectGpt("test")
    return "1"

# @app.route("/showImage")
# def showImage():
#     filename=request.args['file']
#     return send_file(os.path.join(app.config['RESULT_FOLDER'],filename),download_name='result.jpg')

# @app.route("/download")
# def download():
#     filename=request.args['file']
#     return send_file(os.path.join(app.config['RESULT_FOLDER'],filename),download_name='result.jpg',as_attachment=True)


if __name__=="__main__":
    app.run()
