from unittest.mock import patch


def test_chat(client):
    """
    Tests the /ai/chat endpoint.
    """
    with patch("routes.ai.ai_service.get_chat_completion") as mock_get_chat_completion:
        mock_get_chat_completion.return_value = "Test AI response"
        response = client.post(
            "/api/ai/chat", json={"message": "Hello", "data": "Context"}
        )
        assert response.status_code == 200
        assert response.json == {"response": "Test AI response"}
        mock_get_chat_completion.assert_called_once_with("Hello", "Context")


def test_ask_question(client):
    """
    Tests the /ai/ask endpoint.
    """
    with patch("routes.ai.ai_service.get_dummy_answer") as mock_get_dummy_answer:
        mock_get_dummy_answer.return_value = "This is a dummy answer."
        response = client.post("/api/ai/ask", json={"question": "What is F1?"})
        assert response.status_code == 200
        assert response.json == {"answer": "This is a dummy answer."}
        mock_get_dummy_answer.assert_called_once_with("What is F1?")


def test_chat_value_error(client):
    """
    Tests the /ai/chat endpoint for ValueError.
    """
    with patch("routes.ai.ai_service.get_chat_completion") as mock_get_chat_completion:
        mock_get_chat_completion.side_effect = ValueError("Invalid input")
        response = client.post(
            "/api/ai/chat", json={"message": "Hello", "data": "Context"}
        )
        assert response.status_code == 400
        assert response.json == {"error": "Invalid input"}
