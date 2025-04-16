
import streamlit as st
import pandas as pd
import base64

def count_matching_chars(postcode, target1, target2):
    max_match = 0
    for target in [target1.upper(), target2.upper()]:
        match_len = 0
        for a, b in zip(postcode.upper(), target):
            if a == b:
                match_len += 1
            else:
                break
        max_match = max(max_match, match_len)
    return max_match

@st.cache_data
def load_data():
    return pd.read_excel("Taxi List.xlsx")

# Base64-encoded Assesso logo
logo_base64 = """iVBORw0KGgoAAAANSUhEUgAAAEAAAABACAYAAACqaXHeAAAFIklEQVR4Xu2bv4sVQRzHv2sFbdqU
QBES2x6IjZlI4iAiH5DZRAQiVkXiAiFi0YBHiIDqgYrCCII4gIgYiIQ5GIIImtX+v7rJ6Zk5+Z2a9
9btvZy7znZ2bnZnZ1z3cKqrqCiBMqIhyBZl64TkcDHMDfMb+KkE7ivByGqvxAj6AYYBY4A/gBuAMO
mESngMjA4SOQtxqLCIG+KrV9d3kCHASuAf4EGAPMG7sf6ADjFYVliJmwF0ZwDN0R4zQq4EYwGdjwK
DpZ4FYq3AX0Az4U62JeyzP7Aqcv4VLYl9zC7COzrk+Af7OvGnMFvAVMLQKpK+lGdI84Cv4Lfg5tRm
v1z3mjSbwFwHrKjGCvHZxZ8Evgu4hO0g+8tXkzVzGhfmEXHeAJ4HZSpRYiwv1YzeqCmoW0WWkVsBB
M97me+HpBtBbZ6H4VHD+ZKDfPQO7iNSrUYZ3Es3+Xmr6C/hvo3Fa5zN5zNcmkkZlgIZINsKMmU7cC
ZAc8DbYUv8FkG5FMY6vciYk0isO9AvPqz4bmlHEbyAH2KML3MvUNBpiKiQ30R0cFPgJuKLv4h9GuG
9f5jYUN9BMCeG6qGiUWTvxFCkU5AiYHbkgj3sDAjBvccErDi0BvEfUG7TXDsA3w9tAGMDTklA/OKG
eCq6pSTAy8KTQUwrxrMNDe8QzK9lZThOVWWT0EPEaYiG0p2yKshMaVi7ic3BbU0t/N/IDr9LkGWJW
o4S9ItQslZLuIyrgd7Twz7ayvBe0h+vAzEViX7+7jK18TwIs7ZQo9F2S5tD8RQW0btBmyKuRPJSM1
LPcTJllM7VWRHDvUUrKTk7+pNBflTWXkNkE3GR4DtqYOpvl8hZynR3Au0XUb4M7i+To41HKVFdP7I
fnKZtVRXBWpHz+2l7nSFFZWzhPEfEZ6Ft2yy1qsukK9HX1JmtGUBpT9rqRuAk2lj+wXN6lTN4f2IG
AAAAAElFTkSuQmCC"""

st.set_page_config(
    page_title="Taxi Finder",
    page_icon="favicon.ico",
    layout="centered"
)

st.markdown(f"""
<div style='display: flex; align-items: center; justify-content: center; margin-bottom: 2rem;'>
    <img src="data:image/png;base64,{logo_base64}" width="40" style='margin-right: 10px; vertical-align: middle;'>
    <h1 style='font-family: Arial; font-size: 32px; margin: 0;'>Taxi Finder</h1>
</div>
""", unsafe_allow_html=True)

st.markdown("### Enter Start and End Address")
start_address = st.text_input("Start address first line:")
start_postcode = st.text_input("Start address postcode:")
end_address = st.text_input("End address first line:")
end_postcode = st.text_input("End address postcode:")
journey_count = st.text_input("Estimated number of single journeys per year:")

if start_postcode and end_postcode and journey_count:
    df = load_data()
    df["Post code"] = df["Post code"].astype(str)

    start_prefix = start_postcode[:2].upper()
    end_prefix = end_postcode[:2].upper()

    df = df[df["Post code"].str[:2].str.upper().isin([start_prefix, end_prefix])]
    df["Match Score"] = df["Post code"].apply(lambda x: count_matching_chars(x, start_postcode, end_postcode))
    df_filtered = df[df["Match Score"] > 0].sort_values(by="Match Score", ascending=False)
    output_df = df_filtered[["Taxi Company", "Tel", "Email contact", "Post code", "Location"]]

    emails = ", ".join(output_df["Email contact"].dropna().unique())
    email_body = f"""Hi,

Can I please get a quote for journeys between:

{start_address} {start_postcode} and {end_address} {end_postcode}

We're looking at approximately {journey_count} single journeys per year and a standard/wheelchair accessible vehicle is required.

Kind regards,"""

    st.markdown("### 📧 Email Message and Contacts")
    st.markdown(f"<div style='font-family: Arial; font-size: 12pt;'><b>Email contacts:</b> {emails}</div>", unsafe_allow_html=True)
    st.text_area("Email message (copy and paste)", value=email_body, height=250)

    st.markdown("### Matching Taxi Companies")
    output_html = ""
    output_text = ""
    for _, row in output_df.iterrows():
        output_html += f"""<p style='font-family: Arial; font-size: 12pt;'>
<b>{row['Taxi Company']}</b><br>
Tel: {row['Tel']}<br>
Email: {row['Email contact']}<br>
Post Code: {row['Post code']}<br>
Location: {row['Location']}
</p>
"""
        output_text += f"""{row['Taxi Company']}
Tel: {row['Tel']}
Email: {row['Email contact']}
Post Code: {row['Post code']}
Location: {row['Location']}

"""

    st.markdown(output_html, unsafe_allow_html=True)
    st.download_button("Download as text", output_text, file_name="matching_taxi_companies.txt")
else:
    st.info("Please enter both postcodes and number of journeys to search.")
