import streamlit as st
import preprocessor
import helper
import seaborn as sns
import matplotlib.pyplot as plt
st.sidebar.title("Whatsapp Chat Analyzer")

uploaded_file = st.sidebar.file_uploader("Choose a file")
if uploaded_file is not None:
    bytes_data = uploaded_file.getvalue()
    data = bytes_data.decode("utf-8")
  
    df = preprocessor.preprocess(data)
    


    #fetch unique users
    user_list=df['user'].unique().tolist()
    user_list.remove('group_notification')
    user_list.sort()
    user_list.insert(0,"Overall")
    selected_user = st.sidebar.selectbox("Show analysis wrt",user_list)
    if st.sidebar.button("Show Analysis"):
        st.title("Top Statistics")
       

    num_messages, num_words, num_media_messages = helper.fetch_stats(selected_user, df)
    links = helper.fetch_links(selected_user, df)
    st.title("Top Statistics")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Messages", num_messages)

    with col2:
        st.metric("Total Words", num_words)

    with col3:
        st.metric("Media Shared", num_media_messages)

    with col4:
        st.metric("Links Shared", len(links))

    with st.expander("See Links"):
        for link in links:
            st.markdown(f"[{link}]({link})")
            
        # finding busiest users in group4
    st.title("Monthly Timeline")
    st.subheader("The timeline shows the number of messages sent each month. It helps to identify trends and patterns in user activity over time.") 
    col1,col2=st.columns(2)
    timeline=helper.monthly_timeline(selected_user,df) 

    with col1:
        st.header("Line Chart")
        fig,ax=plt.subplots()
        ax.plot(timeline['time'],timeline['message'],color='green')
        plt.xticks(rotation='vertical')
        st.pyplot(fig)
    with col2:
        st.header("Bar Chart")
        fig,ax1=plt.subplots()
        ax1.bar(timeline['time'],timeline['message'],color='orange')
        plt.xticks(rotation='vertical')
        st.pyplot(fig)
    
    st.title("Daily Timeline")
    daly_timeline=helper.daily_timeline(selected_user,df)     
    fig,ax=plt.subplots()
    ax.plot(daly_timeline['only_date'],daly_timeline['message'],color ='red')
    plt.xticks(rotation='vertical')
    st.pyplot(fig) 
    
    #activity map
    st.title("Activity Map")
    col1,col2=st.columns(2)
    with col1:
        st.header("Most Busy Day")  
        busy_day=helper.week_activity_map(selected_user,df)
        fig,ax=plt.subplots()
        colorr=['red','green','blue','orange','yellow','purple','cyan']
        ax.bar(busy_day.index,busy_day.values,color=colorr)
        plt.xticks(rotation='vertical')
        st.pyplot(fig) 
    with col2:
        st.header("Most Busy Month")
        busy_month=helper.month_activity_map(selected_user,df)
        fig,ax=plt.subplots()
        ax.bar(busy_month.index,busy_month.values,color='orange')
        plt.xticks(rotation='vertical')
        st.pyplot(fig)  
        
    #WEEKLY ACTIVITY HEATMAP    
           
    st.title("Weekly Activity Heatmap")
    user_heatmap=helper.activity_heatmap(selected_user,df)
    fig,ax=plt.subplots()
    sns.heatmap(user_heatmap,annot=True,fmt='g',ax=ax,cmap='YlGnBu')
    st.pyplot(fig)
    if selected_user == 'Overall':
        col1,col2=st.columns(2)
        st.title("Most Busy Users")
        x,new_df= helper.fetch_most_busy_users(df)
        fig,ax=plt.subplots()
        col1,col2=st.columns(2)
        with col1:
            color=['red','green','blue','orange','yellow']
            ax.bar(x.index,x.values,color=color)
            plt.xticks(rotation='vertical')
            st.pyplot(fig)
        with col2:
            st.dataframe(new_df)
    st.title("WordCloud")        
    df_wc=helper.create_wordcloud(selected_user,df)
    fig,ax=plt.subplots()
    ax.imshow(df_wc)
    st.pyplot(fig)   
    most_common_df=helper.most_common_words(selected_user,df)
    st.title("Most Common Words")
    fig,ax=plt.subplots()

    
    ax.barh(most_common_df['word'],most_common_df['count'])
    st.pyplot(fig)

    st.dataframe(most_common_df)
    emoji_df=helper.emoji_helper(selected_user,df)
    st.title("Emojis Analysis")
    col1,col2=st.columns(2)
    with col1:
        st.dataframe(emoji_df.head())

    with col2:
        st.subheader("Top 5 Emojis")
        fig,ax=plt.subplots()
        ax.pie(emoji_df['count'].head(),labels=emoji_df['emoji'].head(),autopct="%0.2f")
        st.pyplot(fig)
         


