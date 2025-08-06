#!/usr/bin/env python3
"""
Test script to verify OCR and risk analysis functionality with the provided image
"""

import os
from PIL import Image
from utils.ocr_processor import extract_text_from_image
from utils.risk_analyzer import analyze_legal_risks
from utils.logger import log_analysis_result
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_image_analysis():
    """Test the image analysis pipeline with the provided image"""
    
    # Load the test image
    image_path = "attached_assets/IMG-20250728-WA0004_1754509902810.jpg"
    
    if not os.path.exists(image_path):
        print(f"Error: Image file not found at {image_path}")
        return
    
    try:
        # Load image
        print("Loading image...")
        image = Image.open(image_path)
        print(f"Image loaded: {image.size[0]} x {image.size[1]} pixels, format: {image.format}")
        
        # Extract text using OCR
        print("\nExtracting text with enhanced OCR...")
        extracted_text = extract_text_from_image(image)
        
        print(f"Extracted text ({len(extracted_text)} characters):")
        print(f"'{extracted_text}'")
        
        if not extracted_text or extracted_text.strip() == "":
            extracted_text = "[No text detected]"
            print("Warning: No text detected by OCR")
        
        # Analyze legal risks
        print("\nAnalyzing legal risks...")
        risk_analysis = analyze_legal_risks(extracted_text, "test_cocacola_starwars.jpg")
        
        # Display results
        print("\n" + "="*50)
        print("RISK ANALYSIS RESULTS")
        print("="*50)
        
        overall_risk = risk_analysis.get('overall_risk_level', 'Unknown')
        confidence = risk_analysis.get('confidence_score', 0)
        
        print(f"Overall Risk Level: {overall_risk}")
        print(f"Confidence Score: {confidence:.2f}")
        
        print("\nRisk Categories:")
        categories = risk_analysis.get('risk_categories', {})
        
        for category, details in categories.items():
            level = details.get('level', 'Unknown')
            explanation = details.get('explanation', 'No explanation')
            elements = details.get('identified_elements', [])
            
            print(f"\n{category.upper()} RISK: {level}")
            print(f"Explanation: {explanation}")
            if elements:
                print(f"Identified elements: {', '.join(elements)}")
        
        # General recommendations
        recommendations = risk_analysis.get('general_recommendations', [])
        if recommendations:
            print("\nGeneral Recommendations:")
            for i, rec in enumerate(recommendations, 1):
                print(f"{i}. {rec}")
        
        # Log the analysis
        print("\nLogging analysis...")
        analysis_id = log_analysis_result("test_cocacola_starwars.jpg", extracted_text, risk_analysis)
        print(f"Analysis logged with ID: {analysis_id}")
        
        print("\nTest completed successfully!")
        
    except Exception as e:
        print(f"Error during testing: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY not found in environment variables")
        exit(1)
    
    test_image_analysis()