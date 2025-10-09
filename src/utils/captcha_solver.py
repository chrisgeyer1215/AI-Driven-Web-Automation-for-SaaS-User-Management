import cv2
import pytesseract
from PIL import Image
import numpy as np
from typing import Optional
import base64
import io

class CaptchaSolver:
    """CAPTCHA solving utilities using OCR and image processing"""
    
    def __init__(self):
        self.tesseract_config = '--oem 3 --psm 6 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    
    def solve_text_captcha(self, image_path: str) -> Optional[str]:
        """Solve text-based CAPTCHA using OCR"""
        try:
            # Load and preprocess image
            image = cv2.imread(image_path)
            processed_image = self.preprocess_image(image)
            
            # Extract text using OCR
            text = pytesseract.image_to_string(processed_image, config=self.tesseract_config)
            
            # Clean extracted text
            cleaned_text = ''.join(c for c in text if c.isalnum()).upper()
            
            return cleaned_text if len(cleaned_text) > 3 else None
            
        except Exception as e:
            print(f"CAPTCHA solving failed: {e}")
            return None
    
    def preprocess_image(self, image):
        """Preprocess image for better OCR accuracy"""
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Apply threshold to get binary image
        _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Remove noise using morphological operations
        kernel = np.ones((2, 2), np.uint8)
        cleaned = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
        
        # Resize image for better OCR
        height, width = cleaned.shape
        if height < 50:
            scale_factor = 50 / height
            new_width = int(width * scale_factor)
            cleaned = cv2.resize(cleaned, (new_width, 50), interpolation=cv2.INTER_CUBIC)
        
        return cleaned
    
    def solve_math_captcha(self, image_path: str) -> Optional[str]:
        """Solve mathematical CAPTCHA"""
        try:
            # Extract text first
            text = self.solve_text_captcha(image_path)
            if not text:
                return None
            
            # Look for mathematical expressions
            import re
            
            # Simple addition/subtraction patterns
            math_pattern = r'(\d+)\s*([+\-])\s*(\d+)'
            match = re.search(math_pattern, text)
            
            if match:
                num1, operator, num2 = match.groups()
                num1, num2 = int(num1), int(num2)
                
                if operator == '+':
                    result = num1 + num2
                elif operator == '-':
                    result = num1 - num2
                else:
                    return None
                
                return str(result)
            
            return None
            
        except Exception as e:
            print(f"Math CAPTCHA solving failed: {e}")
            return None
    
    def detect_captcha_type(self, image_path: str) -> str:
        """Detect the type of CAPTCHA"""
        try:
            text = pytesseract.image_to_string(Image.open(image_path))
            
            if any(op in text for op in ['+', '-', '=', 'plus', 'minus']):
                return "math"
            elif any(char.isdigit() for char in text) and any(char.isalpha() for char in text):
                return "alphanumeric"
            elif any(char.isalpha() for char in text):
                return "text"
            else:
                return "unknown"
                
        except:
            return "unknown"