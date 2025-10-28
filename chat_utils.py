from euriai.langchain import create_chat_model

def get_chat_model(api_key: str):
    """Initialize and return the EURI chat model."""
    chat_model = create_chat_model(
        api_key=api_key,
        model="llama-3.1-8b-instant",
        temperature=0.7
    )
    return chat_model


def ask_chat_model(chat_model, prompt: str):
    """Send a prompt to the chat model and return its text response."""
    response = chat_model.invoke(prompt)
    return response.content if hasattr(response, "content") else str(response)
