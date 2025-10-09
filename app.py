import streamlit as st
import re
from typing import List, Dict, Generator
import pandas as pd
import io

def extract_card_details_chunked(text: str, chunk_size: int = 10000, include_no_cvv: bool = False, include_trailing_info: bool = False) -> Generator[str, None, None]:
    """
    Extract card details from text using regex pattern matching with chunked processing.
    
    Args:
        text (str): Input text containing card information
        chunk_size (int): Size of text chunks to process at once
        include_no_cvv (bool): Whether to include cards without CVV
        include_trailing_info (bool): Whether to include cards with trailing information
        
    Yields:
        str: Extracted card details in various formats
    """
    # Pattern for cards with CVV: 16 digits | 2 digits | 4 digits | 3-4 digits
    card_pattern_with_cvv = r'\b\d{16}\|\d{2}\|\d{4}\|\d{3,4}\b'
    
    # Pattern for cards without CVV: 16 digits | 2 digits | 4 digits |
    card_pattern_no_cvv = r'\b\d{16}\|\d{2}\|\d{4}\|\s*(?=\s|$|[^\d])'
    
    # Enhanced pattern for cards with trailing info (excluding parentheses): 
    # 16 digits | 2 digits | 4 digits | [space] [text until parentheses or line end]
    card_pattern_trailing = r'\b\d{16}\|\d{2}\|\d{4}\|\s+[^(\n\r]*'
    
    seen = set()
    
    # Process text in chunks to handle large files
    for i in range(0, len(text), chunk_size):
        chunk = text[i:i + chunk_size + 300]  # Increased overlap for longer trailing info
        
        # Find cards with CVV first (highest priority)
        matches_with_cvv = re.findall(card_pattern_with_cvv, chunk)
        for match in matches_with_cvv:
            if match not in seen and validate_card_format(match, format_type="with_cvv"):
                seen.add(match)
                yield match
        
        # Find cards with trailing info if enabled
        if include_trailing_info:
            matches_trailing = re.findall(card_pattern_trailing, chunk)
            for match in matches_trailing:
                # Clean up trailing whitespace
                clean_match = match.rstrip()
                
                # Extract the card identifier (first 3 parts) for deduplication
                parts = clean_match.split('|')
                if len(parts) >= 4:
                    card_key = '|'.join(parts[:3]) + '|'
                    if card_key not in seen and validate_card_format(clean_match, format_type="trailing"):
                        seen.add(card_key)
                        yield clean_match
        
        # Find cards without CVV if enabled (lowest priority)
        if include_no_cvv:
            matches_no_cvv = re.findall(card_pattern_no_cvv, chunk)
            for match in matches_no_cvv:
                clean_match = match.rstrip()
                if not clean_match.endswith('|'):
                    clean_match += '|'
                if clean_match not in seen and validate_card_format(clean_match, format_type="no_cvv"):
                    seen.add(clean_match)
                    yield clean_match

def validate_card_format(card_detail: str, format_type: str = "with_cvv") -> bool:
    """
    Validate if the extracted card detail follows the correct format.
    
    Args:
        card_detail (str): Card detail string to validate
        format_type (str): Type of format - "with_cvv", "no_cvv", or "trailing"
        
    Returns:
        bool: True if valid format, False otherwise
    """
    try:
        parts = card_detail.split('|')
        
        if len(parts) < 3:
            return False
        
        card_number, month, year = parts[0], parts[1], parts[2]
        
        # Validate card number (16 digits)
        if not (card_number.isdigit() and len(card_number) == 16):
            return False
        
        # Validate month (01-12)
        if not (month.isdigit() and len(month) == 2 and 1 <= int(month) <= 12):
            return False
        
        # Validate year (4 digits, reasonable range)
        if not (year.isdigit() and len(year) == 4 and 2020 <= int(year) <= 2040):
            return False
        
        # Format-specific validation
        if format_type == "with_cvv":
            if len(parts) != 4:
                return False
            cvv = parts[3]
            if not (cvv.isdigit() and len(cvv) in [3, 4]):
                return False
                
        elif format_type == "no_cvv":
            if len(parts) != 4:
                return False
            cvv = parts[3]
            if cvv.strip():  # Should be empty for no CVV format
                return False
                
        elif format_type == "trailing":
            if len(parts) < 4:
                return False
            # For trailing info, we accept any content after the third |
            # Just ensure the first 3 parts are valid
        
        return True
    except Exception:
        return False

