import streamlit as st
from google import genai
from google.genai import types
import pyperclip
from streamlit_ace import st_ace
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
# import requests  # Uncomment for GitHub integration

# Initialize Google GenAI client
client = genai.Client(api_key="AIzaSyDzgs5eDsMYrgSBTnJYWij_6qBW2OLj36g")

# Email configuration (stored in st.secrets)
#EMAIL_SENDER = st.secrets.get("email_sender", "your-email@gmail.com")
#EMAIL_PASSWORD = st.secrets.get("email_password", "your-app-password")
#EMAIL_RECEIVER = st.secrets.get("email_receiver", "developer-email@example.com")

# GitHub configuration (uncomment for GitHub integration)
# GITHUB_TOKEN = st.secrets.get("github_token", "your-personal-access-token")
# GITHUB_REPO = st.secrets.get("github_repo", "username/repo")
# GITHUB_API_URL = f"https://api.github.com/repos/{GITHUB_REPO}/issues"

# System instruction
system_instruction = """Rewrite this news article into classical Sanskrit without English punctuation 
or foreign letters like à¤‘ and with moderate sandhi but proper rules applied. 
A direct translation is not required; instead, provide an original composition 
that conveys the facts and details in an informative, engaging, fun-to-read, 
and easy-to-understand manner, following classical Sanskrit style. 
You may add additional context or gentle humor, or view of the shastras (with correct references), 
but ensure accuracy and avoid altering the core facts (like quotes of people). 
Carefully recheck the output for grammatical accuracy (correct case endings, verb conjugations, 
and sandhi rules) and stylistic consistency before finalizing. Write surnames before names 
and ensure proper sandhi all throughout the name. (e.g. à¤¶à¤°à¥à¤®à¤°à¥‹à¤¹à¤¿à¤¤à¤ƒ)
Similarly write english name in devanagari with original name in brackets (e.g. à¤•à¤¾à¤µà¤¿à¤¨à¥à¤¡à¥€à¤¸à¥à¤¯à¥‡à¤•à¥à¤·à¥ (CoinDCX))
Provide just the translation without any other extra introductory text."""

# Demo input
DEMO_INPUT = """On July 19, 2025, CoinDCX, one of Indiaâ€™s largest crypto exchanges, suffered a major hack resulting in a loss of about $44.2 million. The breach targeted an internal wallet used by CoinDCX for liquidity with a partner exchange and did not affect any customer funds, which remain safe in cold storage. Blockchain investigators like ZachXBT uncovered the hack before CoinDCX made it public, noting the hacker used a sophisticated server-side attack and laundered the funds by moving them from Solana to Ethereum and using Tornado Cash. CoinDCX has drawn some criticism for a 17-hour delay in disclosing the breach, especially since the compromised wallet was not part of the exchangeâ€™s published proof-of-reserves. In response, the company froze all impacted systems, engaged third-party security experts, and has covered the losses using its own treasury to ensure normal trading and withdrawals. CEO Sumit Gupta assured users that all customer holdings are safe, and the company has launched a bug bounty to strengthen future security while cooperating with authorities. This incident, the second major Indian exchange hack within a year, has intensified scrutiny on how centralized crypto platforms handle security and crisis management."""

st.title("à¤¸à¤‚à¤µà¤¾à¤°à¥à¤¤à¥à¤¤à¤¾")
st.markdown(
    """
    ### Disclaimers: 
      * AI translation may contain errors or hallucinations. __*Always proofread*__ before publishing.
      * Generating the response *will* be slow. Please be patient!
      * Please note that this demo supports a limited number of requests and may be unavailable 
      if too many people use the service. Thank you for your understanding.
"""
)

# Initialize session state for logs
if "usage_logs" not in st.session_state:
    st.session_state.usage_logs = []
if "feedback_logs" not in st.session_state:
    st.session_state.feedback_logs = []

# Collapsible prompt section
with st.expander("View Prompt (Non-editable)"):
    st.markdown(
        """
        <div style='background-color: #f0f2f6; padding: 10px; border-radius: 5px;'>
            <pre style='white-space: pre-wrap;'>{}</pre>
        </div>
        """.format(system_instruction),
        unsafe_allow_html=True,
    )

# Demo button
if st.button("Load Demo Article"):
    st.session_state.input_text = DEMO_INPUT

# Cache API responses
@st.cache_data
def generate_sanskrit_translation(input_text, system_instruction):
    api_response = client.models.generate_content(
        model="gemini-2.5-pro",
        config=types.GenerateContentConfig(system_instruction=system_instruction),
        contents=input_text,
    )
    parts = api_response.candidates[0].content.parts
    return "".join(part.text for part in parts)

