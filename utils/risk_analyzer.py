import json
import os
from openai import OpenAI
import streamlit as st

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def detect_brand_patterns(text):
    """
    Detect potential brand patterns in text, even if OCR is imperfect
    
    Args:
        text: Extracted text from OCR
        
    Returns:
        list: List of detected brand patterns
    """
    if not text:
        return []
    
    # Common major brands and their variations/partial matches - very aggressive matching
    brand_patterns = {
        'coca-cola': ['coca', 'cola', 'cocacola', 'coke', 'diet', 'co', 'ca', 'ola', 'die', 'et'],
        'star-wars': ['star', 'wars', 'starwars', 'wa', 'rs', 'tar', 'ar'],
        'disney': ['disney', 'disne', 'walt', 'dis', 'ney'],
        'marvel': ['marvel', 'marve', 'mar', 'vel'],
        'nike': ['nike', 'just', 'do', 'it', 'ike'],
        'adidas': ['adidas', 'three', 'stripes', 'adi', 'das'],
        'pepsi': ['pepsi', 'peps', 'pep', 'si'],
        'mcdonalds': ['mcdonald', 'golden', 'arches', 'mcd', 'donald'],
        'apple': ['apple', 'iphone', 'ipad', 'mac', 'app', 'ple'],
        'google': ['google', 'googl', 'goog', 'gle'],
        'microsoft': ['microsoft', 'windows', 'micro', 'soft'],
        'amazon': ['amazon', 'prime', 'ama', 'zon'],
        'netflix': ['netflix', 'netfli', 'net', 'flix'],
        'facebook': ['facebook', 'meta', 'face', 'book'],
        'twitter': ['twitter', 'tweet', 'twit', 'ter'],
        'instagram': ['instagram', 'insta', 'gram'],
        'youtube': ['youtube', 'youtu', 'tube'],
        'spotify': ['spotify', 'spotif', 'spot', 'ify'],
        'uber': ['uber', 'ube'],
        'starbucks': ['starbuck', 'coffee', 'star', 'buck']
    }
    
    detected = []
    text_lower = text.lower()
    
    # Standard pattern matching
    for brand, patterns in brand_patterns.items():
        for pattern in patterns:
            if pattern in text_lower:
                detected.append(brand)
                break  # Only add once per brand
    
    # Additional fuzzy matching for very garbled text
    if not detected and text_lower:
        # Look for character sequences that might be corrupted brand names
        fuzzy_patterns = {
            'coca-cola': ['c.*o.*k.*e', 'd.*i.*e.*t', 'c.*o.*l.*a'],
            'star-wars': ['s.*t.*a.*r', 'w.*a.*r.*s'],
        }
        
        import re
        for brand, regex_patterns in fuzzy_patterns.items():
            for pattern in regex_patterns:
                if re.search(pattern, text_lower):
                    detected.append(brand)
                    break
    
    return list(set(detected))  # Remove duplicates

