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
Rewrite the provided news article(s) into original classical Sanskrit compositions. Your work must be an informative and engaging creative rewriting, not a literal translation, while preserving all facts from the source. Follow these instructions with maximum strictness.

I. Formatting and Terminology

• Headline Requirement: Each composition must begin with a concise, relevant and boldened Sanskrit headline ending with a single danda (।). Separate the headline from the main body text with a single line break.

• Script & Punctuation: Use Devanagari script only. Forbid absolutely "all the non-Devanagari punctuation" in all contexts (e.g., hyphens, dashes, quotes, quotation marks, commas, question marks, exclamation marks). The use of any form of English punctuation marks (‘ ’, “ ”) for emphasis or citation is strictly forbidden. Use a single double danda (॥) only at the very end of the composition. Use ॰ for initials (एस्॰जयशङ्करः).
• Vocabulary:
    • Year (CE): कृष्टाब्द
    • Government: शासनम्
    • Russia: रष्य
    • Months: प्रथममासः...सप्तममासः for Jan-July; अगस्त्य, सप्ताम्बर, etc., for Aug-Dec.
    • Technical Terms: Use Raghuvira Kosha (e.g., किरणातु for uranium).

II. Grammar, Sandhi, and Compounding (Strict Adherence Required)

• Sandhi and Compounding Rule:
    • Mandatory Internal Sandhi: Sandhi is strictly mandatory and must be perfectly applied within any single compound word (समस्तपदे). This includes all multi-word proper nouns, which must be rendered as a single, unbreakable compound.
    • Moderate External Sandhi: For Sandhi between separate words (वाक्ये), apply it moderately to create a classical flow while prioritizing readability. Any Sandhi applied must be grammatically flawless and follow all relevant Pāṇinian rules (e.g., छे च) without exception.

• Handling Foreign Labels: For non-Sanskrit labels like 'Pool A', form a direct compound with a suitable Sanskrit noun (e.g., एगणे, एवर्गे). Hyphens, spaces, or quotation marks for such labels are strictly forbidden.

• Name and Title Formatting:
    • The surname must precede the first name.
    • Fuse them into a single compound, correctly handling नकारान्त stems (e.g., मोदिन् -> मोदिनरेन्द्रः; तिवारिन् -> तिवारिसर्वेशः).
    • Prefix the academic title डो॰ directly to the name compound without any space (e.g., डो॰शुक्लमूलचन्द्रः).
    • Order of Initials: When a name includes initials, the initials must always precede the name and be joined with it to form a single compound word. For example, write सी॰पी॰राधाकृष्णस्य, not राधाकृष्णसी॰पी॰स्य.
    • Transliterate foreign names, followed by the original in brackets: काविन्डीस्येक्ष् (CoinDCX).
• Verbs: Strictly follow पुरुषः agreement (मध्यमपुरुषः for त्वम्/यूयम्; प्रथमपुरुषः for भवान्). Use लङ् लकारः for definite past events and लुङ् लकारः for indefinite past events.
• Syntax: Use इतिनाम्नः (not इति नाम्नः). Numeral Formatting: Write large numbers in the detailed classical style, connecting ascending units of value with अधिक or a similar term. For example, for the number 2,57,048, the correct form is अष्टचत्वारिंशदधिकसप्तसहस्राधिकपञ्चायुताधिकद्विलक्षम्. Avoid simplistic compound forms like द्विलक्षसप्तपञ्चाशत्सहस्राष्टचत्वारिंशत्. Use singular forms for single persons and avoid honorifics like महोदयः.

• Phonetic Integrity in Transliteration: Transliterated foreign words must strictly conform to internal Sanskrit phonetic rules. For example, 'Instagram' must be rendered as इंष्टग्राम (applying both anusvāra and ṣṭutva rules).

• Syntactic Elegance: Prefer direct and concise finite verb constructions (तिङन्तप्रयोगः). Avoid redundant participial phrases (कृदन्तप्रयोगः) for primary clauses. For example, स जीवतीति is strongly preferred over स जीवन्नस्तीति.

III. Final Output

• Meticulously verify the entire output for perfect grammatical and stylistic adherence to all rules.
• Provide only the final, clean Sanskrit composition(s), with no introductory text.
"""


# Demo input
DEMO_INPUT = """On July 19, 2025, CoinDCX, one of India’s largest crypto exchanges, suffered a major hack resulting in a loss of about $44.2 million. The breach targeted an internal wallet used by CoinDCX for liquidity with a partner exchange and did not affect any customer funds, which remain safe in cold storage. Blockchain investigators like ZachXBT uncovered the hack before CoinDCX made it public, noting the hacker used a sophisticated server-side attack and laundered the funds by moving them from Solana to Ethereum and using Tornado Cash. CoinDCX has drawn some criticism for a 17-hour delay in disclosing the breach, especially since the compromised wallet was not part of the exchange’s published proof-of-reserves. In response, the company froze all impacted systems, engaged third-party security experts, and has covered the losses using its own treasury to ensure normal trading and withdrawals. CEO Sumit Gupta assured users that all customer holdings are safe, and the company has launched a bug bounty to strengthen future security while cooperating with authorities. This incident, the second major Indian exchange hack within a year, has intensified scrutiny on how centralized crypto platforms handle security and crisis management."""

st.title("Sanskrit News Generator")

# Input form (moved to top)
with st.form("input_form"):
    # Action buttons with icons above input box (Paste button removed)
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.form_submit_button("❌"):
            st.session_state.input_text = ""
    with col2:
        if st.form_submit_button("📄"):
            st.session_state.input_text = DEMO_INPUT

    input_text = st.text_area(
        "Enter a detailed news article for best results. Or click the button for sample text  **_Always proofread before publishing_**.",
        height=300,
        key="input_text"
    )
    
    # Display input character count
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
            model="gemini-2.5-pro",
            config=types.GenerateContentConfig(system_instruction=system_instruction),
            contents=input_text,
        )
        parts = api_response.candidates[0].content.parts
    except Exception as e:
        st.error("An error occurred!")
        st.exception(e)  # shows full traceback in the app

    return ' \n From: ' + api_response.model_version + ' \n API Key: ' + st.secrets['google_key'] + '\n ' + "".join(part.text for part in parts)

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
