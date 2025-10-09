import pandas as pd
import json
from typing import List, Dict, Any
from datetime import datetime
import re

class DataProcessor:
    """Utility class for processing and cleaning scraped data"""
    
    @staticmethod
    def normalize_email(email: str) -> str:
        """Normalize email address"""
        if not email:
            return ""
        return email.strip().lower()
    
    @staticmethod
    def normalize_name(name: str) -> str:
        """Normalize user name"""
        if not name:
            return ""
        # Remove extra whitespace and title case
        return ' '.join(name.strip().split()).title()
    
    @staticmethod
    def parse_last_login(login_str: str) -> str:
        """Parse and normalize last login date"""
        if not login_str:
            return ""
        
        # Common date patterns
        patterns = [
            r'\d{4}-\d{2}-\d{2}',  # YYYY-MM-DD
            r'\d{2}/\d{2}/\d{4}',  # MM/DD/YYYY
            r'\d{2}-\d{2}-\d{4}',  # MM-DD-YYYY
        ]
        
        for pattern in patterns:
            match = re.search(pattern, login_str)
            if match:
                return match.group()
        
        # Handle relative dates
        if 'today' in login_str.lower():
            return datetime.now().strftime('%Y-%m-%d')
        elif 'yesterday' in login_str.lower():
            from datetime import timedelta
            yesterday = datetime.now() - timedelta(days=1)
            return yesterday.strftime('%Y-%m-%d')
        
        return login_str.strip()
    
    @staticmethod
    def normalize_role(role: str) -> str:
        """Normalize user role"""
        if not role:
            return "User"
        
        role_mapping = {
            'admin': 'Administrator',
            'administrator': 'Administrator',
            'owner': 'Owner',
            'member': 'Member',
            'user': 'User',
            'guest': 'Guest',
            'viewer': 'Viewer',
            'editor': 'Editor'
        }
        
        normalized = role.strip().lower()
        return role_mapping.get(normalized, role.title())
    
    @staticmethod
    def normalize_status(status: str) -> str:
        """Normalize user status"""
        if not status:
            return "Unknown"
        
        status_mapping = {
            'active': 'Active',
            'inactive': 'Inactive',
            'pending': 'Pending',
            'suspended': 'Suspended',
            'invited': 'Pending',
            'disabled': 'Inactive'
        }
        
        normalized = status.strip().lower()
        return status_mapping.get(normalized, status.title())
    
    @staticmethod
    def validate_user_data(user_data: Dict[str, Any]) -> bool:
        """Validate user data completeness and format"""
        # Check required fields
        if not user_data.get('email') or '@' not in user_data['email']:
            return False
        
        if not user_data.get('name'):
            return False
        
        # Validate email format
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, user_data['email']):
            return False
        
        return True
    
    @staticmethod
    def deduplicate_users(users: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate users based on email"""
        seen_emails = set()
        unique_users = []
        
        for user in users:
            email = user.get('email', '').lower()
            if email and email not in seen_emails:
                seen_emails.add(email)
                unique_users.append(user)
        
        return unique_users
    
    @staticmethod
    def export_to_csv(users: List[Dict[str, Any]], filename: str = "users.csv") -> str:
        """Export user data to CSV"""
        if not users:
            return ""
        
        df = pd.DataFrame(users)
        df.to_csv(filename, index=False)
        return filename
    
    @staticmethod
    def export_to_json(users: List[Dict[str, Any]], filename: str = "users.json") -> str:
        """Export user data to JSON"""
        with open(filename, 'w') as f:
            json.dump(users, f, indent=2)
        return filename
    
    @staticmethod
    def generate_report(users: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate summary report of user data"""
        if not users:
            return {"total_users": 0}
        
        df = pd.DataFrame(users)
        
        report = {
            "total_users": len(users),
            "unique_emails": df['email'].nunique() if 'email' in df.columns else 0,
            "roles_distribution": df['role'].value_counts().to_dict() if 'role' in df.columns else {},
            "status_distribution": df['status'].value_counts().to_dict() if 'status' in df.columns else {},
            "users_with_recent_login": 0,
            "inactive_users": 0
        }
        
        # Calculate recent login stats
        if 'last_login' in df.columns:
            recent_threshold = datetime.now().strftime('%Y-%m-%d')
            # This is a simplified check - in practice, you'd parse dates properly
            report["users_with_recent_login"] = df['last_login'].str.contains(recent_threshold[:7]).sum()
        
        if 'status' in df.columns:
            report["inactive_users"] = (df['status'] == 'Inactive').sum()
        
        return report