# AI-Driven Web Automation for SaaS User Management

## Overview
AI-powered solution for automating SaaS user management tasks including data scraping and provisioning/deprovisioning without relying on APIs.

## Key Features
- AI-driven web automation using OpenAI GPT models
- Headless browser automation with Playwright
- Multi-SaaS application support (Dropbox, Notion, HubSpot, Trello)
- Authentication handling (MFA, session management)
- CAPTCHA solving capabilities
- Extensible architecture for adding new SaaS applications

## Installation
```bash
pip install -r requirements.txt
playwright install
```

## Quick Test
```bash
python test_submission.py
```

## Usage
See `examples/demo.py` for implementation examples.

## Project Structure
- `src/core/` - Core automation components (AI agent, browser manager, auth handler)
- `src/scrapers/` - Data scraping framework with SaaS-specific implementations
- `src/provisioning/` - User management framework with SaaS-specific implementations
- `src/utils/` - Utility components (data processing, CAPTCHA solving)
- `config/` - SaaS application configurations
- `tests/` - Test cases
- `examples/` - Demo implementation