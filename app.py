import pandas as pd
import numpy as np 
import math
import streamlit as st

#Информация о последней статье
clients_la = pd.read_csv('http://89.108.110.60:3000/public/question/8b6c2d50-32b2-4e9c-a65a-e874d593987b.csv',sep=',')
counter = len(clients_la.reader.unique().tolist())

#Новые статьи популярных тем - для холодного старта
popular_articles = pd.read_csv('http://89.108.110.60:3000/public/question/5cc100e7-5512-4813-92cc-060313f202b5.csv',sep=',')
popular_articles_list = popular_articles.articles.tolist()

#Новые статьи за по всем темам
popular_articles_all = pd.read_csv('http://89.108.110.60:3000/public/question/02dcab3d-5ffa-4b62-8235-b40710a755c9.csv',sep=',')

#Создание матрицы для поиска 
def get_matrix():
  df = clients_la.copy() 
  df['num'] = 1  
  matrix = df.pivot_table(index='reader', columns='article', values='num', aggfunc=np.sum).fillna(0)
  return matrix
matrix_for_search = get_matrix()


st.title('Рекомендательная система RBC')
st.header('Выбор клиента')
st.write("На данный момент в списке " + str(counter) + " читателя")
selected_reader = st.selectbox("Выберите читателя", clients_la['reader'].unique())

def rec_system (reader):
    interest_list = ((clients_la.loc[clients_la.reader == reader])['article']).tolist()
    last_article = interest_list[0]
    matrix = matrix_for_search[interest_list]
    s = 0 
    l_readers = matrix.index.tolist()
    similar_readers = [] 
    for reader in l_readers:
        for article in interest_list:
            if matrix[article][reader] == 1:
                s = s + 1
        if s >= math.ceil(len(interest_list)/2):
            similar_readers.append(reader)
            s = 0  
        else: 
            s = 0
    rec_list = []
    for reader in similar_readers:
        rec_list.append((clients_la.loc[clients_la.reader ==  reader])['article'].values[0])
    def get_unique_items(lst):
        unique = []
        for l in lst:
            if l not in unique:
                unique.append(l)
        return unique 
    rec_list = get_unique_items(rec_list)
    for interest in interest_list:
        rec_list = ([x for x in rec_list  if str(x) != interest])
    if len(rec_list) < 15:
        theme = ((clients_la.loc[clients_la.article == last_article])['theme']).values[0]
        popular_articles = (popular_articles_all.loc[popular_articles_all.theme == theme])['articles'].tolist()
        rec_list = get_unique_items(rec_list +  popular_articles + popular_articles_list)
    rec_list = rec_list[0:15]
    return rec_list

st.write("Поиск начнется по клику на кнопку")
find_button = st.button("Подыскать рекомендацию")
if find_button:
    st.write(f"Выбранный клиент: {selected_reader!r}")
    la = (clients_la.loc[clients_la.reader == selected_reader])['article'].values[0]
    st.write(f"Последняя статья:  {la!r}")
    st.write('_**Что можно порекомендовать:**_')
    rec_list = rec_system(selected_reader)
    for j in range( len(rec_list)):
        st.write( str(j + 1) + '. ' + rec_list[j])
    
    df = pd.DataFrame(rec_list)
    df.columns = ['Список рекомендаций']
    df.index = range(1,16)
    df = df.to_csv().encode('utf-8')
    st.download_button( label="Скачать список", data=df, file_name= 'rec_list_'+ selected_reader +'.csv', mime='text/csv')
    st.write('Список будет скачан в csv формате, открывайте его через приложение "Блокнот"')
st.markdown("___")

st.header('Для прочих клиентов')
st.write("Можно _**порекомендовать статьи**_, ставшие популярными за последние 3 дня: ")
for j in range( len(popular_articles_list)):
    st.write( str(j + 1) + '. ' + popular_articles_list[j])
df1 = pd.DataFrame(popular_articles_list)
df1.columns = ['Общий список рекомендаций']
df1.index = range(1,16)
df1 = df1.to_csv().encode('utf-8')
st.download_button( label="Скачать общий список", data=df1, file_name= 'general_rec_list.csv', mime='text/csv')
st.write('Список будет скачан в csv формате, открывайте его через приложение "Блокнот"')
st.markdown("___")

st.subheader("А еще можно выбрать тему и получит список ее популярных статей: ")
selected_theme = st.selectbox("Выберите тему", popular_articles_all['theme'].unique())
view_button = st.button("Показать список")
if view_button:
    rec_list = ((popular_articles_all.loc[popular_articles_all.theme == selected_theme])['articles']).tolist()
    st.write("Список рекомандий для темы: " + selected_theme)
    for j in range( len(rec_list)):
        st.write( str(j + 1) + '. ' + rec_list[j])
    df = pd.DataFrame(rec_list)
    df.columns = ['Список рекомендаций']
    df.index = range(1,len(rec_list) + 1)
    df = df.to_csv().encode('utf-8')
    st.download_button( label="Скачать список", data=df, file_name= (selected_theme + '_rec_list.csv'), mime='text/csv')
    st.write('Список будет скачан в csv формате, открывайте его через приложение "Блокнот"')
