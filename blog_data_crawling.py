import streamlit as st
import pandas as pd
from io import StringIO
import re
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import numpy as np
from io import BytesIO

spreadsheet_url = 'https://docs.google.com/spreadsheets/d/1a1XNbArs57wVm1zC9xPjhZ8K-YgOrMxygJWgGThEWQ0/edit?usp=sharing'


st.sidebar.title('Blogdex data crawiling')

st.sidebar.divider()
st.sidebar.write('## Prepare')
st.sidebar.write('### Chrome debugging mode')
st.sidebar.write('(Check blogdex login)')
chrome_button = st.sidebar.button('Start')
if chrome_button:
    os.system("/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222 --user-data-dir='/Users/rivna/Applications/Google Chrome.app/'")

st.sidebar.divider()
st.sidebar.write('### Choose a CSV file')
uploaded_file = st.sidebar.file_uploader('')


@st.cache_data
def initDf(uploaded_file):
    df = 'no data'
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
    return df

@st.cache_data
def initResulttDf(df):
    resultDf = df
    resultDf.insert(2, '최적화수치', 'n/a')
    resultDf.insert(2, '총구독자', 'n/a')
    resultDf.insert(2, '최고지수', 'n/a')
    resultDf.insert(2, '종합지수', 'n/a')
    resultDf.insert(2, '주제지수', 'n/a')
    return resultDf

resultDf = 'no data'
df = initDf(uploaded_file)
if uploaded_file is not None:
    resultDf = initResulttDf(df)

if uploaded_file is not None:
    st.write('## ' + uploaded_file.name + ' raw data')
    df
else:
    st.write('## Choose a CSV file')
    'no data'

st.sidebar.divider()
st.sidebar.write('### Blogdex data crawling')

@st.cache_data
def getBlogdexData(df):
    data_urls = df['계정URL']
    # st.write(data_urls.count())
    progress_bar = st.sidebar.progress(0)

    co = Options()
    co.add_experimental_option('debuggerAddress', '127.0.0.1:9222')
    driver = webdriver.Chrome(options=co)

    for idx in range(data_urls.count()):
        data_url = data_urls[idx]

        #https://m.blog.naver.com/hyooo88_
        #https://m.blog.naver.com/PostList.naver?blogId=greatting_&tab=1
        #https://oiuio.tistory.com/, http://blog.naver.com/grkcolour
        # data_url = data_url.sub('https://m.blog.naver.com/','')
        # data_url = data_url.sub('https://','')
        # data_url = data_url.sub('&tab=1','')
        # data_url = data_url.sub('/','')
        
        data_url = re.sub('https://m.blog.naver.com/','', data_url)
        data_url = re.sub('http://m.blog.naver.com/','', data_url)
        data_url = re.sub('https://blog.naver.com/','', data_url)
        data_url = re.sub('http://blog.naver.com/','', data_url)
        data_url = re.sub('https://','', data_url)
        data_url = re.sub('&tab=1','', data_url)
        data_url = re.sub('PostList.naver\?blogId=','', data_url)
        data_url = re.sub('/','', data_url)

        # data_url

        url = "https://blogdex.space/blog-index/" + data_url
        driver.get(url)

        driver.implicitly_wait(10)

        try:
            div_1 = driver.find_element(By.XPATH, "//*[@id='__next']/div[1]/main/div/div[2]/div[1]/div[2]/div[1]/div[3]/div[1]/div/div/p")
            div_2 = driver.find_element(By.XPATH, "//*[@id='__next']/div[1]/main/div/div[2]/div[1]/div[2]/div[1]/div[3]/div[2]/div/div/p")
            div_3 = driver.find_element(By.XPATH, "//*[@id='__next']/div[1]/main/div/div[2]/div[1]/div[2]/div[1]/div[3]/div[3]/div/div/p")
            div_4 = driver.find_element(By.XPATH, "//*[@id='__next']/div[1]/main/div/div[2]/div[1]/div[2]/div[3]/div[1]/div/div")
            div_5 = driver.find_element(By.XPATH, "//*[@id='__next']/div[1]/main/div/div[2]/div[1]/div[2]/div[7]/div/div[1]/p")                                                       

            df.loc[int(idx), '주제지수'] = div_1.text
            df.loc[int(idx), '종합지수'] = div_2.text
            df.loc[int(idx), '최고지수'] = div_3.text
            df.loc[int(idx), '총구독자'] = div_4.text
            df.loc[int(idx), '최적화수치'] = div_5.text
        except Exception as e:
            print(e)
               
        progress_bar.progress(int((idx + 1) * 100 / data_urls.count()))

    # df.sort_values(by=['최적화수치'], ascending=False, inplace=True)
    driver.quit()
    return df


st.divider()
st.write('## Result data')

if 'completeData' not in st.session_state:
    st.session_state['completeData'] = 0

if st.session_state['completeData'] == 1:
    resultDf = st.session_state['resultDf']
    
    resultDf
else:
    start_button = st.sidebar.button('start')
    if start_button:
        resultDf = getBlogdexData(resultDf)
        resultDf.sort_values(by=['최적화수치'], ascending=False, inplace=True)
        st.session_state['completeData'] = 1
        st.session_state['resultDf'] = resultDf
        resultDf
    else:
        'no data'
  
st.divider()
st.write('## Save result data')

def to_excel(df):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, index=False, sheet_name='Sheet1')
    workbook = writer.book
    worksheet = writer.sheets['Sheet1']
    format1 = workbook.add_format({'num_format': '0.00'}) 
    worksheet.set_column('A:A', None, format1)  
    writer.close()
    processed_data = output.getvalue()
    return processed_data

col1, col2 = st.columns(2)

downlaod_filename = 'download file name'
if uploaded_file is not None:
    downlaod_filename = uploaded_file.name
    downlaod_filename = re.sub('리뷰어','', downlaod_filename)
    downlaod_filename = re.sub('.csv','.xlsx', downlaod_filename)

with col1:
    downlaod_filename = st.text_input(
        "downloadfile name",
        downlaod_filename,
        key="",
    )

with col2:
    if resultDf is not 'no data':
        download_button = st.download_button('Download file', to_excel(resultDf), file_name = downlaod_filename)