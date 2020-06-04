# -*- coding: utf-8 -*-
import json


filename = 'result.json'
file = open(filename, encoding="utf8")
dict_data = json.load(file)

chat_name='YOUR_GROUP_CHAT_NAME'

chat_data_list=dict_data['chats']['list']
for chat in chat_data_list:
    if chat['name']==chat_name:
        chat_data=chat
        break

#======================#======================#======================
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from nltk.corpus import stopwords
from nltk import download


chat_data_fil=[] 
for m in chat_data['messages']:
    if (m['type'] == 'message' and m['text']!=''):
        chat_data_fil.append(m)


df_chat = pd.DataFrame.from_dict(chat_data_fil)

# Only want user and message, although more info like date could be kept

col_sel=['from','text']
df_chat=df_chat[col_sel]
usernames=[]
messages=[]
for user, mes in df_chat.groupby(['from']):
    usernames.append(user)
    messages.append(mes['text'])


print("Users: ", usernames)

# Stopwords are words commonly used in a language that do not provide much information
# For english, sklearn has a defined list, so stopwords='english' may be used
# For other languages, the nltk.stopwords package can be used. 
download('stopwords')
stopwords = stopwords.words('russian')
add_stopwords=['text','type','link','https','www','html','com','news','ixbt','http']
for w in add_stopwords: stopwords.append(w)

def get_top_n_words(user, stopwords, n=None):
    user_index=usernames.index(user)
    corpus=[str (item) for item in messages[user_index]]
    vec = CountVectorizer(stop_words=stopwords).fit(corpus)
    bag_of_words = vec.transform(corpus)
    sum_words = bag_of_words.sum(axis=0) 
    words_freq = [(word, sum_words[0, idx]) for word, idx in     vec.vocabulary_.items()]
    words_freq =sorted(words_freq, key = lambda x: x[1], reverse=True)
    return words_freq[:n]


#======================#======================#======================




message_count_all=0
for m in chat_data['messages']:
    if (m['type'] != 'service'):
        message_count_all +=1


person = set()
for m in chat_data['messages']:
    if (m['type'] == 'message' and m['text']!=''):
        person.add(m['from'])


stats=[]
messages_m=0
voice_msg=0
stickers=0
photos=0
video=0
links=0


for p in person:
    messages_m=0
    voice_msg=0
    stickers=0
    photos=0
    video=0
    links=0
    for m in chat_data['messages']:
        if m['type'] != 'service':
            if ( m['type'] == 'message' and m['from'] == p):
                messages_m+=1
            if ( m['type'] == 'message' and m['from'] == p and 'media_type' in m.keys() ):
                if m['media_type'] == 'voice_message':
                    voice_msg+=1
            if ( m['type'] == 'message' and m['from'] == p and 'media_type' in m.keys() ):
                if m['media_type'] == 'sticker':
                    stickers+=1
            if ( m['type'] == 'message' and m['from'] == p and 'photo' in m.keys()):
                photos+=1
            if ( m['type'] == 'message' and m['from'] == p and 'mime_type' in m.keys()):
                if 'video/' in m['mime_type']  :
                    video+=1
            if ( m['type'] == 'message' and m['text']!='' and m['from'] == p):
                for item in m['text']:
                    if type(item) is dict:
                        if item['type'] == 'link':
                            links+=1
    stats.append([p, messages_m, voice_msg, stickers, photos ,video, links ])


print(' Всего сообщений в чате "'+chat_name+'": '+ str(message_count_all))

stats.sort(key=lambda x: int(x[1]), reverse = True)
stats = [list for list in stats if list[0] is not None]
for i in stats:
    print( i[0]+':  '+str(i[1]) +' текстовые, '+str(i[2]) +' звуковые, '+str(i[3]) +' стикеры, '+str(i[4]) +' видео, '+str(i[5]) +' ссылки, ')
    print ('топ слов: ', str(i[0]) , ' ' , get_top_n_words(str(i[0]), stopwords, n=10)) 
    print('')

