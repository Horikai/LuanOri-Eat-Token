from flask import Flask, render_template_string, redirect, url_for, request
import secrets
import re
import os
from urllib.parse import urlparse, parse_qs, quote, unquote
from flask import render_template

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LuanOri Get Eat-Token System</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;500;600;700&family=Inter:wght@300;400;500;600;700&display=swap');
        
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Inter', sans-serif; background: #0a0a0a; color: #e0e0e0; min-height: 100vh; overflow-x: hidden; font-weight: 400; }
        .code-font { font-family: 'JetBrains Mono', monospace; }
        .glass-card { background: rgba(20, 20, 20, 0.7); backdrop-filter: blur(10px); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 12px; }
        .platform-card { background: rgba(25, 25, 25, 0.9); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 10px; padding: 20px; transition: all 0.2s ease; cursor: pointer; }
        .platform-card:hover { border-color: rgba(255, 255, 255, 0.2); transform: translateY(-2px); background: rgba(30, 30, 30, 0.95); }
        .accent-color { color: #00d4ff; }
        .accent-bg { background: linear-gradient(135deg, #00d4ff, #0099ff); }
        .token-box { background: rgba(15, 15, 15, 0.95); border: 1px solid rgba(0, 212, 255, 0.3); border-radius: 8px; padding: 16px; font-family: 'JetBrains Mono', monospace; word-break: break-all; }
        .btn-primary { background: linear-gradient(135deg, #00d4ff, #0099ff); border: none; padding: 10px 24px; border-radius: 6px; color: #000; font-weight: 600; cursor: pointer; transition: all 0.2s ease; }
        .btn-primary:hover { transform: translateY(-1px); box-shadow: 0 5px 15px rgba(0, 212, 255, 0.2); }
        .status-active { color: #00ff88; }
        .pulse-dot { width: 8px; height: 8px; border-radius: 50%; background: #00ff88; animation: pulse 1.5s infinite; }
        @keyframes pulse { 0% { opacity: 1; transform: scale(1); } 50% { opacity: 0.5; transform: scale(1.2); } 100% { opacity: 1; transform: scale(1); } }
        .gradient-text { background: linear-gradient(135deg, #00d4ff, #0099ff); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; }
        .fade-in { animation: fadeIn 0.3s ease-out; }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
        .instructions { background: rgba(0, 212, 255, 0.1); border: 1px solid rgba(0, 212, 255, 0.3); border-radius: 8px; padding: 16px; margin-bottom: 20px; }
        .success { background: rgba(0, 255, 136, 0.1); border: 1px solid rgba(0, 255, 136, 0.3); }
    </style>
</head>
<body>
    <div class="max-w-6xl mx-auto p-4 md:p-6">
        <!-- Header -->
        <div class="glass-card p-6 mb-8 fade-in">
            <div class="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
                <div>
                    <h1 class="text-2xl md:text-3xl font-bold gradient-text mb-2">
                        <i class="fas fa-terminal mr-2"></i>LuanOri ACCESS
                    </h1>
                    <p class="text-gray-400 text-sm">EAT Token System - AUTO EXTRACT MODE ✅</p>
                </div>
                <div class="flex items-center space-x-4">
                    <div class="flex items-center space-x-2">
                        <div class="pulse-dot"></div>
                        <span class="text-sm status-active">LIVE</span>
                    </div>
                </div>
            </div>
        </div>

        {% if eat_token %}
        <!-- EAT Token Display -->
        <div class="glass-card p-6 mb-8 fade-in success">
            <div class="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-6">
                <div>
                    <h2 class="text-xl font-bold text-white mb-1">
                        <i class="fas fa-cookie-bite mr-2 accent-color"></i>✅ EAT TOKEN EXTRACTED!
                    </h2>
                    <p class="text-gray-400 text-sm">
                        {% if extracted_from %}From: {{ extracted_from }}{% else %}KiosGamer authentication successful{% endif %}
                    </p>
                </div>
                <button onclick="copyEatToken()" class="btn-primary text-sm px-4 py-2">
                    <i class="far fa-copy mr-2"></i>COPY TOKEN
                </button>
            </div>
            
            <div class="token-box mb-4">
                <code class="text-sm accent-color">{{ eat_token }}</code>
            </div>
            
            <div class="grid grid-cols-2 gap-4">
                <a href="https://ticket.kiosgamer.co.id/?eat={{ eat_token }}&lang=en&region=VN" 
                   target="_blank" class="btn-primary text-center py-3">
                    <i class="fas fa-external-link-alt mr-2"></i>Open KiosGamer
                </a>
                <button onclick="generateCustomURL()" class="btn-primary text-center py-3">
                    <i class="fas fa-link mr-2"></i>Custom URL
                </button>
            </div>
            
            <div id="customURL" class="token-box mt-4 hidden">
                <code class="text-xs">{{ custom_url or '' }}</code>
            </div>
        </div>
        {% endif %}

        <!-- INSTRUCTIONS -->
        <div class="glass-card p-6 mb-8 instructions">
            <h3 class="text-lg font-bold accent-color mb-3"><i class="fas fa-info-circle mr-2"></i>HOW TO GET TOKEN:</h3>
            <ol class="text-sm space-y-2 text-gray-300">
                <li>🔹 Click platform → <strong>NEW TAB</strong> mở KiosGamer</li>
                <li>🔹 Login Facebook/Google/VK/Twitter</li>
                <li>🔹 <strong>PASTE FULL URL</strong> vào ô bên dưới → <strong>AUTO EXTRACT!</strong></li>
                <li>🔹 Hoặc paste trực tiếp EAT token</li>
            </ol>
        </div>

        {% if not eat_token %}
        <div class="glass-card p-6 mb-8">
            <h3 class="text-xl font-bold text-white mb-4 flex items-center">
                <i class="fas fa-paste mr-3 accent-color"></i>PASTE FULL KIOSGAMER URL OR EAT TOKEN
            </h3>
            <div class="flex gap-4 mb-4">
                <input type="text" id="tokenInput" placeholder="https://ticket.kiosgamer.co.id/?eat=... OR paste EAT token directly" 
                       class="flex-1 p-3 bg-black/50 border border-gray-600 rounded-lg text-sm code-font focus:border-accent-color focus:outline-none"
                       value="{{ input_value or '' }}">
                <button onclick="submitToken()" class="btn-primary px-3">
                    <i class="fas fa-magic mr-2"></i>EXTRACT
                </button>
            </div>
            <p class="text-xs text-gray-500 mb-4">Supports: Full KiosGamer URLs OR direct EAT tokens</p>
        </div>
        {% endif %}

        <!-- Login Platforms -->
        <div class="glass-card p-6 mb-8">
            <div class="text-center mb-8">
                <h2 class="text-2xl font-bold text-white mb-3">
                    <i class="fas fa-share mr-2 accent-color"></i>Authentication Providers
                </h2>
                <p class="text-gray-400 max-w-2xl mx-auto">Click để mở <strong>NEW TAB</strong> → Login → Copy FULL URL → Paste vào ô trên</p>
            </div>

            <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
                <a href="https://ticket.kiosgamer.co.id/?lang=en&region=VN" target="_blank" class="platform-card">
                    <div class="flex flex-col items-center text-center">
                        <div class="w-16 h-16 rounded-2xl bg-blue-600/20 flex items-center justify-center mb-4">
                            <i class="fab fa-facebook-f text-blue-400 text-2xl"></i>
                        </div>
                        <h3 class="font-semibold text-white mb-2">Facebook</h3>
                        <span class="text-xs bg-blue-500/20 text-blue-300 px-3 py-1 rounded-full">EN/VN</span>
                    </div>
                </a>

                <a href="https://ticket.kiosgamer.co.id/?lang=en&region=VN" target="_blank" class="platform-card">
                    <div class="flex flex-col items-center text-center">
                        <div class="w-16 h-16 rounded-2xl bg-red-600/20 flex items-center justify-center mb-4">
                            <i class="fab fa-google text-red-400 text-2xl"></i>
                        </div>
                        <h3 class="font-semibold text-white mb-2">Google</h3>
                        <span class="text-xs bg-red-500/20 text-red-300 px-3 py-1 rounded-full">EN/VN</span>
                    </div>
                </a>

                <a href="https://ticket.kiosgamer.co.id/?lang=ru&region=RU" target="_blank" class="platform-card">
                    <div class="flex flex-col items-center text-center">
                        <div class="w-16 h-16 rounded-2xl bg-blue-500/20 flex items-center justify-center mb-4">
                            <i class="fab fa-vk text-blue-400 text-2xl"></i>
                        </div>
                        <h3 class="font-semibold text-white mb-2">VKontakte</h3>
                        <span class="text-xs bg-blue-500/20 text-blue-300 px-3 py-1 rounded-full">RU</span>
                    </div>
                </a>

                <a href="https://ticket.kiosgamer.co.id/?lang=en&region=VN" target="_blank" class="platform-card">
                    <div class="flex flex-col items-center text-center">
                        <div class="w-16 h-16 rounded-2xl bg-sky-500/20 flex items-center justify-center mb-4">
                            <i class="fab fa-x-twitter text-sky-400 text-2xl"></i>
                        </div>
                        <h3 class="font-semibold text-white mb-2">Twitter/X</h3>
                        <span class="text-xs bg-sky-500/20 text-sky-300 px-3 py-1 rounded-full">EN/VN</span>
                    </div>
                </a>
            </div>
        </div>

        <div class="glass-card p-6">
            <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div class="p-4 bg-black/30 rounded-lg text-center">
                    <div class="text-lg font-bold text-white mb-1">4</div>
                    <div class="text-xs text-gray-400">PROVIDERS</div>
                </div>
                <div class="p-4 bg-black/30 rounded-lg text-center">
                    <div class="text-lg font-bold status-active mb-1">{{ 'LIVE' if eat_token else 'WAITING' }}</div>
                    <div class="text-xs text-gray-400">STATUS</div>
                </div>
            </div>
        </div>
    </div>

<script>
let eatToken = "{{ eat_token or '' }}";
const currentHost = "{{ request.host_url.rstrip('/') }}";

function copyEatToken() {
    if (!eatToken) return;

    const textarea = document.createElement("textarea");
    textarea.value = eatToken;
    textarea.style.position = "fixed";
    textarea.style.left = "-9999px";
    textarea.style.top = "-9999px";
    document.body.appendChild(textarea);

    textarea.focus();
    textarea.select();

    try {
        document.execCommand("copy");
        alert("Đã copy EAT token!");
    } catch (err) {
        alert("Không copy được, hãy copy thủ công.");
    }

    document.body.removeChild(textarea);
}


function generateCustomURL() {
    const customDiv = document.getElementById('customURL');
    const customURL = `https://ticket.kiosgamer.co.id/?eat=${eatToken}&lang=en&region=VN&account_id=2680030228&nickname=%E2%80%A2Tao.`;
    customDiv.querySelector('code').textContent = customURL;
    customDiv.classList.remove('hidden');
}

function submitToken() {
    const tokenInput = document.getElementById('tokenInput');
    const input = tokenInput.value.trim();

    if (input.length === 0) {
        alert('❌ Vui lòng paste URL hoặc EAT token!');
        return;
    }

    // FIX: không ép 256 nữa
    if (/^[a-f0-9]{64,}$/i.test(input)) {
        window.location.href = `/?eat=${input}`;
        return;
    }

    try {
        const url = new URL(input.startsWith('http') ? input : 'https://' + input);
        const eat = url.searchParams.get('eat');

        // FIX: không ép 256 nữa
        if (eat && /^[a-f0-9]{64,}$/i.test(eat)) {
            window.location.href = `/?eat=${eat}`;
        } else {
            alert('❌ Không tìm thấy EAT token hợp lệ trong URL!');
        }
    } catch (e) {
        alert('❌ URL không hợp lệ!');
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const tokenInput = document.getElementById('tokenInput');
    if (tokenInput) {
        tokenInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') submitToken();
        });

        if (tokenInput.value && tokenInput.value.length >= 64) {
            setTimeout(submitToken, 500);
        }
    }
});
</script>

</body>
</html>
'''

def extract_eat_token(input_str):
    input_str = input_str.strip()

    # FIX: không ép 256
    if re.fullmatch(r'[a-f0-9]{64,}', input_str, re.IGNORECASE):
        return input_str.lower(), "direct"

    try:
        parsed = urlparse(input_str)
        query_params = parse_qs(parsed.query)
        eat_token = query_params.get('eat', [''])[0]

        # FIX: không ép 256
        if re.fullmatch(r'[a-f0-9]{64,}', eat_token, re.IGNORECASE):
            return eat_token.lower(), f"URL: {parsed.scheme}://{parsed.netloc}{parsed.path}"
    except:
        pass

    return None, None

@app.route("/guide")
def guide():
    return render_template("guide.html")


@app.route('/')
def index():

    eat_from_query = request.args.get('eat')

    # FIX: không ép 256
    if eat_from_query and re.fullmatch(r'[a-f0-9]{64,}', eat_from_query, re.IGNORECASE):
        return render_template_string(
            HTML_TEMPLATE,
            eat_token=eat_from_query.lower(),
            extracted_from=None,
            input_value=''
        )

    input_value = request.args.get('input', '').strip()

    if input_value:
        eat_token, source = extract_eat_token(input_value)
        if eat_token:
            return redirect(url_for('index', eat=eat_token))

    return render_template_string(
        HTML_TEMPLATE,
        eat_token=None,
        extracted_from=None,
        input_value=input_value or ''
    )


if __name__ == '__main__' and not os.environ.get("VERCEL"):
    print("🚀 LuanOri EAT Token Extractor v2.1 - AUTO EXTRACT FIXED!")
    app.run(host='0.0.0.0', port=5001, debug=False)