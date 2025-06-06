from services import ai_service


def test_get_chat_completion(mocker):
    """
    Tests that the get_chat_completion function calls the OpenAI API
    with the correct parameters and returns the expected content.
    """
    # Mock the OpenAI client
    mock_openai_client = mocker.patch("services.ai_service.OpenAI")

    # Mock the response from the chat completions create method
    mock_response = mocker.MagicMock()
    mock_response.choices[0].message.content = "Test AI response"
    mock_openai_client.return_value.chat.completions.create.return_value = mock_response

    # Call the function with test data
    message = "Test message"
    context_data = "Test context"
    response = ai_service.get_chat_completion(message, context_data)

    # Assert the response is correct
    assert response == "Test AI response"

    # Assert that the OpenAI client was initialized
    mock_openai_client.assert_called_once()

    # Assert that the create method was called with the correct prompt structure
    mock_openai_client.return_value.chat.completions.create.assert_called_once()
    call_kwargs = (
        mock_openai_client.return_value.chat.completions.create.call_args.kwargs
    )
    sent_prompt = call_kwargs["messages"][1]["content"]
    assert message in sent_prompt
    assert context_data in sent_prompt


def test_get_dummy_answer():
    """
    Tests the get_dummy_answer function.
    """
    question = "What is the meaning of life?"
    answer = ai_service.get_dummy_answer(question)
    assert "This is a dummy answer" in answer