# Function to send email
def send_email(subject, body):
    try:
        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = EMAIL_SENDER
        msg["To"] = EMAIL_RECEIVER

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, msg.as_string())
        return True
    except Exception as e:
        st.error(f"Failed to send email: {str(e)}")
        return False

# Function to post to GitHub (uncomment to enable)
# def post_to_github(title, body):
#     try:
#         headers = {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}
#         data = {"title": title, "body": body}
#         response = requests.post(GITHUB_API_URL, json=data, headers=headers)
#         if response.status_code == 201:
#             return True
#         else:
#             st.error(f"Failed to post to GitHub: {response.json().get('message', 'Unknown error')}")
#             return False
#     except Exception as e:
#         st.error(f"Failed to post to GitHub: {str(e)}")
#         return False

# Input form
with st.form("input_form"):
    input_text = st.text_area(
        "Enter a detailed news article for best results. "
        "To reiterate -  __*Always proofread*__ before publishing, "
        "as it might contain errors or hallucinations (i.e. made-up facts).",
        height=300,
        key="input_text"
    )
    
    # Display input character count
    st.write(f"Input character count: {len(input_text)}")
    if len(input_text) > 5000:
        st.warning("Input is very long. Consider shortening it for better performance.")

    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        if st.form_submit_button("Paste"):
            try:
                pasted_text = pyperclip.paste()
                st.session_state.input_text = pasted_text
            except Exception as e:
                st.error("Failed to paste text. Please try again or paste manually.")
    with col2:
        if st.form_submit_button("Clear"):
            st.session_state.input_text = ""
    with col3:
        submitted = st.form_submit_button("Submit")

# Process submission with validation, error handling, and progress bar
if submitted:
    if not input_text.strip():
        st.error("Please enter a valid news article.")
    else:
        try:
            with st.spinner("Generating Sanskrit translation... Please wait."):
                response = generate_sanskrit_translation(input_text, system_instruction)
                st.session_state.output = response
                
                # Log usage analytics
                usage_log = f"Submission at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                st.session_state.usage_logs.append(usage_log)
                #send_email("Sanskrit Translation Tool Usage Log", usage_log)
                # post_to_github("Usage Log", usage_log)  # Uncomment for GitHub

                # Display output with syntax highlighting
                st.markdown("### Output")
                st_ace(response, language="text", theme="monokai")
                
                # Copy button
                if st.button("Copy Output"):
                    try:
                        pyperclip.copy(response)
                        st.success("Output copied to clipboard!")
                    except Exception as e:
                        st.error("Failed to copy text. Please try again or copy manually.")
                
                # Download button
                st.download_button(
                    label="Download Output",
                    data=response,
                    file_name="sanskrit_translation.txt",
                    mime="text/plain"
                )
        except Exception as e:
            st.error(f"Error generating translation: {str(e)}")
            if "rate limit" in str(e).lower():
                st.warning("Rate limit exceeded. Please try again later, as this demo supports a limited number of requests.")

# Display cached output if available
if "output" in st.session_state:
    st.markdown("### Output")
    st_ace(st.session_state.output, language="text", theme="monokai")
    if st.button("Copy Output", key="copy_cached"):
        try:
            pyperclip.copy(st.session_state.output)
            st.success("Output copied to clipboard!")
        except Exception as e:
            st.error("Failed to copy text. Please try again or copy manually.")
    st.download_button(
        label="Download Output",
        data=st.session_state.output,
        file_name="sanskrit_translation.txt",
        mime="text/plain",
        key="download_cached"
    )

# Feedback form
st.subheader("Provide Feedback")
with st.form("feedback_form"):
    feedback = st.text_area("Please share your feedback on the translation quality or tool experience:")
    feedback_submitted = st.form_submit_button("Submit Feedback")
    if feedback_submitted:
        if feedback.strip():
            feedback_log = f"Feedback at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}: {feedback}"
            st.session_state.feedback_logs.append(feedback_log)
            #send_email("Sanskrit Translation Tool Feedback", feedback_log)
            # post_to_github("User Feedback", feedback_log)  # Uncomment for GitHub
            st.success("Thank you for your feedback!")
        else:
            st.error("Please enter valid feedback.")

# Optional: Display logs for debugging (can be removed in production)
with st.expander("View Logs (Debugging)"):
    st.markdown("### Usage Logs")
    st.write(st.session_state.usage_logs)
    st.markdown("### Feedback Logs")
    st.write(st.session_state.feedback_logs)

# Responsive design CSS
st.markdown(
    """
    <style>
    .stTextArea textarea { font-size: 16px; }
    @media (max-width: 600px) { .stTextArea textarea { height: 200px !important; } }
    </style>
    """,
    unsafe_allow_html=True
)
