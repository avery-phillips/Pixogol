import pytesseract
from PIL import Image
import cv2
import numpy as np
import streamlit as st

def extract_text_from_image(image):
    """
    Extract text from an image using Tesseract OCR with multiple preprocessing methods
    
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
        
        # Get multiple preprocessed versions of the image
        processed_images = preprocess_image(img_array)
        
        # Try different OCR configurations
        ocr_configs = [
            r'--oem 3 --psm 6',  # Standard config
            r'--oem 3 --psm 8',  # Single word mode (good for logos/brands)
            r'--oem 3 --psm 7',  # Single text line
            r'--oem 3 --psm 11', # Sparse text
            r'--oem 3 --psm 13'  # Raw line without much processing
        ]
        
        all_extracted_text = []
        
        # Try each preprocessing method with selected OCR configs (limit to avoid timeout)
        for processed_img in processed_images[:3]:  # Limit to first 3 methods
            for config in ocr_configs[:3]:  # Limit to first 3 configs
                try:
                    text = pytesseract.image_to_string(processed_img, config=config)
                    if text and text.strip():
                        all_extracted_text.append(clean_extracted_text(text))
                except Exception:
                    continue
        
        # Combine all results and find the best one
        if all_extracted_text:
            # Remove duplicates while preserving order
            unique_texts = []
            for text in all_extracted_text:
                if text and text not in unique_texts:
                    unique_texts.append(text)
            
            # Return the longest result (usually most complete)
            best_text = max(unique_texts, key=len) if unique_texts else ""
            
            # Also combine all unique words found across all attempts
            all_words = set()
            for text in unique_texts:
                words = text.split()
                all_words.update(word.strip('.,!?";:()[]{}') for word in words if len(word) > 1)
            
            combined_text = " ".join(sorted(all_words))
            
            # Return whichever is more comprehensive
            return best_text if len(best_text) > len(combined_text) else combined_text
        else:
            return ""
        
    except Exception as e:
        st.error(f"OCR processing failed: {str(e)}")
        return ""

def preprocess_image(image):
    """
    Preprocess image to improve OCR accuracy with multiple techniques
    
    Args:
        image: OpenCV image array
        
    Returns:
        List of preprocessed image arrays for multi-pass OCR
    """
    try:
        processed_images = []
        
        # Convert to grayscale
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        
        # Method 1: Original grayscale
        processed_images.append(gray)
        
        # Method 2: Enhanced contrast
        enhanced = cv2.equalizeHist(gray)
        processed_images.append(enhanced)
        
        # Method 3: Gaussian blur + threshold
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        processed_images.append(thresh)
        
        # Method 4: Adaptive threshold (good for varying lighting)
        adaptive_thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                               cv2.THRESH_BINARY, 11, 2)
        processed_images.append(adaptive_thresh)
        
        # Method 5: Morphological operations
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
        morph = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
        processed_images.append(morph)
        
        # Method 6: Edge enhancement for text on colored backgrounds
        edges = cv2.Canny(gray, 50, 150)
        dilated_edges = cv2.dilate(edges, kernel, iterations=1)
        processed_images.append(dilated_edges)
        
        return processed_images
        
    except Exception as e:
        # If preprocessing fails, return original image
        st.warning(f"Image preprocessing failed, using original: {str(e)}")
        return [image]

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
