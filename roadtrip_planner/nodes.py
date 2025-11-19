"""
All LangGraph nodes for the road trip planner.

This module contains all node functions that make up the planning workflow.
"""

from .state import RoadTripState, log_node_start, log_node_complete, log_node_error
from .models import RoadTripRequest, RouteSkeleton, DailyPlan
from .llm_clients import call_parser_model_sync, call_planner_model_sync, call_renderer_model_sync
from .tools import media_search_stub
from .config import config
from .logger import logger
from pydantic import BaseModel


# ============================================================================
# Node 1: Parse Request
# ============================================================================

def parse_request(state: RoadTripState) -> RoadTripState:
    """
    Parse the user's natural language query into a structured RoadTripRequest.
    """
    logger.node_start("parse_request")
    state = log_node_start(state, "parse_request")

    try:
        logger.step("Input", f'User query: "{state.user_query}"')
        
        # Build prompt for the parser model
        logger.step("Building prompt for LLM")
        prompt = f"""
Parse the following road trip request into structured data:

User Query: "{state.user_query}"

Extract:
- Origin (starting location)
- Destination (can be None if not specified or if it's a loop trip)
- Start date (if mentioned)
- Number of days (if mentioned)
- Maximum driving hours per day (if mentioned)
- User preferences for nature, city, and food (scale 0.0 to 1.0)
- Budget level (low/medium/high if mentioned)
- Language preference (en/zh if mentioned)

Infer reasonable values when information is implicit.

If a field is not mentioned and cannot be inferred, leave it as None.
""".strip()

        # Call the parser model to get structured output
        logger.step("Calling LLM parser model", f"Model: {config.PARSER_MODEL}")
        parsed_request = call_parser_model_sync(prompt, RoadTripRequest)
        
        logger.step("LLM response received")
        logger.output("Parsed origin", parsed_request.origin)
        logger.output("Parsed destination", parsed_request.destination or "Not specified")
        logger.output("Parsed days", str(parsed_request.num_days or "Not specified"))

        # Apply default values from config if needed
        logger.step("Applying default values")
        if parsed_request.max_drive_hours_per_day is None:
            parsed_request.max_drive_hours_per_day = config.DEFAULT_MAX_DRIVE_HOURS

        if parsed_request.num_days is None:
            parsed_request.num_days = config.DEFAULT_NUM_DAYS

        if parsed_request.budget_level is None:
            parsed_request.budget_level = config.DEFAULT_BUDGET_LEVEL

        if parsed_request.language is None:
            parsed_request.language = config.DEFAULT_LANGUAGE

        # Update state
        state.request = parsed_request
        
        logger.section("Final Parsed Request")
        logger.output("Origin", parsed_request.origin)
        logger.output("Destination", parsed_request.destination or "Same as origin (loop)")
        logger.output("Days", str(parsed_request.num_days))
        logger.output("Max drive hours/day", str(parsed_request.max_drive_hours_per_day))
        logger.output("Budget level", parsed_request.budget_level)
        logger.output("Preferences", 
                     f"Nature: {parsed_request.preferences.nature}, "
                     f"City: {parsed_request.preferences.city}, "
                     f"Food: {parsed_request.preferences.food}")

        # Log completion with details
        details = (
            f"Parsed request: {parsed_request.origin} -> {parsed_request.destination}, "
            f"{parsed_request.num_days} days"
        )
        state = log_node_complete(state, "parse_request", details)
        logger.node_complete("parse_request", details)

    except Exception as e:
        logger.node_error("parse_request", e)
        state = log_node_error(state, "parse_request", e)
        raise

    return state


# ============================================================================
# Node 2: Media Search
# ============================================================================

def media_search(state: RoadTripState) -> RoadTripState:
    """
    Search for relevant media items (from Xiaohongshu, Expedia, etc.) based on the request.
    """
    logger.node_start("media_search")
    state = log_node_start(state, "media_search")

    try:
        if not state.request:
            raise ValueError("Cannot perform media search without a parsed request")

        logger.step("Input", f"Searching for: {state.request.origin} -> {state.request.destination}")
        logger.step("User preferences", 
                   f"Nature: {state.request.preferences.nature}, "
                   f"City: {state.request.preferences.city}, "
                   f"Food: {state.request.preferences.food}")

        # Call media search stub (will be replaced with real API calls)
        logger.step("Calling media search tools (currently mock)")
        media_items = media_search_stub(state.request)

        # Update state
        state.media_items = media_items
        
        logger.section("Media Search Results")
        logger.step("Total items found", len(media_items))
        
        if media_items:
            logger.info("Top media items:")
            for i, item in enumerate(media_items[:5], 1):
                logger.output(f"  {i}. {item.title}", 
                            f"Source: {item.source}, Score: {item.score}, Location: {item.location_name}")

        # Log completion with details
        details = f"Found {len(media_items)} media items"
        state = log_node_complete(state, "media_search", details)
        logger.node_complete("media_search", details)

    except Exception as e:
        logger.node_error("media_search", e)
        state = log_node_error(state, "media_search", e)
        raise

    return state


