from pymongo import MongoClient
from bson.objectid import ObjectId
import nltk
nltk.download('vader_lexicon')
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity as distance
import os
from dotenv import load_dotenv
import requests
load_dotenv()


sid = SentimentIntensityAnalyzer()


class CollConection:

    def __init__(self,dbName,collection):
        self.client = MongoClient(os.getenv('mongo'))
        self.db = self.client[dbName]
        self.collection=self.db[collection]

    def recommendUser(self,user_id):
        x = list(self.collection.find({},{"messages.text":1,'messages.user':1,'_id':0}))
        info = {}
        for i in x:
            for m in i['messages']:
                pass
                info[m['user']]=m['text']
                info[m['user']]=m['text']
        count_vectorizer = CountVectorizer()
        sparse_matrix = count_vectorizer.fit_transform(info.values())
        info_matrix = sparse_matrix.todense()
        df = pd.DataFrame(info_matrix, columns=count_vectorizer.get_feature_names(), index=info.keys())
        similarity_matrix = distance(df, df)
        sim_df = pd.DataFrame(similarity_matrix, columns=info.keys(), index=info.keys())
        recom = sim_df['UNCQA7WS0'].sort_values(ascending=False)[1:]
        users = recom.keys()
        return users[:3]
    
    def getUsername(self,user_id):
        users = list(self.collection.find({},{'users':1,'_id':0}))
        for u in users:
            for i in u['users']:
                if i['user_id'] == user_id:
                    return i['user_name']

    def getChatname(self,chat_id):
        chat = list(self.collection.find({'chat_id':chat_id},{'chat_name':1,'_id':0}))[0]['chat_name']
        return chat

    def getChatMessages(self,chat_id):
        x = list(self.collection.find({'chat_id':chat_id},{'messages':1,'_id':0}))[0]['messages']
        text_list = []
        for i in x:
            text_list.append(i['text'])
        return text_list

    def getUserMessages(self,user_id):
        x = list(self.collection.find({'messages.user':user_id},{'messages':1,'_id':0}))[0]['messages']
        user_messages = []
        for i in x:
            if i['user']==user_id:
                user_messages.append(i['text'])
        return user_messages

    def getChatSentiment(self,chat_id):
        mes = self.getChatMessages(chat_id)
        message_string = " ".join(mes)
        return sid.polarity_scores(message_string)

    def getUserSentiment(self,user_id):
        mes = self.getUserMessages(user_id)
        message_string = " ".join(mes)
        return sid.polarity_scores(message_string)

    def insertInfo(self):
        url = 'https://slack.com/api/'
        chat_names = []
        chat_id = []
        x = requests.get(f'{url}groups.list?token={os.getenv("slack")}').json()   
        for i in x['groups'][:-1]:
            chat_names.append(i['name'])
            chat_id.append(i['id'])

        for i in range(len(chat_id)):
            x = requests.get(f'{url}groups.info?token={os.getenv("slack")}&channel={chat_id[i]}').json()   
            users_list = x['group']['members']
            users = []
            for user in users_list:
                u = requests.get(f'{url}users.info?token={os.getenv("slack")}&user={user}').json()   
                users.append({'user_id':user,
                            'user_name':u['user']['real_name']})
                
            x = requests.get(f'{url}groups.history?token={os.getenv("slack")}&channel={chat_id[i]}&count=50').json()
            messages = []
            for m in x['messages']:
                messages.append({'text':m['text'],
                                'user':m['user']})
                
            self.collection.insert_one({'chat_name':chat_names[i],
                        'chat_id':chat_id[i],
                        'users':users,
                        'messages':messages})