def process_large_text(text: str, include_no_cvv: bool = False, include_trailing_info: bool = False, max_display_results: int = 100) -> tuple[List[str], int, str]:
    """
    Process large text efficiently and return results for display and download.
    
    Args:
        text (str): Input text to process
        include_no_cvv (bool): Whether to include cards without CVV
        include_trailing_info (bool): Whether to include cards with trailing info
        max_display_results (int): Maximum number of results to display in UI
        
    Returns:
        tuple: (display_results, total_count, download_content)
    """
    display_results = []
    download_buffer = io.StringIO()
    total_count = 0
    
    try:
        for card in extract_card_details_chunked(text, include_no_cvv=include_no_cvv, include_trailing_info=include_trailing_info):
            total_count += 1
            download_buffer.write(card + '\n')
            
            # Only keep first max_display_results for UI display
            if len(display_results) < max_display_results:
                display_results.append(card)
                
    except Exception as e:
        st.error(f"Error processing text: {str(e)}")
        return [], 0, ""
    
    download_content = download_buffer.getvalue()
    download_buffer.close()
    
    return display_results, total_count, download_content

def main():
    # Page configuration
    st.set_page_config(
        page_title="Card Details Extractor",
        page_icon="💳",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    # Custom CSS for better styling
    st.markdown("""
    <style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-size: 3rem;
        font-weight: bold;
        margin-bottom: 1rem;
    }
    .subtitle {
        text-align: center;
        color: #666;
        font-size: 1.2rem;
        margin-bottom: 2rem;
    }
    .warning-box {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 1rem 0;
    }
    .results-box {
        background-color: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 0.5rem;
        padding: 1rem;
        font-family: 'Courier New', monospace;
        white-space: pre-line;
        margin: 1rem 0;
        max-height: 400px;
        overflow-y: auto;
    }
    .info-box {
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 1rem 0;
    }
    .option-box {
        background-color: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 1rem 0;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown('<h1 class="main-header">💳 Card Details Extractor</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Extract card information in multiple formats</p>', unsafe_allow_html=True)
    
    # Warning message
    st.markdown("""
    <div class="warning-box">
        <strong>⚠️ Educational Purpose Only:</strong> This tool is designed for learning and testing purposes. 
        Never use with real card information.
    </div>
    """, unsafe_allow_html=True)
    
    # Create two columns for layout
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📝 Input Text")
        
        # Extraction options
        st.markdown('<div class="option-box">', unsafe_allow_html=True)
        st.subheader("⚙️ Extraction Options")
        
        include_no_cvv = st.checkbox(
            "Include cards without CVV",
            value=False,
            help="Extract cards in format: CARD_NUMBER|MM|YYYY|"
        )
        
        include_trailing_info = st.checkbox(
            "Include cards with trailing information",
            value=False,
            help="Extract cards with additional text (excludes parentheses): CARD_NUMBER|MM|YYYY| 4.99 USD CCN Charged"
        )
        
        # Show format examples based on selected options
        formats = ["• Standard: 4489750048620233|01|2026|123"]
        if include_no_cvv:
            formats.append("• No CVV: 4489750048620233|01|2026|")
        if include_trailing_info:
            formats.append("• With Info: 4489750048620233|01|2026| 4.99 USD CCN Charged")
            formats.append("• Note: Text in parentheses will be excluded")
        
        st.info("Will extract formats:\n" + "\n".join(formats))
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Text area for input
        input_text = st.text_area(
            "Paste your text content below:",
            height=200,
            placeholder="Paste text containing card details here...\n\nSupported formats:\n• Standard: 4251319037346824|02|2025|299\n• No CVV: 4489750048620233|01|2026|\n• With Info: 4489750048620233|01|2026| 4.99 USD CCN Charged\n• Note: Text in parentheses like (7lkb6CAIwAZVXRQIgtzL5piqIJGDN0qM) will be excluded",
            help="The extractor will find card details and exclude text in parentheses when trailing info option is enabled"
        )
        
        # Buttons
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            extract_btn = st.button("🔍 Extract Cards", type="primary", use_container_width=True)
        with col_btn2:
            clear_btn = st.button("🗑️ Clear", use_container_width=True)
        
        # File upload option
        st.subheader("📁 Upload File")
        uploaded_file = st.file_uploader(
            "Or upload a text file:",
            type=['txt', 'log', 'csv'],
            help="Upload a text file containing card details (supports large files)"
        )
        
        # File size info
        if uploaded_file is not None:
            file_size = len(uploaded_file.getvalue())
            if file_size > 10 * 1024 * 1024:  # 10MB
                st.warning(f"Large file detected ({file_size / (1024*1024):.1f}MB). Processing may take a moment...")
            else:
                st.info(f"File size: {file_size / 1024:.1f}KB")
    
    with col2:
        st.subheader("📋 Extracted Results")
        
        # Process input
        text_to_process = ""
        
        if uploaded_file is not None:
            try:
                # Handle large files efficiently
                if hasattr(uploaded_file, 'getvalue'):
                    file_bytes = uploaded_file.getvalue()
                else:
                    file_bytes = uploaded_file.read()
                
                text_to_process = file_bytes.decode("utf-8", errors='ignore')
                st.success(f"File loaded: {uploaded_file.name}")
                
            except Exception as e:
                st.error(f"Error reading file: {e}")
                text_to_process = ""
        
        if clear_btn:
            st.session_state.clear()
            st.rerun()
        
        if extract_btn or input_text or text_to_process:
            # Use uploaded file content if available, otherwise use text area input
            final_text = text_to_process if text_to_process else input_text
            
            if final_text.strip():
                with st.spinner("Extracting card details... This may take a moment for large files."):
                    try:
                        # Process large text efficiently
                        display_results, total_count, download_content = process_large_text(
                            final_text, 
                            include_no_cvv=include_no_cvv,
                            include_trailing_info=include_trailing_info
                        )
                        
                        if total_count > 0:
                            st.success(f"Found {total_count} valid card detail(s)")
                            
                            # Download button - always available with full results
                            st.download_button(
                                label=f"💾 Download All Results ({total_count} cards)",
                                data=download_content,
                                file_name="extracted_cards.txt",
                                mime="text/plain",
                                use_container_width=True
                            )
                            
                            # Statistics
                            st.subheader("📊 Statistics")
                            stats_col1, stats_col2 = st.columns(2)
                            with stats_col1:
                                st.metric("Total Cards Found", total_count)
                            with stats_col2:
                                unique_count = len(set(download_content.strip().split('\n'))) if download_content.strip() else 0
                                st.metric("Unique Cards", unique_count)
                            
                            # Show format breakdown
                            if download_content:
                                lines = download_content.strip().split('\n')
                                standard_cvv = sum(1 for line in lines if line.count('|') == 3 and len(line.split('|')[3].strip()) in [3, 4] and line.split('|')[3].strip().isdigit())
                                no_cvv = sum(1 for line in lines if line.count('|') == 3 and not line.split('|')[3].strip())
                                trailing_info = total_count - standard_cvv - no_cvv
                                
                                format_col1, format_col2, format_col3 = st.columns(3)
                                with format_col1:
                                    st.metric("Standard CVV", standard_cvv)
                                with format_col2:
                                    st.metric("No CVV", no_cvv)
                                with format_col3:
                                    st.metric("With Info", trailing_info)
                            
                        else:
                            st.warning("No valid card details found in the provided text.")
                            format_examples = ["• Standard: CARD_NUMBER|MM|YYYY|CVV"]
                            if include_no_cvv:
                                format_examples.append("• No CVV: CARD_NUMBER|MM|YYYY|")
                            if include_trailing_info:
                                format_examples.append("• With Info: CARD_NUMBER|MM|YYYY| additional text (excludes parentheses)")
                            
                            st.info("Make sure your text contains card details in supported formats:\n" + "\n".join(format_examples))
                            
                    except Exception as e:
                        st.error(f"An error occurred during processing: {str(e)}")
                        st.info("Try with a smaller file or check the text format.")
            else:
                st.info("Please paste some text or upload a file to extract card details.")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 1rem;">
        <p>🔒 This application processes data locally and does not store any information.</p>
        <p>Built with Streamlit • For Educational Purposes Only • Supports Multiple Card Formats</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
