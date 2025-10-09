import asyncio
from playwright.async_api import async_playwright, Browser, Page, BrowserContext
from typing import Optional, Dict, Any, List
import json
import base64
from pathlib import Path

class BrowserManager:
    """Manages headless browser operations with Playwright"""
    
    def __init__(self, headless: bool = True, browser_type: str = "chromium"):
        self.headless = headless
        self.browser_type = browser_type
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.playwright = None
    
    async def start(self):
        """Initialize browser instance"""
        self.playwright = await async_playwright().start()
        
        browser_args = [
            "--no-sandbox",
            "--disable-blink-features=AutomationControlled",
            "--disable-web-security",
            "--disable-features=VizDisplayCompositor"
        ]
        
        if self.browser_type == "chromium":
            self.browser = await self.playwright.chromium.launch(
                headless=self.headless,
                args=browser_args
            )
        elif self.browser_type == "firefox":
            self.browser = await self.playwright.firefox.launch(headless=self.headless)
        else:
            self.browser = await self.playwright.webkit.launch(headless=self.headless)
        
        # Create context with realistic user agent
        self.context = await self.browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            viewport={"width": 1920, "height": 1080}
        )
        
        self.page = await self.context.new_page()
        
        # Add stealth scripts to avoid detection
        await self.page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            window.chrome = {runtime: {}};
        """)
    
    async def navigate(self, url: str, wait_for: str = "networkidle") -> bool:
        """Navigate to URL with error handling"""
        try:
            await self.page.goto(url, wait_until=wait_for, timeout=30000)
            return True
        except Exception as e:
            print(f"Navigation failed: {e}")
            return False
    
    async def wait_for_element(self, selector: str, timeout: int = 10000) -> bool:
        """Wait for element to be visible"""
        try:
            await self.page.wait_for_selector(selector, timeout=timeout)
            return True
        except:
            return False
    
    async def click_element(self, selector: str, timeout: int = 5000) -> bool:
        """Click element with retry logic"""
        try:
            await self.page.wait_for_selector(selector, timeout=timeout)
            await self.page.click(selector)
            return True
        except Exception as e:
            print(f"Click failed for {selector}: {e}")
            return False
    
    async def type_text(self, selector: str, text: str, clear: bool = True) -> bool:
        """Type text into input field"""
        try:
            if clear:
                await self.page.fill(selector, text)
            else:
                await self.page.type(selector, text)
            return True
        except Exception as e:
            print(f"Type failed for {selector}: {e}")
            return False
    
    async def extract_text(self, selector: str) -> str:
        """Extract text content from element"""
        try:
            element = await self.page.query_selector(selector)
            if element:
                return await element.text_content()
            return ""
        except:
            return ""
    
    async def extract_attribute(self, selector: str, attribute: str) -> str:
        """Extract attribute value from element"""
        try:
            return await self.page.get_attribute(selector, attribute) or ""
        except:
            return ""
    
    async def get_page_content(self) -> str:
        """Get current page HTML content"""
        try:
            return await self.page.content()
        except:
            return ""
    
    async def take_screenshot(self, path: str = "screenshot.png") -> str:
        """Take screenshot and return path"""
        try:
            await self.page.screenshot(path=path, full_page=True)
            return path
        except Exception as e:
            print(f"Screenshot failed: {e}")
            return ""
    
    async def handle_dialog(self, accept: bool = True, text: str = ""):
        """Handle JavaScript dialogs"""
        def dialog_handler(dialog):
            if accept:
                asyncio.create_task(dialog.accept(text))
            else:
                asyncio.create_task(dialog.dismiss())
        
        self.page.on("dialog", dialog_handler)
    
    async def wait_for_navigation(self, timeout: int = 30000):
        """Wait for page navigation to complete"""
        try:
            await self.page.wait_for_load_state("networkidle", timeout=timeout)
        except:
            pass
    
    async def scroll_to_element(self, selector: str) -> bool:
        """Scroll element into view"""
        try:
            await self.page.locator(selector).scroll_into_view_if_needed()
            return True
        except:
            return False
    
    async def get_all_elements(self, selector: str) -> List[Dict[str, Any]]:
        """Get all elements matching selector with their properties"""
        try:
            elements = await self.page.query_selector_all(selector)
            result = []
            
            for element in elements:
                text = await element.text_content()
                html = await element.inner_html()
                result.append({
                    "text": text,
                    "html": html,
                    "visible": await element.is_visible()
                })
            
            return result
        except:
            return []
    
    async def execute_script(self, script: str) -> Any:
        """Execute JavaScript on the page"""
        try:
            return await self.page.evaluate(script)
        except Exception as e:
            print(f"Script execution failed: {e}")
            return None
    
    async def set_cookies(self, cookies: List[Dict[str, Any]]):
        """Set cookies for the current context"""
        try:
            await self.context.add_cookies(cookies)
        except Exception as e:
            print(f"Failed to set cookies: {e}")
    
    async def get_cookies(self) -> List[Dict[str, Any]]:
        """Get all cookies from current context"""
        try:
            return await self.context.cookies()
        except:
            return []
    
    async def close(self):
        """Clean up browser resources"""
        if self.page:
            await self.page.close()
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()