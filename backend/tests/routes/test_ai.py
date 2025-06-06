from unittest.mock import patch


def test_chat(client):
    """
    Tests the /ai/chat endpoint.
    """
    with patch("routes.ai.ai_service.get_chat_completion") as mock_get_chat_completion:
        mock_get_chat_completion.return_value = "Test AI response"
        messages = [{"role": "user", "content": "Hello"}]
        response = client.post(
            "/api/ai/chat", json={"messages": messages, "year": 2023}
        )
        assert response.status_code == 200
        assert response.json == {"response": "Test AI response"}
        mock_get_chat_completion.assert_called_once_with(messages, 2023)


def test_chat_value_error(client):
    """
    Tests the /ai/chat endpoint for ValueError.
    """
    with patch("routes.ai.ai_service.get_chat_completion") as mock_get_chat_completion:
        mock_get_chat_completion.side_effect = ValueError("Invalid input")
        messages = [{"role": "user", "content": "Hello"}]
        response = client.post(
            "/api/ai/chat", json={"messages": messages, "year": 2023}
        )
        assert response.status_code == 400
        assert response.json == {"error": "Invalid input"}
