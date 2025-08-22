import streamlit as st
from google import genai
from google.ai import generativelanguage as glm
from google.genai import types
from datetime import datetime
# import smtplib
# from email.mime.text import MIMEText as Text

# --- Configuration Section ---

st.set_page_config(layout="wide")
st.title("Sanskrit News Generator")

# Add a sidebar for API key configuration
st.sidebar.title("Configuration")
user_api_key = st.sidebar.text_input(
    "Your Google API Key (Optional)",
    type="password",
    help="If you provide your own key, it will be used instead of the app's default key."
)

# Determine which API key to use
api_key = None
if user_api_key:
    api_key = user_api_key
    st.sidebar.success("Using your provided API key.")
elif "google_key" in st.secrets:
    api_key = st.secrets["google_key"]
else:
    # No key is available, the app will show an error on submission.
    pass


# --- Default Prompts and Demo Content ---

# System instruction (default)
default_system_instruction = """Rewrite this news article into classical Sanskrit without English punctuation 
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


# --- Main Application UI ---

# Input form
with st.form("input_form"):
    # Action buttons with icons above input box
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.form_submit_button("❌ Clear"):
            st.session_state.input_text = ""
    with col2:
        if st.form_submit_button("📄 Load Demo"):
            st.session_state.input_text = DEMO_INPUT

    input_text = st.text_area(
        "Enter a detailed news article for best results. Or click the button for sample text.  **_Always proofread before publishing._**",
        height=300,
        key="input_text"
    )
    
    st.write(f"Input character count: {len(input_text)}")
    if len(input_text) > 5000:
        st.warning("Input is very long. Consider shortening it for better performance.")

    submitted = st.form_submit_button("Submit")

# Collapsible disclaimers
with st.expander("Disclaimers"):
    st.markdown(
        """
        * AI translation may contain errors or hallucinations. __*Always proofread*__ before publishing.
        * Generating the response *will* be slow. Please be patient!
        * If using the default key, please note that this demo supports a limited number of requests and may be unavailable 
        if too many people use the service. Thank you for your understanding.
        """
    )

# Initialize session state for usage logs and system instruction
if "usage_logs" not in st.session_state:
    st.session_state.usage_logs = []
if "system_instruction" not in st.session_state:
    st.session_state.system_instruction = default_system_instruction

# Editable prompt
with st.expander("View/Edit Prompt"):
    st.session_state.system_instruction = st.text_area(
        "System Instruction",
        value=st.session_state.system_instruction,
        height=200
    )


# --- Backend Functions ---

# Cache API responses
@st.cache_data(show_spinner=False)
def generate_sanskrit_translation(input_text, system_instruction, api_key_to_use):
    """
    Generates translation. Client is initialized here to ensure the correct
    API key is used and caching works properly if the key changes.
    """
    client = genai.Client(api_key=api_key_to_use)
    model = client.get_generative_model(model="gemini-1.5-pro-latest")
    
    # Using the new system_instruction parameter for gemini-1.5-pro
    system_instruction_prompt = glm.Content(
        parts=[glm.Part(text=system_instruction)],
        role="system"
    )
    
    response = model.generate_content(
        [system_instruction_prompt, input_text]
    )

    return response.text

# Function to send email for usage logs (Commented out as it's incomplete)
# def send_email(subject, body):
#     try:
#         # These variables would need to be defined, e.g., in st.secrets
#         EMAIL_SENDER = "your_email@gmail.com"
#         EMAIL_PASSWORD = "your_password"
#         EMAIL_RECEIVER = "receiver_email@gmail.com"
#
#         msg = Text(body)
#         msg["Subject"] = subject
#         msg["From"] = EMAIL_SENDER
#         msg["To"] = EMAIL_RECEIVER
#         with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
#             server.login(EMAIL_SENDER, EMAIL_PASSWORD)
#             server.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, msg.as_string())
#         return True
#     except Exception as e:
#         st.error(f"Failed to send usage log email: {str(e)}")
#         return False


# --- Form Submission Logic ---

if submitted:
    # 1. Validate that an API key is available
    if not api_key:
        st.error("Google API key not found. Please add it to your Streamlit secrets (`google_key`) or provide one in the sidebar to continue.")
    # 2. Validate that the input text is not empty
    elif not input_text.strip():
        st.error("Please enter a news article to translate.")
    # 3. If all validations pass, proceed with generation
    else:
        try:
            with st.spinner("Generating Sanskrit translation... Please wait."):
                response = generate_sanskrit_translation(
                    input_text, 
                    st.session_state.system_instruction, 
                    api_key_to_use=api_key
                )
                
                # Log usage analytics
                usage_log = f"Submission at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                st.session_state.usage_logs.append(usage_log)
                # send_email("Sanskrit News Generator Usage Log", usage_log)
                
                # Display output in vertically scrollable box
                st.markdown("### Output")
                st.text_area("Generated Sanskrit Text", response, height=400)
                
                # Download button
                st.download_button(
                    label="Download Output",
                    data=response,
                    file_name="sanskrit_translation.txt",
                    mime="text/plain"
                )
        except Exception as e:
            st.error(f"An error occurred while generating the translation: {str(e)}")
            if "api_key" in str(e).lower():
                 st.warning("The provided API key might be invalid. Please check the key in the sidebar.")
            elif "rate limit" in str(e).lower():
                st.warning("Rate limit exceeded. Please try again later. If you have your own API key, you can provide it in the sidebar.")


# --- Footer ---
st.markdown("---")
st.markdown("For feedback or suggestions, please email [shantanu.oak@gmail.com](mailto:shantanu.oak@gmail.com).")
