import streamlit as st
import os
from PIL import Image
import json
from datetime import datetime
from utils.ocr_processor import extract_text_from_image
from utils.risk_analyzer import analyze_legal_risks
from utils.logger import log_analysis_result
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def main():
    st.set_page_config(
        page_title="Pixogol - AI-Powered Image Risk Assessment",
        page_icon="🔍",
        layout="wide"
    )
    
    st.title("🔍 Pixogol")
    st.subheader("AI-Powered Copyright, Trademark & Brand Risk Detection")
    
    st.markdown("""
    Upload an image to analyze potential copyright, trademark, and brand risks using advanced OCR and AI analysis.
    """)
    
    # Check for required API key
    if not os.getenv("OPENAI_API_KEY"):
        st.error("⚠️ OpenAI API key is required. Please set OPENAI_API_KEY in your environment variables.")
        st.stop()
    
    # File uploader
    uploaded_file = st.file_uploader(
        "Choose an image file",
        type=['png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff'],
        help="Supported formats: PNG, JPG, JPEG, GIF, BMP, TIFF"
    )
    
    if uploaded_file is not None:
        # Create columns for layout
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.subheader("📸 Uploaded Image")
            try:
                image = Image.open(uploaded_file)
                st.image(image, caption=f"Uploaded: {uploaded_file.name}", use_container_width=True)
                
                # Image details
                st.write(f"**Filename:** {uploaded_file.name}")
                st.write(f"**Size:** {image.size[0]} × {image.size[1]} pixels")
                st.write(f"**Format:** {image.format}")
                
            except Exception as e:
                st.error(f"Error loading image: {str(e)}")
                return
        
        with col2:
            st.subheader("🔍 Analysis")
            
            if st.button("🚀 Analyze Image", type="primary"):
                analyze_image(image, uploaded_file.name)

def analyze_image(image, filename):
    """Analyze the uploaded image for legal risks"""
    
    # Create progress bar
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        # Step 1: Extract text using OCR
        status_text.text("🔤 Extracting text from image (trying multiple methods)...")
        progress_bar.progress(25)
        
        extracted_text = extract_text_from_image(image)
        
        if not extracted_text or extracted_text.strip() == "":
            st.warning("⚠️ No text detected in the image. Analysis will be limited to visual elements only.")
            extracted_text = "[No text detected]"
        else:
            st.success(f"✅ Text extracted: {len(extracted_text)} characters found")
        
        progress_bar.progress(50)
        
        # Step 2: Analyze for legal risks
        status_text.text("🧠 Analyzing legal risks with AI...")
        progress_bar.progress(75)
        
        risk_analysis = analyze_legal_risks(extracted_text, filename, image)
        
        progress_bar.progress(90)
        
        # Step 3: Log results
        status_text.text("📝 Logging results...")
        analysis_id = log_analysis_result(filename, extracted_text, risk_analysis)
        
        progress_bar.progress(100)
        status_text.text("✅ Analysis complete!")
        
        # Display results
        display_results(extracted_text, risk_analysis, analysis_id)
        
    except Exception as e:
        st.error(f"❌ Analysis failed: {str(e)}")
        st.exception(e)
    finally:
        progress_bar.empty()
        status_text.empty()

def display_results(extracted_text, risk_analysis, analysis_id):
    """Display the analysis results in a structured format"""
    
    st.success("🎯 Analysis Complete!")
    
    # Display extracted text
    with st.expander("📝 Extracted Text", expanded=False):
        if extracted_text == "[No text detected]":
            st.info("No text was detected in the image.")
        else:
            st.text_area("Text found in image:", extracted_text, height=100, disabled=True)
    
    # Display risk analysis
    st.subheader("⚖️ Legal Risk Assessment")
    
    # Overall risk level
    overall_risk = risk_analysis.get('overall_risk_level', 'Unknown')
    risk_color = {
        'LOW': '🟢',
        'MEDIUM': '🟡', 
        'HIGH': '🔴',
        'CRITICAL': '🔴'
    }.get(overall_risk, '⚪')
    
    st.markdown(f"### {risk_color} Overall Risk Level: **{overall_risk}**")
    
    # Risk categories
    col1, col2, col3 = st.columns(3)
    
    risks = risk_analysis.get('risk_categories', {})
    
    with col1:
        st.metric(
            label="📄 Copyright Risk",
            value=risks.get('copyright', {}).get('level', 'Unknown'),
            help=risks.get('copyright', {}).get('explanation', 'No analysis available')
        )
    
    with col2:
        st.metric(
            label="™️ Trademark Risk", 
            value=risks.get('trademark', {}).get('level', 'Unknown'),
            help=risks.get('trademark', {}).get('explanation', 'No analysis available')
        )
    
    with col3:
        st.metric(
            label="🏢 Brand Risk",
            value=risks.get('brand', {}).get('level', 'Unknown'),
            help=risks.get('brand', {}).get('explanation', 'No analysis available')
        )
    
    # Detailed explanations
    st.subheader("📋 Detailed Analysis")
    
    for category, details in risks.items():
        with st.expander(f"{category.title()} Risk Details"):
            st.write(f"**Risk Level:** {details.get('level', 'Unknown')}")
            st.write(f"**Explanation:** {details.get('explanation', 'No explanation available')}")
            
            if 'recommendations' in details:
                st.write("**Recommendations:**")
                for i, rec in enumerate(details['recommendations'], 1):
                    st.write(f"{i}. {rec}")
    
    # General recommendations
    if 'general_recommendations' in risk_analysis:
        st.subheader("💡 General Recommendations")
        for i, rec in enumerate(risk_analysis['general_recommendations'], 1):
            st.write(f"{i}. {rec}")
    
    # Analysis metadata
    with st.expander("📊 Analysis Metadata"):
        st.write(f"**Analysis ID:** {analysis_id}")
        st.write(f"**Timestamp:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        st.write(f"**Confidence Score:** {risk_analysis.get('confidence_score', 'Not provided')}")
    
    # Download results
    results_json = {
        'analysis_id': analysis_id,
        'timestamp': datetime.now().isoformat(),
        'extracted_text': extracted_text,
        'risk_analysis': risk_analysis
    }
    
    st.download_button(
        label="📥 Download Analysis Report (JSON)",
        data=json.dumps(results_json, indent=2),
        file_name=f"pixogol_analysis_{analysis_id}.json",
        mime="application/json"
    )

if __name__ == "__main__":
    main()