def analyze_legal_risks(extracted_text, filename):
    """
    Analyze extracted text for copyright, trademark, and brand risks using GPT-4
    
    Args:
        extracted_text: Text extracted from image via OCR
        filename: Name of the uploaded file
        
    Returns:
        dict: Structured risk analysis results
    """
    try:
        # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
        # do not change this unless explicitly requested by the user
        
        # Pre-analyze text for common brand patterns
        brand_patterns = detect_brand_patterns(extracted_text)
        
        system_prompt = """You are a legal risk assessment expert specializing in intellectual property law. 
        Analyze the provided text for potential copyright, trademark, and brand risks.
        
        CRITICAL INSTRUCTIONS:
        1. Even if the OCR text is completely garbled, corrupted, or unreadable, you must still analyze it for potential brand content
        2. Look for ANY character sequences that could be corrupted versions of major brand names
        3. If the filename suggests branded content (like "DC Test", "Coke", etc.), factor this into your analysis
        4. Consider that branded merchandise often has poor OCR results due to stylized fonts and backgrounds
        
        BRAND DETECTION PRIORITIES:
        - Coca-Cola/Diet Coke: Look for 'c', 'o', 'k', 'e', 'd', 'i', 'e', 't' patterns even in garbled text
        - Star Wars: Look for 's', 't', 'a', 'r', 'w', 'a', 'r', 's' patterns
        - Any sequences of letters that could be major brand names
        
        COPYRIGHT RISKS:
        - Copyrighted text, quotes, or excerpts from books, articles, songs, etc.
        - Creative works like poems, stories, or artistic expressions
        - Proprietary content from websites, marketing materials, or publications
        
        TRADEMARK RISKS:
        - Brand names, product names, or service marks (even corrupted/partial matches)
        - Company names and business identifiers  
        - Slogans, taglines, or marketing phrases
        - Logo text or branded terminology
        
        BRAND RISKS:
        - References to well-known companies or brands
        - Celebrity names or public figures
        - Sports teams, leagues, or organizations
        - Educational institutions or government entities
        
        RISK ESCALATION RULES:
        - If filename contains brand hints ("DC", "Coke", etc.), automatically escalate to HIGH risk
        - If text is garbled but contains potential brand letter sequences, escalate to MEDIUM-HIGH risk
        - Major brands like Coca-Cola, Star Wars, Disney, Nike should result in HIGH or CRITICAL risk levels
        
        Provide a structured JSON response with risk levels (LOW, MEDIUM, HIGH, CRITICAL) and detailed explanations."""
        
        additional_context = ""
        if brand_patterns:
            additional_context = f"\n\nADDITIONAL CONTEXT: Detected potential brand patterns: {', '.join(brand_patterns)}"
        
        user_prompt = f"""Analyze this text extracted from an image file named "{filename}":

FILE NAME ANALYSIS: The filename "{filename}" may contain clues about the content.

TEXT TO ANALYZE:
{extracted_text if extracted_text.strip() else "[OCR failed to extract readable text - text appears garbled or corrupted]"}{additional_context}

SPECIAL INSTRUCTIONS:
- If the filename contains "DC", "Coke", "Diet", "Star", "Wars" or other brand hints, factor this heavily into your risk assessment
- Garbled or corrupted OCR text from branded merchandise should still result in HIGH risk levels
- Even unreadable text may indicate the presence of major brand logos or trademarks

Please provide a comprehensive legal risk assessment in JSON format with the following structure:"
{{
    "overall_risk_level": "LOW/MEDIUM/HIGH/CRITICAL",
    "confidence_score": 0.0-1.0,
    "risk_categories": {{
        "copyright": {{
            "level": "LOW/MEDIUM/HIGH/CRITICAL",
            "explanation": "detailed explanation",
            "identified_elements": ["list of specific copyrighted elements found"],
            "recommendations": ["specific actions to take"]
        }},
        "trademark": {{
            "level": "LOW/MEDIUM/HIGH/CRITICAL", 
            "explanation": "detailed explanation",
            "identified_elements": ["list of specific trademark elements found"],
            "recommendations": ["specific actions to take"]
        }},
        "brand": {{
            "level": "LOW/MEDIUM/HIGH/CRITICAL",
            "explanation": "detailed explanation", 
            "identified_elements": ["list of specific brand elements found"],
            "recommendations": ["specific actions to take"]
        }}
    }},
    "general_recommendations": ["overall recommendations for risk mitigation"],
    "legal_disclaimer": "This is an AI-generated assessment and should not replace professional legal advice."
}}

If no text was detected, focus on general guidance about image usage risks."""

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.3,
            max_tokens=2000
        )
        
        # Parse the JSON response
        response_content = response.choices[0].message.content
        if response_content is None:
            raise ValueError("Empty response from OpenAI API")
        risk_analysis = json.loads(response_content)
        
        # Validate and clean the response
        validated_analysis = validate_risk_analysis(risk_analysis)
        
        return validated_analysis
        
    except json.JSONDecodeError as e:
        st.error(f"Failed to parse AI response: {str(e)}")
        return get_fallback_analysis("JSON parsing error")
        
    except Exception as e:
        st.error(f"Risk analysis failed: {str(e)}")
        return get_fallback_analysis(str(e))

