import asyncio
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from ..core.browser_manager import BrowserManager
from ..core.ai_agent import AIAgent
from ..core.auth_handler import AuthHandler, AuthConfig

@dataclass
class UserData:
    name: str
    email: str
    role: str
    last_login: str
    status: str
    additional_fields: Dict[str, Any] = None

@dataclass
class ScrapingConfig:
    base_url: str
    login_url: str
    users_page_url: str
    auth_config: AuthConfig
    pagination_config: Dict[str, str] = None

class BaseScraper(ABC):
    """Base class for SaaS application scrapers"""
    
    def __init__(self, browser_manager: BrowserManager, ai_agent: AIAgent):
        self.browser = browser_manager
        self.ai_agent = ai_agent
        self.auth_handler = AuthHandler(browser_manager)
        self.scraped_users = []
    
    @abstractmethod
    async def get_scraping_config(self) -> ScrapingConfig:
        """Return scraping configuration for the specific SaaS application"""
        pass
    
    async def scrape_users(self, credentials: Dict[str, str]) -> List[UserData]:
        """Main method to scrape user data from SaaS application"""
        try:
            config = await self.get_scraping_config()
            
            # Authenticate
            login_success = await self.auth_handler.login(config.auth_config, credentials)
            if not login_success:
                raise Exception("Authentication failed")
            
            # Navigate to users page
            await self.browser.navigate(config.users_page_url)
            await asyncio.sleep(2)
            
            # Analyze page structure
            page_content = await self.browser.get_page_content()
            page_analysis = self.ai_agent.analyze_page(page_content)
            
            # Extract users from all pages
            all_users = []
            page_num = 1
            
            while True:
                # Extract users from current page
                users = await self.extract_users_from_page(page_analysis)
                all_users.extend(users)
                
                # Check for next page
                if not await self.navigate_to_next_page(page_analysis, page_num):
                    break
                
                page_num += 1
                await asyncio.sleep(2)  # Rate limiting
            
            self.scraped_users = all_users
            return all_users
            
        except Exception as e:
            print(f"Scraping failed: {e}")
            return []
    
    async def extract_users_from_page(self, page_analysis: Dict[str, Any]) -> List[UserData]:
        """Extract user data from current page"""
        try:
            page_content = await self.browser.get_page_content()
            
            # Use AI to extract structured user data
            raw_users = self.ai_agent.extract_user_data(page_content)
            
            users = []
            for user_data in raw_users:
                user = UserData(
                    name=user_data.get("name", ""),
                    email=user_data.get("email", ""),
                    role=user_data.get("role", ""),
                    last_login=user_data.get("last_login", ""),
                    status=user_data.get("status", ""),
                    additional_fields=user_data.get("additional_fields", {})
                )
                users.append(user)
            
            return users
            
        except Exception as e:
            print(f"User extraction failed: {e}")
            return []
    
    async def navigate_to_next_page(self, page_analysis: Dict[str, Any], current_page: int) -> bool:
        """Navigate to next page if pagination exists"""
        try:
            pagination_selectors = [
                "a[aria-label='Next']",
                ".pagination .next",
                ".next-page",
                "[data-testid*='next']",
                "button:contains('Next')"
            ]
            
            # Try AI-suggested pagination selector first
            if page_analysis.get("pagination_elements"):
                pagination_selectors.insert(0, page_analysis["pagination_elements"])
            
            for selector in pagination_selectors:
                if await self.browser.wait_for_element(selector, timeout=2000):
                    # Check if next button is enabled
                    is_disabled = await self.browser.extract_attribute(selector, "disabled")
                    if not is_disabled:
                        await self.browser.click_element(selector)
                        await self.browser.wait_for_navigation()
                        return True
            
            return False
            
        except Exception as e:
            print(f"Pagination navigation failed: {e}")
            return False
    
    async def handle_dynamic_loading(self, max_scrolls: int = 10) -> bool:
        """Handle infinite scroll or dynamic content loading"""
        try:
            initial_content = await self.browser.get_page_content()
            
            for i in range(max_scrolls):
                # Scroll to bottom
                await self.browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                await asyncio.sleep(2)
                
                # Check if new content loaded
                new_content = await self.browser.get_page_content()
                if len(new_content) == len(initial_content):
                    break  # No new content loaded
                
                initial_content = new_content
            
            return True
            
        except Exception as e:
            print(f"Dynamic loading handling failed: {e}")
            return False
    
    async def retry_with_adaptation(self, operation, max_retries: int = 3):
        """Retry operation with AI-driven adaptation on failure"""
        for attempt in range(max_retries):
            try:
                return await operation()
            except Exception as e:
                if attempt == max_retries - 1:
                    raise e
                
                # Get current page state for AI analysis
                page_content = await self.browser.get_page_content()
                
                # Ask AI for recovery actions
                recovery_actions = self.ai_agent.handle_error_recovery(str(e), page_content)
                
                # Execute recovery actions
                for action in recovery_actions:
                    await self.execute_action(action)
                
                await asyncio.sleep(2)  # Wait before retry
    
    async def execute_action(self, action):
        """Execute a single automation action"""
        if action.type.value == "click":
            await self.browser.click_element(action.selector)
        elif action.type.value == "type":
            await self.browser.type_text(action.selector, action.value)
        elif action.type.value == "wait":
            await asyncio.sleep(int(action.value or 1))
        elif action.type.value == "navigate":
            await self.browser.navigate(action.value)
        elif action.type.value == "scroll":
            await self.browser.scroll_to_element(action.selector)
    
    async def validate_extracted_data(self, users: List[UserData]) -> List[UserData]:
        """Validate and clean extracted user data"""
        validated_users = []
        
        for user in users:
            # Basic validation
            if user.email and "@" in user.email and user.name:
                # Clean and normalize data
                user.email = user.email.strip().lower()
                user.name = user.name.strip()
                user.role = user.role.strip() if user.role else "Unknown"
                user.status = user.status.strip() if user.status else "Unknown"
                
                validated_users.append(user)
        
        return validated_users
    
    async def export_data(self, users: List[UserData], format: str = "json") -> str:
        """Export scraped data in specified format"""
        if format == "json":
            import json
            data = [user.__dict__ for user in users]
            return json.dumps(data, indent=2)
        elif format == "csv":
            import csv
            import io
            output = io.StringIO()
            if users:
                fieldnames = users[0].__dict__.keys()
                writer = csv.DictWriter(output, fieldnames=fieldnames)
                writer.writeheader()
                for user in users:
                    writer.writerow(user.__dict__)
            return output.getvalue()
        else:
            return str(users)