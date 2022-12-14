# Twitter Dashboard Group Challenge

# Import Packages
import streamlit as st
import pandas as pd
import json
from urllib.request import urlopen
from copy import deepcopy

from plotly.subplots import make_subplots
import plotly.express as px
import plotly.graph_objects as go
import datetime as dt
import plotly.io as pio

from plotly.subplots import make_subplots

import seaborn as sns
import matplotlib.pyplot as plt
from nltk.corpus import stopwords
from wordcloud import WordCloud, STOPWORDS
#from nltk.tokenize import word_tokenize
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
nltk.download('punkt')
nltk.download('stopwords')
import re
import pylab

#import matplotlib.plotly as plt

@st.cache
def load_data(path):
    df = pd.read_csv(path)
    return df

# Load clean data from data folder
df1 = pd.read_csv('./data/tweets_clean.csv')
tweets_clean = deepcopy(df1)

# Create a df aggregating by category for total and mean actions
tweets_agg = tweets_clean.groupby('category').agg({'name': 'nunique',
                                                   'id': 'count',
                                                   'replyCount': ['sum', 'mean'],
                                                   'retweetCount': ['sum', 'mean'],
                                                   'likeCount': ['sum', 'mean'],
                                                   'quoteCount': ['sum', 'mean']
                                                  })

tweets_agg.columns = tweets_agg.columns.droplevel()
tweets_agg.columns = ['Users_Analysed', 'Total_Tweets',
                      'Total_Replies', 'Mean_Replies',
                      'Total_Retweets', 'Mean_Retweets',
                      'Total_Likes', 'Mean_Likes',
                      'Total_Quotes', 'Mean_Quotes']

tweets_agg.reset_index(inplace=True)

# Create a df aggreagting by sourceLabel for pie chart
source_dict = {'Twitter for iPhone': 'Iphone',
               'Twitter for iPad': 'Other',
               'Twitter for Android': 'Android',
               'Twitter for Mac': 'Other',
               'Twitter Web App': 'Web App',
               'Twitter Media Studio': 'Media Studio',
               'Twitter Media Studio - LiveCut': 'Media Studio',
               'The White House': 'The White House',
               'TweetDeck': 'Other',
               'Periscope': 'Periscope',
               'Arrow.': 'Other'}

tweets_source_pie = tweets_clean.replace(source_dict).groupby('sourceLabel').agg({'id': 'count'}).reset_index()
tweets_source_pie.rename({'id': 'Tweets'}, axis=1, inplace=True)

# Create a df aggregating by sourceLabel AND category
source_dict = {'Twitter for iPhone': 'Iphone',
               'Twitter for iPad': 'iPad',
               'Twitter for Android': 'Android',
               'Twitter for Mac': 'Mac',
               'Twitter Web App': 'Web App',
               'Twitter Media Studio': 'Media Studio',
               'Twitter Media Studio - LiveCut': 'Media Studio',
               'The White House': 'The White House',
               'TweetDeck': 'TweetDeck',
               'Periscope': 'Periscope',
               'Arrow.': 'Arrow'}

tweets_cns = tweets_clean.replace(source_dict).groupby(['category', 'sourceLabel']).agg({'id': 'count' }).reset_index()
tweets_cns.rename({'sourceLabel': 'Device', 'id': 'Tweets'}, axis=1, inplace=True)
cns_df = tweets_cns.fillna(0)

# Pie Chart - Device Distribution
cat_plat = go.Figure(go.Pie(labels=tweets_source_pie['sourceLabel'], values=tweets_source_pie['Tweets']))

cat_plat.update_traces(hoverinfo='label+percent+value',
                              hovertemplate='<extra></extra>'+
                              '%{label}<br>'+
                              '<br>Tweets: %{value:.0f}'+
                              '<br>%Total: %{percent}',
                              textinfo='text+value', textfont_size=11,
                              marker=dict(colors=['gold', 'mediumturquoise',  'lightgreen'],
                                          line=dict(color='#000000', width=1))
                             )

cat_plat.update_layout(title="Total Tweets by Platform",
                       width = 700, height = 500,
                       title_font_size = 22,
                       title_x = 0.5,
                       title_xanchor = 'center',
                       font=dict(family="Comic, monospace",
                                 size=14,
                                 color="RoyalBlue")
                      )

# Pie Chart - Total Tweets
cat_tweets = go.Figure((go.Pie(labels=tweets_agg['category'], values=tweets_agg['Total_Tweets'])))

