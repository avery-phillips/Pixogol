import pytesseract
from PIL import Image
import cv2
import numpy as np
import streamlit as st

def extract_text_from_image(image):
    """
    Extract text from an image using Tesseract OCR
    
    Args:
        image: PIL Image object
        
    Returns:
        str: Extracted text from the image
    """
    try:
        # Convert PIL image to numpy array for OpenCV processing
        img_array = np.array(image)
        
        # Convert RGB to BGR if needed (for OpenCV)
        if len(img_array.shape) == 3 and img_array.shape[2] == 3:
            img_array = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
        
        # Preprocess image for better OCR results
        processed_image = preprocess_image(img_array)
        
        # Configure Tesseract
        custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789.,!?@#$%^&*()_+-=[]{}|;:\'\"<>?/~` '
        
        # Extract text
        text = pytesseract.image_to_string(processed_image, config=custom_config)
        
        # Clean up the extracted text
        cleaned_text = clean_extracted_text(text)
        
        return cleaned_text
        
    except Exception as e:
        st.error(f"OCR processing failed: {str(e)}")
        return ""

def preprocess_image(image):
    """
    Preprocess image to improve OCR accuracy
    
    Args:
        image: OpenCV image array
        
    Returns:
        Preprocessed image array
    """
    try:
        # Convert to grayscale
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        
        # Apply Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Apply threshold to get binary image
        _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Apply morphological operations to clean up the image
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        processed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
        
        return processed
        
    except Exception as e:
        # If preprocessing fails, return original image
        st.warning(f"Image preprocessing failed, using original: {str(e)}")
        return image

def clean_extracted_text(text):
    """
    Clean and normalize extracted text
    
    Args:
        text: Raw text from OCR
        
    Returns:
        str: Cleaned text
    """
    if not text:
        return ""
    
    # Remove excessive whitespace
    lines = text.split('\n')
    cleaned_lines = []
    
    for line in lines:
        # Strip whitespace and skip empty lines
        cleaned_line = line.strip()
        if cleaned_line:
            cleaned_lines.append(cleaned_line)
    
    # Join lines with single spaces
    cleaned_text = ' '.join(cleaned_lines)
    
    # Remove multiple consecutive spaces
    import re
    cleaned_text = re.sub(r'\s+', ' ', cleaned_text)
    
    return cleaned_text.strip()

def get_text_confidence(image):
    """
    Get confidence scores for OCR results
    
    Args:
        image: PIL Image object
        
    Returns:
        dict: Confidence metrics
    """
    try:
        img_array = np.array(image)
        if len(img_array.shape) == 3:
            img_array = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
        
        processed_image = preprocess_image(img_array)
        
        # Get detailed OCR data
        data = pytesseract.image_to_data(processed_image, output_type=pytesseract.Output.DICT)
        
        # Calculate average confidence
        confidences = [int(conf) for conf in data['conf'] if int(conf) > 0]
        
        if confidences:
            avg_confidence = sum(confidences) / len(confidences)
            min_confidence = min(confidences)
            max_confidence = max(confidences)
            
            return {
                'average_confidence': avg_confidence,
                'min_confidence': min_confidence,
                'max_confidence': max_confidence,
                'total_words': len(confidences)
            }
        else:
            return {
                'average_confidence': 0,
                'min_confidence': 0,
                'max_confidence': 0,
                'total_words': 0
            }
            
    except Exception as e:
        st.warning(f"Could not calculate OCR confidence: {str(e)}")
        return {
            'average_confidence': 0,
            'min_confidence': 0,
            'max_confidence': 0,
            'total_words': 0
        }
