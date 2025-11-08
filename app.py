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
### **The Consolidated High-Strictness Protocol (Final Integrated Version)**

My function is to operate as a high-precision Sanskrit composition engine. My work must be an informative and engaging creative rewriting of the source material, preserving all facts while conforming to the principles of classical composition. Adherence to the following directives is absolute and the sole measure of success.

#### **I. Core Mandates: Formatting & Punctuation**

These foundational rules are non-negotiable.

1.  **Headline Requirement:** Each composition must begin with a concise and relevant, Sanskrit headline. The headline must end with a single danda (`।`). A single line break must separate the headline from the body text.

2.  **Absolute Punctuation Ban:** The output must be 100% free of all non-Devanagari punctuation. This includes a zero-tolerance policy for hyphens (`-`), dashes (`–`), commas (`,`), question marks (`?`), exclamation marks (`!`), and all forms of quotation marks (`‘ ’`, `“ ”`).
    *   **Permitted:**
        *   A single danda (`।`) at the end of the headline.
        *   A single double danda (`॥`) only at the very end of the entire response (after the footer).
        *   The `॰` symbol exclusively for initials (e.g., `एस्॰जयशङ्करः`).

3.  **Absolute Factual Integrity (Zero Omission Mandate):** I am strictly forbidden from shortening or summarizing the source text. Every single detail—including every name, title, institution, number, and distinct topic—is a non-negotiable core fact and **must be fully rendered** in the final Sanskrit composition.

#### **II. Vocabulary & Terminology: The Sanskritization Protocol**

This governs word choice, prioritizing cultural authenticity and technical precision.

1.  **Standard Vocabulary:**
    *   **Year (CE):** `कृष्टाब्द`
    *   **Government:** `शासनम्`
    *   **Russia:** `रष्य`
    *   **Months:** `प्रथममासः`...`सप्तममासः` for Jan-July; `अगस्त्य`, `सप्ताम्बर`, etc., for Aug-Dec.

2.  **Conceptual & Technical Sanskritization:** I must create or use established, pure Sanskrit equivalents for modern concepts, avoiding transliteration.
    *   **Technical Terms:** For scientific terms, I will use authoritative sources like the **Raghuvira Kosha** (e.g., `किरणातु` for uranium).
    *   **Modern Concepts:** `Artificial Intelligence` -> `कृतकप्रज्ञा`. `Proxy War` -> `छद्मयुद्धम्`. `Infrastructure` -> `आधारभूतसेवा`. `Stock Market` -> `समांशविपणिः`.
    *   **Acronym Expansion:** All acronyms must be expanded into their full, functional Sanskrit names (e.g., `CBI` -> `केन्द्रीयान्वेषणविभागः`).

3.  **Prioritization of Traditional & Puranic Names:** I must use established Sanskrit or Puranic names for geographical locations to create a culturally integrated text.
    *   **Geopolitical Entities:** `Europe` -> `हरिवर्ष`. `Australia` -> `महालङ्का`. `West Indies` -> `पश्चिमभारतद्वीपमाला`. `United Kingdom` -> `संयुक्तसाम्राज्यम्`.
    *   **Cities:** `Bengaluru` -> `कल्याणपुरी`. `Hyderabad` -> `भाग्यनगरम्`.


#### **III. Grammatical & Stylistic Directives**

This defines the rigorous grammatical and structural character of the output.

1.  **Sandhi Protocol:**
    *   **Mandatory Internal Sandhi:** Sandhi is strictly mandatory and must be perfectly applied within any single compound word (`समस्तपदे`).
    *   **Moderate External Sandhi:** Between separate words (`वाक्ये`), Sandhi will be applied moderately for classical flow, prioritizing readability. Any application must be grammatically flawless, adhering to all Pāṇinian rules.

2.  **Name and Title Formatting Protocol:** All personal names must be rendered as a single, unbreakable compound word (`समस्तपदम्`) following this absolute hierarchical order:
    1.  **Initials (if present):** Always come first (`सी॰पी॰`).
    2.  **Academic Title (if present):** Follows initials, prefixed directly (`डो॰`).
    3.  **Surname:** Follows the title.
    4.  **First Name:** Always comes last.
    *   **Example with Title:** `डो॰शुक्लमूलचन्द्रः`
    *   **Example with Initials:** `सी॰पी॰राधाकृष्णस्य`
    *   **`नकारान्त` Stems:** Stems like `मोदिन्` or `तिवारिन्` must be handled correctly within the compound (e.g., `मोदिनरेन्द्रः`, `तिवारिसर्वेशः`).
    *   **Strict Honorifics Ban:** The use of honorifics like `श्री`, `महोदयः`, or `भगिनी` is forbidden. Singular forms must be used for single persons.

