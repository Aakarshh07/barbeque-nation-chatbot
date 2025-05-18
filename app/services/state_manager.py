from enum import Enum
from typing import Dict, Any, Optional
from pydantic import BaseModel
from docx import Document
from pathlib import Path

class ConversationState(str, Enum):
    INITIAL_GREETING = "initial_greeting"
    CITY_SELECTION = "city_selection"
    RESTAURANT_SELECTION = "restaurant_selection"
    QUERY_TYPE = "query_type"
    FAQ_HANDLING = "faq_handling"
    BOOKING_COLLECTION = "booking_collection"
    BOOKING_CONFIRMATION = "booking_confirmation"
    FAREWELL = "farewell"

class StateContext(BaseModel):
    current_state: ConversationState
    city: Optional[str] = None
    restaurant: Optional[str] = None
    query_type: Optional[str] = None
    booking_details: Optional[Dict[str, Any]] = None

class StateManager:
    def __init__(self):
        self.prompts_dir = Path("data/Prompt Templates")
        self.state_prompts = self._load_prompt_templates()
    
    def _load_prompt_templates(self) -> Dict[str, str]:
        """Load prompt templates from DOCX files"""
        prompts = {}
        
        # Load master templates
        master_collect = self._read_docx("master_collect.docx")
        master_inform = self._read_docx("master_inform.docx")
        
        # Load specific templates
        collect_city = self._read_docx("collect_city.docx")
        collect_contact = self._read_docx("collect_contact_information.docx")
        
        # Map templates to states
        prompts[ConversationState.INITIAL_GREETING] = master_inform
        prompts[ConversationState.CITY_SELECTION] = collect_city
        prompts[ConversationState.RESTAURANT_SELECTION] = master_collect
        prompts[ConversationState.QUERY_TYPE] = master_collect
        prompts[ConversationState.FAQ_HANDLING] = master_inform
        prompts[ConversationState.BOOKING_COLLECTION] = collect_contact
        prompts[ConversationState.BOOKING_CONFIRMATION] = master_collect
        prompts[ConversationState.FAREWELL] = "Thank you for choosing Barbeque Nation! Have a great day!"
        
        return prompts
    
    def _read_docx(self, filename: str) -> str:
        """Read content from a DOCX file"""
        try:
            doc = Document(self.prompts_dir / filename)
            return "\n".join(para.text for para in doc.paragraphs if para.text.strip())
        except Exception as e:
            print(f"Error reading {filename}: {str(e)}")
            return ""
    
    def get_state_prompt(self, state: ConversationState, context: StateContext) -> str:
        prompt = self.state_prompts.get(state, "")
        if not prompt:
            return "I'm sorry, I didn't understand that. Could you please rephrase?"
        
        # Format the prompt with context
        try:
            return prompt.format(
                city=context.city,
                restaurant=context.restaurant,
                query_type=context.query_type,
                **context.booking_details or {}
            )
        except KeyError:
            return prompt
    
    def get_next_state(self, current_state: ConversationState, user_input: str) -> ConversationState:
        # Simple state transition logic
        state_transitions = {
            ConversationState.INITIAL_GREETING: {
                "delhi": ConversationState.CITY_SELECTION,
                "bangalore": ConversationState.CITY_SELECTION
            },
            ConversationState.CITY_SELECTION: {
                "default": ConversationState.RESTAURANT_SELECTION
            },
            ConversationState.RESTAURANT_SELECTION: {
                "1": ConversationState.FAQ_HANDLING,
                "2": ConversationState.BOOKING_COLLECTION
            },
            ConversationState.FAQ_HANDLING: {
                "yes": ConversationState.FAQ_HANDLING,
                "no": ConversationState.FAREWELL
            },
            ConversationState.BOOKING_COLLECTION: {
                "default": ConversationState.BOOKING_CONFIRMATION
            },
            ConversationState.BOOKING_CONFIRMATION: {
                "yes": ConversationState.FAREWELL,
                "no": ConversationState.BOOKING_COLLECTION
            }
        }
        
        transitions = state_transitions.get(current_state, {})
        next_state = transitions.get(user_input.lower(), transitions.get("default", current_state))
        return next_state 