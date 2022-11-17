import streamlit as st
import pandas as pd
from bs4 import BeautifulSoup
import requests
import re

st.title("Staples SKU Scraping")
st.subheader("This script seeks to scrape the manufacturing number and the price for a list of SKUs.")

df = pd.DataFrame(None)
SKUURL = []
SKUs = []
uploaded_file = st.file_uploader("Please upload an excel file with the SKUs in the first column with a header of 'SKU'", type = ['xlsx'])
if uploaded_file:
    df = pd.read_excel(uploaded_file)

    st.dataframe(df)
    SKUs = list(df['SKU'])
    base_url = 'https://www.staples.com/product_'

    SKUURL = []
    for sku in SKUs:
        a = base_url + str(sku)
        SKUURL.append(a)
     
prices = []
nums = []
count = 0
# loop through urls
for i in SKUURL:
    count += 1
    session = requests.session()
    session.max_redirects = 60
    price = 'missing'
    manu_num = 'missing'
    man_clean = 'missing'
    url = i
    try:
        page = requests.get(url)
    except:
        st.write('Too many redirects. Moving on...')
    soup = BeautifulSoup(page.text, 'lxml')
    try:
        price = soup.find('div', class_= "price-info__final_price_sku").text
    except:
        st.write("price not found at ", url, "---- Moving on")
    try:
        manu_num = soup.find('span', {"class":"product-info-ux2dot0__sub_info", "id":"manufacturer_number"}).text
        man_clean = re.search('[^:]*$', manu_num).group(0)
        man_clean = man_clean.strip()
    except:
        st.write("Manufacturer number not found at ", url, "---- Moving on")
    st.write('Checking SKU number ', count, 'out of', len(SKUURL), 'total SKUs')
    prices.append(price)
    nums.append(man_clean)

# create DF and export
out = pd.DataFrame()
out['SKU'] = SKUs
out['SKU url'] = SKUURL
out['Price'] = prices
out['Manufacturer Number'] = nums
out.to_excel('staples_output.xlsx', index = False)
if len(out) > 1: 
    st.write("Configuring output file")
    st.write("Output file created")