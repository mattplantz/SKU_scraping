import streamlit as st
import pandas as pd
import bs4
from bs4 import BeautifulSoup
import requests

st.title('Office Depot SKU Scraping')
st.subheader('This script seeks to scrape the manufacturing number and the price for list of SKUs.')
headers = {
    'Accept-Encoding': 'gzip, deflate, sdch',
    'Accept-Language': 'en-US,en;q=0.8',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Cache-Control': 'max-age=0',
    'Connection': 'keep-alive',
}
df = pd.DataFrame(None)
uploaded_file = st.file_uploader("Please upload an excel file with the SKUs in the first column with a header of 'SKU'", type = ['xlsx'])
SKUURL = []
SKUs = []
out = None
if uploaded_file:
    df = pd.read_excel(uploaded_file)

    st.dataframe(df)
    #st.table(df)

    
    SKUs = list(df['SKU'])
    base_url = 'https://www.officedepot.com/a/products/'
    
    
    for SKU in SKUs:
        a = base_url + str(SKU)
        SKUURL.append(a)
    
    # initiate output df
    df['SKUURL'] = SKUURL
prices = []
nums = []
count = 0
for i in SKUURL:
    count += 1
    session = requests.session()
    session.max_redirects = 60
    #print(index, "---",row['SKUURL'])
    mydata = pd.DataFrame(columns = ['row name', 'value'])
    price = 'missing'
    manu_num = 'missing'
    url = i
    try:
        page = requests.get(url, headers=headers)
    except:
        st.write('too many redirects. Moving on...')
    soup = bs4.BeautifulSoup(page.text, 'lxml')
    table = soup.find('table')
    try:
        for j in table.find_all('tr')[1:]:
                 row_data = j.find_all('td')
                 row = [i.text for i in row_data]
                 length = len(mydata)
                 mydata.loc[length] = row
                 price = soup.find('span', class_="od-graphql-price-big-price").text
                 manu_num = mydata['value'][0]  
    except:
        st.write('issue finding manufacturing number. Moving on...')
    #print('count:', i, '--------')
    #print(price)
    #print(manu_num)
    st.write('Checking SKU number ', count, 'out of', len(SKUURL), 'total SKUs')
    prices.append(price)
    nums.append(manu_num)
    
# create output dataframe to export to xlsx file
out = pd.DataFrame()
out['SKU'] = SKUs
out['SKU url'] = SKUURL
out['Price'] = prices
out['Manufacturer Number'] = nums
out.to_excel('Office_Depot_SKU_scrape.xlsx', index = False)
if len(out) > 1: 
    st.write("Configuring output file")
    st.write("Output file created")
st.download_button("Press to Download Output", out.to_excel('Office_Depot_SKU_scrape.xlsx', index = False))
