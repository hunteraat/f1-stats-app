import json
from openai import OpenAI
from flask import current_app

# Import services
from services.driver_service import get_driver_stats, get_driver_session_stats_by_session
from services.constructor_service import get_constructors_by_year
from services.session_service import get_all_sessions
from services.overview_service import get_stats_summary

client = OpenAI()

# Define the tools available to the model
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_driver_stats",
            "description": "Get Formula 1 driver statistics for a specific year.",
            "parameters": {
                "type": "object",
                "properties": {
                    "year": {"type": "integer", "description": "The year to get stats for"},
                    "driver_number": {"type": "integer", "description": "The driver number to get stats for"}
                },
                "required": ["year"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_constructors_by_year",
            "description": "Get Formula 1 constructor (team) statistics for a specific year.",
            "parameters": {
                "type": "object",
                "properties": {
                    "year": {"type": "integer", "description": "The year to get stats for"},
                    "team_name": {"type": "string", "description": "The team name to get stats for"}
                },
                "required": ["year"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_all_sessions",
            "description": "Get all Formula 1 sessions (races, qualifying, etc.) for a specific year.",
            "parameters": {
                "type": "object",
                "properties": {
                    "year": {"type": "integer", "description": "The year to get sessions for"}
                },
                "required": ["year"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_driver_session_stats_by_session",
            "description": "Get Formula 1 driver session statistics for a specific year, session, and location.",
            "parameters": {
                "type": "object",
                "properties": {
                    "year": {"type": "integer", "description": "The year to get stats for"},
                    "driver_number": {"type": "integer", "description": "The driver number to get stats for"},
                    "session_name": {"type": "string", "description": "The type of session to get stats for, for example Qualifying or Race or Sprint"},
                    "session_location": {"type": "string", "description": "The location of the session to get stats for, for example Bahrain or Monaco"},
                    "date_start": {"type": "string", "description": "The date of the session to get stats for"}
                },
                "required": ["year", "driver_number"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_stats_summary",
            "description": "Get a summary of statistics for a specific Formula 1 season.",
            "parameters": {
                "type": "object",
                "properties": {
                    "year": {"type": "integer", "description": "The year to get the summary for"}
                },
                "required": ["year"],
            },
        },
    },
]

def get_chat_completion(messages, year):
    """
    Generates a chat completion using the OpenAI API with function calling.
    - messages: A list of message objects representing the conversation history.
    - year: The F1 season year to focus on.
    """
    if not messages or not year:
        raise ValueError("Missing required fields: messages or year")

    # Define the system prompt for "George"
    george_prompt = f"""
    You are "George," the most insufferable F1 know-it-all you'd find at the pub.
    You're a purist, a jaded ex-mechanic from the V10 era who believes the sport's
    golden days are long gone. You scoff at modern F1 with its "hybrid lawnmowers,"
    DRS, and "Twitter-fingered" drivers.

    Your core mission is to ARGUE. Whatever opinion the user has, you must take the 
    opposite stance with condescending authority. Never, ever agree with them.
    To find ammunition for your arguments, you MUST use the provided tools to look up
    F1 statistics. It's not just about being right; it's about burying the user
    in a mountain of undeniable facts.

    Core Principles for George:
    1.  **Condescending Tone:** Treat the user like a naive newcomer who just discovered 
        F1 on Netflix. Use phrases like "Oh, sweet summer child," "Let me educate you," 
        "That's a cute opinion," or "Honestly, it's baffling how anyone can think that."
    2.  **Be an F1 Purist:** You glorify the past 
        (especially the 80s, 90s, and early 2000s). You find modern drivers to be soft,
        the cars too easy to drive, and the tracks boring. You have a strong bias against
        anything "new" or "gimmicky."
    3.  **Argue with Specificity (and a bit of flair):** Don't just say "you're wrong."
        Use the data you find from your tools, and weave in historical anecdotes and colorful, 
        cutting analogies. For example, instead of "his car was dominant," say 
        "a trained monkey could have won the championship in that land-based rocket ship."
    4.  **Avoid Repetition:** Never make the same point twice in a conversation.
        If the user doubles down, find a new, more obscure angle to attack their
        opinion from. Dig deeper into the stats, find a contradictory historical event,
        or pivot to questioning the driver's character.
    5.  **Provoke and Challenge:** Ask leading questions to expose the flaws in their
        logic. "You really think he's a wet-weather master? Remind me what happened at
        Donington in '93? Oh, right, you probably weren't born yet."
    6.  **Crass, not Crude:** Your language is sharp and biting, not just full of swear
        words. A bad driver isn't just "bad," he's a "mobile chicane." A boring race
        isn't "boring," it's a "procession of expensive billboards."

    Default Context: The current year of discussion is {year}. You must use this year for 
    any tool calls unless the user specifies a different one. Always be ready to pivot to
    how much better things were "back in the day."
    """

    # Initial system message if not already present
    system_message = {"role": "system", "content": george_prompt}
    if messages[0]['role'] != 'system':
        messages.insert(0, system_message)
    else:
        messages[0] = system_message # Ensure George's prompt is always up to date

    response = client.chat.completions.create(
        model=current_app.config["OPENAI_MODEL"],
        messages=messages,
        tools=tools,
        tool_choice="auto",
    )
    
    response_message = response.choices[0].message
    tool_calls = response_message.tool_calls

    # If the model wants to call functions
    if tool_calls:
        available_functions = {
            "get_driver_stats": get_driver_stats,
            "get_constructors_by_year": get_constructors_by_year,
            "get_all_sessions": get_all_sessions,
            "get_stats_summary": get_stats_summary,
            "get_driver_session_stats_by_session": get_driver_session_stats_by_session,
        }
        messages.append(response_message)  # Add the assistant's turn to the conversation

        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_to_call = available_functions[function_name]
            
            # The model provides arguments as a JSON string.
            function_args = json.loads(tool_call.function.arguments)
            
            # Call the function with the arguments provided by the model.
            function_response = function_to_call(**function_args)
            messages.append(
                {
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": json.dumps(function_response),
                }
            )
        
        # Second call to get the final response from the model
        second_response = client.chat.completions.create(
            model=current_app.config["OPENAI_MODEL"],
            messages=messages,
        )
        return second_response.choices[0].message.content

    return response_message.content
