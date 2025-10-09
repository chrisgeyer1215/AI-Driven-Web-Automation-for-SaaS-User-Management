from ..base_provisioner import BaseProvisioner
from ...core.auth_handler import AuthConfig
from typing import Dict, Any

class DropboxProvisioner(BaseProvisioner):
    """Dropbox Business user provisioning"""
    
    async def get_provisioning_config(self) -> Dict[str, Any]:
        auth_config = AuthConfig(
            username_selector="input[name='login_email']",
            password_selector="input[name='login_password']",  # CSS selector, not actual password
            submit_selector="button[type='submit']",
            success_indicator=".admin-console",
            login_url="https://www.dropbox.com/login"
        )
        
        return {
            "auth_config": auth_config,
            "users_page_url": "https://www.dropbox.com/team/admin/members",
            "add_user_url": "https://www.dropbox.com/team/admin/members/invite",
            "form_fields": {
                "email": "input[name='email']",
                "name": "input[name='given_name']",
                "role": "select[name='role']"
            },
            "submit_selector": "button[data-testid='invite-button']"
        }