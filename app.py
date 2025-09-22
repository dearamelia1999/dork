import streamlit as st
import pandas as pd
from search_engines import SearchEngineManager
from utils import format_results_for_display
import json
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Universal Search Engine Dorker",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 1rem 0;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .search-box {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #667eea;
        margin-bottom: 1rem;
    }
    .result-item {
        background: white;
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 8px;
        border-left: 3px solid #28a745;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .stButton > button {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 5px;
        padding: 0.5rem 2rem;
        font-weight: bold;
    }
    .engine-stats {
        background: #e3f2fd;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🔍 Universal Search Engine Dorker</h1>
        <p>Advanced dorking across 8 major search engines</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize session state
    if 'search_results' not in st.session_state:
        st.session_state.search_results = {}
    if 'search_history' not in st.session_state:
        st.session_state.search_history = []
    
    # Sidebar configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Proxy settings
        st.subheader("🌐 Proxy Settings")
        use_proxy = st.checkbox("Use Proxy")
        proxy_url = ""
        
        if use_proxy:
            proxy_type = st.selectbox("Proxy Type", ["HTTP", "HTTPS", "SOCKS5"])
            proxy_host = st.text_input("Proxy Host", placeholder="127.0.0.1")
            proxy_port = st.text_input("Proxy Port", placeholder="8080")
            proxy_user = st.text_input("Username (optional)")
            proxy_pass = st.text_input("Password (optional)", type="password")
            
            if proxy_host and proxy_port:
                if proxy_user and proxy_pass:
                    proxy_url = f"{proxy_type.lower()}://{proxy_user}:{proxy_pass}@{proxy_host}:{proxy_port}"
                else:
                    proxy_url = f"{proxy_type.lower()}://{proxy_host}:{proxy_port}"
        
        # Search engine selection
        st.subheader("🔍 Search Engines")
        all_engines = ["Google", "DuckDuckGo", "Yandex", "Bing", "Baidu", "Yahoo", "StartPage", "Searx"]
        search_engines = st.multiselect(
            "Select Search Engines",
            all_engines,
            default=["Google", "DuckDuckGo", "Bing"]
        )
        
        # Advanced options
        st.subheader("🎯 Advanced Options")
        max_results = st.slider("Max Results per Engine", 5, 50, 20)
        delay_between_requests = st.slider("Delay Between Requests (seconds)", 1, 10, 2)
        
        # Export options
        st.subheader("📁 Export")
        if st.session_state.search_results:
            if st.button("📥 Export Results as JSON"):
                export_data = {
                    'timestamp': datetime.now().isoformat(),
                    'results': st.session_state.search_results
                }
                st.download_button(
                    label="Download JSON",
                    data=json.dumps(export_data, indent=2),
                    file_name=f"dorker_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )
    
    # Main search interface
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown('<div class="search-box">', unsafe_allow_html=True)
        
        # Search query input
        search_query = st.text_area(
            "🔍 Search Query / Dork",
            placeholder='Enter your search query or dork (e.g., site:example.com filetype:pdf, intitle:"admin login", inurl:"/wp-admin")',
            help="Enter any search query or Google dork operators",
            height=100
        )
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown("### 📚 Common Dork Operators")
        st.markdown("""
        - `site:example.com` - Search specific site
        - `filetype:pdf` - Find PDF files
        - `intitle:"admin"` - Pages with "admin" in title
        - `inurl:"/login"` - URLs containing "/login"
        - `ext:sql` - Files with .sql extension
        - `cache:example.com` - Cached version
        - `"password"` - Exact phrase search
        - `-word` - Exclude word from results
        - `OR` - Search for either term
        - `*` - Wildcard operator
        """)
    
    # Predefined dork templates
    st.markdown("### 🎯 Quick Dork Templates")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("🔐 Login Pages"):
            st.session_state.template_query = 'intitle:"login" OR inurl:"/login" OR inurl:"/admin"'
    
    with col2:
        if st.button("📁 File Discovery"):
            st.session_state.template_query = 'filetype:pdf OR filetype:doc OR filetype:xls'
    
    with col3:
        if st.button("🗄️ Database Files"):
            st.session_state.template_query = 'filetype:sql OR filetype:db OR ext:mdb'
    
    with col4:
        if st.button("⚙️ Config Files"):
            st.session_state.template_query = 'filetype:conf OR filetype:config OR filetype:ini'
    
    # Apply template if selected
    if 'template_query' in st.session_state:
        search_query = st.session_state.template_query
        del st.session_state.template_query
        st.rerun()
    
    # Search buttons
    col1, col2, col3 = st.columns(3)
    
    with col1:
        search_selected = st.button("🔍 Search Selected Engines", type="primary")
    
    with col2:
        search_all = st.button("🌐 Search All Engines")
    
    with col3:
        clear_results = st.button("🗑️ Clear Results")
    
    # Clear results
    if clear_results:
        st.session_state.search_results = {}
        st.rerun()
    
    # Perform search
    if (search_selected or search_all) and search_query:
        # Initialize search manager
        manager = SearchEngineManager(proxy_url if use_proxy and proxy_url else None)
        
        # Determine which engines to search
        engines_to_search = search_engines if search_selected else all_engines
        
        if not engines_to_search:
            st.error("❌ Please select at least one search engine")
        else:
            # Show progress
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            results = {}
            total_engines = len(engines_to_search)
            
            for i, engine_name in enumerate(engines_to_search):
                status_text.text(f"Searching {engine_name}...")
                progress_bar.progress((i + 1) / total_engines)
                
                try:
                    engine = manager.get_engine(engine_name)
                    if engine:
                        engine_results = engine.search(search_query)
                        results[engine_name] = engine_results
                    else:
                        results[engine_name] = []
                except Exception as e:
                    st.error(f"Error searching {engine_name}: {str(e)}")
                    results[engine_name] = []
            
            # Store results in session state
            st.session_state.search_results = results
            
            # Add to search history
            search_entry = {
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'query': search_query,
                'engines': engines_to_search
            }
            st.session_state.search_history.append(search_entry)
            
            # Clear progress indicators
            progress_bar.empty()
            status_text.empty()
            
            st.success(f"✅ Search completed across {len(engines_to_search)} engines!")
    
    # Display results
    if st.session_state.search_results:
        st.markdown("---")
        st.header("📊 Search Results")
        
        # Results summary
        total_results = sum(len(results) for results in st.session_state.search_results.values())
        st.info(f"Found {total_results} total results across {len(st.session_state.search_results)} engines")
        
        # Results statistics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown('<div class="engine-stats">', unsafe_allow_html=True)
            st.metric("Total Results", total_results)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="engine-stats">', unsafe_allow_html=True)
            successful_engines = sum(1 for results in st.session_state.search_results.values() if results)
            st.metric("Successful Engines", f"{successful_engines}/{len(st.session_state.search_results)}")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col3:
            st.markdown('<div class="engine-stats">', unsafe_allow_html=True)
            avg_results = total_results / len(st.session_state.search_results) if st.session_state.search_results else 0
            st.metric("Avg Results/Engine", f"{avg_results:.1f}")
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Display results by engine
        for engine_name, results in st.session_state.search_results.items():
            if results:
                with st.expander(f"🔍 {engine_name} Results ({len(results)} found)", expanded=True):
                    for i, result in enumerate(results, 1):
                        st.markdown(f"""
                        <div class="result-item">
                            <h4>{i}. {result['title']}</h4>
                            <p><strong>🔗 URL:</strong> <a href="{result['url']}" target="_blank">{result['url']}</a></p>
                            <p><strong>📝 Snippet:</strong> {result['snippet'][:300]}{'...' if len(result['snippet']) > 300 else ''}</p>
                        </div>
                        """, unsafe_allow_html=True)
            else:
                st.warning(f"No results found on {engine_name}")
    
    # Search history
    if st.session_state.search_history:
        st.markdown("---")
        with st.expander("📚 Search History"):
            for entry in reversed(st.session_state.search_history[-10:]):  # Show last 10 searches
                st.markdown(f"""
                **{entry['timestamp']}** - Query: `{entry['query'][:100]}{'...' if len(entry['query']) > 100 else ''}` - Engines: {', '.join(entry['engines'])}
                """)

if __name__ == "__main__":
    main()
