import openai
import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

class ActionType(Enum):
    CLICK = "click"
    TYPE = "type"
    WAIT = "wait"
    EXTRACT = "extract"
    NAVIGATE = "navigate"
    SCROLL = "scroll"

@dataclass
class Action:
    type: ActionType
    selector: str
    value: Optional[str] = None
    description: str = ""

class AIAgent:
    """AI-powered agent for web automation using GPT models"""
    
    def __init__(self, api_key: str, model: str = "gpt-3.5-turbo"):
        self.client = openai.OpenAI(api_key=api_key)
        self.model = model
        self.context_history = []
    
    def analyze_page(self, html_content: str, screenshot_path: str = None) -> Dict[str, Any]:
        """Analyze page content and identify actionable elements"""
        prompt = f"""
        Analyze this HTML content and identify key elements for user management:
        
        HTML: {html_content[:5000]}...
        
        Return a JSON response with:
        1. user_table_selector: CSS selector for user data table
        2. login_elements: selectors for login form elements
        3. user_action_buttons: selectors for add/remove user buttons
        4. pagination_elements: selectors for pagination controls
        5. data_fields: mapping of user data fields to selectors
        
        Focus on elements related to user management, authentication, and data extraction.
        """
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1
        )
        
        try:
            return json.loads(response.choices[0].message.content)
        except json.JSONDecodeError:
            return {"error": "Failed to parse AI response"}
    
    def generate_automation_steps(self, goal: str, page_analysis: Dict[str, Any]) -> List[Action]:
        """Generate step-by-step automation actions based on goal and page analysis"""
        prompt = f"""
        Goal: {goal}
        Page Analysis: {json.dumps(page_analysis, indent=2)}
        
        Generate a sequence of automation steps as JSON array with this format:
        [
            {{
                "type": "click|type|wait|extract|navigate|scroll",
                "selector": "CSS_SELECTOR",
                "value": "VALUE_IF_NEEDED",
                "description": "Human readable description"
            }}
        ]
        
        Consider:
        - Authentication flows (login, MFA)
        - Navigation to user management sections
        - Data extraction from tables/lists
        - Handling pagination
        - Error handling and retries
        """
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2
        )
        
        try:
            steps_data = json.loads(response.choices[0].message.content)
            return [Action(**step) for step in steps_data]
        except (json.JSONDecodeError, TypeError):
            return []
    
    def adapt_to_ui_changes(self, expected_selector: str, actual_html: str) -> str:
        """Adapt selectors when UI changes are detected"""
        prompt = f"""
        The expected selector '{expected_selector}' is not working.
        
        HTML snippet: {actual_html[:3000]}...
        
        Suggest an alternative CSS selector that would work for the same element type.
        Return only the selector string.
        """
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1
        )
        
        return response.choices[0].message.content.strip()
    
    def extract_user_data(self, html_content: str) -> List[Dict[str, str]]:
        """Extract structured user data from HTML content"""
        prompt = f"""
        Extract user data from this HTML content:
        
        {html_content[:8000]}...
        
        Return JSON array of user objects with fields:
        - name: full name
        - email: email address
        - role: user role/permission level
        - last_login: last login date/time
        - status: active/inactive status
        
        Example format:
        [
            {{
                "name": "John Doe",
                "email": "john@company.com",
                "role": "Admin",
                "last_login": "2024-01-15",
                "status": "Active"
            }}
        ]
        """
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1
        )
        
        try:
            return json.loads(response.choices[0].message.content)
        except json.JSONDecodeError:
            return []
    
    def handle_error_recovery(self, error_context: str, page_state: str) -> List[Action]:
        """Generate recovery actions when automation encounters errors"""
        prompt = f"""
        Error occurred: {error_context}
        Current page state: {page_state[:2000]}...
        
        Generate recovery actions to continue automation.
        Return JSON array of actions to resolve the issue.
        """
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        
        try:
            recovery_data = json.loads(response.choices[0].message.content)
            return [Action(**action) for action in recovery_data]
        except (json.JSONDecodeError, TypeError):
            return []