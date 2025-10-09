#!/usr/bin/env python3
"""
Test cases for AI-driven SaaS automation system
"""

import unittest
import asyncio
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.core.browser_manager import BrowserManager
from src.core.ai_agent import AIAgent
from src.utils.data_processor import DataProcessor
from src.scrapers.base_scraper import UserData
from src.provisioning.base_provisioner import UserProvisioningRequest, ProvisioningAction

class TestDataProcessor(unittest.TestCase):
    """Test data processing utilities"""
    
    def test_normalize_email(self):
        """Test email normalization"""
        self.assertEqual(DataProcessor.normalize_email("  TEST@EXAMPLE.COM  "), "test@example.com")
        self.assertEqual(DataProcessor.normalize_email(""), "")
    
    def test_normalize_name(self):
        """Test name normalization"""
        self.assertEqual(DataProcessor.normalize_name("  john   doe  "), "John Doe")
        self.assertEqual(DataProcessor.normalize_name(""), "")
    
    def test_normalize_role(self):
        """Test role normalization"""
        self.assertEqual(DataProcessor.normalize_role("admin"), "Administrator")
        self.assertEqual(DataProcessor.normalize_role("OWNER"), "Owner")
        self.assertEqual(DataProcessor.normalize_role("custom_role"), "Custom_Role")
    
    def test_normalize_status(self):
        """Test status normalization"""
        self.assertEqual(DataProcessor.normalize_status("active"), "Active")
        self.assertEqual(DataProcessor.normalize_status("PENDING"), "Pending")
        self.assertEqual(DataProcessor.normalize_status("disabled"), "Inactive")
    
    def test_validate_user_data(self):
        """Test user data validation"""
        valid_user = {
            "name": "John Doe",
            "email": "john@example.com",
            "role": "Admin",
            "status": "Active"
        }
        self.assertTrue(DataProcessor.validate_user_data(valid_user))
        
        invalid_user = {
            "name": "",
            "email": "invalid-email",
            "role": "Admin"
        }
        self.assertFalse(DataProcessor.validate_user_data(invalid_user))
    
    def test_deduplicate_users(self):
        """Test user deduplication"""
        users = [
            {"email": "john@example.com", "name": "John Doe"},
            {"email": "jane@example.com", "name": "Jane Smith"},
            {"email": "john@example.com", "name": "John Doe Duplicate"}
        ]
        
        unique_users = DataProcessor.deduplicate_users(users)
        self.assertEqual(len(unique_users), 2)
        
        emails = [user["email"] for user in unique_users]
        self.assertIn("john@example.com", emails)
        self.assertIn("jane@example.com", emails)

class TestBrowserManager(unittest.TestCase):
    """Test browser management functionality"""
    
    def setUp(self):
        """Set up test browser manager"""
        self.browser_manager = BrowserManager(headless=True)
    
    def tearDown(self):
        """Clean up browser resources"""
        if self.browser_manager:
            asyncio.run(self.browser_manager.close())
    
    def test_browser_initialization(self):
        """Test browser initialization"""
        async def run_test():
            await self.browser_manager.start()
            self.assertIsNotNone(self.browser_manager.browser)
            self.assertIsNotNone(self.browser_manager.page)
        
        asyncio.run(run_test())
    
    def test_navigation(self):
        """Test page navigation"""
        async def run_test():
            await self.browser_manager.start()
            success = await self.browser_manager.navigate("https://example.com")
            self.assertTrue(success)
            
            content = await self.browser_manager.get_page_content()
            self.assertIn("Example Domain", content)
        
        asyncio.run(run_test())

class TestAIAgent(unittest.TestCase):
    """Test AI agent functionality"""
    
    def setUp(self):
        """Set up test AI agent"""
        # Skip if no API key available
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            self.skipTest("OpenAI API key not available")
        
        self.ai_agent = AIAgent(api_key)
    
    def test_page_analysis(self):
        """Test page content analysis"""
        sample_html = """
        <html>
            <body>
                <form>
                    <input type="email" name="username" />
                    <input type="password" name="password" />
                    <button type="submit">Login</button>
                </form>
                <table class="users-table">
                    <tr><td>John Doe</td><td>john@example.com</td></tr>
                </table>
            </body>
        </html>
        """
        
        analysis = self.ai_agent.analyze_page(sample_html)
        self.assertIsInstance(analysis, dict)
    
    def test_user_data_extraction(self):
        """Test user data extraction from HTML"""
        sample_html = """
        <table>
            <tr>
                <td>John Doe</td>
                <td>john@example.com</td>
                <td>Admin</td>
                <td>2024-01-15</td>
                <td>Active</td>
            </tr>
        </table>
        """
        
        users = self.ai_agent.extract_user_data(sample_html)
        self.assertIsInstance(users, list)

class TestProvisioningRequest(unittest.TestCase):
    """Test provisioning request functionality"""
    
    def test_provisioning_request_creation(self):
        """Test creating provisioning requests"""
        request = UserProvisioningRequest(
            action=ProvisioningAction.ADD_USER,
            user_email="test@example.com",
            user_name="Test User",
            role="Member"
        )
        
        self.assertEqual(request.action, ProvisioningAction.ADD_USER)
        self.assertEqual(request.user_email, "test@example.com")
        self.assertEqual(request.user_name, "Test User")
        self.assertEqual(request.role, "Member")

class TestIntegration(unittest.TestCase):
    """Integration tests for the complete system"""
    
    def setUp(self):
        """Set up integration test environment"""
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            self.skipTest("OpenAI API key not available for integration tests")
    
    def test_end_to_end_workflow(self):
        """Test complete scraping and provisioning workflow"""
        async def run_integration_test():
            # Initialize components
            browser_manager = BrowserManager(headless=True)
            ai_agent = AIAgent(self.api_key)
            
            try:
                await browser_manager.start()
                
                # Test navigation to a public page
                success = await browser_manager.navigate("https://httpbin.org/html")
                self.assertTrue(success)
                
                # Test page content extraction
                content = await browser_manager.get_page_content()
                self.assertIsNotNone(content)
                
                # Test AI analysis (with simplified HTML)
                simple_html = "<div>Test content</div>"
                analysis = ai_agent.analyze_page(simple_html)
                self.assertIsInstance(analysis, dict)
                
            finally:
                await browser_manager.close()
        
        asyncio.run(run_integration_test())

def run_tests():
    """Run all tests"""
    print("🧪 Running AI-Driven SaaS Automation Tests")
    print("=" * 50)
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test cases
    test_suite.addTest(unittest.makeSuite(TestDataProcessor))
    test_suite.addTest(unittest.makeSuite(TestBrowserManager))
    test_suite.addTest(unittest.makeSuite(TestProvisioningRequest))
    
    # Add AI and integration tests only if API key is available
    if os.getenv("OPENAI_API_KEY"):
        test_suite.addTest(unittest.makeSuite(TestAIAgent))
        test_suite.addTest(unittest.makeSuite(TestIntegration))
    else:
        print("⚠️  Skipping AI and integration tests (no OpenAI API key)")
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print("\n" + "=" * 50)
    if result.wasSuccessful():
        print("✅ All tests passed!")
    else:
        print(f"❌ {len(result.failures)} test(s) failed, {len(result.errors)} error(s)")
        
        if result.failures:
            print("\nFailures:")
            for test, traceback in result.failures:
                print(f"  - {test}: {traceback}")
        
        if result.errors:
            print("\nErrors:")
            for test, traceback in result.errors:
                print(f"  - {test}: {traceback}")

if __name__ == "__main__":
    run_tests()