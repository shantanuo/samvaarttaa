import streamlit as st
from google import genai
from google.genai import types

client = genai.Client(api_key="AIzaSyDzgs5eDsMYrgSBTnJYWij_6qBW2OLj36g")

st.title("संवार्त्ता")
st.markdown(
    """
    ### Disclaimers: 
      * AI translation may contain errors or hallucinations. __*Always proofread*__ before publishing.
      * Generating the response *will* be slow. Please be patient!
      * Please note that this demo supports a limited number of requests and may be unavailable 
      if too many people use the service. Thank you for your understanding.
"""
)

system_instruction = """Rewrite this news article into classical Sanskrit without English punctuation 
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
    
    Provide just the translation without any other extra introductory text.
    """

with st.form("input_form"):
    input_text = st.text_area(
        "Enter a detailed news article for best results. "
        "To reiterate -  __*Always proofread*__ before publishing, "
        "as it might contain errors or hallucinations (i.e. made-up facts).",
        height="stretch",
    )
    submitted = st.form_submit_button("Submit")

if submitted:
    api_response = client.models.generate_content(
        model="gemini-2.5-pro",
        config=types.GenerateContentConfig(system_instruction=system_instruction),
        contents=input_text,
    )
    parts = api_response.candidates[0].content.parts
    response = "".join(part.text for part in parts)
    st.markdown(response)
