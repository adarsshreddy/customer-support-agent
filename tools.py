from langchain.tools import tool

from faq_data import find_best_faq, load_faqs


@tool
def search_faq(query: str) -> str:
    """Search the customer-support FAQ for a relevant answer."""
    faq = find_best_faq(query, load_faqs())
    if faq is None:
        return "No relevant answer was found in the FAQ knowledge base."
    return f"Question: {faq['question']}\nAnswer: {faq['answer']}"


if __name__ == "__main__":
    print(search_faq.invoke({"query": "How can I track my order?"}))
