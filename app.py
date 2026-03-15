import streamlit as st
from google import genai
from google.genai import types
from datetime import datetime
import pyperclip


# Initialize Google GenAI client
# client = genai.Client(api_key=st.secrets['google_key'])


try:
    st.sidebar.title("Configuration")
    user_api_key = st.sidebar.text_input(
        "Type Your Google API Key and hit enter key (Optional)",
        key="user_api_key",
        help="If you provide your own key, it will be used instead of the app's default key."
    )
    
#    st.write("DEBUG value:", repr(user_api_key))
    
    if user_api_key == '':
        key_used = st.secrets['google_key']
        client = genai.Client(api_key=st.secrets['google_key'])
    else:
        key_used = user_api_key
        client = genai.Client(api_key=user_api_key)    
except Exception as e:
    st.error("An error occurred!")
    st.exception(e)  # shows full traceback in the app
    

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

default_system_instruction = """
You are a Sanskrit scholar composing a classical Sanskrit news article.

TASK
Rewrite the given news article as an original Sanskrit composition while preserving every factual detail (names, numbers, institutions, locations, quotes).

OUTPUT STRUCTURE
1. Begin with a short Sanskrit headline ending with a single danda (।).
2. Leave one blank line after the headline.
3. Then write the full article.
4. End the entire response with a double danda (॥).

PUNCTUATION RULES
The output must contain only Devanagari characters.
Forbidden: commas, hyphens, quotes, question marks, exclamation marks, and all non-Devanagari punctuation.
Allowed:
• danda (।) only at the headline end
• double danda (॥) only at the very end
• ॰ only for initials (e.g. एस्॰जयशङ्करः)

FACTUAL ACCURACY
Do not summarize or omit information.
Every person, number, organization, and event must appear in the Sanskrit article.

STYLE
Write in clear classical Sanskrit prose suitable for an educated reader.
Prefer finite verbs rather than participial constructions.
Ensure strict grammatical agreement of gender, number, and case.

SANDHI
• Mandatory inside compounds.
• Moderate between words for readability.

NAMES
Write names as a single compound in the order:
Initials → Title → Surname → First name.

Examples:
डो॰शुक्लमूलचन्द्रः  
सी॰पी॰राधाकृष्णस्य  

Honorifics like श्री or महोदयः are forbidden.

FOREIGN NAMES
Transliterate into Devanagari and optionally include the original in brackets.

Example:
काविन्डीस्येक्ष् (CoinDCX)

VOCABULARY
Prefer Sanskrit equivalents rather than transliteration.

Examples:
Artificial Intelligence → कृतकप्रज्ञा  
Proxy War → छद्मयुद्धम्  
Stock Market → समांशविपणिः  

GEOGRAPHICAL NAMES
Prefer established Sanskrit names where appropriate.

FINAL CHECK
Before responding, internally verify:
• grammar correctness
• sandhi correctness
• absence of forbidden punctuation
• full preservation of all facts

Output only the Sanskrit article.
Prefer classical Sanskrit narrative style similar to historical chronicles or traditional prose.
First internally analyze the English article, then compose the Sanskrit article.

"""


# Demo input
DEMO_INPUT = """On July 19, 2025, CoinDCX, one of India’s largest crypto exchanges, suffered a major hack resulting in a loss of about $44.2 million. The breach targeted an internal wallet used by CoinDCX for liquidity with a partner exchange and did not affect any customer funds, which remain safe in cold storage. Blockchain investigators like ZachXBT uncovered the hack before CoinDCX made it public, noting the hacker used a sophisticated server-side attack and laundered the funds by moving them from Solana to Ethereum and using Tornado Cash. CoinDCX has drawn some criticism for a 17-hour delay in disclosing the breach, especially since the compromised wallet was not part of the exchange’s published proof-of-reserves. In response, the company froze all impacted systems, engaged third-party security experts, and has covered the losses using its own treasury to ensure normal trading and withdrawals. CEO Sumit Gupta assured users that all customer holdings are safe, and the company has launched a bug bounty to strengthen future security while cooperating with authorities. This incident, the second major Indian exchange hack within a year, has intensified scrutiny on how centralized crypto platforms handle security and crisis management."""

st.title("Sanskrit News Generator")

# Input form (moved to top)
with st.form("input_form"):
    # Action buttons with icons above input box (Paste button removed)

    col1, col2 = st.columns([1, 1])
    with col1:
        if st.form_submit_button("🅇"):
            st.session_state.input_text = ""
    with col2:
        if st.form_submit_button("⍰"):
            st.session_state.input_text = DEMO_INPUT

    
    input_text = st.text_area(
        "Enter a detailed news article for best results or click ⍰ for sample text.  **_Always proofread before publishing_**.",
        height=300,
        key="input_text"
    )
    
    # Display input character count
    st.write(f"Input character count: {len(input_text)}")
    if len(input_text) > 5000:
        st.warning("Input is very long. Consider shortening it for better performance.")

    submitted = st.form_submit_button("➣")

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

# Cache API responses
@st.cache_data(show_spinner=False)  # Suppress "Running generate_sanskrit_translation(...)" message
def generate_sanskrit_translation(input_text, system_instruction):
    try:
        api_response = client.models.generate_content(
            model="gemini-3.1-pro-preview",
            config=types.GenerateContentConfig(system_instruction=system_instruction),
            contents=input_text,
        )
        parts = api_response.candidates[0].content.parts
        st.session_state.model_name = api_response.model_version

    except Exception as e:
        st.error("An error occurred!")
        st.exception(e)  # shows full traceback in the app

    return "".join(part.text for part in parts)

# Function to send email for usage logs
def send_email(subject, body):
    try:
        msg = Text(body)
        msg["Subject"] = subject
        msg["From"] = EMAIL_SENDER
        msg["To"] = EMAIL_RECEIVER
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, msg.as_string())
        return True
    except Exception as e:
        st.error(f"Failed to send usage log email: {str(e)}")
        return False

# Process submission with validation, error handling, and progress bar
if submitted:
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
                
                # Display output in vertically scrollable box
                st.markdown("### Output")
                st.markdown(
                    f"""
                    <div style="background-color: #f0f2f6; padding: 10px; border-radius: 5px; max-height: 400px; overflow-y: auto; white-space: pre-wrap;">
                        <pre>{response}</pre>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                
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



if "model_name" in st.session_state:   # check to avoid KeyError
    st.write("From:", st.session_state.model_name)

st.write("API Key:", key_used[:-4] + "*" )

# Feedback request
st.markdown("---")
st.markdown("For feedback or suggestions, please email [shantanu.oak@gmail.com](mailto:shantanu.oak@gmail.com).")

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
