from ..base_scraper import BaseScraper, ScrapingConfig
from ...core.auth_handler import AuthConfig

class NotionScraper(BaseScraper):
    """Notion workspace admin scraper"""
    
    async def get_scraping_config(self) -> ScrapingConfig:
        auth_config = AuthConfig(
            username_selector="input[type='email']",
            password_selector="input[type='password']",
            submit_selector="button[type='submit']",
            success_indicator=".notion-topbar",
            login_url="https://www.notion.so/login"
        )
        
        return ScrapingConfig(
            base_url="https://www.notion.so",
            login_url="https://www.notion.so/login",
            users_page_url="https://www.notion.so/settings/members",
            auth_config=auth_config
        )