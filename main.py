import streamlit as st
import aiohttp
import asyncio
import time
import pandas as pd
import matplotlib.pyplot as plt
from aiohttp import ClientSession, ClientTimeout, TCPConnector

# 🎯 Title
st.set_page_config(page_title="API Tester & Analyzer", layout="wide")
st.title("🚀 API Tester & Analyzer - Ultimate Edition")

# 📥 Inputs
api_url = st.text_input("Enter API URL:")
method = st.selectbox("HTTP Method", ["GET", "POST"])
token = st.text_input("Enter Bearer Token (Optional):", type="password")
req_body = ""
if method == "POST":
    req_body = st.text_area("Enter Request Body (JSON format):", height=150)

times = st.number_input("How many times to hit the API?", min_value=1, max_value=1000, value=100)
max_concurrent_requests = st.slider("Max Concurrent Requests", min_value=1, max_value=50, value=20)
timeout_seconds = st.slider("Timeout per request (seconds)", min_value=1, max_value=30, value=10)

# 🧠 Construct Headers
headers = {"Authorization": f"Bearer {token}"} if token else {}

# 🧪 Show Curl Command
if api_url:
    curl_command = f"curl -X {method} '{api_url}'"
    if token:
        curl_command += f" -H 'Authorization: Bearer {token}'"
    if method == "POST" and req_body.strip():
        curl_command += f" -H 'Content-Type: application/json' -d '{req_body.strip()}'"
    st.subheader("🧪 Try This in Terminal (cURL Preview)")
    st.code(curl_command, language='bash')

