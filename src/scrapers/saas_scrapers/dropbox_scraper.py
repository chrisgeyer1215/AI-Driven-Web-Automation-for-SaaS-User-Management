from ..base_scraper import BaseScraper, ScrapingConfig
from ...core.auth_handler import AuthConfig

class DropboxScraper(BaseScraper):
    """Dropbox Business admin portal scraper"""
    
    async def get_scraping_config(self) -> ScrapingConfig:
        auth_config = AuthConfig(
            username_selector="input[name='login_email']",
            password_selector="input[name='login_password']",
            submit_selector="button[type='submit']",
            success_indicator=".admin-console",
            login_url="https://www.dropbox.com/login"
        )
        
        return ScrapingConfig(
            base_url="https://www.dropbox.com",
            login_url="https://www.dropbox.com/login",
            users_page_url="https://www.dropbox.com/team/admin/members",
            auth_config=auth_config,
            pagination_config={
                "next_button": ".pagination-next",
                "page_size": "50"
            }
        )