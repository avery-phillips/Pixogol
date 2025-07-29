import json
import os
from datetime import datetime
import uuid
import streamlit as st

# Ensure logs directory exists
LOGS_DIR = "logs"
if not os.path.exists(LOGS_DIR):
    os.makedirs(LOGS_DIR)

def log_analysis_result(filename, extracted_text, risk_analysis):
    """
    Log analysis results to JSON file for auditing purposes
    
    Args:
        filename: Original image filename
        extracted_text: Text extracted via OCR
        risk_analysis: AI risk analysis results
        
    Returns:
        str: Unique analysis ID
    """
    try:
        # Generate unique analysis ID
        analysis_id = str(uuid.uuid4())[:8]
        timestamp = datetime.now()
        
        # Create log entry
        log_entry = {
            'analysis_id': analysis_id,
            'timestamp': timestamp.isoformat(),
            'timestamp_readable': timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'filename': filename,
            'extracted_text': extracted_text,
            'extracted_text_length': len(extracted_text) if extracted_text else 0,
            'risk_analysis': risk_analysis,
            'session_info': {
                'user_agent': 'Streamlit App',
                'app_version': '1.0.0'
            }
        }
        
        # Save to daily log file
        log_filename = f"pixogol_analysis_{timestamp.strftime('%Y%m%d')}.jsonl"
        log_filepath = os.path.join(LOGS_DIR, log_filename)
        
        # Append to JSON Lines file
        with open(log_filepath, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
        
        # Also save individual analysis file
        individual_log_filename = f"analysis_{analysis_id}_{timestamp.strftime('%Y%m%d_%H%M%S')}.json"
        individual_log_filepath = os.path.join(LOGS_DIR, individual_log_filename)
        
        with open(individual_log_filepath, 'w', encoding='utf-8') as f:
            json.dump(log_entry, f, indent=2, ensure_ascii=False)
        
        return analysis_id
        
    except Exception as e:
        st.error(f"Failed to log analysis results: {str(e)}")
        # Return a fallback ID even if logging fails
        return f"log_error_{datetime.now().strftime('%H%M%S')}"

def get_analysis_history(days=7):
    """
    Retrieve analysis history from log files
    
    Args:
        days: Number of days to look back
        
    Returns:
        list: List of analysis entries
    """
    try:
        history = []
        current_date = datetime.now()
        
        # Look through the last 'days' worth of log files
        for i in range(days):
            date = current_date - timedelta(days=i)
            log_filename = f"pixogol_analysis_{date.strftime('%Y%m%d')}.jsonl"
            log_filepath = os.path.join(LOGS_DIR, log_filename)
            
            if os.path.exists(log_filepath):
                with open(log_filepath, 'r', encoding='utf-8') as f:
                    for line in f:
                        try:
                            entry = json.loads(line.strip())
                            history.append(entry)
                        except json.JSONDecodeError:
                            continue
        
        # Sort by timestamp (newest first)
        history.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        
        return history
        
    except Exception as e:
        st.error(f"Failed to retrieve analysis history: {str(e)}")
        return []

def get_analysis_stats():
    """
    Get statistics about analyses performed
    
    Returns:
        dict: Statistics summary
    """
    try:
        history = get_analysis_history(days=30)  # Last 30 days
        
        if not history:
            return {
                'total_analyses': 0,
                'analyses_today': 0,
                'analyses_this_week': 0,
                'most_common_risk_level': 'N/A',
                'average_confidence': 0
            }
        
        today = datetime.now().date()
        week_ago = today - timedelta(days=7)
        
        analyses_today = 0
        analyses_this_week = 0
        risk_levels = []
        confidence_scores = []
        
        for entry in history:
            try:
                entry_date = datetime.fromisoformat(entry['timestamp']).date()
                
                if entry_date == today:
                    analyses_today += 1
                
                if entry_date >= week_ago:
                    analyses_this_week += 1
                
                # Extract risk level and confidence
                risk_analysis = entry.get('risk_analysis', {})
                overall_risk = risk_analysis.get('overall_risk_level')
                confidence = risk_analysis.get('confidence_score')
                
                if overall_risk:
                    risk_levels.append(overall_risk)
                
                if isinstance(confidence, (int, float)):
                    confidence_scores.append(confidence)
                    
            except Exception:
                continue
        
        # Calculate most common risk level
        most_common_risk = 'N/A'
        if risk_levels:
            from collections import Counter
            risk_counter = Counter(risk_levels)
            most_common_risk = risk_counter.most_common(1)[0][0]
        
        # Calculate average confidence
        avg_confidence = 0
        if confidence_scores:
            avg_confidence = sum(confidence_scores) / len(confidence_scores)
        
        return {
            'total_analyses': len(history),
            'analyses_today': analyses_today,
            'analyses_this_week': analyses_this_week,
            'most_common_risk_level': most_common_risk,
            'average_confidence': avg_confidence
        }
        
    except Exception as e:
        st.error(f"Failed to calculate analysis statistics: {str(e)}")
        return {
            'total_analyses': 0,
            'analyses_today': 0,
            'analyses_this_week': 0,
            'most_common_risk_level': 'N/A',
            'average_confidence': 0
        }

def export_logs(start_date=None, end_date=None):
    """
    Export logs for a specific date range
    
    Args:
        start_date: Start date for export (datetime object)
        end_date: End date for export (datetime object)
        
    Returns:
        str: JSON string of exported logs
    """
    try:
        if start_date is None:
            start_date = datetime.now() - timedelta(days=30)
        if end_date is None:
            end_date = datetime.now()
        
        # Get all history and filter by date range
        all_history = get_analysis_history(days=365)  # Get full history
        
        filtered_history = []
        for entry in all_history:
            try:
                entry_datetime = datetime.fromisoformat(entry['timestamp'])
                if start_date <= entry_datetime <= end_date:
                    filtered_history.append(entry)
            except Exception:
                continue
        
        export_data = {
            'export_timestamp': datetime.now().isoformat(),
            'date_range': {
                'start': start_date.isoformat(),
                'end': end_date.isoformat()
            },
            'total_entries': len(filtered_history),
            'entries': filtered_history
        }
        
        return json.dumps(export_data, indent=2, ensure_ascii=False)
        
    except Exception as e:
        st.error(f"Failed to export logs: {str(e)}")
        return json.dumps({'error': str(e)}, indent=2)

# Import timedelta for date calculations
from datetime import timedelta