# ⚙️ Async Request Function
async def fetch(session: ClientSession, i: int, url: str, method: str, headers: dict, body: str):
    start_time = time.time()
    try:
        if method == "POST":
            async with session.post(url, headers=headers, data=body.encode("utf-8")) as response:
                data = await response.text()
        else:
            async with session.get(url, headers=headers) as response:
                data = await response.text()

        response_time = round(time.time() - start_time, 3)
        return {
            "Call #": i + 1,
            "Status Code": response.status,
            "Time (s)": response_time,
            "Response": data[:100],
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

# ⚙️ Run Concurrent API Calls
async def run_api_calls(url, headers, times, concurrency, timeout, method, body):
    connector = TCPConnector(limit_per_host=concurrency)
    timeout = ClientTimeout(total=timeout)
    async with ClientSession(connector=connector, timeout=timeout) as session:
        tasks = [fetch(session, i, url, method, headers, body) for i in range(times)]
        return await asyncio.gather(*tasks)

# 🚀 Trigger Button
if st.button("🔥 Run API Test"):
    if not api_url:
        st.error("Please enter a valid API URL.")
    else:
        st.info("Running requests... please wait.")
        try:
            results = asyncio.run(run_api_calls(api_url, headers, times, max_concurrent_requests, timeout_seconds, method, req_body))
            df = pd.DataFrame(results).sort_values(by="Call #")

            # 🧾 Logs
            st.subheader("📄 API Call Logs")
            st.dataframe(df, use_container_width=True)

            # 📊 Status Code Distribution
            st.subheader("📊 Status Code Distribution")
            status_counts = df["Status Code"].value_counts()
            st.bar_chart(status_counts)

            # ⏱ Response Time Line Chart
            st.subheader("🕒 Response Time Over Calls")
            st.line_chart(df["Time (s)"])

            # 📈 Histogram of Latency
            st.subheader("🕹 Latency Distribution (Histogram)")
            fig, ax = plt.subplots()
            ax.hist(df["Time (s)"], bins=20, color='skyblue', edgecolor='black')
            ax.set_title("Response Time Distribution")
            ax.set_xlabel("Response Time (seconds)")
            ax.set_ylabel("Frequency")
            st.pyplot(fig)

            # ⚡️ Summary Metrics
            st.subheader("📌 Summary")
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Avg Time (s)", round(df["Time (s)"].mean(), 3))
            col2.metric("Min Time (s)", round(df["Time (s)"].min(), 3))
            col3.metric("Max Time (s)", round(df["Time (s)"].max(), 3))
            throughput = times / df["Time (s)"].sum() if df["Time (s)"].sum() > 0 else 0
            col4.metric("Throughput (RPS)", f"{throughput:.2f}")

            # 📥 Downloads
            st.subheader("📥 Download Full Report")
            st.download_button("Download as CSV", df.to_csv(index=False), "api_test_report.csv", "text/csv")
            st.download_button("Download as JSON", df.to_json(orient="records"), "api_test_report.json", "application/json")

            st.success("✅ Test Completed Successfully!")

        except Exception as e:
            st.error(f"❌ An error occurred: {str(e)}")

# import streamlit as st
# import aiohttp
# import asyncio
# import time
# import pandas as pd
# import matplotlib.pyplot as plt
# from aiohttp import ClientSession, ClientTimeout, TCPConnector

# st.title("🚀 API Tester & Analyzer")

# # Inputs
# api_url = st.text_input("Enter API URL:")
# token = st.text_input("Enter Bearer Token:", type="password")
# times = st.number_input("How many times to hit the API?", min_value=1, max_value=1000, value=100)

# # Advanced settings
# max_concurrent_requests = st.slider("Max Concurrent Requests", min_value=1, max_value=50, value=20)
# timeout_seconds = st.slider("Timeout (seconds)", min_value=1, max_value=30, value=10)

# # Function to handle API calls
# async def fetch(session: ClientSession, i: int, url: str, headers: dict):
#     start_time = time.time()
#     try:
#         async with session.get(url, headers=headers) as response:
#             response_time = round(time.time() - start_time, 3)
#             data = await response.text()
#             return {
#                 "Call #": i + 1,
#                 "Status Code": response.status,
#                 "Time (s)": response_time,
#                 "Response": data[:100],  # Preview first 100 chars
#                 "Timestamp": pd.Timestamp.now()
#             }
#     except Exception as e:
#         return {
#             "Call #": i + 1,
#             "Status Code": "ERROR",
#             "Time (s)": 0,
#             "Response": str(e),
#             "Timestamp": pd.Timestamp.now()
#         }

# # Function to execute multiple API calls concurrently
# async def run_api_calls(api_url, headers, times, max_concurrent_requests, timeout_seconds):
#     async with ClientSession(connector=TCPConnector(limit_per_host=max_concurrent_requests),
#                              timeout=ClientTimeout(total=timeout_seconds)) as session:
#         tasks = [fetch(session, i, api_url, headers) for i in range(times)]
#         return await asyncio.gather(*tasks)

# # Button to trigger test
# if st.button("🚀 Run Optimized API Test"):
#     if not api_url or not token:
#         st.error("Please provide both API URL and Token.")
#     else:
#         headers = {"Authorization": f"Bearer {token}"}
#         st.info("Running requests...")

#         # Run the concurrent requests using asyncio event loop
#         loop = asyncio.new_event_loop()
#         asyncio.set_event_loop(loop)
#         results = loop.run_until_complete(run_api_calls(api_url, headers, times, max_concurrent_requests, timeout_seconds))

#         # Convert to DataFrame for analysis
#         df = pd.DataFrame(results).sort_values(by="Call #")

#         # Display results in Streamlit
#         st.subheader("📄 API Call Logs")
#         st.dataframe(df)

#         # Status Code Distribution
#         st.subheader("📊 Status Code Distribution")
#         status_counts = df["Status Code"].value_counts()
#         st.bar_chart(status_counts)

#         # Response Time Graph
#         st.subheader("🕒 Response Time Over Calls")
#         st.line_chart(df["Time (s)"])

#         # Advanced Graph: Latency Distribution
#         st.subheader("🕹 Latency Distribution (Histogram)")
#         plt.hist(df["Time (s)"], bins=20, color='skyblue', edgecolor='black')
#         plt.title("Response Time Distribution")
#         plt.xlabel("Response Time (seconds)")
#         plt.ylabel("Frequency")
#         st.pyplot()

#         # Throughput: Requests per second
#         throughput = times / df["Time (s)"].sum()
#         st.subheader(f"💥 Throughput (Requests Per Second): {throughput:.2f} RPS")

#         # Downloadable Report
#         st.download_button("📥 Download Full Report (CSV)", df.to_csv(index=False), "api_test_report.csv", "text/csv")
#         st.download_button("📥 Download Full Report (JSON)", df.to_json(orient="records"), "api_test_report.json", "application/json")

#         st.success("✅ Test Completed Successfully!")
