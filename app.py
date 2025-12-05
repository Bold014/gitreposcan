import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

# --- Configuration & Setup ---
st.set_page_config(
    page_title="GitHub Sourcing Engine", 
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load secrets
try:
    GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
except FileNotFoundError:
    st.error("Please configure GITHUB_TOKEN in .streamlit/secrets.toml")
    st.stop()

HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3.star+json"
}

# --- Custom Styling ---
def local_css():
    st.markdown("""
        <style>
        /* Import Inter font */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
        }

        /* Titles and Headers */
        h1 {
            color: #F8FAFC;
            font-weight: 700;
            letter-spacing: -1px;
        }
        h2, h3 {
            color: #E2E8F0;
            font-weight: 600;
        }
        
        /* Metric Cards */
        div[data-testid="metric-container"] {
            background-color: #1E293B;
            border: 1px solid #334155;
            padding: 15px;
            border-radius: 8px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.2);
        }
        div[data-testid="metric-container"] > label {
            color: #94A3B8;
            font-size: 0.9rem;
        }
        div[data-testid="metric-container"] > div[data-testid="stMetricValue"] {
            color: #F8FAFC;
            font-weight: 700;
        }

        /* Sidebar Styling */
        section[data-testid="stSidebar"] {
            /* Let Streamlit handle background to match theme, just add border */
            border-right: 1px solid #334155;
        }
        
        /* Buttons */
        div.stButton > button {
            width: 100%;
            background-color: #2563EB;
            color: white;
            border: none;
            padding: 0.5rem 1rem;
            border-radius: 6px;
            font-weight: 600;
            transition: all 0.2s;
        }
        div.stButton > button:hover {
            background-color: #1D4ED8;
            box-shadow: 0 4px 6px -1px rgba(37, 99, 235, 0.2);
        }

        /* Custom Badges */
        .badge {
            padding: 4px 8px;
            border-radius: 12px;
            font-size: 0.8rem;
            font-weight: 600;
        }
        .badge-breakout { background-color: #FEF2F2; color: #DC2626; border: 1px solid #FECACA; }
        .badge-growing { background-color: #EFF6FF; color: #2563EB; border: 1px solid #BFDBFE; }
        .badge-early { background-color: #F0FDF4; color: #16A34A; border: 1px solid #BBF7D0; }
        
        </style>
    """, unsafe_allow_html=True)

local_css()

# --- Logic ---

@st.cache_data(ttl=3600)
def fetch_repos(topic, limit=30):
    """Fetch top repositories for a given topic."""
    url = f"https://api.github.com/search/repositories?q=topic:{topic}&sort=stars&order=desc&per_page={limit}"
    try:
        response = requests.get(url, headers=HEADERS)
        if response.status_code != 200:
            return []
        return response.json().get("items", [])
    except Exception:
        return []

