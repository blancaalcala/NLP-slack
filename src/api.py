from bottle import route, run, get, post, request
from mongo import CollConection
import os
import requests
import json

@get('/')
def refresh():
    collChat.deleteColl()

@get('/login') 
def login_form():
    return '''<form method="POST" action="/login">
               Insert your slack api token <input name="token"     type="text" />
                <input type="submit" />
              </form>'''

@post('/login') 
def login_submit():
    token = request.forms.get('token')
    auth = requests.get(f'https://slack.com/api/auth.test?token={token}').text
    status = collChat.continueCode(json.loads(auth)['ok'])
    if status['status']:
        collChat.insertInfo(token)
    return status

@get("/index")
def index():
    return '''
        Welcome to the slack NLP API!:https://github.com/blancaalcala/NLP-slack,
        \nPossible actions:
        \nfirst log in with your slack api token
        \nyou can obtain it here https://api.slack.com/custom-integrations/legacy-tokens,
        \nget user recommendation: /user/user_id/recommend,
        \nget messages from specific chat: /chat/chat_id/list,
        \nget chat sentiment: /chat/chat_id/sentiment,
        \nget user sentiment: /user/user_id/sentiment'''

@get("/user/<user_id>/recommend")
def getuserrecommendation(user_id):
    users_id = collChat.recommendUser(user_id)
    user = collChat.getUsername(user_id)
    users_name = []
    for i in users_id:
        users_name.append(collChat.getUsername(i))
    return f'Recommended users for {user}: {users_name[0]},{users_name[1]},{users_name[2]}'
    
@get("/chat/<chat_id>/list")
def getchat(chat_id):   
    return {collChat.getChatname(chat_id):collChat.getChatMessages(chat_id)}

@get("/user/<user_id>/list")
def getuser(user_id):   
    return {collChat.getUsername(user_id):collChat.getUserMessages(user_id)}

@get("/chat/<chat_id>/sentiment")
def getchatsentiment(chat_id):
    scores = collChat.getChatSentiment(chat_id)
    return f"Chat {collChat.getChatname(chat_id)}: negative score: {scores['neg']}, neutral score: {scores['neu']}, positive score: {scores['pos']}"

@get("/user/<user_id>/sentiment")
def getusersentiment(user_id):
        scores = collChat.getUserSentiment(user_id)
        return f"User {collChat.getUsername(user_id)}: negative score: {scores['neg']}, neutral score: {scores['neu']}, positive score: {scores['pos']}"

collChat=CollConection('API','slack')


port = int(os.getenv("PORT", 8080))
print(f"Running server {port}....")
run(host="0.0.0.0", port=port, debug=True)