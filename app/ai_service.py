import os

from dotenv import load_dotenv
from google import genai
from ddgs import DDGS


# --------------------------------
# LOAD ENVIRONMENT VARIABLES
# --------------------------------

load_dotenv()


# --------------------------------
# GEMINI CLIENT
# --------------------------------

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


# --------------------------------
# GEMINI MODEL
# --------------------------------

MODEL = "gemini-3.5-flash"


# --------------------------------
# WEB SEARCH
# --------------------------------

def search_web(query: str):

    try:

        with DDGS() as ddgs:

            results = list(
                ddgs.text(
                    query,
                    region="in-en",
                    safesearch="moderate",
                    max_results=5
                )
            )

        return results

    except Exception as error:

        print(f"Web search failed: {error}")

        return []


# --------------------------------
# FORMAT WEB RESULTS
# --------------------------------

def format_search_results(results):

    if not results:
        return "No web search results were found."

    formatted_results = []

    for index, result in enumerate(results, start=1):

        title = result.get("title", "")
        body = result.get("body", "")
        url = result.get("href", "")

        formatted_results.append(
            f"""
SOURCE {index}

Title:
{title}

URL:
{url}

Content:
{body}
"""
        )

    return "\n".join(formatted_results)


# --------------------------------
# ASK AI
# --------------------------------

def ask_ai(question: str, document_text: str):

    # --------------------------------
    # STEP 1: CHECK DOCUMENT
    # --------------------------------

    document_prompt = f"""
You are AskMyPDF AI.

Answer the user's question using ONLY the uploaded document.

UPLOADED DOCUMENT:
{document_text}

USER QUESTION:
{question}

Instructions:

- Check whether the document contains enough information.
- If the answer is available, provide the answer.
- If the answer is NOT available, respond with exactly:

NOT_FOUND_IN_DOCUMENT

- Do not use outside knowledge.
- Do not guess.
"""

    try:

        response = client.models.generate_content(
            model=MODEL,
            contents=document_prompt
        )

        document_answer = response.text.strip()

    except Exception as error:

        print(
            f"Document AI failed: {error}"
        )

        document_answer = "NOT_FOUND_IN_DOCUMENT"


    # --------------------------------
    # ANSWER FROM DOCUMENT
    # --------------------------------

    if "NOT_FOUND_IN_DOCUMENT" not in document_answer:

     return {
        "answer": (
            "📄 Answer based on uploaded document\n\n"
            + document_answer
        ),
        "source_type": "document",
        "sources": []
    }


    # --------------------------------
    # STEP 2: WEB SEARCH
    # --------------------------------

    print(
        f"Searching web for: {question}"
    )

    search_results = search_web(question)


    # --------------------------------
    # NO WEB RESULTS
    # --------------------------------

    if not search_results:

        return {
            "answer": (
                "I could not find the answer in the uploaded "
                "document, and web search did not return any "
                "useful results."
            ),
            "source_type": "none",
            "sources": []
        }


    # --------------------------------
    # FORMAT WEB RESULTS
    # --------------------------------

    web_information = format_search_results(
        search_results
    )


    # --------------------------------
    # STEP 3: GEMINI ANSWER
    # --------------------------------

    web_prompt = f"""
You are AskMyPDF AI.

The answer was not found in the uploaded document.

Use the web search results below to answer the user's question.

USER QUESTION:
{question}

WEB SEARCH RESULTS:
{web_information}

Instructions:

- Answer the user's question clearly.
- Use only the information provided in the web search results.
- Do not invent information.
- Prefer reliable sources.
- Keep the answer simple and easy to understand.
- If possible, mention the relevant source website.
- Do not say that you personally browsed the web.
"""

    try:

        response = client.models.generate_content(
            model=MODEL,
            contents=web_prompt
        )

        web_answer = response.text.strip()

    except Exception as error:

        print(
            f"Web answer generation failed: {error}"
        )

        web_answer = (
            "I found the following information from web search:\n\n"
            + web_information
        )


    # --------------------------------
    # CREATE SOURCE LIST
    # --------------------------------

    sources = []

    for result in search_results:

        title = result.get("title", "")
        url = result.get("href", "")

        if title and url:

            sources.append({
                "title": title,
                "url": url
            })


    # --------------------------------
    # RETURN ANSWER + SOURCES
    # --------------------------------

    return {
        "answer": (
            "🌐 Answer based on web information\n\n"
            + web_answer
        ),
        "source_type": "web",
        "sources": sources
    }


# --------------------------------
# DOCUMENT SUMMARY
# --------------------------------

def generate_summary(document_text: str):

    prompt = f"""
You are AskMyPDF AI.

Summarize the following uploaded document.

DOCUMENT:
{document_text}

Instructions:

- Give a clear and easy-to-understand summary.
- Focus on the main concepts and important information.
- Use simple language.
- Do not make up information.
- Use only information available in the document.
- Use bullet points where useful.
- Keep the summary concise but useful.
"""

    try:

        response = client.models.generate_content(
            model=MODEL,
            contents=prompt
        )

        return response.text

    except Exception as error:

        print(
            f"Summary generation failed: {error}"
        )

        return (
            "Gemini is temporarily unavailable. "
            "Please try generating the summary again."
        )


# --------------------------------
# IMPORTANT QUESTIONS
# --------------------------------

def generate_important_questions(document_text: str):

    prompt = f"""
You are AskMyPDF AI.

Analyze the following uploaded document and generate important
questions for exam preparation and revision.

DOCUMENT:
{document_text}

Instructions:

- Generate 10 important questions.
- Focus on the main concepts.
- Include important definitions.
- Include important explanations.
- Include important processes.
- Include important facts.
- Include a short and clear answer below each question.
- Use simple language.
- Do not make up information.
- Use only information available in the document.
- Number the questions from 1 to 10.

Use this format:

1. What is ...?

Answer:
...

2. Explain ...?

Answer:
...

Continue until you have generated 10 questions.
"""

    try:

        response = client.models.generate_content(
            model=MODEL,
            contents=prompt
        )

        return response.text

    except Exception as error:

        print(
            f"Important questions generation failed: {error}"
        )

        return (
            "Gemini is temporarily unavailable. "
            "Please try generating the questions again."
        )