def get_star_velocity(owner, repo, total_stars):
    """Calculate stars gained in the last 7 days."""
    if total_stars == 0:
        return 0
    per_page = 100
    last_page = (total_stars // per_page) + 1
    if last_page > 400: last_page = 400
    
    count_7_days = 0
    cutoff_date = datetime.now() - timedelta(days=7)
    max_pages_to_check = 5
    current_page = last_page
    pages_checked = 0
    
    while pages_checked < max_pages_to_check and current_page > 0:
        url = f"https://api.github.com/repos/{owner}/{repo}/stargazers"
        params = {"page": current_page, "per_page": per_page}
        try:
            r = requests.get(url, headers=HEADERS, params=params)
            if r.status_code != 200: break
            data = r.json()
            if not data: break
            
            for star in reversed(data):
                starred_at_str = star.get("starred_at")
                if not starred_at_str: continue
                starred_at = datetime.strptime(starred_at_str, "%Y-%m-%dT%H:%M:%SZ")
                if starred_at > cutoff_date:
                    count_7_days += 1
                else:
                    return count_7_days
            current_page -= 1
            pages_checked += 1
        except Exception:
            break
            
    return count_7_days

def bucket_repo(velocity, stars):
    if stars > 40000 and velocity == 0: return "🔥 Breakout (Huge)"
    if velocity > 50: return "🔥 Breakout"
    elif velocity > 10: return "📈 Growing"
    else: return "👶 Early"

# --- Layout ---

# Sidebar
with st.sidebar:
    st.title("🔍 Sourcing Config")
    st.markdown("---")
    
    PRESET_TOPICS = [
        "generative-ai", "autonomous-agents", "llm-ops", "rag", 
        "rust", "defi", "vector-database", "wasm", "Custom"
    ]
    
    selected_preset = st.selectbox("Thesis / Trend", PRESET_TOPICS)
    if selected_preset == "Custom":
        topic = st.text_input("Enter Topic", value="machine-learning")
    else:
        topic = selected_preset
        
    days_back = st.slider("Lookback (Days)", 1, 30, 7)
    
    st.markdown("---")
    run_pressed = st.button("Run Sourcing Engine")
    
    st.markdown("### ℹ️ About")
    st.info(
        "Scans GitHub for high-velocity repos.\n"
        "**Velocity:** Stars in last 7 days.\n"
        "**Breakout:** >50 stars/week."
    )

# Main Content
st.title("🚀 GitHub Sourcing Engine")
st.markdown(f"**Target Sector:** `{topic}` | **Strategy:** `High Velocity Discovery`")

with st.expander("ℹ️  **Metric Definitions & Legend (Read Me)**"):
    st.markdown("""
    ### **How to interpret these metrics:**
    
    *   **⚡ Velocity (7d)**:  
        The number of **new stars gained in the last 7 days**.  
        *Why it matters:* This is the best proxy for **real-time developer interest** and "hype". High velocity means the repo is currently viral.
    
    *   **📶 Growth Signal:**  
        Automated classification based on the repo's velocity.
        *   🔥 **Breakout:** (>50 stars/week) Viral growth. Rare and highly valuable.
        *   📈 **Growing:** (>10 stars/week) Steady traction and adoption.
        *   👶 **Early:** (<10 stars/week) Niche or just getting started.
    
    *   **⭐ Total Stars:**  
        All-time star count.  
        *Why it matters:* Indicates long-term **credibility** and maturity.
        
    *   **Owner:**  
        The organization or individual user behind the repo.
    """)

if run_pressed:
    with st.status(f"🔎 Scouting the ecosystem for '{topic}'...", expanded=True) as status:
        st.write("CONNECTING to GitHub API...")
        repos = fetch_repos(topic)
        st.write(f"FOUND {len(repos)} candidate repositories.")
        
        results = []
        progress_bar = st.progress(0)
        
        for i, repo in enumerate(repos):
            st.write(f"Analyzing {repo['name']}...")
            velocity = get_star_velocity(repo['owner']['login'], repo['name'], repo['stargazers_count'])
            bucket = bucket_repo(velocity, repo['stargazers_count'])
            
            results.append({
                "Name": repo['name'],
                "Description": repo['description'],
                "Stars": repo['stargazers_count'],
                "Velocity (7d)": velocity,
                "Bucket": bucket,
                "URL": repo['html_url'],
                "Owner": repo['owner']['login']
            })
            progress_bar.progress((i + 1) / len(repos))
            
        status.update(label="Analysis Complete!", state="complete", expanded=False)

    if results:
        df = pd.DataFrame(results)
        df = df.sort_values(by="Velocity (7d)", ascending=False)
        
        # Dashboard Grid
        st.markdown("### 📊 Market Pulse")
        col1, col2, col3, col4 = st.columns(4)
        
        breakout_count = len(df[df['Bucket'].str.contains("Breakout")])
        avg_vel = df['Velocity (7d)'].mean()
        top_repo = df.iloc[0]['Name']
        
        col1.metric("Candidates Scanned", len(df))
        col2.metric("Breakout Signals", breakout_count)
        col3.metric("Avg Velocity (7d)", f"{avg_vel:.1f}")
        col4.metric("Top Mover", top_repo)
        
        st.markdown("---")
        
        tab1, tab2 = st.tabs(["📈 Growth Visualization", "📋 Deal Flow List"])
        
        with tab1:
            c1, c2 = st.columns([2, 1])
            with c1:
                st.subheader("Velocity Leaders")
                top_10 = df.head(10)
                fig_bar = px.bar(
                    top_10, 
                    x='Velocity (7d)', 
                    y='Name', 
                    orientation='h',
                    color='Bucket',
                    text='Velocity (7d)',
                    color_discrete_map={
                        "🔥 Breakout": "#DC2626",
                        "🔥 Breakout (Huge)": "#991B1B",
                        "📈 Growing": "#2563EB",
                        "👶 Early": "#16A34A"
                    }
                )
                fig_bar.update_layout(
                    yaxis={'categoryorder':'total ascending'}, 
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font_color='#F8FAFC'
                )
                st.plotly_chart(fig_bar, use_container_width=True)
            
            with c2:
                st.subheader("Tier Distribution")
                fig_pie = px.pie(
                    df, 
                    names='Bucket', 
                    color='Bucket',
                    hole=0.4,
                    color_discrete_map={
                        "🔥 Breakout": "#DC2626",
                        "🔥 Breakout (Huge)": "#991B1B",
                        "📈 Growing": "#2563EB",
                        "👶 Early": "#16A34A"
                    }
                )
                st.plotly_chart(fig_pie, use_container_width=True)

        with tab2:
            st.subheader("Qualified Leads")
            st.dataframe(
                df[['Bucket', 'Name', 'Description', 'Velocity (7d)', 'Stars', 'URL']],
                column_config={
                    "URL": st.column_config.LinkColumn("Repo Link"),
                    "Velocity (7d)": st.column_config.NumberColumn("7d Gain (Velocity)", format="%d ⭐", help="Stars gained in the last 7 days"),
                    "Stars": st.column_config.NumberColumn("Total Stars", format="%d", help="All-time star count"),
                    "Bucket": st.column_config.TextColumn("Growth Signal", help="🔥 Breakout (>50/wk), 📈 Growing (>10/wk), 👶 Early (<10/wk)"),
                    "Description": st.column_config.TextColumn("Description", width="medium"),
                },
                use_container_width=True,
                hide_index=True
            )
    else:
        st.warning("No repositories found. Try a different topic.")

else:
    # Landing state
    st.markdown("""
    <div style="background-color: #1E293B; padding: 20px; border-radius: 10px; border: 1px solid #334155; color: #F8FAFC;">
        <h3 style="color: #F8FAFC;">👋 Welcome to the Sourcing Engine</h3>
        <p>This tool helps Venture Capitalists and researchers identify high-momentum open source projects before they hit mainstream radar.</p>
        <ul>
            <li>Select a thesis topic from the sidebar.</li>
            <li>Click <b>Run Sourcing Engine</b> to start the scan.</li>
            <li>Analyze real-time developer traction data.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
