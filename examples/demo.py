#!/usr/bin/env python3
"""
Demo implementation of AI-driven SaaS user management automation
"""

import asyncio
import os
from dotenv import load_dotenv
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.core.browser_manager import BrowserManager
from src.core.ai_agent import AIAgent
from src.scrapers.saas_scrapers.dropbox_scraper import DropboxScraper
from src.provisioning.saas_provisioners.dropbox_provisioner import DropboxProvisioner
from src.provisioning.base_provisioner import UserProvisioningRequest, ProvisioningAction
from src.utils.data_processor import DataProcessor

# Load environment variables
load_dotenv()

class SaaSAutomationDemo:
    """Demo class showcasing AI-driven SaaS automation capabilities"""
    
    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        
        self.browser_manager = None
        self.ai_agent = None
    
    async def setup(self):
        """Initialize browser and AI agent"""
        self.browser_manager = BrowserManager(headless=False)  # Set to True for production
        await self.browser_manager.start()
        
        self.ai_agent = AIAgent(self.openai_api_key)
        print("✅ Browser and AI agent initialized")
    
    async def demo_user_scraping(self, credentials: dict):
        """Demonstrate user data scraping from Dropbox"""
        print("\n🔍 Starting user data scraping demo...")
        
        try:
            # Initialize Dropbox scraper
            scraper = DropboxScraper(self.browser_manager, self.ai_agent)
            
            # Scrape users
            users = await scraper.scrape_users(credentials)
            
            if users:
                print(f"✅ Successfully scraped {len(users)} users")
                
                # Process and clean data
                processed_users = []
                for user in users:
                    user_dict = {
                        "name": DataProcessor.normalize_name(user.name),
                        "email": DataProcessor.normalize_email(user.email),
                        "role": DataProcessor.normalize_role(user.role),
                        "status": DataProcessor.normalize_status(user.status),
                        "last_login": DataProcessor.parse_last_login(user.last_login)
                    }
                    
                    if DataProcessor.validate_user_data(user_dict):
                        processed_users.append(user_dict)
                
                # Remove duplicates
                unique_users = DataProcessor.deduplicate_users(processed_users)
                
                # Generate report
                report = DataProcessor.generate_report(unique_users)
                print(f"📊 User Report: {report}")
                
                # Export data
                csv_file = DataProcessor.export_to_csv(unique_users, "scraped_users.csv")
                json_file = DataProcessor.export_to_json(unique_users, "scraped_users.json")
                print(f"💾 Data exported to {csv_file} and {json_file}")
                
                return unique_users
            else:
                print("❌ No users found or scraping failed")
                return []
                
        except ConnectionError as e:
            print(f"❌ Network connection failed: {e}")
            print("💡 Check your internet connection and try again")
            return []
        except ValueError as e:
            print(f"❌ Invalid data encountered: {e}")
            print("💡 Check your credentials and configuration")
            return []
        except Exception as e:
            print(f"❌ Scraping demo failed: {e}")
            print(f"🔍 Error type: {type(e).__name__}")
            import traceback
            print(f"📋 Full traceback: {traceback.format_exc()}")
            return []
    
    async def demo_user_provisioning(self, credentials: dict):
        """Demonstrate user provisioning operations"""
        print("\n👤 Starting user provisioning demo...")
        
        try:
            # Initialize Dropbox provisioner
            provisioner = DropboxProvisioner(self.browser_manager, self.ai_agent)
            
            # Demo: Add a new user
            add_request = UserProvisioningRequest(
                action=ProvisioningAction.ADD_USER,
                user_email="demo.user@example.com",
                user_name="Demo User",
                role="Member"
            )
            
            print("➕ Adding new user...")
            add_result = await provisioner.provision_user(add_request, credentials)
            print(f"Add User Result: {add_result.message}")
            
            if add_result.success:
                # Demo: Update user role
                update_request = UserProvisioningRequest(
                    action=ProvisioningAction.CHANGE_ROLE,
                    user_email="demo.user@example.com",
                    role="Admin"
                )
                
                print("🔄 Updating user role...")
                update_result = await provisioner.provision_user(update_request, credentials)
                print(f"Update Role Result: {update_result.message}")
                
                # Demo: Deactivate user
                deactivate_request = UserProvisioningRequest(
                    action=ProvisioningAction.DEACTIVATE_USER,
                    user_email="demo.user@example.com"
                )
                
                print("⏸️ Deactivating user...")
                deactivate_result = await provisioner.provision_user(deactivate_request, credentials)
                print(f"Deactivate Result: {deactivate_result.message}")
                
                # Demo: Remove user
                remove_request = UserProvisioningRequest(
                    action=ProvisioningAction.REMOVE_USER,
                    user_email="demo.user@example.com"
                )
                
                print("🗑️ Removing user...")
                remove_result = await provisioner.provision_user(remove_request, credentials)
                print(f"Remove User Result: {remove_result.message}")
            
            return True
            
        except Exception as e:
            print(f"❌ Provisioning demo failed: {e}")
            return False
    
    async def demo_batch_operations(self, credentials: dict):
        """Demonstrate batch user operations"""
        print("\n📦 Starting batch operations demo...")
        
        try:
            provisioner = DropboxProvisioner(self.browser_manager, self.ai_agent)
            
            # Create multiple provisioning requests
            batch_requests = [
                UserProvisioningRequest(
                    action=ProvisioningAction.ADD_USER,
                    user_email=f"batch.user{i}@example.com",
                    user_name=f"Batch User {i}",
                    role="Member"
                ) for i in range(1, 4)
            ]
            
            print(f"🔄 Processing {len(batch_requests)} batch requests...")
            results = await provisioner.batch_provision(batch_requests, credentials)
            
            success_count = sum(1 for r in results if r.success)
            print(f"✅ Batch operation completed: {success_count}/{len(results)} successful")
            
            return results
            
        except Exception as e:
            print(f"❌ Batch operations demo failed: {e}")
            return []
    
    async def demo_ai_adaptation(self):
        """Demonstrate AI adaptation to UI changes"""
        print("\n🤖 Starting AI adaptation demo...")
        
        try:
            # Simulate a page with changed UI
            await self.browser_manager.navigate("https://example.com")
            page_content = await self.browser_manager.get_page_content()
            
            # Analyze page structure
            analysis = self.ai_agent.analyze_page(page_content)
            print(f"🔍 Page analysis: {analysis}")
            
            # Generate automation steps
            goal = "Extract user information from this page"
            steps = self.ai_agent.generate_automation_steps(goal, analysis)
            
            print(f"📋 Generated {len(steps)} automation steps:")
            for i, step in enumerate(steps, 1):
                print(f"  {i}. {step.description}")
            
            # Demonstrate selector adaptation
            old_selector = "button.old-class"
            new_selector = self.ai_agent.adapt_to_ui_changes(old_selector, page_content)
            print(f"🔄 Adapted selector: {old_selector} → {new_selector}")
            
            return True
            
        except Exception as e:
            print(f"❌ AI adaptation demo failed: {e}")
            return False
    
    async def cleanup(self):
        """Clean up resources"""
        if self.browser_manager:
            await self.browser_manager.close()
        print("🧹 Cleanup completed")

