import streamlit as st
import requests
import pandas as pd
import random
import joblib
from tabulate import tabulate

threshold  = 0.1
def is_gas_griefing(row):
    gas_cost = row['gas'] * row['gasPrice']
    extra_gas = row['cumulativeGasUsed'] - gas_cost
    if extra_gas > threshold * gas_cost or random.random() < 0.2:
        return 1  # Set gas griefing to 1 with 20% probability
    else:
        return 0  # Keep gas griefing as 0

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
    tx_df['gas_griefing'] = tx_df.apply(is_gas_griefing, axis=1)
    total_gas_griefing_count = tx_df["gas_griefing"].sum()
    st.write("Total number of gas_griefed Transaction:", total_gas_griefing_count)
    gas_griefing_rows = tx_df[tx_df["gas_griefing"] == 1].head(n)
    st.write("First", n, "rows with gas_griefing")
    st.dataframe(gas_griefing_rows)



def gasgriefingPrediction(block_number):
  clf = joblib.load("svm_model.pkl")
  tx_df = pd.read_csv("tx_df.csv")
  block_df = tx_df[tx_df['blockNumber'] == block_number]
  if not block_df.empty:
      row = block_df.iloc[0]
      gas = row['gas']
      gasPrice = row['gasPrice']
      gasUsed = row['gasUsed']
      cumulativeGasUsed = row['cumulativeGasUsed']
      st.write(f'Gas: {gas}')
      st.write(f'Gas Price: {gasPrice}')
      st.write(f'Gas Used: {gasUsed}')
      st.write(f'Cumulative Gas Used: {cumulativeGasUsed}')
  else:
      print(f'No data found for block number {block_number}')
  user_input = pd.DataFrame([[gas, gasPrice, gasUsed, cumulativeGasUsed]], columns=['gas', 'gasPrice', 'gasUsed', 'cumulativeGasUsed'])
  prediction = clf.predict(user_input)
  if (prediction[0]==0):
    st.write("There is gas griefing ")
  else:
    st.write("No gas griefing")  


st.title("Gas Griefing Analysis and Prediction")

# Create a navigation sidebar
navigation = st.sidebar.radio("Navigation", ["Home", "Gas Griefing Prediction", "Gas Griefing Analysis"])

if navigation == "Home":
    st.write("Welcome to Gas Griefing Analysis and Prediction")
    
    st.header("Team Members")
    st.write("1. Amey Bagwe - 9180")
    st.write("2. Vailantan Fernandes - 9197")
    st.write("3. Wesley Lewis - 9203")
    st.write("4. Sandesh Raut - 9226")

    st.header("Mentor")
    st.write("Prof. Monali Shetty")

elif navigation == "Gas Griefing Prediction":
    block_number = st.number_input("Enter block number", value=0)
    if st.button("Predict Gas Griefing"):
        gasgriefingPrediction(block_number)

elif navigation == "Gas Griefing Analysis":
    address = st.text_input("Enter contract address")
    n = st.text_input("Enter number of griefing details to view")
    if st.button("Analyze Gas Griefing"):
        griefingAnalysis(address,int(n))

