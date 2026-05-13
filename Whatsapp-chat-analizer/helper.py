import re
import os
import pandas as pd
from collections import Counter
from urlextract import URLExtract
import emoji
from textblob import TextBlob

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
    file_path = os.path.join(os.path.dirname(__file__), 'stop_hinglish.txt')
    f = open(file_path, 'r', encoding='utf-8')
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
    file_path = os.path.join(os.path.dirname(__file__), 'stop_hinglish.txt')
    f = open(file_path, 'r', encoding='utf-8')
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
    emoji_counter = Counter(emojis)
    emoji_df = pd.DataFrame(emoji_counter.most_common(), columns=['emoji', 'count'])
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

def sentiment_analysis(selected_user,df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
    df['sentiment'] = df['message'].apply(lambda x: TextBlob(x).sentiment.polarity)
    return df[['message', 'sentiment']]



def communication_grade(selected_user, df):

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user].copy()

    total_messages = len(df)

    if total_messages == 0:
        return "N/A", 0

    total_sentiment = 0
    total_words = 0
    questions = 0

    for msg in df['message']:

        msg = str(msg)

        # sentiment
        polarity = TextBlob(msg).sentiment.polarity
        total_sentiment += polarity

        # words
        words = re.findall(r'\w+', msg)
        total_words += len(words)

        # questions
        if '?' in msg:
            questions += 1

    avg_sentiment = total_sentiment / total_messages
    avg_words = total_words / total_messages
    question_ratio = questions / total_messages
    score = 0

    score += (avg_sentiment + 1) * 25

    # message length score
    score += min(avg_words * 2, 25)

    # engagement score
    score += min(question_ratio * 100, 25)

    # activity score
    score += min(total_messages / 50, 25)

    final_score = round(score, 2)

    # grading
    if final_score >= 85:
        grade = "A+"
    elif final_score >= 70:
        grade = "A"
    elif final_score >= 55:
        grade = "B"
    elif final_score >= 40:
        grade = "C"
    else:
        grade = "D"

    return grade, final_score