cat_tweets.update_traces(hoverinfo='label+percent+value',
                              hovertemplate='<extra></extra>'+
                              '%{label}<br>'+
                              '<br>Tweets: %{value:.0f}'+
                              '<br>%Total: %{percent}',
                              textinfo='text+value', textfont_size=11,
                              marker=dict(colors=['gold', 'mediumturquoise',  'lightgreen'],
                                          line=dict(color='#000000', width=1))
                             )

cat_tweets.update_layout(title="Total Tweets by Category",
                         width = 700, height = 500,
                         title_font_size = 22,
                         title_x = 0.5,
                         title_xanchor = 'center',
                         #legend_title="Category",
                         font=dict(family="Comic, monospace",
                                   size=14,
                                   color="RoyalBlue")
                        )

# Paste here data frames or plots

# Set Streamlit title and header
st.set_page_config(page_title='Twitter Analysis 2022',
                   page_icon='random',
                   layout='wide') # 'wide' or 'centered'

st.title('Analysis of tweeting behaviour and engagement from high profile users in 2022')

tab1, tab2, tab3 = st.tabs(['Category Analysis', 'User Analysis', 'Time Series'])

with tab1:
   st.header("A cat")
   st.image("https://static.streamlit.io/examples/cat.jpg", width=200)
   st.plotly_chart(cat_plat)
   st.plotly_chart(cat_tweets)

with tab2:
   st.header("A dog")
   st.image("https://static.streamlit.io/examples/dog.jpg", width=200)

   celebs = list(df1["name"].unique())
   celeb = st.selectbox("Select the twitter user", celebs)
                   # ('Bill Gates', 'Elon Musk', 'Harry Potter'))
   stop_words = set(stopwords.words('english'))
   stop_words = (list(stop_words)) + [" ", "based", "regarding", "good", "right", "even", "", "thank", "Thank", "https"]

   wordcloud_dic = {}

   # Setting stop words

   for i in range(len(celebs)):
       # selecting the celbrity

       df = df1[df1['name'] == celebs[i]]
       # saving the Tweet-content in a string variable
       x = str(df["content"])
       token = word_tokenize(x)

       # using regex to only select alphanumeric
       l = []
       for j in range(len(token)):
           l.append(re.sub(r'\W+', '', token[j]))

       # getting rid of stop words
       filtered = []
       for w in l:
           if w.lower() not in stop_words:
               filtered.append(w)

       # creating dic to count number of words
       word_dic = {}
       for m in filtered:
           if m in word_dic:
               word_dic[m] += 1
           else:
               word_dic[m] = 1

       s = {k: v for k, v in sorted(word_dic.items(), key=lambda item: item[1], reverse=True)}

       # Wordcloud
       comment_words = ''
       stop_words2 = list(STOPWORDS)

       # putting list back into a string
       token_2 = (" ".join(s))

       wordcloud = WordCloud(width=800, height=800,
                             background_color='white',
                             stopwords=stop_words2,
                             max_words=100,
                             min_word_length=3,
                             min_font_size=10).generate(token_2)

       wordcloud_dic[celebs[i]] = wordcloud

   # index=celebs.index(celeb)

   fig2 = plt.figure(figsize=(8, 8), facecolor=None)
   plt.imshow(wordcloud_dic[celeb])
   plt.axis("off")
   plt.tight_layout(pad=0)
   plt.title(celeb + ' Tweetcloud')

   st.pyplot(fig2)

   '''if celeb == 'Bill Gates':
       st.write(celeb)
   else:
       st.write('Elon Musk or Harry Potter')'''

