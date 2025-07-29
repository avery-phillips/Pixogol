# Pixogol - AI-Powered Image Risk Assessment

## Overview

Pixogol is a Streamlit web application that provides AI-powered copyright, trademark, and brand risk detection for uploaded images. The system uses OCR (Optical Character Recognition) to extract text from images and then leverages OpenAI's GPT-4o model to analyze potential intellectual property risks.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Framework**: Streamlit web framework
- **Layout**: Wide layout with two-column design for image display and analysis results
- **File Upload**: Supports multiple image formats (PNG, JPG, JPEG, GIF, BMP, TIFF)
- **User Interface**: Clean, intuitive interface with emoji icons and clear section headers

### Backend Architecture
- **Modular Design**: Utility modules for OCR processing, risk analysis, and logging
- **Environment Configuration**: Uses python-dotenv for environment variable management
- **Error Handling**: Comprehensive error handling with user-friendly error messages

### Data Processing Pipeline
1. **Image Upload**: User uploads image through Streamlit file uploader
2. **OCR Processing**: Extract text using Tesseract OCR with image preprocessing
3. **Risk Analysis**: Analyze extracted text using OpenAI GPT-4o model
4. **Logging**: Store analysis results in JSON Lines format for auditing

## Key Components

### OCR Processor (`utils/ocr_processor.py`)
- **Technology**: Tesseract OCR with OpenCV image preprocessing
- **Preprocessing**: Image enhancement for better OCR accuracy
- **Text Cleaning**: Post-processing to clean extracted text
- **Character Whitelist**: Configured to extract standard alphanumeric and punctuation characters

### Risk Analyzer (`utils/risk_analyzer.py`)
- **AI Model**: OpenAI GPT-4o (latest model as of May 13, 2024)
- **Analysis Categories**: 
  - Copyright risks (creative works, proprietary content)
  - Trademark risks (brand names, slogans)
  - Brand risks (company references, celebrity names)
- **Risk Levels**: LOW, MEDIUM, HIGH, CRITICAL classifications
- **Output Format**: Structured JSON responses

### Logger (`utils/logger.py`)
- **Format**: JSON Lines (.jsonl) for structured logging
- **Daily Rotation**: Separate log files for each day
- **Unique IDs**: UUID-based analysis tracking
- **Audit Trail**: Comprehensive metadata including timestamps and session info

## Data Flow

1. User uploads image file via Streamlit interface
2. Image is processed and displayed in the left column
3. OCR processor extracts text from the image using Tesseract
4. Extracted text is sent to OpenAI GPT-4o for risk analysis
5. AI provides structured risk assessment with explanations
6. Results are displayed in the right column
7. Analysis is logged to daily JSON Lines file for auditing

## External Dependencies

### Core Dependencies
- **Streamlit**: Web application framework
- **OpenAI**: AI-powered risk analysis (requires API key)
- **Tesseract OCR**: Text extraction from images
- **OpenCV**: Image preprocessing
- **PIL (Pillow)**: Image handling and manipulation

### Required Environment Variables
- **OPENAI_API_KEY**: Required for AI risk analysis functionality

### System Requirements
- Tesseract OCR must be installed on the system
- OpenCV for image processing capabilities

## Deployment Strategy

### Environment Setup
- Environment variables managed through .env file
- Error checking for required API keys with user-friendly messages
- Automatic directory creation for logs

### File Structure
- Modular utility functions in separate files for maintainability
- Centralized logging in dedicated logs directory
- Clean separation of concerns between OCR, AI analysis, and logging

### Scalability Considerations
- JSON Lines logging format for easy parsing and analysis
- Unique analysis IDs for tracking individual requests
- Daily log rotation to manage file sizes
- Stateless design suitable for horizontal scaling

## Development Notes

- The application uses the latest OpenAI model (gpt-4o) and should not be changed unless explicitly requested
- Image preprocessing is optimized for better OCR accuracy
- Comprehensive error handling ensures graceful degradation
- Logging provides full audit trail for compliance and debugging purposes