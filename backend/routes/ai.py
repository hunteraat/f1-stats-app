from flask import request, jsonify
import os
from openai import OpenAI
from . import ai_bp
from utils import add_cors_headers
import logging

ai_bp = add_cors_headers(ai_bp)

@ai_bp.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        message = data.get('message')
        context_data = data.get('data')

        if not message or not context_data:
            return jsonify({'error': 'Missing required fields'}), 400

        # Initialize OpenAI client
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        # Generate prompt
        prompt = f"""You are an F1 statistics assistant. You have access to the following data:

{context_data}

Please answer the following question based on this data:
{message}"""

        # Call OpenAI API
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "You are an F1 statistics assistant. Provide clear, concise answers based on the data provided. Refuse to answer questions that are not related to F1 statistics."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.7,
            max_tokens=500
        )

        return jsonify({"response": response.choices[0].message.content})
    except Exception as e:
        logging.error(f"Error in AI chat: {str(e)}")
        return jsonify({'error': str(e)}), 500 