with tab3:
   #selecting the celebrity
   celebs_tab3 = list(df1["name"].unique())+['-']
   celeb_tab3 = st.selectbox("Select the twitter user", celebs_tab3)
   st.write(celeb_tab3)
   
   #creating the plots for a chosen celebrity
   
   df_1=df1.loc[df1['name']==celeb_tab3]
   df_1=df_1[['date','replyCount', 'retweetCount', 'likeCount','quoteCount']]
   df_1['ratio_like_to_reply']=df_1['likeCount']/df_1['replyCount']
   df_1['ratio_like_to_retweet']=df_1['likeCount']/df_1['retweetCount']
   df_1['date'] = pd.to_datetime(df_1['date'])
      
   #fig_tab3=go.Figure()
   fig_tab3 = make_subplots(rows=3, cols=2,specs=[[{"secondary_y": True}, {"secondary_y": True}],
                                       [{"secondary_y": True},{"secondary_y": True}],
                                       [{"secondary_y": True}, {"secondary_y": True}]],
                   subplot_titles=("Number of likes during the year", "Number of replies during the year",                                    "Number of quotes during the year", "Number of retweets during the year",
                                 "likes/retweets during the year",
                                  "likes/replies during the year"))
  
   
   # Top left
   fig_tab3.add_trace(
       go.Scatter(x=df_1['date'],  y=df_1["likeCount"]),
       row=1, col=1, secondary_y=False)

   # Top right
   fig_tab3.add_trace(
       go.Scatter(x=df_1['date'],  y=df_1["replyCount"]),
       row=1, col=2, secondary_y=False)
   # Middle left 
   fig_tab3.add_trace(
       go.Scatter(x=df_1['date'],  y=df_1["quoteCount"]),
       row=2, col=1, secondary_y=False)
   # Middle right 
   fig_tab3.add_trace(
       go.Scatter(x=df_1['date'],  y=df_1["retweetCount"]),
       row=2, col=2, secondary_y=False)
   # Bottom left 
   fig_tab3.add_trace(
       go.Scatter(x=df_1['date'],  y=df_1["ratio_like_to_retweet"]),
       row=3, col=1, secondary_y=False)
   # Bottom right 
   fig_tab3.add_trace(
       go.Scatter(x=df_1['date'],  y=df_1["ratio_like_to_reply"]),
       row=3, col=2, secondary_y=False)

   fig_tab3.update_layout(showlegend=False)
   st.plotly_chart(fig_tab3)


   #tweets every day
   df_1['date'] = pd.to_datetime(df_1['date'])
   days=df_1.groupby(pd.Grouper(key='date',freq='D')).sum()
   days['ratio_like_to_reply']=days['likeCount']/days['replyCount']
   days['ratio_like_to_retweet']=days['likeCount']/days['retweetCount']

   fig2_tab3 = make_subplots(rows=3, cols=2,specs=[[{"secondary_y": True}, {"secondary_y": True}],
                                        [{"secondary_y": True},{"secondary_y": True}],
                                        [{"secondary_y": True}, {"secondary_y": True}]],
                    subplot_titles=("Number of likes per day during the year", "Number of replies per day during the year", 
                                   "Number of quotes per day during the year", "Number of retweets per day during the year",
                                  "likes/retweets for each day during the year",
                                   "likes/replies for each day during the year"))

    
    # Top left
   fig2_tab3.add_trace(
        go.Scatter(x=days.index,  y=days["likeCount"]),
        row=1, col=1, secondary_y=False)


    # Top right
   fig2_tab3.add_trace(
        go.Scatter(x=days.index,  y=days["replyCount"]),
        row=1, col=2, secondary_y=False)

    # Middle left 
   fig2_tab3.add_trace(
        go.Scatter(x=days.index,  y=days["quoteCount"]),
        row=2, col=1, secondary_y=False)

    # Middle right 
   fig2_tab3.add_trace(
        go.Scatter(x=days.index,  y=days["retweetCount"]),
        row=2, col=2, secondary_y=False)

    # Bottom left 
   fig2_tab3.add_trace(
        go.Scatter(x=days.index,  y=days["ratio_like_to_retweet"]),
        row=3, col=1, secondary_y=False)

    # Bottom right 
   fig2_tab3.add_trace(
        go.Scatter(x=days.index,  y=days["ratio_like_to_reply"]),
        row=3, col=2, secondary_y=False)

   fig2_tab3.update_layout(showlegend=False)
   st.plotly_chart(fig2_tab3)


   #tweets every week
   weeks=df_1.groupby(pd.Grouper(key='date', freq='W-MON')).sum()
   weeks['ratio_like_to_reply']=weeks['likeCount']/weeks['replyCount']
   weeks['ratio_like_to_retweet']=weeks['likeCount']/weeks['retweetCount']

   fig3_tab3 = make_subplots(rows=3, cols=2,specs=[[{"secondary_y": True}, {"secondary_y": True}],
                                        [{"secondary_y": True},{"secondary_y": True}],
                                        [{"secondary_y": True}, {"secondary_y": True}]],
                   subplot_titles=("Number of likes per week during the year", "Number of replies per week during the year", 
                                   "Number of quotes per week during the year", "Number of retweets per week during the year",
                                  "likes/retweets for each week during the year",
                                   "likes/replies for each week during the year"))


    # Top left
   fig3_tab3.add_trace(
        go.Scatter(x=weeks.index,  y=weeks["likeCount"]),
        row=1, col=1, secondary_y=False)


    # Top right
   fig3_tab3.add_trace(
        go.Scatter(x=weeks.index,  y=weeks["replyCount"]),
        row=1, col=2, secondary_y=False)

    # Middle left 
   fig3_tab3.add_trace(
        go.Scatter(x=weeks.index,  y=weeks["quoteCount"]),
        row=2, col=1, secondary_y=False)

    # Middle right 
   fig3_tab3.add_trace(
        go.Scatter(x=weeks.index,  y=weeks["retweetCount"]),
        row=2, col=2, secondary_y=False)

    # Bottom left 
   fig3_tab3.add_trace(
        go.Scatter(x=weeks.index,  y=weeks["ratio_like_to_retweet"]),
        row=3, col=1, secondary_y=False)
    # Bottom right 
   fig3_tab3.add_trace(
        go.Scatter(x=weeks.index,  y=weeks["ratio_like_to_reply"]),
        row=3, col=2, secondary_y=False)

   fig3_tab3.update_layout(showlegend=False)
   st.plotly_chart(fig3_tab3)


   #tweets every month
   months=df_1.groupby(pd.Grouper(key='date',freq='M')).sum()
   months['ratio_like_to_reply']=months['likeCount']/months['replyCount']
   months['ratio_like_to_retweet']=months['likeCount']/months['retweetCount']

   fig4_tab3 = make_subplots(rows=3, cols=2,specs=[[{"secondary_y": True}, {"secondary_y": True}],
                                        [{"secondary_y": True},{"secondary_y": True}],
                                        [{"secondary_y": True}, {"secondary_y": True}]],
                   subplot_titles=("Number of likes per month during the year", "Number of replies per month during the year", 
                                   "Number of quotes per month during the year", "Number of retweets per month during the year",
                                  "likes/retweets for each month during the year",
                                   "likes/replies for each month during the year"))


    # Top left
   fig4_tab3.add_trace(
        go.Scatter(x=months.index,  y=months["likeCount"]),
        row=1, col=1, secondary_y=False)


   # Top right
   fig4_tab3.add_trace(
        go.Scatter(x=months.index,  y=months["replyCount"]),
        row=1, col=2, secondary_y=False)

   # Middle left 
   fig4_tab3.add_trace(
        go.Scatter(x=months.index,  y=months["quoteCount"]),
        row=2, col=1, secondary_y=False)

   # Middle right 
   fig4_tab3.add_trace(
        go.Scatter(x=months.index,  y=months["retweetCount"]),
        row=2, col=2, secondary_y=False)

   # Bottom left 
   fig4_tab3.add_trace(
        go.Scatter(x=months.index,  y=months["ratio_like_to_retweet"]),
        row=3, col=1, secondary_y=False)
   # Bottom right 
   fig4_tab3.add_trace(
        go.Scatter(x=months.index,  y=months["ratio_like_to_reply"]),
        row=3, col=2, secondary_y=False)

   fig4_tab3.update_layout(showlegend=False)
   st.plotly_chart(fig4_tab3)

   #tweets by the week day
   df_1['day_of_week'] = df_1['date'].dt.day_name()
   day_of_week=df_1.drop('date', axis=1).groupby(df_1['day_of_week']).sum()
   sorter = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
   sorterIndex = dict(zip(sorter,range(len(sorter))))
   day_of_week['Day_id'] = day_of_week.index
   day_of_week['Day_id'] = day_of_week['Day_id'].map(sorterIndex)
   day_of_week.sort_values('Day_id', inplace=True)

   fig5_tab3 = make_subplots(rows=2, cols=2,specs=[[{"secondary_y": True}, {"secondary_y": True}],
                                        [{"secondary_y": True},{"secondary_y": True}]],
                   subplot_titles=("Number of likes for day of the week", "Number of replies for day of the week", 
                                   "Number of quotes for day of the week", "Number of retweets for day of the week"))

    # Top left
   fig5_tab3.add_trace(
        go.Scatter(x=day_of_week.index,  y=day_of_week["likeCount"]),
        row=1, col=1, secondary_y=False)


    # Top right
   fig5_tab3.add_trace(
        go.Scatter(x=day_of_week.index,  y=day_of_week["replyCount"]),
        row=1, col=2, secondary_y=False)

    # Bottom left 
   fig5_tab3.add_trace(
        go.Scatter(x=day_of_week.index,  y=day_of_week["quoteCount"]),
        row=2, col=1, secondary_y=False)

    # Bottom right 
   fig5_tab3.add_trace(
        go.Scatter(x=day_of_week.index,  y=day_of_week["retweetCount"]),
        row=2, col=2, secondary_y=False)



   fig5_tab3.update_layout(showlegend=False)
   st.plotly_chart(fig5_tab3)



