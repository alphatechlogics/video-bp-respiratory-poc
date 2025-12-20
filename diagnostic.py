"""
Diagnostic Script for Streamlit Cloud
Run this to check what packages are installed and their versions
"""

import streamlit as st
import sys
import subprocess
import importlib.metadata

st.set_page_config(page_title="Package Diagnostic Tool", layout="wide")

st.title("📦 Package Diagnostic Tool")
st.write("This tool helps diagnose package installation issues on Streamlit Cloud")

# Expected packages
EXPECTED_PACKAGES = {
    'streamlit': '1.31.0',
    'opencv-python-headless': '4.9.0.80',
    'numpy': '1.26.4',
    'vitallens': '0.4.6',
    'matplotlib': '3.8.0',
    'av': '11.0.0'
}

st.header("🐍 Python Environment")
st.write(f"**Python Version:** {sys.version}")
st.write(f"**Python Executable:** {sys.executable}")

st.header("📋 Expected vs Installed Packages")

# Create a comparison table
data = []
for package, expected_version in EXPECTED_PACKAGES.items():
    try:
        # Try to import the package
        if package == 'opencv-python-headless':
            import cv2
            installed_version = cv2.__version__
            status = "✅ Installed"
            module_name = "cv2"
        else:
            try:
                installed_version = importlib.metadata.version(package)
                status = "✅ Installed"
                module_name = package
            except importlib.metadata.PackageNotFoundError:
                installed_version = "Not Found"
                status = "❌ Missing"
                module_name = package
        
        # Check if version matches
        if installed_version != "Not Found":
            if installed_version == expected_version:
                version_status = "✅ Match"
            else:
                version_status = "⚠️ Different"
        else:
            version_status = "❌ N/A"
        
        data.append({
            "Package": package,
            "Expected": expected_version,
            "Installed": installed_version,
            "Status": status,
            "Version Match": version_status
        })
    except Exception as e:
        data.append({
            "Package": package,
            "Expected": expected_version,
            "Installed": f"Error: {str(e)}",
            "Status": "❌ Error",
            "Version Match": "❌ N/A"
        })

# Display as dataframe
import pandas as pd
df = pd.DataFrame(data)
st.dataframe(df, use_container_width=True)

# Check for issues
missing_packages = [p for p in data if p["Status"] == "❌ Missing"]
version_mismatches = [p for p in data if p["Version Match"] == "⚠️ Different"]

if missing_packages:
    st.error(f"⚠️ {len(missing_packages)} package(s) are missing!")
    for pkg in missing_packages:
        st.write(f"- {pkg['Package']}")
else:
    st.success("✅ All expected packages are installed!")

if version_mismatches:
    st.warning(f"⚠️ {len(version_mismatches)} package(s) have different versions:")
    for pkg in version_mismatches:
        st.write(f"- **{pkg['Package']}**: Expected {pkg['Expected']}, Got {pkg['Installed']}")

st.header("🔍 Detailed Import Tests")

# Test each critical import
st.subheader("1. Testing OpenCV (cv2)")
try:
    import cv2
    st.success(f"✅ OpenCV imported successfully - Version: {cv2.__version__}")
    st.write(f"Build info: {cv2.getBuildInformation()[:500]}...")
except Exception as e:
    st.error(f"❌ OpenCV import failed: {str(e)}")

st.subheader("2. Testing NumPy")
try:
    import numpy as np
    st.success(f"✅ NumPy imported successfully - Version: {np.__version__}")
    test_array = np.array([1, 2, 3])
    st.write(f"Test array created: {test_array}")
except Exception as e:
    st.error(f"❌ NumPy import failed: {str(e)}")

st.subheader("3. Testing Matplotlib")
try:
    import matplotlib
    import matplotlib.pyplot as plt
    st.success(f"✅ Matplotlib imported successfully - Version: {matplotlib.__version__}")
except Exception as e:
    st.error(f"❌ Matplotlib import failed: {str(e)}")

st.subheader("4. Testing VitalLens")
try:
    import vitallens
    st.success(f"✅ VitalLens imported successfully")
    st.write(f"Available methods: {dir(vitallens)[:10]}...")
    
    # Check if API key is configured
    if hasattr(st, 'secrets') and 'VITALLENS_API_KEY' in st.secrets:
        st.success("✅ API Key is configured in secrets")
    else:
        st.warning("⚠️ API Key NOT found in secrets")
except Exception as e:
    st.error(f"❌ VitalLens import failed: {str(e)}")

st.subheader("5. Testing AV (PyAV)")
try:
    import av
    st.success(f"✅ AV imported successfully - Version: {av.__version__}")
except Exception as e:
    st.error(f"❌ AV import failed: {str(e)}")

st.header("🔧 System Information")

# Check system packages
st.subheader("System Libraries (from packages.txt)")
try:
    result = subprocess.run(['dpkg', '-l'], capture_output=True, text=True, timeout=5)
    packages_to_check = [
        'libgl1-mesa-glx',
        'libglib2.0-0',
        'libsm6',
        'libxext6',
        'libxrender',
        'libgomp1',
        'ffmpeg'
    ]
    
    st.write("Checking system packages:")
    for pkg in packages_to_check:
        if pkg in result.stdout:
            st.write(f"✅ {pkg} - Installed")
        else:
            st.write(f"❌ {pkg} - Not found")
except Exception as e:
    st.warning(f"Could not check system packages: {str(e)}")

st.header("📝 All Installed Packages")
if st.checkbox("Show all installed packages"):
    try:
        result = subprocess.run([sys.executable, '-m', 'pip', 'list'], 
                              capture_output=True, text=True, timeout=10)
        st.code(result.stdout, language='text')
    except Exception as e:
        st.error(f"Error getting package list: {str(e)}")

st.header("💡 Recommendations")

if missing_packages or version_mismatches:
    st.write("### Suggested Actions:")
    
    if missing_packages:
        st.write("**1. Missing Packages:**")
        st.code("""# Add to requirements.txt:
""" + "\n".join([p['Package'] for p in missing_packages]))
    
    if version_mismatches:
        st.write("**2. Version Mismatches:**")
        st.write("Consider using flexible version constraints:")
        st.code("""# In requirements.txt, use:
streamlit>=1.28.0
opencv-python-headless>=4.8.0
numpy>=1.24.0,<2.0.0
vitallens>=0.4.0
matplotlib>=3.7.0
av>=10.0.0
""")
    
    st.write("**3. Force rebuild:**")
    st.write("- Go to Streamlit Cloud")
    st.write("- Click 'Reboot app' or push a commit")
else:
    st.success("✅ All packages look good! If you're still having issues, it might be:")
    st.write("- API key configuration")
    st.write("- Video file format/size issues")
    st.write("- Network connectivity to VitalLens API")

st.header("🔐 Secrets Check")
if hasattr(st, 'secrets'):
    st.write("Secrets object exists: ✅")
    if 'VITALLENS_API_KEY' in st.secrets:
        api_key = st.secrets['VITALLENS_API_KEY']
        st.write(f"API Key configured: ✅")
        st.write(f"API Key length: {len(api_key)} characters")
        st.write(f"API Key starts with: {api_key[:4]}..." if len(api_key) > 4 else "Too short")
    else:
        st.error("❌ VITALLENS_API_KEY not found in secrets!")
else:
    st.error("❌ Secrets not available!")

st.markdown("---")
st.caption("Run this diagnostic script first, then switch to your main app.py")
