import streamlit as st
from google import genai
from google.genai import types
from datetime import datetime
import time

# Initialize Google GenAI client
client = genai.Client(api_key="AIzaSyDzgs5eDsMYrgSBTnJYWij_6qBW2OLj36g")

# Email configuration
EMAIL_CONFIG = {
    "sender": st.secrets.get("email_sender", "your-email@gmail.com"),
    "password": st.secrets.get("email_password", "your-app-password"),
    "receiver": st.secrets.get("email_receiver", "shantanu.oak@gmail.com"),
    "smtp_server": st.secrets.get("smtp_server", "smtp.gmail.com"),
    "smtp_port": st.secrets.get("smtp_port", 465)
}

# System instruction (default)
DEFAULT_SYSTEM_INSTRUCTION = """Rewrite this news article into classical Sanskrit without English punctuation 
or foreign letters like ऑ and with moderate sandhi but proper rules applied. 
A direct translation is not required; instead, provide an original composition 
that conveys the facts and details in an informative, engaging, fun-to-read, 
and easy-to-understand manner, following classical Sanskrit style. 
You may add additional context or gentle humor, or view of the shastras (with correct references), 
but ensure accuracy and avoid altering the core facts (like quotes of people). 
Carefully recheck the output for grammatical accuracy (correct case endings, verb conjugations, 
and sandhi rules) and stylistic consistency before finalizing. Write surnames before names 
and ensure proper sandhi all throughout the name. (e.g. शर्मरोहितः)
Similarly write english name in devanagari with original name in brackets (e.g. काविन्डीस्येक्ष् (CoinDCX))
Provide just the translation without any other extra introductory text."""

# Demo input
DEMO_INPUT = """On July 19, 2025, CoinDCX, one of India’s largest crypto exchanges, suffered a major hack resulting in a loss of about $44.2 million. The breach targeted an internal wallet used by CoinDCX for liquidity with a partner exchange and did not affect any customer funds, which remain safe in cold storage. Blockchain investigators like ZachXBT uncovered the hack before CoinDCX made it public, noting the hacker used a sophisticated server-side attack and laundered the funds by moving them from Solana to Ethereum and using Tornado Cash. CoinDCX has drawn some criticism for a 17-hour delay in disclosing the breach, especially since the compromised wallet was not part of the exchange’s published proof-of-reserves. In response, the company froze all impacted systems, engaged third-party security experts, and has covered the losses using its own treasury to ensure normal trading and withdrawals. CEO Sumit Gupta assured users that all customer holdings are safe, and the company has launched a bug bounty to strengthen future security while cooperating with authorities. This incident, the second major Indian exchange hack within a year, has intensified scrutiny on how centralized crypto platforms handle security and crisis management."""