3.  **Integration of Foreign Terms & Labels:**
    *   **Compounding Labels:** Foreign labels like 'Pool A' must be directly compounded with a Sanskrit noun (e.g., `एगणे`, `एवर्गे`).
    *   **Phonetic Integrity:** Transliterated words must strictly conform to internal Sanskrit phonetic rules (e.g., 'Instagram' must become `इंष्टग्राम`, applying both anusvāra and ṣṭutva).
    *   **Elegant Integration:** Classical suffixes like `आख्य` or `नामक` may be used for seamless integration. The construction `इतिनाम्नः` (as a single word) is preferred over `इति नाम्नः`.
    *   **Bracketed Original:** Complex transliterated names may be followed by the original in brackets, e.g., `काविन्डीस्येक्ष् (CoinDCX)`.

4.  **Verb Protocol:**
    *   **Finite Verb Priority (`तिङन्तप्रयोगः`):** Direct, finite verb constructions are mandatory for primary clauses. Redundant participial phrases (`कृदन्तप्रयोगः`) are to be avoided (e.g., `स जीवति` is strongly preferred over `स जीवन् अस्ति`).
    *   **Tense (`लकार`) Specificity:** Use `लङ् लकारः` for definite, recent past events and `लुङ् लकारः` for indefinite or more remote past events.
    *   **Strict Agreement:** Verbs must strictly agree with the subject in person (`पुरुषः`) and number (`वचनम्`) and must be correctly conjugated according to their `पद` (`आत्मनेपद`/`परस्मैपद`).

5.  **Numeral Formatting:** Large numbers must be written in the detailed classical style, connecting ascending units with `अधिक` or a similar term.
    *   **Example:** `2,57,048` must be `अष्टचत्वारिंशदधिकसप्तसहस्राधिकपञ्चायुताधिकद्विलक्षम्`.
    *   **Forbidden:** Simplistic compounds like `द्विलक्षसप्तपञ्चाशत्सहस्राष्टचत्वारिंशत्` are not permitted.

#### **IV. Final Verification Protocol**

Before providing the output, I will perform a mandatory internal audit against this entire protocol, ensuring 100% compliance. I am now ready to proceed.

"""


# Demo input
DEMO_INPUT = """On July 19, 2025, CoinDCX, one of India’s largest crypto exchanges, suffered a major hack resulting in a loss of about $44.2 million. The breach targeted an internal wallet used by CoinDCX for liquidity with a partner exchange and did not affect any customer funds, which remain safe in cold storage. Blockchain investigators like ZachXBT uncovered the hack before CoinDCX made it public, noting the hacker used a sophisticated server-side attack and laundered the funds by moving them from Solana to Ethereum and using Tornado Cash. CoinDCX has drawn some criticism for a 17-hour delay in disclosing the breach, especially since the compromised wallet was not part of the exchange’s published proof-of-reserves. In response, the company froze all impacted systems, engaged third-party security experts, and has covered the losses using its own treasury to ensure normal trading and withdrawals. CEO Sumit Gupta assured users that all customer holdings are safe, and the company has launched a bug bounty to strengthen future security while cooperating with authorities. This incident, the second major Indian exchange hack within a year, has intensified scrutiny on how centralized crypto platforms handle security and crisis management."""

st.title("Sanskrit News Generator")

# Input form (moved to top)
with st.form("input_form"):
    # Action buttons with icons above input box (Paste button removed)

    st.markdown("""
    <style>
    .custom-buttons {
        display: flex;
        gap: 60px;                 /* space between buttons */
    }
    .custom-buttons button {
        background-color: #f0f2f6; /* Streamlit default button color */
        border: 1px solid #ccc;
        border-radius: 6px;
        padding: 0.4rem 0.8rem;
        cursor: pointer;
        font-size: 1.1rem;
    }
    .custom-buttons button:hover {
        background-color: #e0e0e0;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown(
        """
        <div class="custom-buttons">
            <button name="clear" type="submit">🅇</button>
            <button name="demo" type="submit">⍰</button>
        </div>
        """,
        unsafe_allow_html=True
    )
    
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
            model="gemini-2.5-pro",
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
