import asyncio
import json
import time
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from .browser_manager import BrowserManager

@dataclass
class AuthConfig:
    username_selector: str
    password_selector: str
    submit_selector: str
    mfa_selector: Optional[str] = None
    success_indicator: str = ""
    login_url: str = ""

class AuthHandler:
    """Handles authentication flows including MFA and session management"""
    
    def __init__(self, browser_manager: BrowserManager):
        self.browser = browser_manager
        self.session_cookies = {}
        self.auth_tokens = {}
    
    async def login(self, auth_config: AuthConfig, credentials: Dict[str, str]) -> bool:
        """Perform login with credentials"""
        try:
            # Navigate to login page
            if auth_config.login_url:
                await self.browser.navigate(auth_config.login_url)
            
            # Wait for login form
            if not await self.browser.wait_for_element(auth_config.username_selector):
                return False
            
            # Enter credentials
            await self.browser.type_text(auth_config.username_selector, credentials["username"])
            await asyncio.sleep(1)
            await self.browser.type_text(auth_config.password_selector, credentials["password"])
            await asyncio.sleep(1)
            
            # Submit form
            await self.browser.click_element(auth_config.submit_selector)
            await self.browser.wait_for_navigation()
            
            # Handle MFA if present
            if auth_config.mfa_selector and await self.browser.wait_for_element(auth_config.mfa_selector, timeout=5000):
                mfa_success = await self.handle_mfa(auth_config.mfa_selector, credentials.get("mfa_code", ""))
                if not mfa_success:
                    return False
            
            # Verify login success
            if auth_config.success_indicator:
                success = await self.browser.wait_for_element(auth_config.success_indicator, timeout=10000)
                if success:
                    await self.save_session()
                return success
            
            # If no success indicator, assume success if no error elements
            await asyncio.sleep(3)
            await self.save_session()
            return True
            
        except Exception as e:
            print(f"Login failed: {e}")
            return False
    
    async def handle_mfa(self, mfa_selector: str, mfa_code: str = "") -> bool:
        """Handle Multi-Factor Authentication"""
        try:
            if not mfa_code:
                # Wait for manual MFA input or automated solution
                print("MFA required. Please enter code manually or provide mfa_code in credentials.")
                # Wait up to 60 seconds for manual input
                for _ in range(60):
                    await asyncio.sleep(1)
                    # Check if MFA page is still present
                    if not await self.browser.wait_for_element(mfa_selector, timeout=1000):
                        return True
                return False
            
            # Enter MFA code
            await self.browser.type_text(mfa_selector, mfa_code)
            
            # Look for MFA submit button
            mfa_submit_selectors = [
                "button[type='submit']",
                "input[type='submit']",
                ".mfa-submit",
                "#mfa-submit",
                "[data-testid*='submit']"
            ]
            
            for selector in mfa_submit_selectors:
                if await self.browser.wait_for_element(selector, timeout=2000):
                    await self.browser.click_element(selector)
                    break
            
            await self.browser.wait_for_navigation()
            return True
            
        except Exception as e:
            print(f"MFA handling failed: {e}")
            return False
    
    async def save_session(self):
        """Save current session cookies and tokens"""
        try:
            self.session_cookies = await self.browser.get_cookies()
            
            # Extract common auth tokens from localStorage/sessionStorage
            auth_tokens = await self.browser.execute_script("""
                return {
                    localStorage: Object.fromEntries(Object.entries(localStorage)),
                    sessionStorage: Object.fromEntries(Object.entries(sessionStorage))
                };
            """)
            
            if auth_tokens:
                self.auth_tokens = auth_tokens
                
        except Exception as e:
            print(f"Failed to save session: {e}")
    
    async def restore_session(self) -> bool:
        """Restore saved session"""
        try:
            if self.session_cookies:
                await self.browser.set_cookies(self.session_cookies)
            
            if self.auth_tokens:
                # Restore localStorage and sessionStorage
                for storage_type, data in self.auth_tokens.items():
                    if data and isinstance(data, dict):
                        script = f"""
                            const storage = {storage_type};
                            const data = {json.dumps(data)};
                            for (const [key, value] of Object.entries(data)) {{
                                storage.setItem(key, value);
                            }}
                        """
                        await self.browser.execute_script(script)
            
            return True
            
        except Exception as e:
            print(f"Failed to restore session: {e}")
            return False
    
    async def check_session_validity(self, check_url: str, success_indicator: str) -> bool:
        """Check if current session is still valid"""
        try:
            await self.browser.navigate(check_url)
            return await self.browser.wait_for_element(success_indicator, timeout=5000)
        except:
            return False
    
    async def handle_captcha(self, captcha_selector: str) -> bool:
        """Handle CAPTCHA challenges"""
        try:
            # Take screenshot of CAPTCHA
            screenshot_path = await self.browser.take_screenshot("captcha.png")
            
            # For now, wait for manual solving
            print(f"CAPTCHA detected. Screenshot saved to {screenshot_path}")
            print("Please solve CAPTCHA manually and press Enter to continue...")
            
            # Wait for manual intervention
            input("Press Enter after solving CAPTCHA...")
            
            return True
            
        except Exception as e:
            print(f"CAPTCHA handling failed: {e}")
            return False
    
    async def detect_auth_elements(self, page_content: str) -> AuthConfig:
        """Auto-detect authentication elements on the page"""
        # Common selectors for login forms
        username_selectors = [
            "input[type='email']",
            "input[name*='username']",
            "input[name*='email']",
            "input[id*='username']",
            "input[id*='email']",
            "#username", "#email", "#user"
        ]
        
        password_selectors = [
            "input[type='password']",
            "input[name*='password']",
            "input[id*='password']",
            "#password", "#pass"
        ]
        
        submit_selectors = [
            "button[type='submit']",
            "input[type='submit']",
            ".login-button",
            ".signin-button",
            "[data-testid*='login']",
            "[data-testid*='signin']"
        ]
        
        # Find working selectors
        username_selector = ""
        password_selector = ""
        submit_selector = ""
        
        for selector in username_selectors:
            if await self.browser.wait_for_element(selector, timeout=1000):
                username_selector = selector
                break
        
        for selector in password_selectors:
            if await self.browser.wait_for_element(selector, timeout=1000):
                password_selector = selector
                break
        
        for selector in submit_selectors:
            if await self.browser.wait_for_element(selector, timeout=1000):
                submit_selector = selector
                break
        
        return AuthConfig(
            username_selector=username_selector,
            password_selector=password_selector,
            submit_selector=submit_selector
        )