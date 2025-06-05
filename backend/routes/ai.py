import logging

from flask import jsonify, request

from services import ai_service
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

        response_content = ai_service.get_chat_completion(message, context_data)
        return jsonify({"response": response_content})

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logging.error(f"Error in AI chat: {e}")
        return jsonify({"error": "An error occurred during AI chat"}), 500


@ai_bp.route("/ask", methods=["POST"])
def ask_question():
    """
    Receives a question from the user, generates a response using OpenAI,
    and returns the answer.
    """
    try:
        data = request.get_json()
        question = data.get("question")
        answer = ai_service.get_dummy_answer(question)
        return jsonify({"answer": answer})

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logging.error(f"Error in ask_question: {e}")
        return jsonify({"error": "An error occurred while asking question"}), 500
