import logging
import os

from flask import jsonify, request
from openai import OpenAI

from . import ai_bp
from utils import add_cors_headers

ai_bp = add_cors_headers(ai_bp)


@ai_bp.route("/chat", methods=["POST"])
def chat():
    """
    Handles chat requests by sending a formatted prompt to the OpenAI API.
    """
    try:
        data = request.get_json()
        message = data.get("message")
        context_data = data.get("data")

        if not message or not context_data:
            return jsonify({"error": "Missing required fields"}), 400

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

        return jsonify({"response": response.choices[0].message.content})
    except Exception as e:
        logging.error(f"Error in AI chat: {str(e)}")
        return jsonify({"error": str(e)}), 500


@ai_bp.route("/ask", methods=["POST"])
def ask_question():
    """
    Receives a question from the user, generates a response using OpenAI,
    and returns the answer.
    """
    data = request.get_json()
    question = data.get("question")

    if not question:
        return jsonify({"error": "Question not provided"}), 400

    try:
        # This is where you would integrate with your OpenAI service
        # For now, we'll just return a dummy response
        answer = (
            "This is a dummy answer. In a real application, "
            "this would be a response from OpenAI."
        )
        return jsonify({"answer": answer})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
