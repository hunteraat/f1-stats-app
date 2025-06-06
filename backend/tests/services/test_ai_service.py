import pytest
from flask import Flask
from unittest.mock import MagicMock, patch
from services import ai_service

@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    app = Flask(__name__)
    app.config.update({
        "TESTING": True,
        "OPENAI_MODEL": "gpt-test",
    })
    yield app

def test_get_chat_completion_direct_response(app):
    """
    Tests get_chat_completion when the model returns a direct response.
    """
    with app.app_context():
        messages = [{"role": "user", "content": "Lewis Hamilton is the GOAT."}]
        year = 2024

        with patch('services.ai_service.client') as mock_client:
            # Mock OpenAI response
            mock_response = MagicMock()
            mock_response.choices[0].message.content = "The GOAT? Please. He had a rocket ship for a car."
            mock_response.choices[0].message.tool_calls = None
            mock_client.chat.completions.create.return_value = mock_response

            response = ai_service.get_chat_completion(messages, year)

            assert response == "The GOAT? Please. He had a rocket ship for a car."
            mock_client.chat.completions.create.assert_called_once()
            called_args, called_kwargs = mock_client.chat.completions.create.call_args
            assert called_kwargs['model'] == 'gpt-test'
            assert called_kwargs['messages'][-1]['content'] == "Lewis Hamilton is the GOAT."

@patch('services.ai_service.get_driver_stats')
def test_get_chat_completion_with_tool_call(mock_get_driver_stats, app):
    """
    Tests get_chat_completion when the model requests a tool call.
    """
    with app.app_context():
        messages = [{"role": "user", "content": "Verstappen wasn't even that good in 2023."}]
        year = 2023

        # Mock the service function
        mock_get_driver_stats.return_value = {"driver": "Max Verstappen", "wins": 19, "points": 575}

        with patch('services.ai_service.client') as mock_client:
            # Mock first OpenAI response (with tool call)
            mock_tool_call_response = MagicMock()
            tool_call = MagicMock()
            tool_call.id = "call_123"
            tool_call.function.name = "get_driver_stats"
            # The model asks for stats for a specific driver
            tool_call.function.arguments = '{"year": 2023, "driver_number": 1}'
            mock_tool_call_response.choices[0].message.tool_calls = [tool_call]
            
            # Mock second OpenAI response (final answer)
            mock_final_response = MagicMock()
            mock_final_response.choices[0].message.content = "Not that good? He won 19 races. Are we watching the same sport?"

            # Set the side_effect for multiple calls
            mock_client.chat.completions.create.side_effect = [
                mock_tool_call_response,
                mock_final_response
            ]

            response = ai_service.get_chat_completion(messages, year)

            assert response == "Not that good? He won 19 races. Are we watching the same sport?"
            assert mock_client.chat.completions.create.call_count == 2
            # Assert that our service function was called with the arguments from the model
            mock_get_driver_stats.assert_called_once_with(year=2023, driver_number=1)

            # Check the messages sent in the second call
            _, second_call_kwargs = mock_client.chat.completions.create.call_args
            last_message = second_call_kwargs['messages'][-1]
            assert last_message['role'] == 'tool'
            assert last_message['tool_call_id'] == "call_123"
            assert '"wins": 19' in last_message['content']