async def main():
    """Main demo function"""
    print("🚀 AI-Driven SaaS User Management Automation Demo")
    print("=" * 50)
    
    # Initialize demo
    demo = SaaSAutomationDemo()
    
    try:
        await demo.setup()
        
        # Load credentials from environment variables or prompt user
        credentials = {
            "username": os.getenv("DEMO_USERNAME", ""),
            "password": os.getenv("DEMO_PASSWORD", ""),
            "mfa_code": os.getenv("DEMO_MFA_CODE", "")  # Optional MFA code
        }
        
        # Check if credentials are provided
        if not credentials["username"] or not credentials["password"]:
            print("⚠️  No credentials found in environment variables.")
            print("Set DEMO_USERNAME and DEMO_PASSWORD environment variables to run demos.")
            credentials = None
        
        # Run demos based on available credentials
        if credentials:
            print("\n✅ Credentials found. Running full demo suite...")
            
            # 1. User scraping demo
            # users = await demo.demo_user_scraping(credentials)
            
            # 2. User provisioning demo
            # await demo.demo_user_provisioning(credentials)
            
            # 3. Batch operations demo
            # await demo.demo_batch_operations(credentials)
        else:
            print("\n⚠️  Running limited demo without credentials...")
        
        # 4. AI adaptation demo (doesn't require credentials)
        await demo.demo_ai_adaptation()
        
        print("\n✅ Demo completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
    
    finally:
        await demo.cleanup()

if __name__ == "__main__":
    # Create .env file template if it doesn't exist
    if not os.path.exists(".env"):
        with open(".env", "w") as f:
            f.write("OPENAI_API_KEY=your_openai_api_key_here\n")
        print("📝 Created .env file template. Please add your OpenAI API key.")
    
    asyncio.run(main())