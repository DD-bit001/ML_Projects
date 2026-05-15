
import re
import pandas as pd


def preprocess(data):

   pattern = r'\[?\d{1,2}[/-]\d{1,2}[/-]\d{2,4},\s\d{1,2}:\d{2}(?::\d{2})?\s?(?:am|pm|AM|PM)?\]?\s?[-–]\s'
   message=re.split(pattern,data)[1:]
   dates=re.findall(pattern , data)
   df=pd.DataFrame({'user_message':message,'message_date':dates})
   #converting the message date type
   
   def parse_date(date_str):
    date_str = re.sub(r'[\[\]]', '', date_str).strip().rstrip('-').strip()
    for fmt in (
        '%m/%d/%y, %H:%M',
        '%d/%m/%y, %H:%M',
        '%m/%d/%Y, %H:%M',
        '%d/%m/%Y, %H:%M',
        '%m/%d/%y, %I:%M %p',
        '%d/%m/%y, %I:%M %p',
    ):
        try:
            return pd.to_datetime(date_str, format=fmt)
        except ValueError:
            continue
    return pd.NaT  # fallback if nothing matches

   df['message_date'] = df['message_date'].apply(parse_date)
   df.rename(columns={'message_date':'date'}, inplace =True)
   users=[]
   messages=[]
   for message in df['user_message']:
     entry=re.split('([\w\W]+?):\s',message)
     if entry[1:]:
       users.append(entry[1])
       messages.append(entry[2])
     else:
       users.append('group_notification')
       messages.append(entry[0])
   df['user']=  users
   df['message']=messages    
   df.drop(columns=['user_message'],inplace=True)
   df['year']=df['date'].dt.year
   df['month']=df['date'].dt.month_name()
   df['day']=df['date'].dt.day
   df['hour']=df['date'].dt.hour
   df['minutes']=df['date'].dt.minute
   df['month_num']=df['date'].dt.month 
   df['day_name']=df['date'].dt.day_name()
   period=[]
   for hour in df[['day_name','hour']]['hour']:
    
     if hour==23:
       
       period.append(str(hour)+'-'+str('00'))
     elif hour==0:
       period.append(str('00')+'-'+str(hour+1))
     else:
       period.append(str(hour)+'-'+str(hour+1))
   df['period']=period
   return df