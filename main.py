import streamlit as st
import aiohttp
import asyncio
import time
import pandas as pd
import matplotlib.pyplot as plt
from aiohttp import ClientSession, ClientTimeout, TCPConnector

st.title("🚀  API Tester & Analyzer ")

# Inputs
api_url = st.text_input("Enter API URL:")
token = st.text_input("Enter Bearer Token:", type="password")
times = st.number_input("How many times to hit the API?", min_value=1, max_value=1000, value=100)

# Advanced settings
max_concurrent_requests = st.slider("Max Concurrent Requests", min_value=1, max_value=50, value=20)
timeout_seconds = st.slider("Timeout (seconds)", min_value=1, max_value=30, value=10)

# Function to handle API calls
async def fetch(session: ClientSession, i: int, url: str, headers: dict):
    start_time = time.time()
    try:
        async with session.get(url, headers=headers) as response:
            response_time = round(time.time() - start_time, 3)
            data = await response.text()
            return {
                "Call #": i + 1,
                "Status Code": response.status,
                "Time (s)": response_time,
                "Response": data[:100],  # Preview first 100 chars
                "Timestamp": pd.Timestamp.now()
            }
    except Exception as e:
        return {
            "Call #": i + 1,
            "Status Code": "ERROR",
            "Time (s)": 0,
            "Response": str(e),
            "Timestamp": pd.Timestamp.now()
        }

# Function to execute multiple API calls concurrently
async def run_api_calls(api_url, headers, times, max_concurrent_requests):
    async with ClientSession(connector=TCPConnector(limit_per_host=max_concurrent_requests),
                             timeout=ClientTimeout(total=timeout_seconds)) as session:
        tasks = [fetch(session, i, api_url, headers) for i in range(times)]
        return await asyncio.gather(*tasks)

# Button to trigger test
if st.button("🚀 Run Optimized API Test"):
    if not api_url or not token:
        st.error("Please provide both API URL and Token.")
    else:
        headers = {"Authorization": f"Bearer {token}"}
        st.info("Running requests...")

        # Run the concurrent requests using asyncio.run()
        results = asyncio.run(run_api_calls(api_url, headers, times, max_concurrent_requests))

        # Convert to DataFrame for analysis
        df = pd.DataFrame(results).sort_values(by="Call #")

        # Display results in Streamlit
        st.subheader("📄 API Call Logs")
        st.dataframe(df)

        # Status Code Distribution
        st.subheader("📊 Status Code Distribution")
        status_counts = df["Status Code"].value_counts()
        st.bar_chart(status_counts)

        # Response Time Graph
        st.subheader("🕒 Response Time Over Calls")
        st.line_chart(df["Time (s)"])

        # Advanced Graph: Latency Distribution
        st.subheader("🕹 Latency Distribution (Histogram)")
        plt.hist(df["Time (s)"], bins=20, color='skyblue', edgecolor='black')
        plt.title("Response Time Distribution")
        plt.xlabel("Response Time (seconds)")
        plt.ylabel("Frequency")
        st.pyplot()

        # Throughput: Requests per second
        throughput = times / (df["Time (s)"].sum() / 1000)  # RPS = total requests / total time in seconds
        st.subheader(f"💥 Throughput (Requests Per Second): {throughput:.2f} RPS")

        # Downloadable Report
        st.download_button("📥 Download Full Report (CSV)", df.to_csv(index=False), "api_test_report.csv", "text/csv")
        st.download_button("📥 Download Full Report (JSON)", df.to_json(orient="records"), "api_test_report.json", "application/json")

        st.success("✅ Test Completed Successfully!")
