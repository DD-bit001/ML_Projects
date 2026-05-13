import re
import pandas as pd
from collections import Counter
from urlextract import URLExtract
import emoji
extract = URLExtract()
def fetch_stats(selected_user,df):
    if selected_user =='Overall':
        num_messages = df.shape[0]
        num_words = len(df['message'].str.split().sum())
        num_media_messages = df[df['message'] == '<Media omitted>\n'].shape[0]
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
    num_messages = df.shape[0]
    words = []
    for message in df['message']:
        words.extend(message.split())
    num_words = len(words)
    num_media_messages = df[df['message'] == '<Media omitted>\n'].shape[0]
    return num_messages,num_words,num_media_messages
def fetch_links(selected_user,df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
    links = []
    for message in df['message']:
        links.extend(extract.find_urls(message))
    return links
def fetch_most_busy_users(df):
    x = df['user'].value_counts().head()

    new_df = (df['user'].value_counts(normalize=True) * 100) \
                .round(2) \
                .reset_index()

    new_df.columns = ['name', 'percent']

    return x, new_df
def create_wordcloud(selected_user,df):
    from wordcloud import WordCloud
    f = open('stop_hinglish.txt', 'r')
    stop_words = f.read()

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    temp = df[df['user'] != 'group_notification']
    temp = temp[temp['message'] != '<Media omitted>\n']

    def remove_stop_words(message):
        y = []
        for word in message.lower().split():
            if word not in stop_words:
                y.append(word)
        return " ".join(y)

    wc = WordCloud(width=500,height=500,min_font_size=10,background_color='white')
    temp['message'] = temp['message'].apply(remove_stop_words)
    df_wc = wc.generate(temp['message'].str.cat(sep=" "))
    return df_wc

def most_common_words(selected_user,df):
    f = open('stop_hinglish.txt', 'r')
    stop_words = f.read()
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
    temp = df[df['user'] != 'group_notification']
    temp = temp[~temp['message'].str.contains('<Media omitted>', na=False)]
    words=[]
    for message in temp['message']:
        for word in message.lower().split():
            if word not in stop_words:
                words.append(word)
    most_common_df=pd.DataFrame(Counter(words).most_common(20))
    most_common_df.columns=['word','count']
    return most_common_df

def emoji_helper(selected_user,df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
    emojis = []
    for message in df['message']:
        emojis.extend([c for c in message if c in emoji.EMOJI_DATA])
    emoji_df = pd.DataFrame(Counter(emojis).most_common(len(Counter(emojis))))
    emoji_df.columns = ['emoji', 'count']
    return emoji_df
def monthly_timeline(selected_user,df):
    
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
    timeline=df.groupby(['year','month_num','month']).count()['message'].reset_index()
    time=[]
    for i in range(timeline.shape[0]):
        time.append(timeline['month'][i]+'-'+str(timeline['year'][i]))
    timeline['time']=time
    return timeline
def daily_timeline(selected_user,df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
    df['only_date']=df['date'].dt.date    
    daily_timeline=df.groupby('only_date').count()['message'].reset_index()
    return daily_timeline
def week_activity_map(selected_user,df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
    return df['day_name'].value_counts()
def month_activity_map(selected_user,df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
    return df['month'].value_counts()

def activity_heatmap(selected_user,df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
    user_heatmap=df.pivot_table(index='day_name',columns='period',values='message',aggfunc='count').fillna(0)
    return user_heatmap