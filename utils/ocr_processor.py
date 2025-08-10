import pytesseract
from PIL import Image
import cv2
import numpy as np
import streamlit as st

def extract_text_from_image(image):
    """
    Extract text from an image using optimized OCR for branded merchandise
    
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
        
        # Try multiple focused OCR approaches
        all_extracted_text = []
        
        # Approach 1: Basic OCR on original image
        try:
            gray = cv2.cvtColor(img_array, cv2.COLOR_BGR2GRAY) if len(img_array.shape) == 3 else img_array
            text1 = pytesseract.image_to_string(gray, config=r'--oem 3 --psm 6')
            if text1.strip():
                all_extracted_text.append(clean_extracted_text(text1))
        except:
            pass
            
        # Approach 2: Enhanced contrast
        try:
            gray = cv2.cvtColor(img_array, cv2.COLOR_BGR2GRAY) if len(img_array.shape) == 3 else img_array
            enhanced = cv2.equalizeHist(gray)
            text2 = pytesseract.image_to_string(enhanced, config=r'--oem 3 --psm 6')
            if text2.strip():
                all_extracted_text.append(clean_extracted_text(text2))
        except:
            pass
            
        # Approach 3: Color-based text extraction (good for branded items)
        try:
            color_text = extract_text_by_color(img_array)
            if color_text.strip():
                all_extracted_text.append(clean_extracted_text(color_text))
        except:
            pass
            
        # Approach 4: High contrast binary thresholding
        try:
            gray = cv2.cvtColor(img_array, cv2.COLOR_BGR2GRAY) if len(img_array.shape) == 3 else img_array
            _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
            text3 = pytesseract.image_to_string(binary, config=r'--oem 3 --psm 8')
            if text3.strip():
                all_extracted_text.append(clean_extracted_text(text3))
        except:
            pass
            
        # Approach 5: Individual word detection with scaling
        try:
            gray = cv2.cvtColor(img_array, cv2.COLOR_BGR2GRAY) if len(img_array.shape) == 3 else img_array
            # Scale up image for better OCR
            scale_factor = 2
            height, width = gray.shape[:2]
            scaled = cv2.resize(gray, (width * scale_factor, height * scale_factor), interpolation=cv2.INTER_CUBIC)
            text4 = pytesseract.image_to_string(scaled, config=r'--oem 3 --psm 8')
            if text4.strip():
                all_extracted_text.append(clean_extracted_text(text4))
        except:
            pass
        
        # Combine all results with quality scoring
        if all_extracted_text:
            # Score each extraction method result
            scored_results = []
            for text in all_extracted_text:
                if text and len(text) > 3:  # Minimum length filter
                    # Calculate quality score
                    words = text.split()
                    if len(words) > 0:
                        # Prefer results with recognizable English words
                        quality_score = calculate_text_quality(text)
                        scored_results.append((text, quality_score))
            
            if scored_results:
                # Sort by quality score (higher is better)
                scored_results.sort(key=lambda x: x[1], reverse=True)
                
                # Use the highest quality result, or combine top results if similar quality
                best_text = scored_results[0][0]
                best_score = scored_results[0][1]
                
                # If multiple results have similar high quality, combine them
                combined_words = set()
                for text, score in scored_results:
                    if score >= best_score * 0.8:  # Within 80% of best score
                        words = text.lower().split()
                        for word in words:
                            if len(word) > 1 and word.isalpha():
                                combined_words.add(word)
                
                return " ".join(sorted(combined_words)) if combined_words else best_text
            
        return ""
        
    except Exception as e:
        st.error(f"OCR processing failed: {str(e)}")
        return ""

def extract_text_by_color(image):
    """
    Extract text by isolating colored regions that likely contain text
    
    Args:
        image: OpenCV image array (BGR)
        
    Returns:
        str: Extracted text from color-isolated regions
    """
    try:
        # Convert BGR to HSV for better color isolation
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        
        # Define color ranges for common brand text colors
        # Red text (like Coca-Cola)
        red_lower1 = np.array([0, 50, 50])
        red_upper1 = np.array([10, 255, 255])
        red_lower2 = np.array([170, 50, 50])
        red_upper2 = np.array([180, 255, 255])
        
        # Black text
        black_lower = np.array([0, 0, 0])
        black_upper = np.array([180, 255, 50])
        
        # White text
        white_lower = np.array([0, 0, 200])
        white_upper = np.array([180, 30, 255])
        
        all_text = []
        
        # Try each color mask
        masks = [
            cv2.inRange(hsv, red_lower1, red_upper1) + cv2.inRange(hsv, red_lower2, red_upper2),
            cv2.inRange(hsv, black_lower, black_upper),
            cv2.inRange(hsv, white_lower, white_upper)
        ]
        
        for mask in masks:
            if np.sum(mask) > 0:  # If mask found something
                # Apply mask and extract text
                masked_image = cv2.bitwise_and(image, image, mask=mask)
                gray_masked = cv2.cvtColor(masked_image, cv2.COLOR_BGR2GRAY)
                
                # Clean up the mask
                kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
                cleaned_mask = cv2.morphologyEx(gray_masked, cv2.MORPH_CLOSE, kernel)
                
                text = pytesseract.image_to_string(cleaned_mask, config=r'--oem 3 --psm 8')
                if text.strip():
                    all_text.append(text.strip())
        
        return ' '.join(all_text)
        
    except Exception:
        return ""

def clean_extracted_text(text):
    """
    Clean and normalize extracted text with quality filtering
    
    Args:
        text: Raw text from OCR
        
    Returns:
        str: Cleaned text or empty string if text quality is poor
    """
    if not text:
        return ""
    
    import re
    
    # Remove excessive whitespace and normalize
    lines = text.split('\n')
    cleaned_lines = []
    
    for line in lines:
        cleaned_line = line.strip()
        if cleaned_line:
            cleaned_lines.append(cleaned_line)
    
    cleaned_text = ' '.join(cleaned_lines)
    cleaned_text = re.sub(r'\s+', ' ', cleaned_text)
    
    # Quality filtering - reject text with too many non-alphanumeric characters
    if cleaned_text:
        # Count alphanumeric vs special characters
        alphanumeric_count = sum(c.isalnum() or c.isspace() for c in cleaned_text)
        total_count = len(cleaned_text)
        
        # If less than 60% of characters are alphanumeric/space, likely garbage
        if total_count > 0 and (alphanumeric_count / total_count) < 0.6:
            return ""
        
        # Remove lines with excessive punctuation or special characters
        words = cleaned_text.split()
        clean_words = []
        
        for word in words:
            # Only keep words that are mostly letters/numbers
            if len(word) >= 2:
                clean_chars = sum(c.isalnum() for c in word)
                if clean_chars / len(word) >= 0.7:  # At least 70% alphanumeric
                    clean_words.append(word)
        
        # Return cleaned text only if we have meaningful words
        if clean_words:
            return ' '.join(clean_words)
    
    return ""

def calculate_text_quality(text):
    """
    Calculate a quality score for extracted text
    
    Args:
        text: Extracted text to evaluate
        
    Returns:
        float: Quality score (0-1, higher is better)
    """
    if not text or len(text) < 2:
        return 0.0
    
    score = 0.0
    
    # Factor 1: Ratio of alphabetic characters
    alpha_ratio = sum(c.isalpha() for c in text) / len(text)
    score += alpha_ratio * 0.4
    
    # Factor 2: Presence of complete words (length > 2)
    words = text.split()
    if words:
        complete_words = [w for w in words if len(w) > 2 and w.isalpha()]
        word_ratio = len(complete_words) / len(words)
        score += word_ratio * 0.3
    
    # Factor 3: Lack of excessive punctuation
    punct_ratio = sum(not c.isalnum() and not c.isspace() for c in text) / len(text)
    score += (1 - punct_ratio) * 0.2
    
    # Factor 4: Reasonable word length distribution
    if words:
        avg_word_length = sum(len(w) for w in words) / len(words)
        # Optimal word length is around 4-8 characters
        if 3 <= avg_word_length <= 10:
            score += 0.1
    
    return min(score, 1.0)

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
            gray = cv2.cvtColor(img_array, cv2.COLOR_BGR2GRAY)
        else:
            gray = img_array
        
        # Get detailed OCR data
        data = pytesseract.image_to_data(gray, output_type=pytesseract.Output.DICT)
        
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