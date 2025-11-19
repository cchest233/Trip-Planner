"""
LLM client abstraction layer using OpenAI SDK.

Provides typed interfaces for calling different LLM models with structured output.
Supports OpenAI and OpenAI-compatible APIs (like Silicon Flow).
Includes support for function calling / tool use.
"""

import json
from typing import Type, TypeVar, List, Dict, Any, Optional, Callable
from pydantic import BaseModel
from openai import OpenAI

from .config import config

T = TypeVar("T", bound=BaseModel)


class LLMClientError(Exception):
    """Base exception for LLM client errors."""
    pass


def _get_openai_client() -> OpenAI:
    """
    Create an OpenAI client instance with configuration.
    
    Supports both OpenAI and Silicon Flow (OpenAI-compatible) endpoints.

    Returns:
        Configured OpenAI client instance
    """
    if config.OPENAI_BASE_URL:
        # Custom endpoint (e.g., Silicon Flow)
        return OpenAI(
            api_key=config.OPENAI_API_KEY,
            base_url=config.OPENAI_BASE_URL
        )
    else:
        # Default OpenAI endpoint
        return OpenAI(api_key=config.OPENAI_API_KEY)


def call_parser_model(
    prompt: str,
    output_model: Type[T],
    temperature: float | None = None
) -> T:
    """
    Call the parser model to extract structured data from natural language.

    Args:
        prompt: The prompt to send to the model
        output_model: Pydantic model class for structured output
        temperature: Optional temperature override (default from config)

    Returns:
        Parsed instance of output_model

    Raises:
        LLMClientError: If the model call fails

    Example:
        >>> from .models import RoadTripRequest
        >>> request = call_parser_model(
        ...     "I want to drive from SF to LA in 3 days",
        ...     RoadTripRequest
        ... )
    """
    try:
        client = _get_openai_client()
        
        # Build system prompt
        system_prompt = (
            "You are an expert travel planner assistant. "
            "Extract structured information from user queries about road trips. "
            "Be thorough and infer reasonable defaults when information is missing. "
            f"You must respond with valid JSON matching this schema: {output_model.model_json_schema()}"
        )
        
        # Call the API with JSON mode
        response = client.chat.completions.create(
            model=config.PARSER_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=temperature or config.DEFAULT_TEMPERATURE,
            response_format={"type": "json_object"}
        )
        
        # Parse the response
        content = response.choices[0].message.content
        data = json.loads(content)
        
        # Validate with Pydantic
        return output_model.model_validate(data)

    except Exception as e:
        raise LLMClientError(f"Parser model call failed: {str(e)}") from e


def call_planner_model(
    prompt: str,
    output_model: Type[T],
    temperature: float | None = None
) -> T:
    """
    Call the planner model to generate route plans and select POIs.

    Args:
        prompt: The prompt to send to the model
        output_model: Pydantic model class for structured output
        temperature: Optional temperature override (default from config)

    Returns:
        Parsed instance of output_model

    Raises:
        LLMClientError: If the model call fails

    Example:
        >>> from .models import RouteSkeleton
        >>> skeleton = call_planner_model(
        ...     "Plan a 3-day route from SF to LA...",
        ...     RouteSkeleton
        ... )
    """
    try:
        client = _get_openai_client()
        
        # Build system prompt
        system_prompt = (
            "You are an expert road trip planner. "
            "Plan optimal routes considering driving time, scenery, and user preferences. "
            "Recommend popular and high-quality points of interest. "
            "Balance driving time with exploration time. "
            f"You must respond with valid JSON matching this schema: {output_model.model_json_schema()}"
        )
        
        # Call the API with JSON mode
        response = client.chat.completions.create(
            model=config.PLANNER_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=temperature or config.DEFAULT_TEMPERATURE,
            response_format={"type": "json_object"}
        )
        
        # Parse the response
        content = response.choices[0].message.content
        data = json.loads(content)
        
        # Validate with Pydantic
        return output_model.model_validate(data)

    except Exception as e:
        raise LLMClientError(f"Planner model call failed: {str(e)}") from e


def call_renderer_model(
    prompt: str,
    temperature: float | None = None
) -> str:
    """
    Call the renderer model to generate human-readable text output.

    Args:
        prompt: The prompt to send to the model
        temperature: Optional temperature override (default from config)

    Returns:
        Generated text response

    Raises:
        LLMClientError: If the model call fails

    Example:
        >>> text = call_renderer_model(
        ...     "Convert this itinerary to natural language: ..."
        ... )
    """
    try:
        client = _get_openai_client()
        
        # Build system prompt
        system_prompt = (
            "You are a travel writing expert. "
            "Convert structured itineraries into engaging, readable descriptions. "
            "Use clear formatting and highlight key attractions and experiences. "
            "Be concise but informative."
        )
        
        # Call the API (no JSON mode for text output)
        response = client.chat.completions.create(
            model=config.RENDERER_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=temperature or config.DEFAULT_TEMPERATURE,
        )
        
        # Return the text response
        return response.choices[0].message.content

    except Exception as e:
        raise LLMClientError(f"Renderer model call failed: {str(e)}") from e


