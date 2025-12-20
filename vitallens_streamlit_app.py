import streamlit as st
import cv2
import numpy as np
import vitallens
import tempfile
import matplotlib.pyplot as plt
import os

# Page config
st.set_page_config(
    page_title="VitalLens Health Assessment",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS matching Shen AI design
st.markdown('''
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    * {
        font-family: 'Inter', sans-serif;
    }

    /* Remove default padding */
    .main {
        padding: 0 !important;
        background: #fafafa;
    }

    .block-container {
        padding: 2rem 3rem !important;
        max-width: 100% !important;
    }

    /* Header section */
    .header-section {
        text-align: center;
        padding: 1rem 0 2rem 0;
    }

    .main-title {
        font-size: 2.5rem;
        font-weight: 700;
        color: #111;
        margin-bottom: 0.5rem;
    }

    .main-subtitle {
        font-size: 1.1rem;
        color: #666;
        font-weight: 400;
        line-height: 1.6;
    }

    /* Instructions box - left side */
    .instructions-container {
        background: white;
        border-radius: 16px;
        padding: 2rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        margin-bottom: 2rem;
    }

    .section-title {
        font-size: 1.4rem;
        font-weight: 600;
        color: #111;
        margin-bottom: 1.5rem;
    }

    .instruction-item {
        display: flex;
        align-items: flex-start;
        margin-bottom: 1.2rem;
        font-size: 0.95rem;
        color: #333;
    }

    .instruction-number {
        background: #f5f5f5;
        color: #666;
        min-width: 28px;
        height: 28px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 600;
        font-size: 0.85rem;
        margin-right: 0.8rem;
        flex-shrink: 0;
    }

    /* Video container - center */
    .video-section {
        background: white;
        border-radius: 16px;
        padding: 2rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        margin-bottom: 2rem;
    }

    .video-wrapper {
        position: relative;
        background: #000;
        border-radius: 12px;
        overflow: hidden;
        aspect-ratio: 4/3;
        display: flex;
        align-items: center;
        justify-content: center;
    }

    .placeholder-text {
        color: #999;
        font-size: 1rem;
    }

    /* Metrics grid - right side */
    .metrics-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 1rem;
        margin-top: 1rem;
    }

    .metric-card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        text-align: center;
        transition: transform 0.2s;
    }

    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.12);
    }

    .metric-icon {
        font-size: 2rem;
        margin-bottom: 0.5rem;
    }

    .metric-label {
        font-size: 0.85rem;
        color: #666;
        font-weight: 500;
        margin-bottom: 0.3rem;
    }

    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: #111;
    }

    .metric-unit {
        font-size: 0.9rem;
        color: #999;
        font-weight: 500;
    }

    /* Start button */
    .stButton > button {
        width: 100%;
        background: #22c55e !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 1rem 2rem !important;
        font-size: 1.1rem !important;
        font-weight: 600 !important;
        letter-spacing: 0.5px !important;
        transition: all 0.2s !important;
        box-shadow: 0 4px 12px rgba(34, 197, 94, 0.3) !important;
        margin-top: 1rem !important;
    }

    .stButton > button:hover {
        background: #16a34a !important;
        box-shadow: 0 6px 16px rgba(34, 197, 94, 0.4) !important;
        transform: translateY(-1px);
    }

    /* File uploader styling */
    .stFileUploader {
        border: 2px dashed #ddd;
        border-radius: 12px;
        padding: 2rem;
        text-align: center;
        background: #fafafa;
    }

    .stFileUploader > div {
        text-align: center;
    }

    /* Info message */
    .upload-info {
        text-align: center;
        padding: 3rem 2rem;
        color: #999;
        font-size: 1rem;
    }

    /* Hide Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {visibility: hidden;}

    /* Chart styling */
    .chart-container {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        margin-bottom: 1rem;
    }

    .chart-title {
        font-size: 1.1rem;
        font-weight: 600;
        color: #111;
        margin-bottom: 1rem;
    }

    /* Additional metrics section */
    .more-metrics {
        text-align: center;
        padding: 1rem;
        color: #666;
        font-size: 0.9rem;
        font-weight: 500;
        cursor: pointer;
    }

    /* Scenario dropdown */
    .stSelectbox {
        margin-top: 1rem;
    }

    .scenario-description {
        background: #f9fafb;
        border-radius: 8px;
        padding: 1rem;
        margin-top: 1rem;
        font-size: 0.9rem;
        color: #555;
        line-height: 1.6;
    }
</style>
''', unsafe_allow_html=True)

# Header
st.markdown('''
<div class="header-section">
    <div class="main-title">Monitor 2 health metrics in just 30 seconds—with a video scan.</div>
    <div class="main-subtitle">Measure health markers like blood pressure, BMI, heart rate (HR), heart rate variability (HRV) and more in just 30 seconds via video scan.</div>
</div>
''', unsafe_allow_html=True)

# Create three columns layout
col1, col2, col3 = st.columns([2, 3, 2], gap="large")

# LEFT COLUMN - Instructions
with col1:
    st.markdown('<div class="instructions-container">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">How to take assessment</div>', unsafe_allow_html=True)

    instructions = [
        "Ensure good lighting for clear visibility.",
        "Position your device's camera so it's level with your eyes.",
        "Avoid talking or moving your head."
    ]

    for i, instruction in enumerate(instructions, 1):
        st.markdown(f'<div class="instruction-item"><div class="instruction-number">{i}</div><div>{instruction}</div></div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # Scenario selection
    st.markdown('<div class="instructions-container">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Apply Shen in various scenarios</div>', unsafe_allow_html=True)
    scenario = st.selectbox("", ["Health Assessment", "Fitness Tracking", "Wellness Monitoring"], label_visibility="collapsed")

    st.markdown('''
    <div class="scenario-description">
        This health assessment uses rPPG, computer vision, and advanced AI to build a full profile of your health markers.
        <br><br>
        Click <strong>START</strong> to take a 30 seconds video scan and get insights into your health.
    </div>
    ''', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# MIDDLE COLUMN - Video Display
with col2:
    st.markdown('<div class="video-section">', unsafe_allow_html=True)

    video_file = st.file_uploader("📹 Upload Video", type=["mp4", "avi", "mov"])

    video_path = None
    if video_file is not None:
        # Save uploaded file to temporary location
        tfile = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
        tfile.write(video_file.read())
        video_path = tfile.name
        tfile.close()

    if video_path:
        st.video(video_path)
    else:
        st.markdown('<div class="video-wrapper"><div class="upload-info">📹 Please upload a video file to begin assessment</div></div>', unsafe_allow_html=True)

    # Start button
    if video_path:
        if st.button("START", use_container_width=True):
            with st.spinner("Loading and analyzing video..."):
                try:
                    # Load video
                    cap = cv2.VideoCapture(video_path)
                    fps = cap.get(cv2.CAP_PROP_FPS) or 30
                    frames = []
                    
                    while True:
                        ret, frame = cap.read()
                        if not ret:
                            break
                        frames.append(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                    
                    cap.release()
                    video_array = np.array(frames)

                    st.success(f"✅ Video loaded: {len(frames)} frames at {fps:.1f} FPS")

                    # Initialize VitalLens with API key from secrets
                    API_KEY = st.secrets.get("VITALLENS_API_KEY", "GdsxHv55ys3pWHUEc8tZm5Sr6H5oeb7n30NouKyX")
                    
                    vl = vitallens.VitalLens(
                        method=vitallens.Method.VITALLENS,
                        api_key=API_KEY,
                        mode=vitallens.Mode.BURST,
                        export_to_json=True,
                        export_dir=tempfile.gettempdir(),
                        estimate_rolling_vitals=True
                    )

                    # Analyze
                    with st.spinner("Analyzing vital signs..."):
                        results = vl(video_array, fps=fps, export_filename="vitals_analysis")

                    if not results:
                        st.error("⚠️ No face detected in video!")
                    else:
                        st.session_state['results'] = results[0]['vital_signs']
                        st.session_state['fps'] = fps
                        st.rerun()
                
                except Exception as e:
                    st.error(f"❌ Error processing video: {str(e)}")
                
                finally:
                    # Clean up temporary file
                    if os.path.exists(video_path):
                        try:
                            os.unlink(video_path)
                        except:
                            pass

    st.markdown('</div>', unsafe_allow_html=True)

# RIGHT COLUMN - Metrics Display
with col3:
    if 'results' in st.session_state:
        vital_signs = st.session_state['results']

        hr_global = vital_signs.get('heart_rate', {}).get('value')
        rr_global = vital_signs.get('respiratory_rate', {}).get('value')

        # Metrics grid
        st.markdown('<div class="metrics-grid">', unsafe_allow_html=True)

        # Heart Rate
        if hr_global:
            st.markdown(f'<div class="metric-card"><div class="metric-icon">❤️</div><div class="metric-label">Heart Rate</div><div class="metric-value">{hr_global:.0f}<span class="metric-unit"> bpm</span></div></div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="metric-card"><div class="metric-icon">❤️</div><div class="metric-label">Heart Rate</div><div class="metric-value">--</div></div>', unsafe_allow_html=True)

        # Breathing Rate
        if rr_global:
            st.markdown(f'<div class="metric-card"><div class="metric-icon">🫁</div><div class="metric-label">Breathing Rate</div><div class="metric-value">{rr_global:.0f}<span class="metric-unit"> rpm</span></div></div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="metric-card"><div class="metric-icon">🫁</div><div class="metric-label">Breathing Rate</div><div class="metric-value">--</div></div>', unsafe_allow_html=True)

        # Blood Pressure placeholder
        st.markdown('<div class="metric-card"><div class="metric-icon">🩺</div><div class="metric-label">Blood Pressure</div><div class="metric-value">--</div></div>', unsafe_allow_html=True)

        # BMI placeholder
        st.markdown('<div class="metric-card"><div class="metric-icon">📊</div><div class="metric-label">Body Mass Index</div><div class="metric-value">--</div></div>', unsafe_allow_html=True)

        # HRV placeholder
        st.markdown('<div class="metric-card"><div class="metric-icon">💓</div><div class="metric-label">Heart Rate Variability</div><div class="metric-value">--</div></div>', unsafe_allow_html=True)

        # Cardiac Stress placeholder
        st.markdown('<div class="metric-card"><div class="metric-icon">📈</div><div class="metric-label">Cardiac Stress Index</div><div class="metric-value">--</div></div>', unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

        # More metrics indicator
        st.markdown('<div class="more-metrics">+25 More Health Markers</div>', unsafe_allow_html=True)
    else:
        # Show empty state
        st.markdown('<div class="metrics-grid">', unsafe_allow_html=True)

        metrics = [
            ("❤️", "Heart Rate"),
            ("🫁", "Breathing Rate"),
            ("🩺", "Blood Pressure"),
            ("📊", "Body Mass Index"),
            ("💓", "Heart Rate Variability"),
            ("📈", "Cardiac Stress Index")
        ]

        for icon, label in metrics:
            st.markdown(f'<div class="metric-card"><div class="metric-icon">{icon}</div><div class="metric-label">{label}</div><div class="metric-value">--</div></div>', unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('<div class="more-metrics">+25 More Health Markers</div>', unsafe_allow_html=True)

# Display detailed charts if results exist
if 'results' in st.session_state:
    vital_signs = st.session_state['results']
    fps = st.session_state['fps']

    has_rolling_hr = 'rolling_heart_rate' in vital_signs
    has_rolling_rr = 'rolling_respiratory_rate' in vital_signs

    st.markdown("---")
    st.markdown('<div class="section-title" style="text-align: center; margin: 2rem 0;">📈 Detailed Analysis</div>', unsafe_allow_html=True)

    chart_col1, chart_col2 = st.columns(2, gap="large")

    with chart_col1:
        if has_rolling_hr:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.markdown('<div class="chart-title">Heart Rate Over Time</div>', unsafe_allow_html=True)

            rolling_hr = vital_signs['rolling_heart_rate']['data']
            time_axis = np.arange(len(rolling_hr)) / fps
            hr_global = vital_signs.get('heart_rate', {}).get('value')

            fig, ax = plt.subplots(figsize=(7, 4), facecolor='white')
            ax.plot(time_axis, rolling_hr, color='#ef4444', linewidth=2.5)
            if hr_global:
                ax.axhline(y=hr_global, color='#dc2626', linestyle='--', linewidth=1.5, alpha=0.7)
            ax.set_xlabel("Time (seconds)", fontsize=10)
            ax.set_ylabel("Heart Rate (bpm)", fontsize=10)
            ax.grid(True, alpha=0.2, linestyle='-', linewidth=0.5)
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            plt.tight_layout()
            st.pyplot(fig)
            plt.close()
            st.markdown('</div>', unsafe_allow_html=True)

    with chart_col2:
        if has_rolling_rr:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.markdown('<div class="chart-title">Respiratory Rate Over Time</div>', unsafe_allow_html=True)

            rolling_rr = vital_signs['rolling_respiratory_rate']['data']
            time_axis = np.arange(len(rolling_rr)) / fps
            rr_global = vital_signs.get('respiratory_rate', {}).get('value')

            fig, ax = plt.subplots(figsize=(7, 4), facecolor='white')
            ax.plot(time_axis, rolling_rr, color='#3b82f6', linewidth=2.5)
            if rr_global:
                ax.axhline(y=rr_global, color='#2563eb', linestyle='--', linewidth=1.5, alpha=0.7)
            ax.set_xlabel("Time (seconds)", fontsize=10)
            ax.set_ylabel("Respiratory Rate (rpm)", fontsize=10)
            ax.grid(True, alpha=0.2, linestyle='-', linewidth=0.5)
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            plt.tight_layout()
            st.pyplot(fig)
            plt.close()
            st.markdown('</div>', unsafe_allow_html=True)
