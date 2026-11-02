import os
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv
from google.genai.errors import APIError
from langchain_google_genai import ChatGoogleGenerativeAI
from streamlit.errors import StreamlitSecretNotFoundError

from faq_data import find_best_faq, load_faqs


load_dotenv(Path(__file__).with_name(".env"))

if not os.environ.get("GOOGLE_API_KEY") and os.environ.get("GEMINI_API_KEY"):
    os.environ["GOOGLE_API_KEY"] = os.environ["GEMINI_API_KEY"]


def get_api_key() -> str | None:
    """Return a Gemini key from environment variables or Streamlit secrets."""
    api_key = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")
    if api_key:
        return api_key

    try:
        return st.secrets.get("GOOGLE_API_KEY") or st.secrets.get("GEMINI_API_KEY")
    except StreamlitSecretNotFoundError:
        return None


def generate_answer(question: str, history: list[dict[str, str]], faqs: list[dict[str, str]]) -> str:
    api_key = get_api_key()
    if not api_key:
        return (
            "I couldn't find that in the FAQ. Add a Gemini key as "
            "`GOOGLE_API_KEY` or `GEMINI_API_KEY` to enable answers beyond the FAQ."
        )

    faq_context = "\n".join(
        f"Q: {faq['question']}\nA: {faq['answer']}" for faq in faqs
    )
    system_prompt = (
        "You are a helpful customer-support assistant. Answer clearly and briefly. "
        "Use the FAQ as the only source for company-specific policies. Never invent "
        "order details, refund eligibility, delivery dates, or actions you have taken. "
        "If the FAQ does not answer a company-specific question, say so and ask for "
        "the information needed or direct the customer to the support team. Do not "
        "request passwords, payment-card numbers, or authentication codes.\n\n"
        f"FAQ:\n{faq_context}"
    )
    messages: list[tuple[str, str]] = [("system", system_prompt)]
    messages.extend(
        (message["role"], message["content"])
        for message in history[-10:]
        if message["role"] in {"user", "assistant"}
    )
    messages.append(("human", question))

    model = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")
    response = ChatGoogleGenerativeAI(
        model=model,
        temperature=0.2,
        google_api_key=api_key,
    ).invoke(messages)
    return str(response.content).strip()


def main() -> None:
    st.set_page_config(page_title="Customer Support", page_icon="💬")
    st.title("Customer Support Assistant")
    st.caption("Ask a question about orders, delivery, returns, or support.")

    faqs = load_faqs()

    with st.sidebar:
        st.subheader("Frequently asked questions")
        for faq in faqs:
            with st.expander(faq["question"]):
                st.write(faq["answer"])
        st.divider()
        st.caption(
            "This assistant uses the FAQ for company policies and cannot access "
            "your order or account details."
        )

    if "messages" not in st.session_state:
        st.session_state.messages = []

    if not st.session_state.messages:
        with st.chat_message("assistant"):
            st.markdown(
                "Hi! I can help with common support questions. "
                "What would you like to know?"
            )

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if question := st.chat_input("Type your question"):
        st.session_state.messages.append({"role": "user", "content": question})
        with st.chat_message("user"):
            st.markdown(question)

        match = find_best_faq(question, faqs)
        try:
            answer = match["answer"] if match else generate_answer(
                question, st.session_state.messages[:-1], faqs
            )
        except APIError as error:
            st.error(f"Gemini could not answer right now: {error}")
            st.stop()

        st.session_state.messages.append({"role": "assistant", "content": answer})
        with st.chat_message("assistant"):
            st.markdown(answer)


if __name__ == "__main__":
    main()
