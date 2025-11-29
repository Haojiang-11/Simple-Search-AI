import streamlit as st
import pandas as pd
from search_engine import get_search_engine
import time
import base64
import os

# Page Config
st.set_page_config(page_title="AI Paper Search Agent", layout="wide")

# Helper to load background
def get_base64_bg(file_path):
    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()
    return None

bg_base64 = get_base64_bg("background.jpg")

# Custom CSS for clean UI
st.markdown(f"""
<style>
    /* Import Google Fonts for a more academic look */
    @import url('https://fonts.googleapis.com/css2?family=Merriweather:ital,wght@0,300;0,400;0,700;1,300&family=Lato:wght@400;700&display=swap');

    /* Global Variables - Macaron Theme */
    :root {{
        --bg-color: #FDFBF7; /* Parchment / Warm White */
        --card-bg: #FFFFFF;
        --text-color: #5D4037; /* Softer Brown Text */
        --accent-color: #B2DFDB; /* Macaron Mint */
        --primary-color: #8D6E63; /* Light Latte */
        --secondary-color: #FFCCBC; /* Macaron Peach */
        --sidebar-bg: #FFF3E0; /* Very light peach/cream for sidebar */
        --border-color: #E0F2F1;
    }}

    /* App Background */
    .stApp {{
        background-color: var(--bg-color);
        background-image: url("data:image/jpg;base64,{bg_base64}");
        background-size: cover;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }}
    
    /* Typography */
    h1, h2, h3, .main-header, .step-header {{
        font-family: 'Merriweather', serif !important;
        color: #795548 !important; /* Lighter Brown for Headers */
    }}
    
    p, div, span, button, label {{
        font-family: 'Lato', sans-serif;
        color: var(--text-color);
    }}

    /* Input Box Styling */
    div[data-testid="stTextInput"] input {{
        background-color: #FAFAFA !important;
        color: #5D4037 !important;
        border: 1px solid #B2DFDB !important;
        border-radius: 8px !important;
    }}
    
    div[data-testid="stSelectbox"] > div > div {{
        background-color: #FAFAFA !important;
        border: 1px solid #B2DFDB !important;
        border-radius: 8px !important;
        color: #5D4037 !important;
    }}

    /* Main Header Style - Cleaner, No Icons */
    .main-header {{
        font-size: 3.5rem; 
        font-weight: 300; 
        text-align: center;
        margin-bottom: 2rem;
        padding-bottom: 1rem;
        border-bottom: 1px solid #B2DFDB; 
        color: #8D6E63; /* Pastel Brown */
        letter-spacing: 2px;
    }}
    
    /* Step Header */
    .step-header {{
        font-size: 1.4rem; 
        font-weight: 500; 
        background-color: #E0F2F1; /* Light Mint */
        padding: 0.8rem 1.5rem;
        border-radius: 20px;
        color: #00695C !important;
        margin-top: 2rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }}
    
    /* Card Styling */
    .card {{
        background-color: rgba(255, 255, 255, 0.9);
        padding: 2rem; 
        border-radius: 16px; 
        margin-bottom: 1.5rem; 
        border: 1px solid #F0F4C3; /* Light Lime border */
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.02); 
        transition: all 0.3s ease;
    }}
    
    .card:hover {{
        transform: translateY(-3px);
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.05);
        border-color: #B2DFDB;
    }}
    
    .card h3 a {{
        text-decoration: none;
        color: #795548;
        font-size: 1.3rem;
        font-weight: 600;
    }}
    
    .card h3 a:hover {{
        color: #009688;
    }}
    
    /* Buttons - Macaron Colors */
    .stButton>button {{
        background-color: #E0F7FA !important; /* Mint */
        border: none !important;
        color: #00695C !important;
        border-radius: 20px !important;
        font-weight: 600 !important;
        padding: 0.5rem 1rem !important;
        transition: all 0.3s !important;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05) !important;
    }}
    
    .stButton>button:hover {{
        background-color: #B2DFDB !important;
        transform: scale(1.02);
        box-shadow: 0 4px 8px rgba(0,0,0,0.1) !important;
    }}
    
    /* Primary Button Override (e.g. Search) */
    div[data-testid="stButton"] button[kind="primary"] {{
        background-color: #FFCCBC !important; /* Peach */
        color: #BF360C !important;
    }}
    
    div[data-testid="stButton"] button[kind="primary"]:hover {{
        background-color: #FFAB91 !important;
    }}

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {{
        background-color: #FFF8E1; /* Creamy/Light Orange */
        border-right: 1px solid #FFE0B2;
    }}
    
    /* Sidebar Elements */
    section[data-testid="stSidebar"] h1, section[data-testid="stSidebar"] h2, section[data-testid="stSidebar"] h3 {{
        color: #8D6E63 !important;
    }}
    
    /* --- FORCE LIGHT MODE OVERRIDES --- */
    
    /* 1. Top Header Bar */
    header[data-testid="stHeader"] {{
        background-color: rgba(255, 255, 255, 0.5) !important;
        backdrop-filter: blur(5px);
    }}
    
    /* 2. TextArea (User Intent Input) */
    div[data-testid="stTextArea"] textarea {{
        background-color: #FAFAFA !important;
        color: #5D4037 !important;
        border: 1px solid #B2DFDB !important;
        border-radius: 8px !important;
    }}
    
    div[data-testid="stTextArea"] textarea::placeholder {{
        color: #A1887F !important; /* Visible placeholder color */
        opacity: 1;
    }}
    
    /* 3. Selectbox & Dropdowns */
    /* Input field itself */
    div[data-baseweb="select"] > div {{
        background-color: #FAFAFA !important;
        border-color: #B2DFDB !important;
        color: #5D4037 !important;
    }}
    
    /* Placeholder for normal text inputs */
    div[data-testid="stTextInput"] input::placeholder {{
        color: #A1887F !important;
        opacity: 1;
    }}
    
    /* Dropdown Menu (Popover) */
    div[data-baseweb="popover"] {{
        background-color: #FAFAFA !important;
    }}
    
    ul[data-testid="stSelectboxVirtualDropdown"] {{
        background-color: #FAFAFA !important;
    }}
    
    li[role="option"] {{
        background-color: #FAFAFA !important;
        color: #5D4037 !important;
    }}
    
    li[role="option"]:hover, li[role="option"][aria-selected="true"] {{
        background-color: #E0F2F1 !important; /* Light Mint Highlight */
        color: #00695C !important;
    }}
    
    /* Remove default Streamlit dark text if any */
    .stMarkdown, .stText {{
        color: #5D4037 !important;
    }}

</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Session State Initialization
# -----------------------------------------------------------------------------
if 'step' not in st.session_state:
    st.session_state.step = 1
if 'user_intent' not in st.session_state:
    st.session_state.user_intent = ""
if 'generated_keywords' not in st.session_state:
    st.session_state.generated_keywords = []
if 'search_results' not in st.session_state:
    st.session_state.search_results = []
if 'final_keywords' not in st.session_state:
    st.session_state.final_keywords = []
if 'keyword_cache' not in st.session_state:
    st.session_state.keyword_cache = {} # Format: {keyword: [list of papers]}

# -----------------------------------------------------------------------------
# Sidebar: Global Settings
# -----------------------------------------------------------------------------
st.sidebar.markdown("## Configuration")

# API Key Input
deepseek_api_key = st.sidebar.text_input("DeepSeek API Key", type="password", placeholder="sk-...", help="Enter your DeepSeek API Key here to enable AI features.")
if not deepseek_api_key:
    st.sidebar.warning("⚠️ AI features require an API Key.")

conference = st.sidebar.selectbox("Conference", ["ICLR", "NeurIPS", "ICML", "CVPR", "ECCV", "ICCV", "AAAI"])

# Determine available years
all_years = [2026, 2025, 2024, 2023, 2022]
if conference == "ECCV":
    available_years = [y for y in all_years if y % 2 == 0]
elif conference == "ICCV":
    available_years = [y for y in all_years if y % 2 != 0]
else:
    available_years = all_years

year = st.sidebar.selectbox("Year", [str(y) for y in available_years], index=1)

st.sidebar.caption("💡 Click to switch conference or year.")

# Status selector for OpenReview conferences
status = "Accepted"
if conference in ["ICLR", "NeurIPS", "ICML"]:
    status = st.sidebar.radio("Paper Status", ["Accepted", "Under Review"])

# Initialize Engine with User Key
engine = get_search_engine(deepseek_api_key)

# Mode Selection
st.sidebar.divider()
search_mode = st.sidebar.radio("Search Mode", ["Basic Search", "AI Smart Search"])

if st.sidebar.button("Reset Session"):
    st.session_state.step = 1
    st.session_state.user_intent = ""
    st.session_state.generated_keywords = []
    st.session_state.keyword_cache = {}
    st.session_state.search_results = []
    st.rerun()

# -----------------------------------------------------------------------------
# Main Logic
# -----------------------------------------------------------------------------
st.markdown('<div class="main-header">Academic Paper Search</div>', unsafe_allow_html=True)

# =============================================================================
# MODE 1: Basic Search (Direct Keyword Search)
# =============================================================================
if search_mode == "Basic Search":
    col_search, col_btn = st.columns([4, 1])
    with col_search:
        query = st.text_input("Enter keywords", placeholder="e.g., diffusion model, reinforcement learning", label_visibility="collapsed")
    with col_btn:
        search_clicked = st.button("🔍 Search", type="primary", use_container_width=True)
        
    if search_clicked:
        if not query.strip():
            st.warning("Please enter a keyword.")
        else:
            with st.spinner(f"📖 Searching {conference} {year} ({status})..."):
                # Direct search using engine
                results = engine.search(conference, year, query, status)
                st.session_state.search_results = results
                
                if not results:
                    st.warning("No papers found.")
                else:
                    st.success(f"Found {len(results)} papers.")

    # Display results for Basic Search
    if st.session_state.search_results and search_mode == "Basic Search":
        for i, paper in enumerate(st.session_state.search_results):
            with st.container():
                st.markdown(f"""
                <div class="card">
                    <h3><a href="{paper['link']}" target="_blank">{i+1}. {paper['title']}</a></h3>
                    <div style="color:#5D4037; font-size:0.9em; margin-bottom:0.5em; font-style: italic;">
                        🖋️ {', '.join(paper['authors'][:5])}{' et al.' if len(paper['authors'])>5 else ''} | 🏛️ {paper['status']}
                    </div>
                """, unsafe_allow_html=True)
                
                with st.expander("📖 Show Abstract"):
                    st.write(paper['abstract'])
                    
                if paper.get('pdf'):
                    st.markdown(f"[📄 Download PDF]({paper['pdf']})")
                    
                st.markdown("</div>", unsafe_allow_html=True)

# =============================================================================
# MODE 2: AI Smart Search (Step-by-Step Wizard)
# =============================================================================
elif search_mode == "AI Smart Search":
    
    # progress bar
    progress_map = {1: 10, 2: 50, 3: 100}
    st.progress(progress_map[st.session_state.step], text=f"Step {st.session_state.step} of 3")

    # -----------------------------------------------------------------------------
    # STEP 1: Intent Input
    # -----------------------------------------------------------------------------
    if st.session_state.step == 1:
        st.markdown('<div class="step-header">Step 1: Define Your Research Topic 🖋️</div>', unsafe_allow_html=True)
        
        user_input = st.text_area("Describe your research interest in natural language:", 
                                  height=150,
                                  placeholder="e.g., I want to find papers about jailbreaking large vision language models (LVLMs) or multimodal safety.",
                                  value=st.session_state.user_intent)
        
        if st.button("🧠 Analyze Intent & Generate Keywords"):
            if not user_input.strip():
                st.warning("Please describe your intent first.")
            else:
                st.session_state.user_intent = user_input
                with st.spinner("☕ Brewing keywords with DeepSeek..."):
                    keywords = engine.extract_keywords_with_deepseek(user_input)
                    # Initialize keywords with 0 count or None
                    st.session_state.generated_keywords = [{"keyword": k, "active": True, "count": None} for k in keywords]
                    # Clear cache on new intent
                    st.session_state.keyword_cache = {}
                    st.session_state.step = 2
                    st.rerun()

    # -----------------------------------------------------------------------------
    # STEP 2: Review Keywords & Scan
    # -----------------------------------------------------------------------------
    elif st.session_state.step == 2:
        st.markdown('<div class="step-header">Step 2: Review & Scan</div>', unsafe_allow_html=True)
        st.info(f"Intent: {st.session_state.user_intent}")
        
        # Check for AI Failure / Fallback
        if len(st.session_state.generated_keywords) == 1 and \
           st.session_state.generated_keywords[0]['keyword'] == st.session_state.user_intent:
            st.warning("⚠️ AI extraction failed (likely missing API Key). Using your original prompt as the keyword. **Please manually add ENGLISH keywords below to ensure search results!**")
        else:
            st.markdown("AI has generated the following keywords. You can edit, add, or uncheck them:")
        
        st.markdown("Click **'Scan / Update Counts'** to check how many papers match each keyword.")
        
        # Ensure generated_keywords is valid
        if not st.session_state.generated_keywords:
             st.session_state.generated_keywords = [{"keyword": st.session_state.user_intent, "active": True, "count": None}]

        # Prepare Data for Editor
        # We need to update the 'count' field based on cache if available
        for item in st.session_state.generated_keywords:
            kw = item['keyword']
            if kw in st.session_state.keyword_cache:
                item['count'] = len(st.session_state.keyword_cache[kw])
            else:
                if item.get('count') is None:
                    item['count'] = None # Not scanned yet

        edited_df = st.data_editor(
            pd.DataFrame(st.session_state.generated_keywords),
            num_rows="dynamic",
            use_container_width=True,
            column_config={
                "active": st.column_config.CheckboxColumn("Include?", default=True),
                "keyword": st.column_config.TextColumn("Keyword (English)", required=True, help="Search query sent to the database."),
                "count": st.column_config.NumberColumn("Found Papers", disabled=True, help="Number of papers found. Click Scan to update.")
            },
            hide_index=True
        )
        
        col1, col2, col3, col4 = st.columns([1, 1, 2, 2])
        with col1:
            if st.button("Back", help="Go back to Step 1"):
                st.session_state.step = 1
                st.rerun()
        
        with col2:
             if st.button("Reset", help="Reset keywords"):
                st.session_state.generated_keywords = []
                st.session_state.keyword_cache = {}
                st.rerun()

        with col3:
            # Removed emoji from label to fix display issues
            if st.button("Scan / Update Counts", type="secondary", help="Search papers for each keyword"):
                # Update generated_keywords from editor (to capture user edits)
                updated_keywords = []
                # Iterate over edited dataframe
                for index, row in edited_df.iterrows():
                    updated_keywords.append({
                        "keyword": row['keyword'],
                        "active": row['active'],
                        "count": row['count']
                    })
                st.session_state.generated_keywords = updated_keywords
                
                # Run search for each keyword (if active)
                with st.status("Scanning keywords...", expanded=True) as status_box:
                    for item in st.session_state.generated_keywords:
                        kw = item['keyword']
                        if item['active']:
                            # If not in cache or force update
                            if kw not in st.session_state.keyword_cache:
                                status_box.write(f"Searching: {kw}...")
                                results = engine.search(conference, year, kw, status)
                                st.session_state.keyword_cache[kw] = results
                                item['count'] = len(results)
                            else:
                                status_box.write(f"Used cached: {kw} ({len(st.session_state.keyword_cache[kw])} papers)")
                        else:
                            item['count'] = None # Skip inactive
                    status_box.update(label="Scan Complete!", state="complete", expanded=False)
                st.rerun()

        with col4:
            if st.button("Confirm & Analyze", type="primary"):
                # Save final state
                updated_keywords = []
                for index, row in edited_df.iterrows():
                     updated_keywords.append({
                        "keyword": row['keyword'],
                        "active": row['active'],
                        "count": row['count']
                    })
                st.session_state.generated_keywords = updated_keywords
                
                # Filter active keywords that have results
                active_kws = [item['keyword'] for item in st.session_state.generated_keywords if item['active']]
                
                if not active_kws:
                    st.error("Please select at least one keyword.")
                else:
                    st.session_state.final_keywords = active_kws
                    st.session_state.step = 3
                    st.rerun()

    # -----------------------------------------------------------------------------
    # STEP 3: Rerank & Results
    # -----------------------------------------------------------------------------
    elif st.session_state.step == 3:
        st.markdown('<div class="step-header">Step 3: AI Analysis & Recommendations</div>', unsafe_allow_html=True)
        
        # Collect papers from cache
        all_papers = []
        seen_links = set()
        
        # Retrieve results from cache for active keywords
        for kw in st.session_state.final_keywords:
            if kw in st.session_state.keyword_cache:
                results = st.session_state.keyword_cache[kw]
                # Dedup logic
                for p in results: 
                    if p['link'] not in seen_links:
                        all_papers.append(p)
                        seen_links.add(p['link'])
        
        if not all_papers:
            st.warning("No papers found in the selected keywords. Please go back and Scan/Update Counts.")
            if st.button("Back to Keywords"):
                st.session_state.step = 2
                st.rerun()
        else:
            # Check if we already reranked
            if not st.session_state.search_results:
                with st.spinner(f"🧠 DeepSeek is analyzing {len(all_papers)} unique papers..."):
                    # 2. AI Rerank
                    reranked = engine.deepseek_rerank_papers(st.session_state.user_intent, all_papers, top_n=25)
                    st.session_state.search_results = reranked
                    st.rerun()
            
            # Display Results
            st.success(f"DeepSeek selected top {len(st.session_state.search_results)} papers from {len(all_papers)} candidates.")
            
            if st.button("New Search"):
                st.session_state.step = 1
                st.session_state.user_intent = ""
                st.session_state.generated_keywords = []
                st.session_state.keyword_cache = {}
                st.session_state.search_results = []
                st.rerun()
            
            st.divider()
            
            for i, paper in enumerate(st.session_state.search_results):
                with st.container():
                    col_content, col_op = st.columns([10, 1])
                    
                    with col_content:
                        # Render card using markdown for custom styling
                        st.markdown(f"""
                        <div class="card">
                            <h3><a href="{paper['link']}" target="_blank" style="text-decoration:none; color:#1E3A8A;">{i+1}. {paper['title']}</a></h3>
                            <div style="color:#666; font-size:0.9em; margin-bottom:0.5em;">
                                {', '.join(paper['authors'][:5])}{' et al.' if len(paper['authors'])>5 else ''} | {paper['status']}
                            </div>
                            <div class="recommendation-reason">
                                <b>DeepSeek:</b> {paper.get('recommendation_reason', 'Matched via keyword.')}
                            </div>
                        """, unsafe_allow_html=True)
                        
                        with st.expander("Show Abstract"):
                            st.write(paper['abstract'])
                            
                        if paper.get('pdf'):
                            st.markdown(f"[Download PDF]({paper['pdf']})")
                            
                        st.markdown("</div>", unsafe_allow_html=True)

                    with col_op:
                        st.markdown("<br><br>", unsafe_allow_html=True) # Spacing
                        if st.button("🗑️", key=f"del_{i}", help="Dismiss this paper"):
                            st.session_state.search_results.pop(i)
                            st.rerun()
