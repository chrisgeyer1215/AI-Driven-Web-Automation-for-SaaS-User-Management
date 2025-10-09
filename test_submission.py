#!/usr/bin/env python3
"""
Submission Test Runner - Validates core functionality
"""

import os
import sys
import asyncio

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_imports():
    """Test that all core modules can be imported"""
    print("🔍 Testing core imports...")
    
    try:
        from src.core.ai_agent import AIAgent
        from src.core.browser_manager import BrowserManager
        from src.core.auth_handler import AuthHandler
        from src.scrapers.base_scraper import BaseScraper, UserData
        from src.provisioning.base_provisioner import BaseProvisioner, UserProvisioningRequest
        from src.utils.data_processor import DataProcessor
        from src.utils.captcha_solver import CaptchaSolver
        print("✅ All core modules imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False

def test_data_processing():
    """Test data processing functionality"""
    print("🔍 Testing data processing...")
    
    try:
        from src.utils.data_processor import DataProcessor
        
        # Test basic functionality
        email = DataProcessor.normalize_email("  TEST@EXAMPLE.COM  ")
        assert email == "test@example.com"
        
        name = DataProcessor.normalize_name("  john   doe  ")
        assert name == "John Doe"
        
        valid_user = {"name": "John Doe", "email": "john@example.com"}
        assert DataProcessor.validate_user_data(valid_user)
        
        print("✅ Data processing tests passed")
        return True
    except Exception as e:
        print(f"❌ Data processing test failed: {e}")
        return False

def test_configuration():
    """Test configuration loading"""
    print("🔍 Testing configuration...")
    
    try:
        import json
        with open("config/saas_configs.json", "r") as f:
            config = json.load(f)
        
        assert "dropbox" in config
        assert "notion" in config
        print("✅ Configuration loaded successfully")
        return True
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

async def test_browser():
    """Test browser manager"""
    print("🔍 Testing browser manager...")
    
    try:
        from src.core.browser_manager import BrowserManager
        
        browser = BrowserManager(headless=True)
        await browser.start()
        
        success = await browser.navigate("https://httpbin.org/html")
        if success:
            content = await browser.get_page_content()
            assert len(content) > 100
        
        await browser.close()
        print("✅ Browser manager tests passed")
        return True
    except Exception as e:
        print(f"❌ Browser test failed: {e}")
        return False

async def main():
    """Run submission tests"""
    print("🚀 AI-Driven SaaS Automation - Submission Validation")
    print("=" * 50)
    
    tests = [
        ("Core Imports", test_imports, False),
        ("Data Processing", test_data_processing, False),
        ("Configuration", test_configuration, False),
        ("Browser Manager", test_browser, True),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func, is_async in tests:
        try:
            result = await test_func() if is_async else test_func()
            if result:
                passed += 1
        except Exception as e:
            print(f"❌ {test_name} failed: {e}")
    
    print(f"\n📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 SUBMISSION READY!")
    else:
        print("⚠️  Some tests failed - check setup")

if __name__ == "__main__":
    asyncio.run(main())