# ============================================================================
# Node 3: Plan Route Skeleton
# ============================================================================

def plan_route_skeleton(state: RoadTripState) -> RoadTripState:
    """
    Generate a high-level route skeleton for the entire trip.
    """
    logger.node_start("plan_route_skeleton")
    state = log_node_start(state, "plan_route_skeleton")

    try:
        if not state.request:
            raise ValueError("Cannot plan route without a parsed request")
        
        logger.step("Input", f"{state.request.num_days} days, {len(state.media_items)} media items")
        logger.step("Route", f"{state.request.origin} -> {state.request.destination}")

        # Build context from media items
        media_context = "\n".join([
            f"- {item.title} ({item.location_name or 'Unknown'}) [score: {item.score}]"
            for item in state.media_items[:10]
        ])

        # Build prompt for route planning
        prompt = f"""
Plan a high-level route skeleton for this road trip:

Origin: {state.request.origin}
Destination: {state.request.destination or state.request.origin + " (loop trip)"}
Number of Days: {state.request.num_days}
Max Drive Hours/Day: {state.request.max_drive_hours_per_day}

User Preferences:
- Nature: {state.request.preferences.nature}
- City: {state.request.preferences.city}
- Food: {state.request.preferences.food}

Relevant Media/Attractions Found:
{media_context if media_context else "(No media items available)"}

Create a day-by-day route skeleton. For each day:
1. Specify start and end locations
2. List 2-4 candidate stops along the route
3. Ensure total driving time per day is under {state.request.max_drive_hours_per_day} hours
4. Balance driving with exploration time
5. Consider user preferences when selecting candidate stops

The route should flow logically and make geographic sense.
""".strip()

        # Call the planner model
        logger.step("Calling LLM planner model", f"Model: {config.PLANNER_MODEL}")
        route_skeleton = call_planner_model_sync(prompt, RouteSkeleton)
        logger.step("LLM response received")

        # Validate that we have the right number of days
        if len(route_skeleton.days) != state.request.num_days:
            print(f"Warning: Expected {state.request.num_days} days, got {len(route_skeleton.days)}")

        # Update state
        state.route_skeleton = route_skeleton
        
        logger.section("Route Skeleton Created")
        logger.step("Total days", len(route_skeleton.days))
        for day in route_skeleton.days:
            logger.output(f"Day {day.day_index}", 
                        f"{day.start_location} -> {day.end_location}")
            logger.info(f"   Candidate stops: {', '.join(day.candidate_stops)}")

        # Log completion with details
        details = f"Created route skeleton with {len(route_skeleton.days)} days"
        state = log_node_complete(state, "plan_route_skeleton", details)
        logger.node_complete("plan_route_skeleton", details)

    except Exception as e:
        logger.node_error("plan_route_skeleton", e)
        state = log_node_error(state, "plan_route_skeleton", e)
        raise

    return state


# ============================================================================
# Node 4: Select Daily POIs
# ============================================================================

