import re

with open('app.py', 'r', encoding='utf-8') as f:
    code = f.read()

# Add the starry background CSS rules right after <style>
starry_bg_css = """
    /* Night Sky Background */
    [data-testid="stAppViewContainer"] {
        background-color: #0b101e !important;
        background-image: radial-gradient(white, rgba(255,255,255,.2) 2px, transparent 4px),
                          radial-gradient(white, rgba(255,255,255,.15) 1px, transparent 3px),
                          radial-gradient(white, rgba(255,255,255,.1) 2px, transparent 4px),
                          radial-gradient(rgba(255,255,255,.4), rgba(255,255,255,.1) 1px, transparent 3px);
        background-size: 550px 550px, 350px 350px, 250px 250px, 150px 150px; 
        background-position: 0 0, 40px 60px, 130px 270px, 70px 100px;
        background-attachment: fixed;
    }
    
    [data-testid="stHeader"] {
        background-color: transparent !important;
    }
    
    [data-testid="stSidebar"] {
        background-color: rgba(11, 16, 30, 0.95) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }
"""

code = code.replace('<style>', '<style>\n' + starry_bg_css)

replacements = [
    ('background: var(--secondary-background-color);', 'background: rgba(15, 23, 42, 0.85);\n        backdrop-filter: blur(10px);'),
    ('color: var(--text-color);', 'color: #f1f5f9;'),
    ('border: 1px solid rgba(128, 128, 128, 0.2);', 'border: 1px solid rgba(255, 255, 255, 0.1);'),
    ('border-top: 1px solid rgba(128, 128, 128, 0.2);', 'border-top: 1px solid rgba(255, 255, 255, 0.1);'),
    ('border-bottom: 1px solid rgba(128, 128, 128, 0.2);', 'border-bottom: 1px solid rgba(255, 255, 255, 0.1);'),
    ('background: rgba(128, 128, 128, 0.1);', 'background: rgba(255, 255, 255, 0.05);'),
    ('background: rgba(128, 128, 128, 0.2);', 'background: rgba(255, 255, 255, 0.1);'),
]

for old, new in replacements:
    code = code.replace(old, new)


with open('app.py', 'w', encoding='utf-8') as f:
    f.write(code)
