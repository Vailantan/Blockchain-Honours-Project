import streamlit as st
import requests
import pandas as pd
import joblib
import json



def griefingAnalysis(address, n):
    url = "https://api.etherscan.io/api"
    api_key = "PKIMHSFM4A19PAUIIGVHZPUTFHRKRXDHJM"
    params = {
        "module": "account",
        "action": "txlist",
        "startblock": 0,
        "endblock": 99999999,
        "page": 1,
        "address": address,
        "sort": "asc",
        "apikey": api_key
    }

    response = requests.get(url, params=params)
    data1 = response.json()
    tx_df = pd.DataFrame()
    tx_df["nonce"] = [int(data1["result"][i]["nonce"]) for i in range(len(data1["result"]))]
    tx_df["blockNumber"] = [int(data1["result"][i]["blockNumber"]) for i in range(len(data1["result"]))]
    tx_df["blockHash"] = [data1["result"][i]["blockHash"] for i in range(len(data1["result"]))]
    tx_df["from"] = [data1["result"][i]["from"] for i in range(len(data1["result"]))]
    tx_df["to"] = [data1["result"][i]["to"] for i in range(len(data1["result"]))]
    tx_df["gas"] = [int(data1["result"][i]["gas"]) for i in range(len(data1["result"]))]
    tx_df["gasUsed"] = [int(data1["result"][i]["gasUsed"]) for i in range(len(data1["result"]))]
    tx_df["gasPrice"] = [int(data1["result"][i]["gasPrice"]) for i in range(len(data1["result"]))]
    tx_df["hash"] = [data1["result"][i]["hash"] for i in range(len(data1["result"]))]
    tx_df["cumulativeGasUsed"] = [int(data1["result"][i]["cumulativeGasUsed"]) for i in range(len(data1["result"]))]
    tx_df["contractAddress"] = [data1["result"][i]["contractAddress"] for i in range(len(data1["result"]))]
    tx_df['gas_griefing'] = tx_df.apply(lambda row: 1 if row["gas"] * 0.984375 < row["gasUsed"] else 0, axis=1)
    total_gas_griefing_count = tx_df["gas_griefing"].sum()
    st.write("Total number of gas_griefed Transaction:", total_gas_griefing_count)
    gas_griefing_rows = tx_df[tx_df["gas_griefing"] == 1].head(n)
    st.write("First", n, "rows with gas_griefing")
    st.dataframe(gas_griefing_rows)

def get_block_details(block_number):
    list1 =[]
    api_key = 'YourApiKeyToken'
    base_url = 'https://api.etherscan.io/api?module=proxy&action=eth_getBlockByNumber'
    block_num_hex = hex(block_number)
    url = f'{base_url}&tag={block_num_hex}&boolean=true&apikey={api_key}'
    
    response = requests.get(url)
    data = json.loads(response.text)
    
    result = data['result']
    
    gas = int(result['gasLimit'], 16)
    gas_used = int(result['gasUsed'], 16)
    
    list1.append(gas)
    list1.append(gas_used)
    return list1

def gasgriefingPrediction(block_number):
  clf = joblib.load("model.pkl")
  list1 = get_block_details(block_number)
  user_input = pd.DataFrame([[list1[0], list1[1]]], columns=['gas', 'gasUsed'])
  prediction = clf.predict(user_input)
  st.write(f"Gas : {list1[0]}")
  st.write(f"Gas Used : {list1[1]}")
  if (prediction[0]==0):
    st.write("No gas griefing ")
  else:
    st.write("There is gas griefing")  


st.title("Gas Griefing Detection and Analysis")

# Create a navigation sidebar
navigation = st.sidebar.radio("Navigation", ["Home", "Gas Griefing Detection", "Gas Griefing Analysis"])

if navigation == "Home":
    st.write("Welcome to Gas Griefing Detection and Analysis")
    
    st.header("Team Members")
    st.write("1. Amey Bagwe - 9180")
    st.write("2. Vailantan Fernandes - 9197")
    st.write("3. Wesley Lewis - 9203")
    st.write("4. Sandesh Raut - 9226")

    st.header("Mentor")
    st.write("Prof. Monali Shetty")

elif navigation == "Gas Griefing Detection":
    block_number = st.number_input("Enter block number", value=0)
    if st.button("Detect Gas Griefing"):
        gasgriefingPrediction(block_number)

elif navigation == "Gas Griefing Analysis":
    address = st.text_input("Enter contract address")
    n = st.text_input("Enter number of griefing details to view")
    if st.button("Analyze Gas Griefing"):
        griefingAnalysis(address,int(n))

