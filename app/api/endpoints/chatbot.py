from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
from app.services.knowledge_base import KnowledgeBase
from app.services.state_manager import StateManager, ConversationState, StateContext
from app.core.config import settings # Import settings to access city list

router = APIRouter()
kb = KnowledgeBase()
state_manager = StateManager()

class ChatRequest(BaseModel):
    message: str
    session_id: str
    current_state: Optional[str] = None # Accept current state from frontend

class ChatResponse(BaseModel):
    response: str
    state: str
    options: Optional[Dict[str, Any]] = None

# In-memory session storage (replace with proper database in production)
sessions: Dict[str, StateContext] = {}

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        # Get or create session context
        context = sessions.get(request.session_id)
        if not context:
            # Use state from frontend if available and valid, otherwise default to initial
            initial_state = ConversationState(request.current_state) if request.current_state in ConversationState.__members__.values() else ConversationState.INITIAL_GREETING
            context = StateContext(current_state=initial_state)
            sessions[request.session_id] = context
        else:
            # Update context with the state from the frontend if provided and valid
            if request.current_state and request.current_state in ConversationState.__members__.values():
                 context.current_state = ConversationState(request.current_state)
            # If frontend state is invalid or not provided, keep the existing state in the context

        # Process user input
        user_input = request.message.lower()
        
        # --- Simplified State Transition and Response Logic --- #
        next_state = context.current_state # Start by assuming state doesn't change
        response = "I didn't understand that. Can you please rephrase?"
        options = None

        if context.current_state == ConversationState.INITIAL_GREETING:
            # Any input after initial greeting moves to city selection
            next_state = ConversationState.CITY_SELECTION
            response = "Welcome to Barbeque Nation! How can I help you today? Please select your city."
            options = {"cities": list(settings.CITIES.keys())} # Use city names from settings

        elif context.current_state == ConversationState.CITY_SELECTION:
            # After city selection, validate and capture the city, then move to restaurant selection
            selected_city_lower = user_input # user_input is already lower case
            # Check if the entered city is valid (case-insensitive comparison)
            if selected_city_lower in settings.CITIES.keys(): 
                 context.city = selected_city_lower.capitalize() # Store capitalized version in context
                 next_state = ConversationState.RESTAURANT_SELECTION
                 # No response generated here, will be generated in the next block based on next_state
            else:
                 # Stay in CITY_SELECTION if city is invalid and ask again
                 response = f"Sorry, I don't recognize that city. Please select a city from the options."
                 options = {"cities": list(settings.CITIES.keys())}
                 # next_state remains CITY_SELECTION, response and options set above
                 context.current_state = next_state # Update state for response generation
                 return ChatResponse(
                     response=response,
                     state=context.current_state.value,
                     options=options
                 )
        
        elif context.current_state == ConversationState.RESTAURANT_SELECTION:
             # Handle input after listing locations and actions.
             # Check if user input matches a location or a next action (Menu, Book, FAQ)
             recognized_input = user_input.lower()
             locations = settings.CITIES.get(context.city, [])
             location_names_lower = [loc.lower() for loc in locations]

             if recognized_input in location_names_lower:
                  # User selected a location
                  context.restaurant = f"Barbeque Nation - {context.city}" # Use city-based restaurant name for KB lookup
                  context.query_type = "Location_Info" # Indicate query is about a location
                  next_state = ConversationState.QUERY_TYPE # Move to query type
                  # Response will be generated in the next block based on next_state and query_type

             elif "menu" in recognized_input:
                  # User selected Menu
                  context.restaurant = f"Barbeque Nation - {context.city}" # Use city-based restaurant name for KB lookup
                  context.query_type = "Menu"
                  next_state = ConversationState.QUERY_TYPE # Move to query type
                  # Response will be generated in the next block

             elif "book table" in recognized_input or "booking" in recognized_input:
                  # User selected Book Table
                  context.query_type = "Booking"
                  next_state = ConversationState.BOOKING_COLLECTION # Move to booking collection
                   # Response will be generated in the next block

             elif "faqs" in recognized_input or "faq" in recognized_input:
                  # User selected FAQs
                  context.restaurant = f"Barbeque Nation - {context.city}" # Use city-based restaurant name for KB lookup
                  context.query_type = "FAQs"
                  next_state = ConversationState.QUERY_TYPE # Move to query type
                   # Response will be generated in the next block

             else:
                  # Input not recognized in this state, repeat the prompt
                  response = "I didn't understand that. Please select a location or one of the actions (Menu, Book Table, FAQs)."
                  options = {"locations": locations, "next_actions": ["Menu", "Book Table", "FAQs"]}
                  # next_state remains RESTAURANT_SELECTION, response and options set above
                  context.current_state = next_state # Update state for response generation
                  return ChatResponse(
                     response=response,
                     state=context.current_state.value,
                     options=options
                  )
        
        # Update the context with the determined next state *before* generating the response
        context.current_state = next_state

        # --- Generate response based on the NEW state and Context --- #

        if context.current_state == ConversationState.INITIAL_GREETING:
             # This state should ideally only happen on the very first message
             # and immediately transition to CITY_SELECTION as handled above.
             # A fallback response if somehow we stay here:
            response = "Welcome to Barbeque Nation! How can I help you today? Please select your city."
            options = {"cities": list(settings.CITIES.keys())} 

        elif context.current_state == ConversationState.CITY_SELECTION:
            # We transitioned into this state, ask for the city.
            response = "Please select a city (Delhi or Bangalore):"
            options = {"cities": list(settings.CITIES.keys())} 

        elif context.current_state == ConversationState.RESTAURANT_SELECTION:
            # We transitioned into this state after capturing the city.
            # List the locations for the captured city and available actions.
            locations = settings.CITIES.get(context.city, []) # Get locations from settings
            if locations:
                 response = f"Here are the locations in {context.city}:\n" + "\n".join([f"- {loc}" for loc in locations]) + "\n\nPlease select a location or tell me what you'd like to do (e.g., view menu, book a table, FAQs)."
                 options = {"locations": locations, "next_actions": ["Menu", "Book Table", "FAQs"]}
            else:
                 # Fallback if no locations found (shouldn't happen with valid city)
                 response = f"Sorry, no locations found for {context.city}. Please select another city."
                 options = {"cities": list(settings.CITIES.keys())}

        elif context.current_state == ConversationState.QUERY_TYPE:
            # Handle queries about Menu, FAQs, or Location Info
            if context.query_type == "Menu":
                # Fetch and display Menu
                menu_items = kb.get_menu(context.restaurant)
                if menu_items:
                    response = f"Here is the menu for {context.restaurant}:\n" + "\n".join(menu_items)
                    options = None # Or options to go back or ask something else
                else:
                    response = f"Sorry, I couldn't find the menu for {context.restaurant}."
                    options = None

            elif context.query_type == "FAQs":
                # Fetch and display FAQs
                faqs = kb.get_faqs(context.restaurant)
                if faqs:
                    response = f"Here are some FAQs for {context.restaurant}:\n" + "\n".join(faqs)
                    options = None # Or options to ask another FAQ or go back
                else:
                    response = f"Sorry, I couldn't find FAQs for {context.restaurant}."
                    options = None

            elif context.query_type == "Location_Info":
                 # Handle general query after location selection (simplified)
                 response = f"You've selected a location in {context.city}. What specific information are you looking for about this location?"
                 options = {"query_types": ["FAQs", "Booking"]} # Offer next steps

            else:
                # Fallback for unrecognized query type in this state
                response = "What would you like to know? (1 for FAQs, 2 for Booking)"
                options = {"query_types": ["FAQs", "Booking"]}

        elif context.current_state == ConversationState.BOOKING_COLLECTION:
            response = "Please provide your booking details (name, date, time, guests)"
            options = {"booking_fields": ["name", "date", "time", "guests"]}
            # Add logic here to capture booking details and transition to BOOKING_CONFIRMATION

        elif context.current_state == ConversationState.BOOKING_CONFIRMATION:
             # In a real app, process booking details and ask for confirmation
             response = "Would you like to confirm your booking? (yes/no)"
             options = {"confirmation": ["yes", "no"]}
            # Add logic here to transition to FAREWELL or back to booking collection

        elif context.current_state == ConversationState.FAREWELL:
            response = "Thank you for choosing Barbeque Nation! Have a great day!"
            options = None
            # Conversation ends here
            
        else:
            # Fallback for any unhandled state
            response = "I'm not sure how to proceed. Can we start over?"
            options = None # Maybe provide a restart option

        # --- End Generate response based on the NEW state and Context --- #
        
        # Update session context with the final state for this turn
        sessions[request.session_id] = context

        return ChatResponse(
            response=response,
            state=context.current_state.value, # Return the new state
            options=options
        )
        
    except Exception as e:
        print(f"Error in chatbot endpoint: {e}") # Log the error on the backend
        # Reset state on major error to allow restarting
        if request.session_id in sessions:
             del sessions[request.session_id]
        raise HTTPException(status_code=500, detail="Sorry, there was an error processing your request. Please try again.")

