from bottle import route, run, get, post, request
from mongo import CollConection
import os


@get("/")
def index():
    return '''Welcome to the slack NLP API!'''

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
    return collChat.getMessages(chat_id)

@get("/chat/<chat_id>/sentiment")
def getchatsentiment(chat_id):
    scores = collChat.getChatSentiment(chat_id)
    return f"Chat {collChat.getChatname(chat_id)}: negative score: {scores['neg']}, neutral score: {scores['neu']}, positive score: {scores['pos']}"

@get("/user/<user_id>/sentiment")
def getusersentiment(user_id):
    scores = collChat.getUserSentiment(user_id)
    return f"User {collChat.getUsername(user_id)}: negative score: {scores['neg']}, neutral score: {scores['neu']}, positive score: {scores['pos']}"

@get("/refresh_info")
def insertinfo():
    collChat.insertInfo()
    return 'Info has ben added!'

collChat=CollConection('API','slack')

port = int(os.getenv("PORT", 8080))
print(f"Running server {port}....")

run(host="0.0.0.0", port=port, debug=True)