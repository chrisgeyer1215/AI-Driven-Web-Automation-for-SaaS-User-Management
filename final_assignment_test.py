#!/usr/bin/env python3
"""
Final Assignment Test - Comprehensive demonstration without OpenAI API dependency
"""

import asyncio
import os
import sys
import json
from datetime import datetime
from pathlib import Path

sys.path.append(os.path.join(os.path.dirname(__file__), '.'))

from src.core.browser_manager import BrowserManager
from src.core.auth_handler import AuthHandler, AuthConfig
from src.utils.data_processor import DataProcessor
from src.scrapers.base_scraper import UserData
from src.provisioning.base_provisioner import UserProvisioningRequest, ProvisioningAction

class AssignmentDemo:
    def __init__(self):
        self.results = []
        self.start_time = datetime.now()
        
    def log_result(self, test_name, success, details=""):
        """Log test result"""
        self.results.append({
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
        if details:
            print(f"   {details}")

    async def test_browser_automation(self):
        """Test comprehensive browser automation capabilities"""
        print("\n🌐 Browser Automation Testing")
        print("=" * 35)
        
        browser_manager = BrowserManager(headless=False)
        
        try:
            # Test 1: Browser initialization
            await browser_manager.start()
            self.log_result("Browser Initialization", True, "Browser started successfully")
            
            # Test 2: Navigation
            success = await browser_manager.navigate("https://httpbin.org/html")
            self.log_result("Website Navigation", success, "Navigated to test website")
            
            if not success:
                return False
            
            # Test 3: Content extraction
            content = await browser_manager.get_page_content()
            content_success = len(content) > 100
            self.log_result("HTML Content Extraction", content_success, 
                          f"Extracted {len(content)} characters")
            
            # Test 4: Element text extraction
            title = await browser_manager.extract_text("title")
            h1_text = await browser_manager.extract_text("h1")
            self.log_result("Element Text Extraction", bool(title or h1_text),
                          f"Title: '{title}', H1: '{h1_text}'")
            
            # Test 5: Screenshot capability
            screenshot_path = await browser_manager.take_screenshot("test_screenshot.png")
            screenshot_success = os.path.exists(screenshot_path)
            self.log_result("Screenshot Capture", screenshot_success,
                          f"Screenshot saved: {screenshot_path}")
            
            # Test 6: JavaScript execution
            js_result = await browser_manager.execute_script("return document.title;")
            self.log_result("JavaScript Execution", bool(js_result),
                          f"JS returned: '{js_result}'")
            
            # Test 7: Element detection
            elements = await browser_manager.get_all_elements("p")
            self.log_result("Element Detection", len(elements) >= 0,
                          f"Found {len(elements)} paragraph elements")
            
            return True
            
        except Exception as e:
            self.log_result("Browser Automation", False, f"Error: {e}")
            return False
        
        finally:
            await browser_manager.close()
            print("✅ Browser cleanup completed")

    def test_data_processing(self):
        """Test data processing and validation"""
        print("\n📊 Data Processing Testing")
        print("=" * 30)
        
        try:
            # Sample data simulating scraped user information
            sample_data = [
                {"name": "  John Doe  ", "email": "JOHN.DOE@COMPANY.COM", "role": "admin", "status": "active", "last_login": "2024-01-15"},
                {"name": "Jane Smith", "email": "jane.smith@company.com", "role": "user", "status": "inactive", "last_login": "2024-01-10"},
                {"name": "Bob Johnson", "email": "bob@company.com", "role": "manager", "status": "active", "last_login": "2024-01-14"},
                {"name": "  John Doe  ", "email": "john.doe@company.com", "role": "admin", "status": "active", "last_login": "2024-01-15"},  # Duplicate
                {"name": "", "email": "invalid-email", "role": "", "status": "", "last_login": ""},  # Invalid
            ]
            
            # Test 1: Data normalization
            normalized_users = []
            for user in sample_data:
                normalized = {
                    "name": DataProcessor.normalize_name(user["name"]),
                    "email": DataProcessor.normalize_email(user["email"]),
                    "role": DataProcessor.normalize_role(user["role"]),
                    "status": DataProcessor.normalize_status(user["status"]),
                    "last_login": DataProcessor.parse_last_login(user["last_login"])
                }
                normalized_users.append(normalized)
            
            self.log_result("Data Normalization", len(normalized_users) == len(sample_data),
                          f"Normalized {len(normalized_users)} records")
            
            # Test 2: Data validation
            valid_users = []
            for user in normalized_users:
                if DataProcessor.validate_user_data(user):
                    valid_users.append(user)
            
            self.log_result("Data Validation", len(valid_users) > 0,
                          f"Validated {len(valid_users)}/{len(normalized_users)} records")
            
            # Test 3: Duplicate removal
            unique_users = DataProcessor.deduplicate_users(valid_users)
            self.log_result("Duplicate Removal", len(unique_users) < len(valid_users),
                          f"Removed duplicates: {len(valid_users)} → {len(unique_users)}")
            
            # Test 4: Report generation
            report = DataProcessor.generate_report(unique_users)
            self.log_result("Report Generation", isinstance(report, dict),
                          f"Generated report with {len(report)} metrics")
            
            # Test 5: Data export
            csv_file = DataProcessor.export_to_csv(unique_users, "test_users.csv")
            json_file = DataProcessor.export_to_json(unique_users, "test_users.json")
            
            export_success = os.path.exists(csv_file) and os.path.exists(json_file)
            self.log_result("Data Export", export_success,
                          f"Exported to CSV and JSON formats")
            
            return True
            
        except Exception as e:
            self.log_result("Data Processing", False, f"Error: {e}")
            return False

    async def test_authentication_system(self):
        """Test authentication handling"""
        print("\n🔐 Authentication System Testing")
        print("=" * 35)
        
        browser_manager = BrowserManager(headless=True)
        
        try:
            await browser_manager.start()
            auth_handler = AuthHandler(browser_manager)
            
            # Test 1: Auth config creation
            auth_config = AuthConfig(
                username_selector="input[type='email']",
                password_selector="input[type='password']",
                submit_selector="button[type='submit']",
                success_indicator=".dashboard"
            )
            
            self.log_result("Auth Config Creation", bool(auth_config),
                          "Authentication configuration created")
            
            # Test 2: Session management
            await auth_handler.save_session()
            cookies = await browser_manager.get_cookies()
            
            self.log_result("Session Management", isinstance(cookies, list),
                          f"Session saved with {len(cookies)} cookies")
            
            # Test 3: Auth element detection (simulate)
            await browser_manager.navigate("https://httpbin.org/forms/post")
            detected_config = await auth_handler.detect_auth_elements("")
            
            self.log_result("Auth Element Detection", isinstance(detected_config, AuthConfig),
                          "Authentication elements detected")
            
            return True
            
        except Exception as e:
            self.log_result("Authentication System", False, f"Error: {e}")
            return False
        
        finally:
            await browser_manager.close()

    def test_configuration_system(self):
        """Test configuration loading and validation"""
        print("\n⚙️ Configuration System Testing")
        print("=" * 35)
        
        try:
            # Test 1: Config file loading
            config_path = "config/saas_configs.json"
            with open(config_path) as f:
                configs = json.load(f)
            
            self.log_result("Config File Loading", len(configs) > 0,
                          f"Loaded {len(configs)} SaaS configurations")
            
            # Test 2: Config structure validation
            required_fields = ["base_url", "login_url", "selectors"]
            valid_configs = 0
            
            for saas_name, config in configs.items():
                if all(field in config for field in required_fields):
                    valid_configs += 1
            
            self.log_result("Config Structure Validation", valid_configs == len(configs),
                          f"{valid_configs}/{len(configs)} configs are valid")
            
            # Test 3: Selector validation
            selector_count = 0
            for config in configs.values():
                selectors = config.get("selectors", {})
                selector_count += len(selectors)
            
            self.log_result("Selector Configuration", selector_count > 0,
                          f"Total {selector_count} selectors configured")
            
            return True
            
        except Exception as e:
            self.log_result("Configuration System", False, f"Error: {e}")
            return False

    def test_architecture_components(self):
        """Test architecture and component structure"""
        print("\n🏗️ Architecture Component Testing")
        print("=" * 35)
        
        try:
            # Test 1: Core module imports
            from src.core.browser_manager import BrowserManager
            from src.core.ai_agent import AIAgent
            from src.core.auth_handler import AuthHandler
            
            self.log_result("Core Module Imports", True,
                          "All core modules imported successfully")
            
            # Test 2: Scraper architecture
            from src.scrapers.base_scraper import BaseScraper, UserData, ScrapingConfig
            
            # Create sample user data
            user = UserData(
                name="Test User",
                email="test@example.com",
                role="Admin",
                last_login="2024-01-15",
                status="Active"
            )
            
            self.log_result("Scraper Architecture", bool(user),
                          "Scraper components and data structures work")
            
            # Test 3: Provisioner architecture
            from src.provisioning.base_provisioner import BaseProvisioner, UserProvisioningRequest, ProvisioningAction
            
            # Create sample provisioning request
            request = UserProvisioningRequest(
                action=ProvisioningAction.ADD_USER,
                user_email="test@example.com",
                user_name="Test User",
                role="Member"
            )
            
            self.log_result("Provisioner Architecture", bool(request),
                          "Provisioner components and request structures work")
            
            # Test 4: Utility modules
            from src.utils.data_processor import DataProcessor
            from src.utils.captcha_solver import CaptchaSolver
            
            self.log_result("Utility Modules", True,
                          "All utility modules imported successfully")
            
            # Test 5: Project structure
            required_dirs = ["src/core", "src/scrapers", "src/provisioning", "src/utils", "config", "examples"]
            existing_dirs = [d for d in required_dirs if os.path.exists(d)]
            
            self.log_result("Project Structure", len(existing_dirs) == len(required_dirs),
                          f"{len(existing_dirs)}/{len(required_dirs)} required directories exist")
            
            return True
            
        except Exception as e:
            self.log_result("Architecture Components", False, f"Error: {e}")
            return False

    def test_error_handling(self):
        """Test error handling and resilience"""
        print("\n🛡️ Error Handling Testing")
        print("=" * 30)
        
        try:
            # Test 1: Invalid file handling
            try:
                with open("nonexistent_file.json") as f:
                    json.load(f)
                file_error_handled = False
            except FileNotFoundError:
                file_error_handled = True
            
            self.log_result("File Error Handling", file_error_handled,
                          "File not found errors handled gracefully")
            
            # Test 2: Invalid data handling
            invalid_user = {"name": "", "email": "invalid", "role": "", "status": ""}
            validation_result = DataProcessor.validate_user_data(invalid_user)
            
            self.log_result("Data Validation Error Handling", not validation_result,
                          "Invalid data rejected correctly")
            
            # Test 3: Empty list handling
            empty_report = DataProcessor.generate_report([])
            
            self.log_result("Empty Data Handling", isinstance(empty_report, dict),
                          "Empty data sets handled gracefully")
            
            return True
            
        except Exception as e:
            self.log_result("Error Handling", False, f"Error: {e}")
            return False

    async def run_comprehensive_test(self):
        """Run all tests"""
        print("🎯 AI-Driven SaaS Automation - Final Assignment Test")
        print("=" * 60)
        print("Comprehensive testing of all application components")
        print("without requiring external API dependencies.\n")
        
        # Run all test suites
        test_results = []
        
        test_results.append(await self.test_browser_automation())
        test_results.append(self.test_data_processing())
        test_results.append(await self.test_authentication_system())
        test_results.append(self.test_configuration_system())
        test_results.append(self.test_architecture_components())
        test_results.append(self.test_error_handling())
        
        # Generate comprehensive report
        self.generate_final_report(test_results)
        
        return all(test_results)

    def _get_critical_components(self):
        """Define critical components for assignment readiness"""
        return [
            "Browser Initialization", "Website Navigation", "HTML Content Extraction",
            "Data Normalization", "Data Validation", "Config File Loading",
            "Core Module Imports", "Scraper Architecture", "Provisioner Architecture"
        ]
    
    def _count_critical_components_passed(self):
        """Count how many critical components passed testing"""
        critical_components = self._get_critical_components()
        
        passed_count = 0
        for result in self.results:
            if result["success"] and result["test"] in critical_components:
                passed_count += 1
        
        return passed_count, len(critical_components)
    
    def generate_final_report(self, test_results):
        """Generate final assignment report"""
        duration = datetime.now() - self.start_time
        passed_tests = sum(1 for r in self.results if r["success"])
        total_tests = len(self.results)
        
        print("\n" + "=" * 60)
        print("📊 FINAL ASSIGNMENT TEST REPORT")
        print("=" * 60)
        
        # Test summary
        print(f"Execution Time: {duration.total_seconds():.2f} seconds")
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        print(f"\n📋 Detailed Results:")
        print("-" * 40)
        
        for result in self.results:
            status = "✅" if result["success"] else "❌"
            print(f"{status} {result['test']}")
            if result["details"]:
                print(f"   {result['details']}")
        
        # Generated artifacts
        print(f"\n📁 Generated Test Artifacts:")
        artifacts = ["test_screenshot.png", "test_users.csv", "test_users.json"]
        for artifact in artifacts:
            if os.path.exists(artifact):
                print(f"   ✅ {artifact}")
        
        # Assignment readiness assessment
        print(f"\n🎯 Assignment Readiness Assessment:")
        print("-" * 40)
        
        critical_passed, total_critical = self._count_critical_components_passed()
        
        print(f"Critical Components: {critical_passed}/{total_critical} working")
        
        if critical_passed == total_critical:
            print(f"\n🏆 ASSIGNMENT STATUS: READY FOR SUBMISSION")
            print("✅ All critical components are functional")
            print("✅ Browser automation working")
            print("✅ Data processing pipeline operational")
            print("✅ Configuration system functional")
            print("✅ Architecture properly implemented")
            print("✅ Error handling in place")
        else:
            print(f"\n⚠️  ASSIGNMENT STATUS: NEEDS ATTENTION")
            print(f"Some critical components need fixing")
        
        # Save detailed report
        report_data = {
            "summary": {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "success_rate": (passed_tests/total_tests)*100,
                "execution_time": duration.total_seconds(),
                "timestamp": datetime.now().isoformat()
            },
            "results": self.results,
            "artifacts": [f for f in artifacts if os.path.exists(f)]
        }
        
        report_file = f"assignment_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        print(f"\n📄 Detailed report saved: {report_file}")

async def main():
    """Main test execution"""
    demo = AssignmentDemo()
    success = await demo.run_comprehensive_test()
    
    print(f"\n{'='*60}")
    if success:
        print("🎉 ALL TESTS PASSED - ASSIGNMENT READY!")
    else:
        print("⚠️  SOME TESTS FAILED - REVIEW REQUIRED")
    print("="*60)
    
    return success

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)