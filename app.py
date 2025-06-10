import streamlit as st
import requests
import json
import jwt
from datetime import datetime, timedelta
import time

# Page configuration
st.set_page_config(
    page_title="WoWonder JWT Token Generator",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-size: 3rem;
        font-weight: bold;
        margin-bottom: 2rem;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 1rem;
        border-radius: 0.375rem;
        margin: 1rem 0;
    }
    .error-box {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
        padding: 1rem;
        border-radius: 0.375rem;
        margin: 1rem 0;
    }
    .info-box {
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        color: #0c5460;
        padding: 1rem;
        border-radius: 0.375rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Main header
st.markdown('<h1 class="main-header">🔐 WoWonder JWT Token Generator</h1>', unsafe_allow_html=True)

# Initialize session state
if 'access_token' not in st.session_state:
    st.session_state.access_token = None
if 'jwt_token' not in st.session_state:
    st.session_state.jwt_token = None
if 'user_data' not in st.session_state:
    st.session_state.user_data = None

# Sidebar configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # API Configuration
    st.subheader("API Settings")
    api_url = st.text_input("API Base URL", value="https://zzatem.com", help="Base URL for your WoWonder site")
    
    # Credentials
    st.subheader("Authentication")
    username = st.text_input("Username", value="Cathlene", help="Your WoWonder username")
    password = st.text_input("Password", value="ZZatem1!", type="password", help="Your WoWonder password")
    server_key = st.text_input("Server Key", value="ad18880474e60cd46a62b81194a6c296", type="password", help="Your WoWonder server key")
    
    # JWT Configuration
    st.subheader("JWT Settings")
    jwt_secret = st.text_input("JWT Secret Key", value="your-secret-key", type="password", help="Secret key for JWT signing")
    jwt_expiry_hours = st.number_input("Token Expiry (hours)", min_value=1, max_value=168, value=24, help="JWT token expiry time in hours")

# Main content area
col1, col2 = st.columns([1, 1])

with col1:
    st.header("🔑 Authentication")
    
    if st.button("🚀 Authenticate & Generate Token", type="primary", use_container_width=True):
        if not all([api_url, username, password, server_key]):
            st.error("❌ Please fill in all required fields")
        else:
            with st.spinner("🔄 Authenticating..."):
                try:
                    # Authentication request
                    auth_url = f"{api_url.rstrip('/')}/api/auth"
                    
                    headers = {
                        'Content-Type': 'application/x-www-form-urlencoded'
                    }
                    
                    data = {
                        'username': username,
                        'password': password,
                        'server_key': server_key
                    }
                    
                    response = requests.post(auth_url, headers=headers, data=data, timeout=30)
                    
                    if response.status_code == 200:
                        auth_data = response.json()
                        
                        if auth_data.get('api_status') == 200:
                            st.session_state.access_token = auth_data.get('access_token')
                            st.session_state.user_data = auth_data.get('user_data', {})
                            
                            # Generate JWT Token
                            payload = {
                                'user_id': st.session_state.user_data.get('user_id', ''),
                                'username': username,
                                'access_token': st.session_state.access_token,
                                'iat': datetime.utcnow(),
                                'exp': datetime.utcnow() + timedelta(hours=jwt_expiry_hours),
                                'iss': api_url,
                                'aud': 'woowonder-app'
                            }
                            
                            st.session_state.jwt_token = jwt.encode(payload, jwt_secret, algorithm='HS256')
                            
                            st.success("✅ Authentication successful! JWT token generated.")
                        else:
                            st.error(f"❌ Authentication failed: {auth_data.get('message', 'Unknown error')}")
                    else:
                        st.error(f"❌ HTTP Error {response.status_code}: {response.text}")
                        
                except requests.exceptions.RequestException as e:
                    st.error(f"❌ Network error: {str(e)}")
                except Exception as e:
                    st.error(f"❌ Unexpected error: {str(e)}")

with col2:
    st.header("📊 Token Information")
    
    if st.session_state.access_token and st.session_state.jwt_token:
        # Display success message
        st.markdown('<div class="success-box">🎉 <strong>Token Generated Successfully!</strong></div>', unsafe_allow_html=True)
        
        # Access Token
        st.subheader("🔓 Access Token")
        st.code(st.session_state.access_token, language="text")
        
        # JWT Token
        st.subheader("🎫 JWT Token")
        st.code(st.session_state.jwt_token, language="text")
        
        # Copy buttons
        col_copy1, col_copy2 = st.columns(2)
        with col_copy1:
            if st.button("📋 Copy Access Token", use_container_width=True):
                st.write("Access token copied to display above!")
        
        with col_copy2:
            if st.button("📋 Copy JWT Token", use_container_width=True):
                st.write("JWT token copied to display above!")
        
        # Token Details
        st.subheader("📋 Token Details")
        try:
            decoded_jwt = jwt.decode(st.session_state.jwt_token, jwt_secret, algorithms=['HS256'])
            
            token_info = {
                "User ID": decoded_jwt.get('user_id', 'N/A'),
                "Username": decoded_jwt.get('username', 'N/A'),
                "Issued At": datetime.fromtimestamp(decoded_jwt.get('iat', 0)).strftime('%Y-%m-%d %H:%M:%S'),
                "Expires At": datetime.fromtimestamp(decoded_jwt.get('exp', 0)).strftime('%Y-%m-%d %H:%M:%S'),
                "Issuer": decoded_jwt.get('iss', 'N/A'),
                "Audience": decoded_jwt.get('aud', 'N/A')
            }
            
            for key, value in token_info.items():
                st.write(f"**{key}:** {value}")
                
        except jwt.InvalidTokenError:
            st.error("❌ Invalid JWT token")
    
    else:
        st.markdown('<div class="info-box">ℹ️ <strong>No tokens generated yet.</strong><br>Click "Authenticate & Generate Token" to get started.</div>', unsafe_allow_html=True)

# User Information Section
if st.session_state.user_data:
    st.header("👤 User Information")
    
    col_user1, col_user2 = st.columns(2)
    
    with col_user1:
        st.write(f"**User ID:** {st.session_state.user_data.get('user_id', 'N/A')}")
        st.write(f"**Username:** {st.session_state.user_data.get('username', 'N/A')}")
        st.write(f"**Email:** {st.session_state.user_data.get('email', 'N/A')}")
    
    with col_user2:
        st.write(f"**First Name:** {st.session_state.user_data.get('first_name', 'N/A')}")
        st.write(f"**Last Name:** {st.session_state.user_data.get('last_name', 'N/A')}")
        st.write(f"**Status:** {st.session_state.user_data.get('status', 'N/A')}")

# Token Validation Section
st.header("🔍 Token Validation")

col_validate1, col_validate2 = st.columns(2)

with col_validate1:
    st.subheader("Validate JWT Token")
    token_to_validate = st.text_area("Enter JWT Token to Validate", height=100)
    
    if st.button("🔍 Validate Token", use_container_width=True):
        if token_to_validate:
            try:
                decoded = jwt.decode(token_to_validate, jwt_secret, algorithms=['HS256'])
                st.success("✅ Token is valid!")
                st.json(decoded)
            except jwt.ExpiredSignatureError:
                st.error("❌ Token has expired")
            except jwt.InvalidTokenError:
                st.error("❌ Invalid token")
        else:
            st.warning("⚠️ Please enter a token to validate")

with col_validate2:
    st.subheader("Token Status")
    if st.session_state.jwt_token:
        try:
            decoded = jwt.decode(st.session_state.jwt_token, jwt_secret, algorithms=['HS256'])
            exp_time = datetime.fromtimestamp(decoded['exp'])
            current_time = datetime.utcnow()
            
            if current_time < exp_time:
                time_left = exp_time - current_time
                st.success(f"✅ Token is valid for {time_left}")
            else:
                st.error("❌ Token has expired")
                
        except jwt.InvalidTokenError:
            st.error("❌ Invalid token")
    else:
        st.info("ℹ️ No active token")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 2rem;">
    <p>🔐 <strong>WoWonder JWT Token Generator</strong></p>
    <p>Securely generate and manage JWT tokens for your WoWonder API integration</p>
</div>
""", unsafe_allow_html=True)

# Instructions
with st.expander("📖 Instructions"):
    st.markdown("""
    ### How to use this JWT Token Generator:
    
    1. **Configure API Settings**: Enter your WoWonder site URL and credentials
    2. **Set JWT Parameters**: Configure your JWT secret key and expiry time
    3. **Generate Token**: Click "Authenticate & Generate Token" to create your JWT
    4. **Copy Tokens**: Use the copy buttons to get your access token and JWT
    5. **Validate Tokens**: Use the validation section to check token validity
    
    ### Security Notes:
    - Keep your server key and JWT secret secure
    - Use HTTPS in production environments
    - Regularly rotate your JWT secret keys
    - Monitor token usage and expiry times
    
    ### API Endpoints:
    - Authentication: `{your-site}/api/auth`
    - User Data: `{your-site}/api/get-user-data?access_token={token}`
    """)

# Clear session button
if st.button("🗑️ Clear All Tokens", type="secondary"):
    for key in ['access_token', 'jwt_token', 'user_data']:
        if key in st.session_state:
            del st.session_state[key]
    st.success("✅ All tokens cleared!")
    st.experimental_rerun()