@router.get("/restaurants/{city}")
async def get_restaurants(city: str):
    restaurants = kb.get_restaurants_by_city(city)
    if not restaurants:
        raise HTTPException(status_code=404, detail=f"No restaurants found in {city}")
    return {"restaurants": restaurants}

@router.get("/restaurant/{restaurant_name}")
async def get_restaurant_info(restaurant_name: str):
    info = kb.get_restaurant_info(restaurant_name)
    if not info:
        raise HTTPException(status_code=404, detail=f"Restaurant {restaurant_name} not found")
    return info

@router.get("/restaurant/{restaurant_name}/menu")
async def get_restaurant_menu(restaurant_name: str):
    menu = kb.get_menu(restaurant_name)
    if not menu:
        raise HTTPException(status_code=404, detail=f"Menu not found for {restaurant_name}")
    return {"menu": menu}

@router.get("/restaurant/{restaurant_name}/faq")
async def get_restaurant_faq(restaurant_name: str, query: Optional[str] = None):
    if query:
        result = kb.search_faq(restaurant_name, query)
        if not result:
            raise HTTPException(status_code=404, detail=f"No FAQ found matching '{query}'")
        return {"faq": result}
    else:
        faq = kb.get_faq(restaurant_name)
        if not faq:
            raise HTTPException(status_code=404, detail=f"FAQ not found for {restaurant_name}")
        return {"faq": faq} 