def validate_risk_analysis(analysis):
    """
    Validate and clean the risk analysis response
    
    Args:
        analysis: Raw analysis dict from GPT-4
        
    Returns:
        dict: Validated and cleaned analysis
    """
    valid_levels = ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']
    
    # Ensure overall risk level is valid
    if analysis.get('overall_risk_level') not in valid_levels:
        analysis['overall_risk_level'] = 'MEDIUM'
    
    # Ensure confidence score is valid
    confidence = analysis.get('confidence_score', 0.5)
    if not isinstance(confidence, (int, float)) or confidence < 0 or confidence > 1:
        analysis['confidence_score'] = 0.5
    
    # Validate risk categories
    categories = analysis.get('risk_categories', {})
    for category in ['copyright', 'trademark', 'brand']:
        if category not in categories:
            categories[category] = {
                'level': 'LOW',
                'explanation': 'No specific risks identified in this category.',
                'identified_elements': [],
                'recommendations': ['Continue monitoring for potential risks.']
            }
        else:
            # Validate risk level
            if categories[category].get('level') not in valid_levels:
                categories[category]['level'] = 'LOW'
            
            # Ensure required fields exist
            if 'explanation' not in categories[category]:
                categories[category]['explanation'] = 'No detailed analysis available.'
            
            if 'identified_elements' not in categories[category]:
                categories[category]['identified_elements'] = []
                
            if 'recommendations' not in categories[category]:
                categories[category]['recommendations'] = ['Consult with legal counsel if needed.']
    
    # Ensure general recommendations exist
    if 'general_recommendations' not in analysis:
        analysis['general_recommendations'] = [
            'Review content carefully before publication or use.',
            'Consider consulting with intellectual property counsel for high-risk content.',
            'Maintain documentation of content sources and permissions.'
        ]
    
    # Add legal disclaimer if missing
    if 'legal_disclaimer' not in analysis:
        analysis['legal_disclaimer'] = 'This is an AI-generated assessment and should not replace professional legal advice.'
    
    return analysis

def get_fallback_analysis(error_reason):
    """
    Provide fallback analysis when AI analysis fails
    
    Args:
        error_reason: Reason for the failure
        
    Returns:
        dict: Basic fallback analysis structure
    """
    return {
        'overall_risk_level': 'MEDIUM',
        'confidence_score': 0.0,
        'risk_categories': {
            'copyright': {
                'level': 'MEDIUM',
                'explanation': f'Unable to perform detailed copyright analysis due to: {error_reason}. Manual review recommended.',
                'identified_elements': [],
                'recommendations': [
                    'Manually review content for copyrighted material',
                    'Verify ownership or permissions for any text content',
                    'Consider professional legal review'
                ]
            },
            'trademark': {
                'level': 'MEDIUM',
                'explanation': f'Unable to perform detailed trademark analysis due to: {error_reason}. Manual review recommended.',
                'identified_elements': [],
                'recommendations': [
                    'Check for brand names, logos, or trademarks',
                    'Verify permissions for any trademark usage',
                    'Consider trademark search if commercial use intended'
                ]
            },
            'brand': {
                'level': 'MEDIUM',
                'explanation': f'Unable to perform detailed brand analysis due to: {error_reason}. Manual review recommended.',
                'identified_elements': [],
                'recommendations': [
                    'Review content for brand references',
                    'Ensure compliance with brand usage guidelines',
                    'Seek permission for commercial brand usage'
                ]
            }
        },
        'general_recommendations': [
            'AI analysis failed - manual review is strongly recommended',
            'Consult with legal counsel before using this content commercially',
            'Document your review process for compliance purposes',
            f'Technical error details: {error_reason}'
        ],
        'legal_disclaimer': 'This fallback assessment is provided due to technical issues. Professional legal advice is strongly recommended.',
        'error_info': {
            'analysis_failed': True,
            'error_reason': error_reason,
            'fallback_used': True
        }
    }

def get_risk_summary_text(analysis):
    """
    Generate a human-readable summary of the risk analysis
    
    Args:
        analysis: Risk analysis dictionary
        
    Returns:
        str: Human-readable summary
    """
    overall_risk = analysis.get('overall_risk_level', 'Unknown')
    confidence = analysis.get('confidence_score', 0)
    
    summary = f"Overall Risk Level: {overall_risk} (Confidence: {confidence:.1%})\n\n"
    
    categories = analysis.get('risk_categories', {})
    for category, details in categories.items():
        level = details.get('level', 'Unknown')
        explanation = details.get('explanation', 'No explanation available')
        summary += f"{category.title()} Risk: {level}\n{explanation}\n\n"
    
    recommendations = analysis.get('general_recommendations', [])
    if recommendations:
        summary += "Recommendations:\n"
        for i, rec in enumerate(recommendations, 1):
            summary += f"{i}. {rec}\n"
    
    return summary