# Initialize session state
def initialize_session_state():
    defaults = {
        "usage_logs": [],
        "system_instruction": DEFAULT_SYSTEM_INSTRUCTION,
        "input_text": "",
        "output": None,
        "error_logs": []
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

initialize_session_state()

# Function to send email with retry logic
def send_email(subject, body, max_retries=3):
    for attempt in range(max_retries):
        try:
            msg = MIMEText(body)
            msg["Subject"] = subject
            msg["From"] = EMAIL_CONFIG["sender"]
            msg["To"] = EMAIL_CONFIG["receiver"]
            with smtplib.SMTP_SSL(EMAIL_CONFIG["smtp_server"], EMAIL_CONFIG["smtp_port"]) as server:
                server.login(EMAIL_CONFIG["sender"], EMAIL_CONFIG["password"])
                server.sendmail(EMAIL_CONFIG["sender"], EMAIL_CONFIG["receiver"], msg.as_string())
            return True
        except Exception as e:
            if attempt == max_retries - 1:
                st.error(f"Failed to send usage log email after {max_retries} attempts: {str(e)}")
                st.session_state.error_logs.append(f"Email error at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}: {str(e)}")
                return False
            time.sleep(2 ** attempt)  # Exponential backoff

# Function to render output
def render_output(text):
    if text:
        st.markdown("### Output")
        st.markdown(
            f"""
            <div style="background-color: #f0f2f6; padding: 10px; border-radius: 5px; max-height: 400px; overflow-y: auto; white-space: pre-wrap;">
                <pre>{text}</pre>
            </div>
            """,
            unsafe_allow_html=True
        )
        st.download_button(
            label="Download Output",
            data=text,
            file_name="sanskrit_translation.txt",
            mime="text/plain",
            key=f"download_{'cached' if text == st.session_state.output else 'new'}"
        )

st.title("Sanskrit News Generator")

# Input form (at top)
with st.form("input_form"):
    input_text = st.text_area(
        "Enter a detailed news article for best results. **_Always proofread before publishing_**.",
        value=st.session_state.input_text,
        height=300,
        key="input_text_area"
    )
    
    # Real-time input character count
    char_count_placeholder = st.empty()
    char_count_placeholder.write(f"Input character count: {len(input_text)}")
    if len(input_text) > 5000:
        st.warning("Input is very long. Consider shortening it for better performance.")

    # Action buttons (Clear, Demo, Submit) side by side
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        clear_clicked = st.form_submit_button("❌", key="clear_button")
    with col2:
        demo_clicked = st.form_submit_button("Demo", key="demo_button")
    with col3:
        submitted = st.form_submit_button("Submit")

    # Handle button actions
    if clear_clicked:
        st.session_state.input_text = ""
    elif demo_clicked:
        with st.spinner("Loading demo article..."):
            st.session_state.input_text = DEMO_INPUT
    elif submitted:
        if not input_text.strip():
            st.error("Please enter a valid news article.")
        else:
            try:
                with st.spinner("Generating Sanskrit translation... Please wait."):
                    response = generate_sanskrit_translation(input_text, st.session_state.system_instruction)
                    st.session_state.output = response
                    # Log usage analytics
                    usage_log = f"Submission at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                    st.session_state.usage_logs.append(usage_log)
                    #send_email("Sanskrit News Generator Usage Log", usage_log)
                    render_output(response)
            except Exception as e:
                error_msg = str(e).lower()
                st.session_state.error_logs.append(f"API error at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}: {error_msg}")
                if "rate limit" in error_msg:
                    st.warning("Rate limit exceeded. Please try again later, as this demo supports a limited number of requests.")
                elif "invalid input" in error_msg:
                    st.error("Invalid input format. Please ensure the news article is properly formatted.")
                else:
                    st.error(f"Error generating translation: {error_msg}")

# Collapsible disclaimers
with st.expander("Disclaimers"):
    st.markdown(
        """
        * AI translation may contain errors or hallucinations. __*Always proofread*__ before publishing.
        * Generating the response *will* be slow. Please be patient!
        * Please note that this demo supports a limited number of requests and may be unavailable 
        if too many people use the service. Thank you for your understanding.
        """
    )

# Editable prompt with reset option
with st.expander("View/Edit Prompt"):
    st.session_state.system_instruction = st.text_area(
        "System Instruction",
        value=st.session_state.system_instruction,
        height=200
    )
    if st.button("Reset to Default Prompt"):
        st.session_state.system_instruction = DEFAULT_SYSTEM_INSTRUCTION

# Cache API responses
@st.cache_data(show_spinner=False)
def generate_sanskrit_translation(input_text, system_instruction):
    api_response = client.models.generate_content(
        model="gemini-2.5-pro",
        config=types.GenerateContentConfig(system_instruction=system_instruction),
        contents=input_text,
    )
    parts = api_response.candidates[0].content.parts
    return "".join(part.text for part in parts)

# Display cached output if available
if st.session_state.output and not (clear_clicked or demo_clicked or submitted):
    render_output(st.session_state.output)

# Feedback request
st.markdown("---")
st.markdown("For feedback or suggestions, please email [shantanu.oak@gmail.com](mailto:shantanu.oak@gmail.com).")

# Responsive design CSS
st.markdown(
    """
    <style>
    .stTextArea textarea { font-size: 16px; }
    @media (max-width: 600px) {
        .stTextArea textarea { height: 200px !important; }
        [data-testid="column"] { display: inline-block; margin-right: 10px; }
        [data-testid="column"] button { width: auto; min-width: 60px; padding: 5px; }
    }
    [data-testid="stButton"] button { min-width: 60px; padding: 5px; }
    </style>
    """,
    unsafe_allow_html=True
)