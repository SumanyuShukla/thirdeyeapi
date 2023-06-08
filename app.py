from flask import Flask, request, session, make_response, jsonify, send_file
from flask_cors import CORS
import random
import os
import sys
import time
import json
from docx import Document
from sqlalchemy.orm import sessionmaker
from langchain.document_loaders import DirectoryLoader,TextLoader
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.llms import AzureOpenAI
from user import *
engine = create_engine('sqlite:///third_eye.db', echo=True)

sys.path.append("utils")
from common_utils import *

app=Flask(__name__)
UPLOAD_FOLDER=os.path.join(os.path.abspath(os.getcwd()),"uploaded_docs")
RESULT_FOLDER=os.path.join(os.path.abspath(os.getcwd()),"documents")

app.config['RESULT_FOLDER']=RESULT_FOLDER
app.config['UPLOAD_FOLDER']=UPLOAD_FOLDER

CORS(app)

openai.api_type = "azure"
openai.api_key = "32c8f6789c1649f588d42312a2d827d0"
openai.api_base = "https://bigaidea.openai.azure.com/"
openai.api_version = "2023-03-15-preview"

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
                "name":result.name,
                "id":result.id
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
    data=request.args.get("data")
    data=json.loads(data)
    document = Document()
    for attribute,value in data.items():
        document.add_paragraph(value)
    # doc_name=str(get_id(token))+"_"+str(round(time.time() * 1000))+".docx"
    doc_name=str(round(time.time() * 1000))+".docx"
    document.save(os.path.join(app.config['RESULT_FOLDER'],doc_name))
    return send_file(os.path.join(app.config['RESULT_FOLDER'],doc_name),download_name=doc_name,as_attachment=True)
    # else:
    #     return "Invalid User!"

@app.route("/chat", methods=['POST'])
def chat():
    prompt=request.form['prompt']
    template=request.form['template']
    # print(prompt)
    # print(template)
    result=connectGpt(prompt,template)
    if result!='0':
        return result
    else:
        return "Failed"

@app.route("/uploadDocs", methods=['POST'])
def upload_docs():
    os.environ["OPENAI_API_KEY"] = "32c8f6789c1649f588d42312a2d827d0"
    files=request.files.getlist('files')
    userid=request.form['id']
    try:
        folder=os.path.join(app.config['UPLOAD_FOLDER'],userid)
        if not os.path.exists(folder):
            os.makedirs(folder)
        # print(files)
        for f in files:
            f.save(os.path.join(folder,f.filename))
        loader = DirectoryLoader(folder, glob="*.txt",loader_cls=TextLoader)
        docs = loader.load()
        textSplitter=RecursiveCharacterTextSplitter(chunk_size=1000,chunk_overlap=200)
        texts=textSplitter.split_documents(docs)
        persist_directory=os.path.join('db',userid)
        if not os.path.exists(persist_directory):
            os.makedirs(persist_directory)
        embeddings = OpenAIEmbeddings(model="text-embedding-ada-002",chunk_size=1)
        vectordb = Chroma.from_documents(documents=texts, embedding=embeddings, persist_directory=persist_directory)
        vectordb.persist()
        vectordb=None
        return "1"
    except Exception as e:
        print(e)
        return "0"

@app.route("/chatDoc", methods=['POST'])
def chatDoc():
    prompt=request.form['prompt']
    userid=request.form['id']
    persist_directory=os.path.join('db',userid)
    if not os.path.exists(persist_directory):
        return "0"
    embeddings = OpenAIEmbeddings(model="text-embedding-ada-002",chunk_size=1)
    vectordb=Chroma(persist_directory=persist_directory,embedding_function=embeddings)
    retriever=vectordb.as_retriever()
    llm = AzureOpenAI(
        deployment_name="bigaidea"
    )
    qa=RetrievalQA.from_chain_type(llm=llm,chain_type="stuff",retriever=retriever,return_source_documents=False)
    # query="create a business proposal for the company"
    response=qa(prompt)
    return response
    # if result!='0':
    #     return result
    # else:
    #     return "Failed"

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
