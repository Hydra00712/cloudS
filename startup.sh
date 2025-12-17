#!/bin/bash
# Streamlit startup script for Azure App Service

# Install requirements
pip install --no-cache-dir -r requirements_app.txt

# Configure Streamlit
mkdir -p ~/.streamlit
cat > ~/.streamlit/config.toml << EOF
[server]
headless = true
port = 8000
runOnSave = true
shell.showWarningOnDirectoryDelete = false

[client]
toolbarMode = "minimal"
EOF

# Run Streamlit
streamlit run app_streamlit.py --server.port 8000 --server.address 0.0.0.0
