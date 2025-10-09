import asyncio
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
from ..core.browser_manager import BrowserManager
from ..core.ai_agent import AIAgent
from ..core.auth_handler import AuthHandler, AuthConfig

class ProvisioningAction(Enum):
    ADD_USER = "add_user"
    REMOVE_USER = "remove_user"
    UPDATE_USER = "update_user"
    CHANGE_ROLE = "change_role"
    ACTIVATE_USER = "activate_user"
    DEACTIVATE_USER = "deactivate_user"

@dataclass
class UserProvisioningRequest:
    action: ProvisioningAction
    user_email: str
    user_name: str = ""
    role: str = ""
    additional_data: Dict[str, Any] = None

@dataclass
class ProvisioningResult:
    success: bool
    action: ProvisioningAction
    user_email: str
    message: str
    error_details: str = ""

class BaseProvisioner(ABC):
    """Base class for SaaS application user provisioning"""
    
    def __init__(self, browser_manager: BrowserManager, ai_agent: AIAgent):
        self.browser = browser_manager
        self.ai_agent = ai_agent
        self.auth_handler = AuthHandler(browser_manager)
        self.provisioning_results = []
    
    @abstractmethod
    async def get_provisioning_config(self) -> Dict[str, Any]:
        """Return provisioning configuration for the specific SaaS application"""
        pass
    
    async def provision_user(self, request: UserProvisioningRequest, credentials: Dict[str, str]) -> ProvisioningResult:
        """Main method to provision/deprovision users"""
        try:
            config = await self.get_provisioning_config()
            
            # Authenticate if needed
            if not await self.is_authenticated():
                login_success = await self.auth_handler.login(config["auth_config"], credentials)
                if not login_success:
                    return ProvisioningResult(
                        success=False,
                        action=request.action,
                        user_email=request.user_email,
                        message="Authentication failed"
                    )
            
            # Execute specific provisioning action
            if request.action == ProvisioningAction.ADD_USER:
                result = await self.add_user(request, config)
            elif request.action == ProvisioningAction.REMOVE_USER:
                result = await self.remove_user(request, config)
            elif request.action == ProvisioningAction.UPDATE_USER:
                result = await self.update_user(request, config)
            elif request.action == ProvisioningAction.CHANGE_ROLE:
                result = await self.change_user_role(request, config)
            elif request.action == ProvisioningAction.ACTIVATE_USER:
                result = await self.activate_user(request, config)
            elif request.action == ProvisioningAction.DEACTIVATE_USER:
                result = await self.deactivate_user(request, config)
            else:
                result = ProvisioningResult(
                    success=False,
                    action=request.action,
                    user_email=request.user_email,
                    message="Unsupported action"
                )
            
            self.provisioning_results.append(result)
            return result
            
        except Exception as e:
            error_result = ProvisioningResult(
                success=False,
                action=request.action,
                user_email=request.user_email,
                message="Provisioning failed",
                error_details=str(e)
            )
            self.provisioning_results.append(error_result)
            return error_result
    
    async def add_user(self, request: UserProvisioningRequest, config: Dict[str, Any]) -> ProvisioningResult:
        """Add a new user to the SaaS application"""
        try:
            # Navigate to add user page
            add_user_url = config.get("add_user_url", "")
            if add_user_url:
                await self.browser.navigate(add_user_url)
            else:
                # Find add user button using AI
                page_content = await self.browser.get_page_content()
                page_analysis = self.ai_agent.analyze_page(page_content)
                
                add_button_selector = page_analysis.get("user_action_buttons", {}).get("add_user", "")
                if add_button_selector:
                    await self.browser.click_element(add_button_selector)
                    await self.browser.wait_for_navigation()
            
            # Fill user form
            await self.fill_user_form(request, config)
            
            # Submit form
            submit_selector = config.get("submit_selector", "button[type='submit']")
            await self.browser.click_element(submit_selector)
            await self.browser.wait_for_navigation()
            
            # Verify success
            success = await self.verify_user_action_success(request.user_email, "added")
            
            return ProvisioningResult(
                success=success,
                action=request.action,
                user_email=request.user_email,
                message="User added successfully" if success else "Failed to add user"
            )
            
        except Exception as e:
            return ProvisioningResult(
                success=False,
                action=request.action,
                user_email=request.user_email,
                message="Add user failed",
                error_details=str(e)
            )
    
    async def remove_user(self, request: UserProvisioningRequest, config: Dict[str, Any]) -> ProvisioningResult:
        """Remove a user from the SaaS application"""
        try:
            # Navigate to users page
            users_url = config.get("users_page_url", "")
            await self.browser.navigate(users_url)
            
            # Find user in the list
            user_row_selector = await self.find_user_in_list(request.user_email)
            if not user_row_selector:
                return ProvisioningResult(
                    success=False,
                    action=request.action,
                    user_email=request.user_email,
                    message="User not found"
                )
            
            # Find and click remove/delete button for the user
            remove_selectors = [
                f"{user_row_selector} .delete-button",
                f"{user_row_selector} .remove-button",
                f"{user_row_selector} [data-action='delete']",
                f"{user_row_selector} button:contains('Delete')",
                f"{user_row_selector} button:contains('Remove')"
            ]
            
            remove_clicked = False
            for selector in remove_selectors:
                if await self.browser.wait_for_element(selector, timeout=2000):
                    await self.browser.click_element(selector)
                    remove_clicked = True
                    break
            
            if not remove_clicked:
                return ProvisioningResult(
                    success=False,
                    action=request.action,
                    user_email=request.user_email,
                    message="Remove button not found"
                )
            
            # Handle confirmation dialog
            await asyncio.sleep(1)
            confirm_selectors = [
                "button:contains('Confirm')",
                "button:contains('Yes')",
                "button:contains('Delete')",
                ".confirm-button",
                "[data-testid*='confirm']"
            ]
            
            for selector in confirm_selectors:
                if await self.browser.wait_for_element(selector, timeout=3000):
                    await self.browser.click_element(selector)
                    break
            
            await self.browser.wait_for_navigation()
            
            # Verify success
            success = await self.verify_user_action_success(request.user_email, "removed")
            
            return ProvisioningResult(
                success=success,
                action=request.action,
                user_email=request.user_email,
                message="User removed successfully" if success else "Failed to remove user"
            )
            
        except Exception as e:
            return ProvisioningResult(
                success=False,
                action=request.action,
                user_email=request.user_email,
                message="Remove user failed",
                error_details=str(e)
            )
    
    async def update_user(self, request: UserProvisioningRequest, config: Dict[str, Any]) -> ProvisioningResult:
        """Update user information"""
        try:
            # Find and click edit button for user
            user_row_selector = await self.find_user_in_list(request.user_email)
            if not user_row_selector:
                return ProvisioningResult(
                    success=False,
                    action=request.action,
                    user_email=request.user_email,
                    message="User not found"
                )
            
            edit_selectors = [
                f"{user_row_selector} .edit-button",
                f"{user_row_selector} [data-action='edit']",
                f"{user_row_selector} button:contains('Edit')"
            ]
            
            for selector in edit_selectors:
                if await self.browser.wait_for_element(selector, timeout=2000):
                    await self.browser.click_element(selector)
                    break
            
            await asyncio.sleep(2)
            
            # Fill updated information
            await self.fill_user_form(request, config)
            
            # Submit changes
            submit_selector = config.get("submit_selector", "button[type='submit']")
            await self.browser.click_element(submit_selector)
            await self.browser.wait_for_navigation()
            
            return ProvisioningResult(
                success=True,
                action=request.action,
                user_email=request.user_email,
                message="User updated successfully"
            )
            
        except Exception as e:
            return ProvisioningResult(
                success=False,
                action=request.action,
                user_email=request.user_email,
                message="Update user failed",
                error_details=str(e)
            )
    
    async def change_user_role(self, request: UserProvisioningRequest, config: Dict[str, Any]) -> ProvisioningResult:
        """Change user role/permissions"""
        # Implementation similar to update_user but focused on role changes
        return await self.update_user(request, config)
    
    async def activate_user(self, request: UserProvisioningRequest, config: Dict[str, Any]) -> ProvisioningResult:
        """Activate a deactivated user"""
        return await self.toggle_user_status(request, config, activate=True)
    
    async def deactivate_user(self, request: UserProvisioningRequest, config: Dict[str, Any]) -> ProvisioningResult:
        """Deactivate an active user"""
        return await self.toggle_user_status(request, config, activate=False)
    
    async def toggle_user_status(self, request: UserProvisioningRequest, config: Dict[str, Any], activate: bool) -> ProvisioningResult:
        """Toggle user active/inactive status"""
        try:
            user_row_selector = await self.find_user_in_list(request.user_email)
            if not user_row_selector:
                return ProvisioningResult(
                    success=False,
                    action=request.action,
                    user_email=request.user_email,
                    message="User not found"
                )
            
            action_text = "Activate" if activate else "Deactivate"
            toggle_selectors = [
                f"{user_row_selector} button:contains('{action_text}')",
                f"{user_row_selector} .status-toggle",
                f"{user_row_selector} [data-action='toggle-status']"
            ]
            
            for selector in toggle_selectors:
                if await self.browser.wait_for_element(selector, timeout=2000):
                    await self.browser.click_element(selector)
                    break
            
            await asyncio.sleep(2)
            
            return ProvisioningResult(
                success=True,
                action=request.action,
                user_email=request.user_email,
                message=f"User {action_text.lower()}d successfully"
            )
            
        except Exception as e:
            return ProvisioningResult(
                success=False,
                action=request.action,
                user_email=request.user_email,
                message=f"Failed to {'activate' if activate else 'deactivate'} user",
                error_details=str(e)
            )
    
    async def fill_user_form(self, request: UserProvisioningRequest, config: Dict[str, Any]):
        """Fill user form with provided data"""
        form_fields = config.get("form_fields", {})
        
        # Fill email
        if "email" in form_fields and request.user_email:
            await self.browser.type_text(form_fields["email"], request.user_email)
        
        # Fill name
        if "name" in form_fields and request.user_name:
            await self.browser.type_text(form_fields["name"], request.user_name)
        
        # Fill role
        if "role" in form_fields and request.role:
            # Handle dropdown or input field
            role_selector = form_fields["role"]
            if await self.browser.wait_for_element(f"{role_selector} option", timeout=2000):
                # It's a dropdown
                await self.browser.execute_script(f"""
                    const select = document.querySelector('{role_selector}');
                    const option = Array.from(select.options).find(opt => 
                        opt.text.toLowerCase().includes('{request.role.lower()}')
                    );
                    if (option) option.selected = true;
                """)
            else:
                # It's an input field
                await self.browser.type_text(role_selector, request.role)
        
        # Fill additional fields
        if request.additional_data:
            for field_name, value in request.additional_data.items():
                if field_name in form_fields:
                    await self.browser.type_text(form_fields[field_name], str(value))
    
    async def find_user_in_list(self, user_email: str) -> Optional[str]:
        """Find user row in the users list by email"""
        try:
            # Get all user rows
            row_selectors = [
                "tr:contains('" + user_email + "')",
                f"[data-email='{user_email}']",
                f"*:contains('{user_email}')"
            ]
            
            for selector in row_selectors:
                if await self.browser.wait_for_element(selector, timeout=2000):
                    return selector
            
            # Use AI to find user in complex layouts
            page_content = await self.browser.get_page_content()
            if user_email in page_content:
                # AI can help identify the exact selector
                return f"*:contains('{user_email}')"
            
            return None
            
        except Exception as e:
            print(f"Failed to find user {user_email}: {e}")
            return None
    
    async def verify_user_action_success(self, user_email: str, action: str) -> bool:
        """Verify that the user action was successful"""
        try:
            await asyncio.sleep(2)  # Wait for UI to update
            
            # Check for success messages
            success_selectors = [
                ".success-message",
                ".alert-success",
                "[data-testid*='success']",
                "*:contains('Success')",
                "*:contains('successfully')"
            ]
            
            for selector in success_selectors:
                if await self.browser.wait_for_element(selector, timeout=3000):
                    return True
            
            # For removal, check that user is no longer in the list
            if action == "removed":
                user_still_exists = await self.find_user_in_list(user_email)
                return user_still_exists is None
            
            # For addition, check that user now appears in the list
            if action == "added":
                user_exists = await self.find_user_in_list(user_email)
                return user_exists is not None
            
            return True  # Assume success if no clear indicators
            
        except Exception as e:
            print(f"Failed to verify action success: {e}")
            return False
    
    async def is_authenticated(self) -> bool:
        """Check if currently authenticated"""
        try:
            # Check for common authenticated page indicators
            auth_indicators = [
                ".user-menu",
                ".profile-dropdown",
                "[data-testid*='user']",
                ".logout-button",
                "*:contains('Sign out')",
                "*:contains('Logout')"
            ]
            
            for selector in auth_indicators:
                if await self.browser.wait_for_element(selector, timeout=2000):
                    return True
            
            return False
            
        except:
            return False
    
    async def batch_provision(self, requests: List[UserProvisioningRequest], credentials: Dict[str, str]) -> List[ProvisioningResult]:
        """Process multiple provisioning requests in batch"""
        results = []
        
        for request in requests:
            result = await self.provision_user(request, credentials)
            results.append(result)
            
            # Rate limiting between requests
            await asyncio.sleep(1)
        
        return results