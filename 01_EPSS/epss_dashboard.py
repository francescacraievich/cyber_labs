"""
EPSS Tracker Dashboard
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import requests
from datetime import datetime
import os

# Page config
st.set_page_config(
    page_title="EPSS Tracker",
    page_icon="📊",
    layout="wide"
)

# Professional dark theme
st.markdown("""
<style>
    .main {background-color: #0e1117;}
    h1, h2, h3 {color: #fafafa; font-weight: 400;}
    .stSelectbox {background-color: #262730;}
    .metric-card {
        background-color: #1e1e1e;
        padding: 15px;
        border-radius: 5px;
        border: 1px solid #333;
    }
</style>
""", unsafe_allow_html=True)

st.title("EPSS Evolution Tracker")

# Load submission and full dataset
@st.cache_data
def load_submission():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(script_dir, 'data', 'TheCybeerGirl.csv')
    df = pd.read_csv(csv_path, index_col=0)
    return df

@st.cache_data
def load_full_dataset():
    """Load full dataset with CVE publication dates and initial EPSS values"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(script_dir, 'data', 'vuln_2025_09.csv')
    df = pd.read_csv(csv_path, index_col=0)
    # Extract just the date from the timestamp
    df['cve.published_date'] = pd.to_datetime(df['cve.published']).dt.date.astype(str)
    return df

submission_df = load_submission()
full_dataset = load_full_dataset()
selected_cves = submission_df['cve.id'].to_list()

# Create lookup for initial data from September dataset
initial_data = {}
for cve_id in selected_cves:
    cve_row = full_dataset[full_dataset['cve.id'] == cve_id]
    if not cve_row.empty:
        initial_data[cve_id] = {
            'published': cve_row.iloc[0]['cve.published_date'],
            'epss': cve_row.iloc[0]['epss'],
            'percentile': cve_row.iloc[0]['percentile']
        }

# Sidebar
st.sidebar.header("Configuration")
group_name = st.sidebar.text_input("Group name", "Francesca Craievich")
metric_mode = st.sidebar.radio("Display metric", ["EPSS Score", "Percentile"], index=0)

# Fetch historical EPSS data using monthly snapshots + recent time-series
@st.cache_data(ttl=3600)
def fetch_historical_epss(cve_list):
    """Fetch EPSS history by sampling monthly snapshots + last 30 days detail"""
    results = {}

    # Generate sample dates: biweekly from Oct 2025 to ~30 days ago
    from datetime import timedelta
    sample_dates = []
    d = datetime(2025, 10, 1)
    now = datetime.now()
    cutoff = now - timedelta(days=30)
    while d < cutoff:
        sample_dates.append(d.strftime('%Y-%m-%d'))
        d = d + timedelta(days=14)

    cve_str = ",".join(cve_list)

    try:
        # 1. Fetch biweekly snapshots — batch all CVEs per date
        for sample_date in sample_dates:
            url = f"https://api.first.org/data/v1/epss?cve={cve_str}&date={sample_date}"
            response = requests.get(url, timeout=15)
            if response.status_code == 200:
                for item in response.json().get('data', []):
                    cve_id = item['cve']
                    if cve_id not in results:
                        results[cve_id] = []
                    results[cve_id].append({
                        'date': item['date'],
                        'epss': float(item['epss']),
                        'percentile': float(item['percentile'])
                    })

        # 2. Fetch last 30 days detail via time-series (per CVE)
        for cve_id in cve_list:
            url = f"https://api.first.org/data/v1/epss?cve={cve_id}&scope=time-series"
            response = requests.get(url, timeout=15)
            if response.status_code == 200:
                data = response.json().get('data', [])
                if data and len(data) > 0:
                    if cve_id not in results:
                        results[cve_id] = []
                    for item in data[0].get('time-series', []):
                        results[cve_id].append({
                            'date': item['date'],
                            'epss': float(item['epss']),
                            'percentile': float(item['percentile'])
                        })

        # Deduplicate by date and sort for each CVE
        for cve_id in results:
            seen = {}
            for h in results[cve_id]:
                seen[h['date']] = h
            results[cve_id] = sorted(seen.values(), key=lambda x: x['date'])

    except Exception as e:
        st.sidebar.error(f"API Error: {str(e)}")

    return results

@st.cache_data(ttl=3600)
def fetch_current_epss(cve_list):
    """Fetch current EPSS scores from FIRST API"""
    results = {}

    try:
        # Batch request
        cve_str = ",".join(cve_list)
        url = f"https://api.first.org/data/v1/epss?cve={cve_str}"
        response = requests.get(url, timeout=15)

        if response.status_code == 200:
            data = response.json()
            for item in data.get('data', []):
                results[item['cve']] = {
                    'epss': float(item['epss']),
                    'percentile': float(item['percentile']),
                    'date': item['date']
                }
    except Exception as e:
        st.sidebar.error(f"API Error: {str(e)}")

    return results

# Fetch data
with st.spinner("Fetching EPSS historical data from FIRST API..."):
    historical_data = fetch_historical_epss(selected_cves)
    current_data = fetch_current_epss(selected_cves)

# Calculate changes
changes_data = []
for idx, row in submission_df.iterrows():
    cve_id = row['cve.id']
    initial_epss = row['epss']
    initial_percentile = row['percentile']

    if cve_id in current_data:
        current_epss = current_data[cve_id]['epss']
        current_percentile = current_data[cve_id]['percentile']
        last_update = current_data[cve_id]['date']
    else:
        current_epss = initial_epss
        current_percentile = initial_percentile
        last_update = '2025-10-01'

    delta_epss = current_epss - initial_epss
    delta_pct = ((current_epss - initial_epss) / initial_epss * 100) if initial_epss > 0 else 0

    changes_data.append({
        'CVE ID': cve_id,
        'Initial EPSS': initial_epss,
        'Current EPSS': current_epss,
        'Delta': delta_epss,
        'Change (%)': delta_pct,
        'Initial Percentile': initial_percentile,
        'Current Percentile': current_percentile,
        'Last Update': last_update
    })

changes_df = pd.DataFrame(changes_data)

# Main layout
col1, col2 = st.columns([2, 1])

with col1:
    use_percentile = (metric_mode == "Percentile")
    metric_key = 'percentile' if use_percentile else 'epss'
    metric_label = "Percentile" if use_percentile else "EPSS Score"

    st.subheader(f"{metric_label} Evolution")
    st.caption(f"Group: {group_name}")

    fig = go.Figure()

    colors = [
        '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
        '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf'
    ]

    for i, (idx, row) in enumerate(submission_df.iterrows()):
        cve_id = row['cve.id']

        if cve_id in initial_data:
            start_date = initial_data[cve_id]['published']
            start_val = initial_data[cve_id][metric_key]
        else:
            start_date = '2025-09-01'
            start_val = row[metric_key] if metric_key in row else row['epss']

        dates = [start_date]
        values = [start_val]

        if cve_id in historical_data and len(historical_data[cve_id]) > 0:
            history = historical_data[cve_id]
            filtered = [h for h in history if h['date'] >= start_date]

            if len(filtered) > 0:
                for point in filtered:
                    dates.append(point['date'])
                    values.append(point[metric_key])
            else:
                dates.append(datetime.now().strftime('%Y-%m-%d'))
                values.append(values[-1])
        else:
            dates.append(datetime.now().strftime('%Y-%m-%d'))
            values.append(start_val)

        fig.add_trace(go.Scatter(
            x=dates, y=values, mode='lines', name=cve_id,
            line=dict(color=colors[i % len(colors)], width=2),
            hovertemplate=(
                f'<b>{cve_id}</b><br>'
                f'Date: %{{x}}<br>'
                f'{metric_label}: %{{y:.5f}}<br>'
                '<extra></extra>'
            )
        ))

    y_max = 1.0 if use_percentile else max(changes_df['Current EPSS'].max() * 1.2, 0.01)
    fig.update_layout(
        xaxis_title="Date",
        yaxis_title=metric_label,
        plot_bgcolor='#1e1e1e',
        paper_bgcolor='#1e1e1e',
        font=dict(color='#fafafa', family='Arial', size=12),
        xaxis=dict(gridcolor='#333333', showgrid=True, linecolor='#555555'),
        yaxis=dict(gridcolor='#333333', showgrid=True, linecolor='#555555',
                   range=[0, y_max]),
        hovermode='closest', height=500,
        legend=dict(
            orientation="v", yanchor="top", y=0.98, xanchor="left", x=1.02,
            bgcolor='rgba(30, 30, 30, 0.9)', bordercolor='#888888',
            borderwidth=1, font=dict(size=12, color='#ffffff')
        ),
        margin=dict(r=150)
    )

    st.plotly_chart(fig, use_container_width=True)

with col2:
    # Add spacing to align with left column title
    st.markdown("<div style='height: 60px;'></div>", unsafe_allow_html=True)

    st.subheader("Summary Statistics")

    # Metrics
    total_cves = len(selected_cves)
    increased_count = (changes_df['Delta'] > 0).sum()
    decreased_count = (changes_df['Delta'] < 0).sum()
    unchanged_count = (changes_df['Delta'] == 0).sum()

    st.markdown(f"""
    <div class="metric-card">
        <p style="margin: 5px 0; color: #ffffff; font-weight: 500;">Total CVEs</p>
        <h2 style="margin: 5px 0; color: #ffffff;">{total_cves}</h2>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown(f"""
    <div class="metric-card">
        <p style="margin: 5px 0; color: #ffffff; font-weight: 500;">Status Distribution</p>
        <p style="margin: 5px 0; color: #4caf50; font-weight: 500;">Increased: {increased_count}</p>
        <p style="margin: 5px 0; color: #f44336; font-weight: 500;">Decreased: {decreased_count}</p>
        <p style="margin: 5px 0; color: #ffffff; font-weight: 500;">Unchanged: {unchanged_count}</p>
    </div>
    """, unsafe_allow_html=True)

# Detailed changes table
st.markdown("---")
st.subheader("Detailed CVE Changes")

# Format table
display_df = changes_df.copy()
display_df['Initial EPSS'] = display_df['Initial EPSS'].apply(lambda x: f"{x:.5f}")
display_df['Current EPSS'] = display_df['Current EPSS'].apply(lambda x: f"{x:.5f}")
display_df['Delta'] = display_df['Delta'].apply(lambda x: f"{x:+.5f}")
display_df['Change (%)'] = display_df['Change (%)'].apply(lambda x: f"{x:+.2f}%")
display_df['Initial Percentile'] = display_df['Initial Percentile'].apply(lambda x: f"{x:.5f}")
display_df['Current Percentile'] = display_df['Current Percentile'].apply(lambda x: f"{x:.5f}")

# Style function
def highlight_changes(row):
    delta_val = float(row['Delta'])
    if delta_val > 0:
        color = 'background-color: rgba(76, 175, 80, 0.2)'
    elif delta_val < 0:
        color = 'background-color: rgba(244, 67, 54, 0.2)'
    else:
        color = ''
    return [color] * len(row)

styled_df = display_df.style.apply(highlight_changes, axis=1)

st.dataframe(
    styled_df,
    use_container_width=True,
    height=400
)

# Footer
st.markdown("---")
st.caption(f"Last update: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
st.caption("Data source: FIRST.org EPSS API | Dataset: September 2025 CVEs")
