import os
from openai import OpenAI


def get_chat_completion(message, context_data):
    """
    Generates a chat completion using the OpenAI API.
    """
    if not message or not context_data:
        raise ValueError("Missing required fields: message or context_data")

    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    prompt = (
        f"You are an F1 statistics assistant. You have access to the "
        f"following data:\n\n{context_data}\n\nPlease answer the "
        f"following question based on this data:\n{message}"
    )

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an F1 statistics assistant. Provide clear, "
                    "concise answers based on the data provided. Refuse "
                    "to answer questions that are not related to F1 statistics."
                ),
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.7,
        max_tokens=500,
    )

    return response.choices[0].message.content


def get_dummy_answer(question):
    """
    Returns a dummy answer for a given question.
    DEPRECATED or for testing purposes.
    """
    if not question:
        raise ValueError("Question not provided")

    # In a real application, this would be a more complex service call.
    # For now, it returns a simple, static string.
    return (
        "This is a dummy answer. In a real application, "
        "this would be a response from OpenAI."
    )
