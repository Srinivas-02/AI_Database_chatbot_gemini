import os
from dotenv import load_dotenv
from db_chatbot import getValuefromDB,getSql,getNLPAnswer
from google import genai    
load_dotenv()
client = genai.Client(api_key=os.environ.get('GEMINI_API_KEY'))
global history
history = []
def addtohistory(role,message):
    global history
    history.append(f" role : {role} , message : {message} ")

print(" Welcome, please chat with your database here..")    
try:
    while(True):
        question = input("user : ")
        addtohistory('user', question)
        sql_command = getSql(client,question,history)
        answer = getValuefromDB(sql_command)
        reply = getNLPAnswer(client,question,answer,history)
        print(f"Model : {reply}")
        addtohistory('model',reply)
except KeyboardInterrupt:        
    print(f"\n\n Thank you for using the chatbot")
except Exception as e:
    print(f" There is an issue : {e}")



