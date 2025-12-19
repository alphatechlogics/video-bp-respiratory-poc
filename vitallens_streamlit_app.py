import streamlit as st
import cv2
import numpy as np
import tempfile
import matplotlib.pyplot as plt

# Must be first Streamlit command
st.set_page_config(
    page_title="VitalLens Health Assessment",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Initialize session state
if 'results' not in st.session_state:
    st.session_state.results = None
if 'fps' not in st.session_state:
    st.session_state.fps = None

# Import VitalLens after Streamlit config
try:
    import vitallens
    VITALLENS_AVAILABLE = True
except ImportError as e:
    VITALLENS_AVAILABLE = False
    st.error(f"VitalLens import error: {e}")

# Custom CSS
st.markdown('''
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    * { font-family: 'Inter', sans-serif; }
    .main { padding: 0 !important; background: #fafafa; }
    .block-container { padding: 2rem 3rem !important; max-width: 100% !important; }
    
    .header-section { text-align: center; padding: 1rem 0 2rem 0; }
    .main-title { font-size: 2.5rem; font-weight: 700; color: #111; margin-bottom: 0.5rem; }
    .main-subtitle { font-size: 1.1rem; color: #666; font-weight: 400; line-height: 1.6; }
    
    .instructions-container {
        background: white; border-radius: 16px; padding: 2rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08); margin-bottom: 2rem;
    }
    .section-title { font-size: 1.4rem; font-weight: 600; color: #111; margin-bottom: 1.5rem; }
    
    .instruction-item {
        display: flex; align-items: flex-start; margin-bottom: 1.2rem;
        font-size: 0.95rem; color: #333;
    }
    .instruction-number {
        background: #f5f5f5; color: #666; min-width: 28px; height: 28px;
        border-radius: 50%; display: flex; align-items: center; justify-content: center;
        font-weight: 600; font-size: 0.85rem; margin-right: 0.8rem; flex-shrink: 0;
    }
    
    .video-section {
        background: white; border-radius: 16px; padding: 2rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08); margin-bottom: 2rem;
    }
    
    .metrics-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-top: 1rem; }
    .metric-card {
        background: white; border-radius: 12px; padding: 1.5rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08); text-align: center; transition: transform 0.2s;
    }
    .metric-card:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,0.12); }
    .metric-icon { font-size: 2rem; margin-bottom: 0.5rem; }
    .metric-label { font-size: 0.85rem; color: #666; font-weight: 500; margin-bottom: 0.3rem; }
    .metric-value { font-size: 2rem; font-weight: 700; color: #111; }
    .metric-unit { font-size: 0.9rem; color: #999; font-weight: 500; }
    
    .stButton > button {
        width: 100%; background: #22c55e !important; color: white !important;
        border: none !important; border-radius: 12px !important; padding: 1rem 2rem !important;
        font-size: 1.1rem !important; font-weight: 600 !important;
        box-shadow: 0 4px 12px rgba(34, 197, 94, 0.3) !important; margin-top: 1rem !important;
    }
    .stButton > button:hover {
        background: #16a34a !important; box-shadow: 0 6px 16px rgba(34, 197, 94, 0.4) !important;
        transform: translateY(-1px);
    }
    
    .chart-container {
        background: white; border-radius: 12px; padding: 1.5rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08); margin-bottom: 1rem;
    }
    .chart-title { font-size: 1.1rem; font-weight: 600; color: #111; margin-bottom: 1rem; }
    .more-metrics {
        text-align: center; padding: 1rem; color: #666;
        font-size: 0.9rem; font-weight: 500;
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {visibility: hidden;}
</style>
''', unsafe_allow_html=True)

# Header
st.markdown('''
<div class="header-section">
    <div class="main-title">Monitor 2 health metrics in just 30 seconds—with a video scan.</div>
    <div class="main-subtitle">Measure health markers like blood pressure, BMI, heart rate (HR), heart rate variability (HRV) and more in just 30 seconds via video scan.</div>
</div>
''', unsafe_allow_html=True)

# Main Layout
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
    
    st.markdown('</div></div>', unsafe_allow_html=True)
    
    # Scenario section
    st.markdown('<div class="instructions-container">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Scenario Selection</div>', unsafe_allow_html=True)
    
    scenario = st.radio(
        "Choose assessment type",
        ["Health Assessment", "Fitness Tracking", "Wellness Monitoring"],
        label_visibility="collapsed"
    )
    
    st.markdown('''
    <div style="background: #f9fafb; border-radius: 8px; padding: 1rem; margin-top: 1rem; font-size: 0.9rem; color: #555; line-height: 1.6;">
        This health assessment uses rPPG, computer vision, and advanced AI to build a full profile of your health markers.
        <br><br>
        Click <strong>START ANALYSIS</strong> to take a 30 second video scan.
    </div>
    ''', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# MIDDLE COLUMN - Video Upload & Analysis
with col2:
    st.markdown('<div class="video-section">', unsafe_allow_html=True)
    
    # File upload
    video_file = st.file_uploader(
        "Upload Video File",
        type=["mp4", "avi", "mov"],
        help="Upload a video showing your face clearly"
    )
    
    # API Key
    api_key = st.text_input(
        "VitalLens API Key",
        type="password",
        placeholder="Enter your API key from VitalLens",
        help="Get your API key from the VitalLens dashboard"
    )
    
    # Display video if uploaded
    if video_file:
        st.video(video_file)
        
        # Save to temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmp_file:
            tmp_file.write(video_file.read())
            video_path = tmp_file.name
    else:
        video_path = None
        st.info("📹 Please upload a video file to begin")
    
    # Analysis button
    if video_path and api_key and VITALLENS_AVAILABLE:
        if st.button("START ANALYSIS", type="primary", use_container_width=True):
            try:
                # Load video
                with st.spinner("Loading video..."):
                    cap = cv2.VideoCapture(video_path)
                    if not cap.isOpened():
                        st.error("Cannot open video file")
                        st.stop()
                    
                    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
                    frames = []
                    
                    while len(frames) < 1800:  # Max 60 seconds
                        ret, frame = cap.read()
                        if not ret:
                            break
                        frames.append(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                    
                    cap.release()
                
                if not frames:
                    st.error("No frames could be read from video")
                    st.stop()
                
                video_array = np.array(frames)
                st.success(f"✅ Loaded {len(frames)} frames ({len(frames)/fps:.1f}s)")
                
                # Initialize VitalLens
                with st.spinner("Initializing VitalLens..."):
                    vl = vitallens.VitalLens(
                        method=vitallens.Method.VITALLENS,
                        api_key=api_key,
                        mode=vitallens.Mode.BURST,
                        export_to_json=False,
                        estimate_rolling_vitals=True
                    )
                
                # Analyze
                with st.spinner("Analyzing vital signs..."):
                    results = vl(video_array, fps=fps)
                
                if not results:
                    st.error("⚠️ No face detected. Ensure face is visible and well-lit.")
                else:
                    st.session_state.results = results[0]['vital_signs']
                    st.session_state.fps = fps
                    st.success("✅ Analysis complete!")
                    st.rerun()
                    
            except Exception as e:
                st.error(f"Error: {str(e)}")
                import traceback
                st.code(traceback.format_exc())
    
    elif not VITALLENS_AVAILABLE:
        st.error("VitalLens library not available")
    elif not api_key:
        st.warning("Please enter your API key")
    
    st.markdown('</div>', unsafe_allow_html=True)

# RIGHT COLUMN - Metrics
with col3:
    if st.session_state.results:
        vital_signs = st.session_state.results
        hr = vital_signs.get('heart_rate', {}).get('value')
        rr = vital_signs.get('respiratory_rate', {}).get('value')
        
        st.markdown('<div class="metrics-grid">', unsafe_allow_html=True)
        
        # Heart Rate
        hr_display = f'{hr:.0f}<span class="metric-unit"> bpm</span>' if hr else '--'
        st.markdown(f'<div class="metric-card"><div class="metric-icon">❤️</div><div class="metric-label">Heart Rate</div><div class="metric-value">{hr_display}</div></div>', unsafe_allow_html=True)
        
        # Respiratory Rate
        rr_display = f'{rr:.0f}<span class="metric-unit"> rpm</span>' if rr else '--'
        st.markdown(f'<div class="metric-card"><div class="metric-icon">🫁</div><div class="metric-label">Breathing Rate</div><div class="metric-value">{rr_display}</div></div>', unsafe_allow_html=True)
        
        # Placeholders
        for icon, label in [("🩺", "Blood Pressure"), ("📊", "Body Mass Index"), 
                            ("💓", "Heart Rate Variability"), ("📈", "Cardiac Stress Index")]:
            st.markdown(f'<div class="metric-card"><div class="metric-icon">{icon}</div><div class="metric-label">{label}</div><div class="metric-value">--</div></div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('<div class="more-metrics">+25 More Health Markers</div>', unsafe_allow_html=True)
    else:
        # Empty state
        st.markdown('<div class="metrics-grid">', unsafe_allow_html=True)
        for icon, label in [("❤️", "Heart Rate"), ("🫁", "Breathing Rate"), ("🩺", "Blood Pressure"),
                            ("📊", "Body Mass Index"), ("💓", "Heart Rate Variability"), ("📈", "Cardiac Stress Index")]:
            st.markdown(f'<div class="metric-card"><div class="metric-icon">{icon}</div><div class="metric-label">{label}</div><div class="metric-value">--</div></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('<div class="more-metrics">+25 More Health Markers</div>', unsafe_allow_html=True)

# Charts Section
if st.session_state.results:
    vital_signs = st.session_state.results
    fps = st.session_state.fps
    
    has_hr = 'rolling_heart_rate' in vital_signs
    has_rr = 'rolling_respiratory_rate' in vital_signs
    
    if has_hr or has_rr:
        st.markdown("---")
        st.markdown('<div class="section-title" style="text-align: center; margin: 2rem 0;">📈 Detailed Analysis</div>', unsafe_allow_html=True)
        
        c1, c2 = st.columns(2, gap="large")
        
        with c1:
            if has_hr:
                rolling_hr = vital_signs['rolling_heart_rate']['data']
                time_axis = np.arange(len(rolling_hr)) / fps
                hr_avg = vital_signs.get('heart_rate', {}).get('value')
                
                fig, ax = plt.subplots(figsize=(7, 4), facecolor='white')
                ax.plot(time_axis, rolling_hr, color='#ef4444', linewidth=2.5, label='Heart Rate')
                if hr_avg:
                    ax.axhline(y=hr_avg, color='#dc2626', linestyle='--', linewidth=1.5, alpha=0.7, label=f'Avg: {hr_avg:.0f} bpm')
                ax.set_xlabel("Time (seconds)", fontsize=10)
                ax.set_ylabel("Heart Rate (bpm)", fontsize=10)
                ax.grid(True, alpha=0.2)
                ax.spines['top'].set_visible(False)
                ax.spines['right'].set_visible(False)
                ax.legend(loc='upper right', fontsize=8)
                plt.tight_layout()
                st.pyplot(fig)
                plt.close()
        
        with c2:
            if has_rr:
                rolling_rr = vital_signs['rolling_respiratory_rate']['data']
                time_axis = np.arange(len(rolling_rr)) / fps
                rr_avg = vital_signs.get('respiratory_rate', {}).get('value')
                
                fig, ax = plt.subplots(figsize=(7, 4), facecolor='white')
                ax.plot(time_axis, rolling_rr, color='#3b82f6', linewidth=2.5, label='Respiratory Rate')
                if rr_avg:
                    ax.axhline(y=rr_avg, color='#2563eb', linestyle='--', linewidth=1.5, alpha=0.7, label=f'Avg: {rr_avg:.0f} rpm')
                ax.set_xlabel("Time (seconds)", fontsize=10)
                ax.set_ylabel("Respiratory Rate (rpm)", fontsize=10)
                ax.grid(True, alpha=0.2)
                ax.spines['top'].set_visible(False)
                ax.spines['right'].set_visible(False)
                ax.legend(loc='upper right', fontsize=8)
                plt.tight_layout()
                st.pyplot(fig)
                plt.close()