# Keep the _sync naming for backward compatibility
call_parser_model_sync = call_parser_model
call_planner_model_sync = call_planner_model
call_renderer_model_sync = call_renderer_model


# ============================================================================
# Function Calling Support
# ============================================================================

def call_llm_with_tools(
    prompt: str,
    tools: List[Dict[str, Any]],
    tool_functions: Dict[str, Callable],
    model: Optional[str] = None,
    temperature: Optional[float] = None,
    max_iterations: int = 5
) -> Dict[str, Any]:
    """
    Call LLM with function calling support.
    
    The LLM can decide to call tools, and this function will execute them
    and feed the results back to the LLM until it provides a final answer.
    
    Args:
        prompt: The user prompt/question
        tools: List of tool definitions in OpenAI format
        tool_functions: Dict mapping tool names to actual functions
        model: Model name (defaults to PLANNER_MODEL)
        temperature: Temperature setting
        max_iterations: Maximum number of tool call iterations
    
    Returns:
        Dict with 'content' (final answer) and 'tool_calls' (list of executed tools)
    
    Example:
        >>> from .tools import TOOL_DEFINITIONS, TOOL_FUNCTIONS
        >>> result = call_llm_with_tools(
        ...     "How long does it take to drive from SF to LA?",
        ...     TOOL_DEFINITIONS,
        ...     TOOL_FUNCTIONS
        ... )
        >>> print(result['content'])
    """
    try:
        client = _get_openai_client()
        model_name = model or config.PLANNER_MODEL
        temp = temperature or config.DEFAULT_TEMPERATURE
        
        messages = [
            {
                "role": "system",
                "content": "You are a helpful travel planning assistant with access to tools for calculating routes, finding places, and gathering travel information. Use the tools when needed to provide accurate information."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
        
        executed_tools = []
        
        for iteration in range(max_iterations):
            # Call the LLM
            response = client.chat.completions.create(
                model=model_name,
                messages=messages,
                tools=tools,
                tool_choice="auto",
                temperature=temp
            )
            
            message = response.choices[0].message
            
            # Check if the model wants to call tools
            if not message.tool_calls:
                # No tool calls, return the final answer
                return {
                    "content": message.content,
                    "tool_calls": executed_tools,
                    "iterations": iteration + 1
                }
            
            # Add assistant message to history
            messages.append({
                "role": "assistant",
                "content": message.content,
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": tc.type,
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments
                        }
                    }
                    for tc in message.tool_calls
                ]
            })
            
            # Execute each tool call
            for tool_call in message.tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)
                
                # Get the actual function
                if function_name not in tool_functions:
                    result = {"error": f"Unknown function: {function_name}"}
                else:
                    try:
                        # Call the function
                        result = tool_functions[function_name](**function_args)
                    except Exception as e:
                        result = {"error": str(e)}
                
                # Record the execution
                executed_tools.append({
                    "name": function_name,
                    "arguments": function_args,
                    "result": result
                })
                
                # Add tool result to messages
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(result)
                })
        
        # Max iterations reached
        return {
            "content": "I've reached the maximum number of tool calls. Please try a simpler query.",
            "tool_calls": executed_tools,
            "iterations": max_iterations
        }
    
    except Exception as e:
        raise LLMClientError(f"LLM with tools call failed: {str(e)}") from e


def call_planner_model_with_tools(
    prompt: str,
    output_model: Type[T],
    tools: Optional[List[Dict[str, Any]]] = None,
    tool_functions: Optional[Dict[str, Callable]] = None,
    temperature: Optional[float] = None
) -> T:
    """
    Call planner model with optional tool support, then return structured output.
    
    This combines function calling with structured output:
    1. LLM can call tools to gather information
    2. After tool calls complete, parse final response into structured format
    
    Args:
        prompt: The prompt to send
        output_model: Pydantic model for final structured output
        tools: Optional tool definitions
        tool_functions: Optional tool function mapping
        temperature: Temperature setting
    
    Returns:
        Parsed instance of output_model
    
    Example:
        >>> from .models import RouteSkeleton
        >>> from .tools import TOOL_DEFINITIONS, TOOL_FUNCTIONS
        >>> skeleton = call_planner_model_with_tools(
        ...     "Plan a route from SF to LA with exact distances",
        ...     RouteSkeleton,
        ...     TOOL_DEFINITIONS,
        ...     TOOL_FUNCTIONS
        ... )
    """
    if tools and tool_functions:
        # First, let LLM gather information using tools
        tool_result = call_llm_with_tools(
            prompt=prompt,
            tools=tools,
            tool_functions=tool_functions,
            model=config.PLANNER_MODEL,
            temperature=temperature
        )
        
        # Now ask for structured output based on gathered information
        enhanced_prompt = f"""
{prompt}

Based on the information gathered:
{tool_result['content']}

Tool calls made:
{json.dumps(tool_result['tool_calls'], indent=2)}

Please provide your response in the required JSON format.
"""
        
        return call_planner_model(enhanced_prompt, output_model, temperature)
    else:
        # No tools, use standard planner call
        return call_planner_model(prompt, output_model, temperature)