def select_daily_pois(state: RoadTripState) -> RoadTripState:
    """
    Select specific POIs for each day based on the route skeleton.
    """
    logger.node_start("select_daily_pois")
    state = log_node_start(state, "select_daily_pois")

    try:
        if not state.request:
            raise ValueError("Cannot select POIs without a parsed request")
        if not state.route_skeleton:
            raise ValueError("Cannot select POIs without a route skeleton")
        
        logger.step("Input", f"{len(state.route_skeleton.days)} days, {len(state.media_items)} media items")
        logger.step("Task", "Selecting 3-5 POIs per day based on preferences")

        # Build context from route skeleton
        route_context = "\n".join([
            f"Day {day.day_index}: {day.start_location} -> {day.end_location}\n"
            f"  Candidate stops: {', '.join(day.candidate_stops)}"
            for day in state.route_skeleton.days
        ])

        # Build context from media items
        media_context = "\n".join([
            f"- {item.title} at {item.location_name or 'Unknown'} "
            f"[{item.category if hasattr(item, 'category') else 'N/A'}] "
            f"(score: {item.score}, tags: {', '.join(item.tags or [])})"
            for item in state.media_items
        ])

        # Build prompt for POI selection
        prompt = f"""
Select specific POIs (Points of Interest) for each day of the road trip.

Route Skeleton:
{route_context}

Available Media/Attractions:
{media_context if media_context else "(No media items available)"}

User Preferences:
- Nature: {state.request.preferences.nature}
- City: {state.request.preferences.city}
- Food: {state.request.preferences.food}

For each day, select 3-5 specific POIs that:
1. Are located along or near the day's route
2. Match the candidate stops from the route skeleton
3. Align with user preferences
4. Have high relevance scores (if available)
5. Provide a good mix of activities

For each POI, specify:
- name: The specific name of the place
- location_name: City/area where it's located
- category: "nature", "city", "food", or "other"
- score: Relevance score (0.0-1.0)
- description: Brief description (optional)

Also estimate the total driving time for each day.
""".strip()

        # Create a temporary model for the response
        class DailyPlanListResponse(BaseModel):
            plans: list[DailyPlan]

        logger.step("Calling LLM planner model", f"Model: {config.PLANNER_MODEL}")
        response = call_planner_model_sync(prompt, DailyPlanListResponse)
        daily_plans = response.plans
        logger.step("LLM response received")

        # Update state
        state.daily_plan = daily_plans
        
        logger.section("POIs Selected")
        total_pois = sum(len(plan.stops) for plan in daily_plans)
        logger.step("Total POIs", f"{total_pois} across {len(daily_plans)} days")
        
        for plan in daily_plans:
            logger.output(f"Day {plan.day_index}", f"{len(plan.stops)} stops")
            for poi in plan.stops:
                logger.info(f"   • {poi.name} ({poi.category}) - {poi.location_name}")

        # Log completion with details
        details = f"Selected {total_pois} POIs across {len(daily_plans)} days"
        state = log_node_complete(state, "select_daily_pois", details)
        logger.node_complete("select_daily_pois", details)

    except Exception as e:
        logger.node_error("select_daily_pois", e)
        state = log_node_error(state, "select_daily_pois", e)
        raise

    return state


# ============================================================================
# Node 5: Render Itinerary
# ============================================================================

def render_itinerary(state: RoadTripState) -> RoadTripState:
    """
    Convert the structured daily plans into a human-readable itinerary.
    """
    logger.node_start("render_itinerary")
    state = log_node_start(state, "render_itinerary")

    try:
        if not state.request:
            raise ValueError("Cannot render itinerary without a parsed request")
        if not state.daily_plan:
            raise ValueError("Cannot render itinerary without daily plans")
        
        logger.step("Input", f"{len(state.daily_plan)} days with POIs")
        logger.step("Language", state.request.language or "en")

        # Build structured Itinerary object
        total_drive_hours = sum(
            plan.estimated_drive_hours or 0.0
            for plan in state.daily_plan
        )

        from .models import Itinerary
        itinerary = Itinerary(
            days=state.daily_plan,
            summary=(
                f"{state.request.num_days}-day road trip from "
                f"{state.request.origin} to {state.request.destination or state.request.origin}"
            ),
            total_drive_hours=total_drive_hours
        )

        # Build prompt for rendering
        language = state.request.language or "en"
        language_instruction = (
            "in English" if language == "en"
            else "in Chinese (中文)" if language == "zh"
            else f"in {language}"
        )

        # Build daily summary
        daily_summary = "\n\n".join([
            f"Day {plan.day_index}: {plan.start_location} -> {plan.end_location}\n"
            f"Stops ({len(plan.stops)}):\n" +
            "\n".join([f"  - {poi.name} ({poi.category}): {poi.description or 'N/A'}"
                      for poi in plan.stops])
            for plan in state.daily_plan
        ])

        prompt = f"""
Convert this structured road trip itinerary into an engaging, human-readable description {language_instruction}:

Trip Summary:
{itinerary.summary}
Total Drive Time: {total_drive_hours:.1f} hours

Daily Plan:
{daily_summary}

Please create a narrative that:
1. Has a welcoming introduction
2. For each day, includes:
   - Day header with route
   - Driving time estimate
   - Detailed descriptions of each stop/POI
   - Practical tips or highlights
3. Uses emojis sparingly for visual appeal
4. Is engaging and makes the reader excited about the trip

Format the output in Markdown.
""".strip()

        # Call the renderer model
        logger.step("Calling LLM renderer model", f"Model: {config.RENDERER_MODEL}")
        itinerary_text = call_renderer_model_sync(prompt)
        logger.step("LLM response received")

        # Update state
        state.itinerary_text = itinerary_text
        
        logger.section("Itinerary Rendered")
        logger.step("Output length", f"{len(itinerary_text)} characters")
        logger.step("Language", language)
        logger.output("Preview (first 300 chars)", itinerary_text[:300])

        # Log completion with details
        details = f"Rendered itinerary with {len(state.daily_plan)} days in {language}"
        state = log_node_complete(state, "render_itinerary", details)
        logger.node_complete("render_itinerary", details)

    except Exception as e:
        logger.node_error("render_itinerary", e)
        state = log_node_error(state, "render_itinerary", e)
        raise

    return state