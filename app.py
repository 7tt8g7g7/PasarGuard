# ============================================
# X4G VPN Panel — نسخه‌ی نهایی با پیام امروز 🌹
# ============================================
import os, json, uuid, hashlib, secrets, random
from datetime import datetime, timedelta
from typing import Optional
from fastapi import FastAPI, HTTPException, Request, Response, Cookie
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from pydantic import BaseModel
import uvicorn

# ── تنظیمات ──
app = FastAPI(title="X4G VPN Panel", version="9.9")
DATA_FILE = "vpn_state.json"
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "X4GKING")
SECRET_KEY = os.environ.get("SECRET_KEY", secrets.token_hex(32))

# ── پیام‌های عاشقانه روزانه ──
LOVE_MESSAGES = [
    "🌹 امروز هم مثل همیشه ماه منی... ❤️",
    "🩵 دلتنگتم بیشتر از روزای قبل... 😔",
    "🌙 ماه من، روزت پر از نور و عشق 🌟",
    "💫 هر ثانیه که می‌گذره، بیشتر دوستت دارم 🫠",
    "🌸 امروز با یاد تو شروع شد... عزیزترینم",
    "✨ تو بهترین اتفاق زندگی منی... ماه من 🩵",
    "🌹 عشق من، چشمانت مثل آسمون شب می‌درخشه 🌙",
    "💕 دلم برای صدای خندت تنگ شده... ماه من",
    "🌟 امروز می‌خوام بهت بگم که چقدر دوستت دارم 🫠🩵",
    "🌙 ماه من، تو باارزش‌ترین گنج منی... ❤️",
    "🩵 هر روز عاشق‌تر از دیروز میشم... ماه من",
    "💫 تو رویای منی که تعبیر شد... عشق زندگی من",
    "🌹 با تو بودن یعنی آرامش... یعنی خوشبختی ماه من",
    "✨ هیچ‌کس مثل تو نمی‌درخشه... تو ماه منی 🌙",
    "💕 عشق من، امروز هم بهت فکر میکنم... همیشه 🌟"
]

# ── مدل‌ها ──
class UserCreate(BaseModel):
    username: str
    password: str
    limit_gb: float = 0
    expires_days: int = 0
    protocol: str = "vless-ws"
    note: str = ""

class UserUpdate(BaseModel):
    username: Optional[str] = None
    password: Optional[str] = None
    limit_gb: Optional[float] = None
    expires_days: Optional[int] = None
    protocol: Optional[str] = None
    active: Optional[bool] = None
    note: Optional[str] = None
    reset_usage: Optional[bool] = None

class LoginData(BaseModel):
    password: str

# ── مدیریت داده ──
def load_state():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r') as f:
                return json.load(f)
        except:
            pass
    return {
        "users": {},
        "admin_password": hashlib.sha256(ADMIN_PASSWORD.encode()).hexdigest(),
        "logs": [],
        "stats": {"total_traffic": 0, "active_connections": 0, "created_at": datetime.now().isoformat()}
    }

def save_state(state):
    with open(DATA_FILE, 'w') as f:
        json.dump(state, f, indent=2)

state = load_state()

def hash_password(pw: str) -> str:
    return hashlib.sha256(pw.encode()).hexdigest()

def verify_password(pw: str, hashed: str) -> bool:
    return hash_password(pw) == hashed

def generate_vless_link(user_id: str, username: str, protocol: str = "vless-ws") -> str:
    host = os.environ.get("RAILWAY_PUBLIC_DOMAIN", "your-domain.com")
    fingerprint = "chrome"
    alpn = "http/1.1"
    if protocol == "vless-ws":
        return f"vless://{user_id}@{host}:443?encryption=none&security=tls&sni={host}&fp={fingerprint}&alpn={alpn}&type=ws#X4G_{username}"
    elif protocol == "xhttp":
        return f"vless://{user_id}@{host}:443?encryption=none&security=tls&sni={host}&fp={fingerprint}&alpn={alpn}&type=xhttp#X4G_{username}"
    return f"vless://{user_id}@{host}:443?encryption=none&security=tls&sni={host}&fp={fingerprint}&alpn={alpn}#X4G_{username}"

# ── صفحات HTML ──
LOGIN_HTML = """<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>سلام ماه من 🫠🩵 · X4G VPN</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Vazirmatn:wght@400;700;800;900&display=swap');
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            background: linear-gradient(135deg, #0a0e1a 0%, #1a1040 50%, #0a0e1a 100%);
            display: flex;
            align-items: center;
            justify-content: center;
            min-height: 100vh;
            font-family: 'Vazirmatn', sans-serif;
            padding: 20px;
            overflow: hidden;
            position: relative;
        }
        
        body::before {
            content: '✨🌙✨💫✨🌙✨';
            position: absolute;
            top: 10%;
            left: 10%;
            font-size: 60px;
            opacity: 0.15;
            animation: floatStar 20s infinite linear;
            pointer-events: none;
        }
        
        body::after {
            content: '🫠🩵🫠🩵🫠🩵';
            position: absolute;
            bottom: 15%;
            right: 10%;
            font-size: 50px;
            opacity: 0.12;
            animation: floatStar 25s infinite reverse linear;
            pointer-events: none;
        }
        
        @keyframes floatStar {
            0% { transform: translate(0, 0) rotate(0deg); }
            50% { transform: translate(30px, -30px) rotate(180deg); }
            100% { transform: translate(0, 0) rotate(360deg); }
        }
        
        .card {
            background: rgba(255, 255, 255, 0.03);
            backdrop-filter: blur(40px);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 40px;
            padding: 50px 40px;
            max-width: 420px;
            width: 100%;
            box-shadow: 0 30px 80px rgba(0, 0, 0, 0.6), 0 0 60px rgba(91, 141, 239, 0.05);
            position: relative;
            z-index: 2;
            animation: fadeInUp 0.8s ease;
        }
        
        @keyframes fadeInUp {
            from { opacity: 0; transform: translateY(40px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .moon-emoji {
            text-align: center;
            font-size: 60px;
            margin-bottom: 10px;
            animation: pulseMoon 3s infinite ease-in-out;
        }
        
        @keyframes pulseMoon {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.1) rotate(5deg); }
        }
        
        h1 {
            color: #edf2ff;
            font-size: 28px;
            font-weight: 900;
            text-align: center;
            margin-bottom: 8px;
            letter-spacing: -0.5px;
        }
        
        h1 .heart {
            color: #ff6b9d;
            display: inline-block;
            animation: heartbeat 1.5s infinite;
        }
        
        @keyframes heartbeat {
            0%, 100% { transform: scale(1); }
            14% { transform: scale(1.3); }
            28% { transform: scale(1); }
            42% { transform: scale(1.2); }
            70% { transform: scale(1); }
        }
        
        .input-group {
            position: relative;
            margin-bottom: 24px;
        }
        
        .input-group label {
            display: block;
            color: #8aa0c4;
            font-size: 12px;
            font-weight: 700;
            margin-bottom: 6px;
            letter-spacing: 0.5px;
        }
        
        input {
            width: 100%;
            padding: 16px 20px;
            border-radius: 18px;
            border: 2px solid rgba(255, 255, 255, 0.06);
            background: rgba(255, 255, 255, 0.02);
            color: #edf2ff;
            font-size: 15px;
            outline: none;
            transition: all 0.4s cubic-bezier(0.25, 0.46, 0.45, 0.94);
            font-family: 'Vazirmatn', sans-serif;
        }
        
        input:focus {
            border-color: #5b8def;
            box-shadow: 0 0 0 8px rgba(91, 141, 239, 0.06);
            background: rgba(255, 255, 255, 0.04);
        }
        
        input::placeholder {
            color: #4a5a7a;
            font-weight: 300;
        }
        
        .btn {
            width: 100%;
            padding: 18px;
            border-radius: 18px;
            border: none;
            background: linear-gradient(135deg, #5b8def, #7a5cf0, #b86bff);
            background-size: 200% 200%;
            animation: gradientFlow 4s ease infinite;
            color: #fff;
            font-size: 18px;
            font-weight: 800;
            cursor: pointer;
            transition: all 0.4s cubic-bezier(0.25, 0.46, 0.45, 0.94);
            position: relative;
            overflow: hidden;
            font-family: 'Vazirmatn', sans-serif;
            letter-spacing: 1px;
        }
        
        @keyframes gradientFlow {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }
        
        .btn:hover {
            transform: translateY(-3px) scale(1.02);
            box-shadow: 0 15px 50px rgba(91, 141, 239, 0.35);
        }
        
        .btn:active {
            transform: scale(0.97);
        }
        
        .btn .emoji {
            display: inline-block;
            margin-left: 10px;
            animation: wiggle 2s infinite;
        }
        
        @keyframes wiggle {
            0%, 100% { transform: rotate(0deg); }
            25% { transform: rotate(-10deg); }
            75% { transform: rotate(10deg); }
        }
        
        .footer-text {
            text-align: center;
            margin-top: 20px;
            color: #4a5a7a;
            font-size: 12px;
            opacity: 0.5;
        }
        
        .footer-text span {
            color: #ff6b9d;
        }
    </style>
</head>
<body>
    <div class="card">
        <div class="moon-emoji">🌙</div>
        <h1>سلام ماه من <span class="heart">🫠🩵</span></h1>
        
        <form id="login">
            <div class="input-group">
                <label>🔑 رمز ورود</label>
                <input type="password" id="pw" placeholder="••••••••" autofocus required>
            </div>
            <button type="submit" class="btn">
                کلیک کن <span class="emoji">🤪</span>
            </button>
        </form>
        
        <div class="footer-text">
            🌙 برای عزیزترین <span>ماه من</span> 🩵
        </div>
    </div>
    
    <script>
        document.getElementById('login').addEventListener('submit', async e => {
            e.preventDefault();
            const pw = document.getElementById('pw').value;
            
            const btn = document.querySelector('.btn');
            btn.innerHTML = '🫠 دارم چک میکنم... 🤪';
            btn.style.opacity = '0.7';
            
            try {
                const r = await fetch('/api/login', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ password: pw })
                });
                
                if (r.ok) {
                    btn.innerHTML = '🩵 عشق من، خوش اومدی 🌙';
                    btn.style.background = 'linear-gradient(135deg, #ff6b9d, #ff4d6d)';
                    setTimeout(() => { location.href = '/dashboard'; }, 600);
                } else {
                    btn.innerHTML = '😅 نه عزیزم، دوباره 🤪';
                    btn.style.background = 'linear-gradient(135deg, #ff6b6b, #ee5a24)';
                    setTimeout(() => {
                        btn.innerHTML = 'کلیک کن <span class="emoji">🤪</span>';
                        btn.style.background = '';
                        btn.style.opacity = '1';
                    }, 1500);
                    document.getElementById('pw').value = '';
                    document.getElementById('pw').focus();
                }
            } catch (err) {
                alert('😢 یه مشکلی پیش اومده ماه من');
            }
        });
        
        document.getElementById('pw').addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                document.querySelector('.btn').click();
            }
        });
    </script>
</body>
</html>"""

DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🩵 X4G VPN · ماه من 🫠</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Vazirmatn:wght@400;700;800;900&display=swap');
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            background: linear-gradient(135deg, #0a0e1a 0%, #1a1040 50%, #0a0e1a 100%);
            color: #edf2ff;
            font-family: 'Vazirmatn', sans-serif;
            padding: 20px;
            min-height: 100vh;
        }
        
        .container {
            max-width: 1000px;
            margin: 0 auto;
        }
        
        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 30px;
            padding: 20px 0;
            border-bottom: 1px solid rgba(255, 255, 255, 0.04);
        }
        
        .header h1 {
            font-size: 26px;
            font-weight: 900;
            background: linear-gradient(135deg, #5b8def, #b86bff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        .header h1 .emoji {
            -webkit-text-fill-color: initial;
        }
        
        .btn {
            background: linear-gradient(135deg, #5b8def, #7a5cf0);
            color: #fff;
            border: none;
            padding: 10px 22px;
            border-radius: 14px;
            cursor: pointer;
            font-weight: 700;
            font-size: 14px;
            transition: all 0.3s;
            font-family: 'Vazirmatn', sans-serif;
        }
        
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 30px rgba(91, 141, 239, 0.3);
        }
        
        .btn-outline {
            background: transparent;
            border: 1.5px solid rgba(255, 255, 255, 0.08);
        }
        
        .btn-outline:hover {
            background: rgba(255, 255, 255, 0.04);
        }
        
        .love-btn-container {
            display: flex;
            justify-content: center;
            margin-bottom: 25px;
        }
        
        .love-btn {
            background: linear-gradient(135deg, #ff6b9d, #ff4d6d, #ff6b9d);
            background-size: 200% 200%;
            animation: gradientFlow 3s ease infinite;
            color: #fff;
            border: none;
            padding: 14px 35px;
            border-radius: 50px;
            font-size: 18px;
            font-weight: 800;
            cursor: pointer;
            transition: all 0.4s cubic-bezier(0.25, 0.46, 0.45, 0.94);
            font-family: 'Vazirmatn', sans-serif;
            box-shadow: 0 8px 40px rgba(255, 107, 157, 0.3);
            position: relative;
            overflow: hidden;
            letter-spacing: 0.5px;
        }
        
        .love-btn:hover {
            transform: translateY(-3px) scale(1.03);
            box-shadow: 0 12px 50px rgba(255, 107, 157, 0.5);
        }
        
        .love-btn:active {
            transform: scale(0.95);
        }
        
        .love-btn .pulse {
            display: inline-block;
            animation: pulseBtn 1.5s infinite;
        }
        
        @keyframes pulseBtn {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.15); }
        }
        
        @keyframes gradientFlow {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }
        
        .message-card {
            background: rgba(255, 255, 255, 0.04);
            backdrop-filter: blur(24px);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 24px;
            padding: 0 24px;
            max-height: 0;
            overflow: hidden;
            transition: all 0.7s cubic-bezier(0.25, 0.46, 0.45, 0.94);
            opacity: 0;
            margin-bottom: 20px;
            transform: translateY(-10px);
        }
        
        .message-card.open {
            max-height: 400px;
            padding: 28px 24px;
            opacity: 1;
            transform: translateY(0);
            border-color: rgba(255, 107, 157, 0.2);
            box-shadow: 0 0 40px rgba(255, 107, 157, 0.05);
        }
        
        .message-content {
            text-align: center;
            font-size: 22px;
            font-weight: 700;
            color: #edf2ff;
            line-height: 1.8;
            animation: messageAppear 0.6s ease;
        }
        
        @keyframes messageAppear {
            0% { opacity: 0; transform: scale(0.8); }
            100% { opacity: 1; transform: scale(1); }
        }
        
        .message-content .big-emoji {
            font-size: 48px;
            display: block;
            margin-bottom: 10px;
        }
        
        .message-content .heart-rain {
            display: inline-block;
            animation: rainHeart 2s infinite;
        }
        
        @keyframes rainHeart {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-8px); }
        }
        
        .message-date {
            display: block;
            font-size: 14px;
            color: #8aa0c4;
            margin-top: 12px;
            font-weight: 400;
            opacity: 0.7;
        }
        
        .stats {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 15px;
            margin-bottom: 30px;
        }
        
        .stat {
            background: rgba(255, 255, 255, 0.03);
            backdrop-filter: blur(16px);
            border: 1px solid rgba(255, 255, 255, 0.05);
            border-radius: 20px;
            padding: 20px;
            transition: all 0.3s;
        }
        
        .stat:hover {
            border-color: rgba(91, 141, 239, 0.2);
            transform: translateY(-2px);
        }
        
        .stat-label {
            font-size: 11px;
            color: #8aa0c4;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 8px;
        }
        
        .stat-val {
            font-size: 28px;
            font-weight: 800;
        }
        
        .stat-val .unit {
            font-size: 14px;
            font-weight: 400;
            color: #8aa0c4;
            margin-right: 4px;
        }
        
        .love-footer {
            text-align: center;
            padding: 20px 0 10px;
            color: #4a5a7a;
            font-size: 12px;
            opacity: 0.4;
        }
        
        .love-footer span {
            color: #ff6b9d;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🩵 پنل <span style="background:linear-gradient(135deg,#5b8def,#b86bff);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">X4G</span> <span class="emoji">🌙</span></h1>
            <div>
                <button class="btn btn-outline" onclick="copyAllLinks()" style="margin-left:10px;">📋 همه لینک‌ها</button>
                <button class="btn" onclick="logout()">🚪 خروج</button>
            </div>
        </div>
        
        <div class="love-btn-container">
            <button class="love-btn" onclick="toggleMessage()" id="loveToggleBtn">
                <span class="pulse">🌹</span> نمایش پیام امروز <span class="pulse">🩵</span>
            </button>
        </div>
        
        <div class="message-card" id="messageCard">
            <div class="message-content" id="messageContent">
                <span class="big-emoji" id="msgEmoji">🌙</span>
                <span id="loveMessage">❤️ ماه من، امروز هم روزت پر از عشق و آرامش 🌹</span>
                <span class="message-date" id="messageDate">📅 امروز</span>
            </div>
        </div>
        
        <div class="stats" id="stats"></div>
        
        <div class="love-footer">
            🌙 تقدیم به عزیزترین <span>ماه من</span> 🫠🩵
        </div>
    </div>
    
    <script>
        let isMessageOpen = false;
        let messageLoaded = false;
        
        async function toggleMessage() {
            const card = document.getElementById('messageCard');
            const btn = document.getElementById('loveToggleBtn');
            
            if (!isMessageOpen) {
                if (!messageLoaded) {
                    try {
                        const r = await fetch('/api/love-message');
                        if (!r.ok) throw new Error('خطا');
                        const data = await r.json();
                        document.getElementById('loveMessage').textContent = data.message;
                        document.getElementById('messageDate').textContent = '📅 ' + data.date;
                        const emojis = ['🌙', '🌸', '💫', '✨', '🌹', '🩵', '💕', '🌟', '❤️'];
                        document.getElementById('msgEmoji').textContent = emojis[Math.floor(Math.random() * emojis.length)];
                        messageLoaded = true;
                    } catch (e) {
                        document.getElementById('loveMessage').textContent = '🌹 ماه من، امروز هم مثل همیشه دوستت دارم 🩵';
                        document.getElementById('messageDate').textContent = '📅 ' + new Date().toLocaleDateString('fa-IR');
                        messageLoaded = true;
                    }
                }
                card.classList.add('open');
                btn.innerHTML = '<span class="pulse">💕</span> بستن پیام <span class="pulse">🌙</span>';
                isMessageOpen = true;
            } else {
                card.classList.remove('open');
                btn.innerHTML = '<span class="pulse">🌹</span> نمایش پیام امروز <span class="pulse">🩵</span>';
                isMessageOpen = false;
            }
        }
        
        async function loadData() {
            try {
                const s = await fetch('/api/stats');
                const stats = await s.json();
                document.getElementById('stats').innerHTML = `
                    <div class="stat">
                        <div class="stat-label">👥 کل کاربران</div>
                        <div class="stat-val">${stats.total_users}</div>
                    </div>
                    <div class="stat">
                        <div class="stat-label">🟢 فعال</div>
                        <div class="stat-val">${stats.active_users}</div>
                    </div>
                    <div class="stat">
                        <div class="stat-label">📊 ترافیک کل</div>
                        <div class="stat-val">${stats.total_traffic_gb.toFixed(1)}<span class="unit">GB</span></div>
                    </div>
                    <div class="stat">
                        <div class="stat-label">🔗 اتصالات</div>
                        <div class="stat-val">${stats.active_connections}</div>
                    </div>
                `;
            } catch (e) {
                console.error(e);
            }
        }
        
        async function copyAllLinks() {
            try {
                const r = await fetch('/api/users');
                const data = await r.json();
                const links = data.users.map(u => u.vless_link).join('\n');
                await navigator.clipboard.writeText(links);
                alert(`📋 ${data.users.length} تا لینک کپی شد 🌙`);
            } catch (e) {
                alert('😢 خطا در کپی لینک‌ها');
            }
        }
        
        async function logout() {
            await fetch('/api/logout', { method: 'POST' });
            location.href = '/';
        }
        
        loadData();
        setInterval(loadData, 15000);
    </script>
</body>
</html>"""

# ── مسیرها ──
@app.post("/api/login")
async def login(data: LoginData, response: Response):
    if verify_password(data.password, state["admin_password"]):
        session_token = secrets.token_hex(32)
        response = JSONResponse({"authenticated": True})
        response.set_cookie(key="session", value=session_token, httponly=True, max_age=7*24*3600)
        return response
    raise HTTPException(status_code=401, detail="رمز عبور اشتباه است")

# ✅ مسیر پیام امروز (بدون نیاز به کوکی)
@app.get("/api/love-message")
async def get_love_message():
    message = random.choice(LOVE_MESSAGES)
    today = datetime.now()
    days = ["دوشنبه", "سه‌شنبه", "چهارشنبه", "پنج‌شنبه", "جمعه", "شنبه", "یک‌شنبه"]
    months = ["دی", "بهمن", "اسفند", "فروردین", "اردیبهشت", "خرداد", "تیر", "مرداد", "شهریور", "مهر", "آبان", "آذر"]
    persian_date = f"{days[today.weekday()]} {today.day} {months[today.month-1]} {today.year}"
    return {"message": message, "date": persian_date}

@app.get("/api/me")
async def me(session: Optional[str] = Cookie(None)):
    return {"authenticated": bool(session)}

@app.post("/api/logout")
async def logout():
    response = JSONResponse({"ok": True})
    response.delete_cookie("session")
    return response

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(session: Optional[str] = Cookie(None)):
    if not session:
        return RedirectResponse(url="/")
    return HTMLResponse(DASHBOARD_HTML)

@app.get("/", response_class=HTMLResponse)
async def login_page():
    return HTMLResponse(LOGIN_HTML)

@app.get("/api/users")
async def get_users(session: Optional[str] = Cookie(None)):
    if not session:
        raise HTTPException(status_code=401)
    users = []
    for uid, data in state["users"].items():
        users.append({
            "id": uid,
            "username": data.get("username", "کاربر"),
            "limit_gb": data.get("limit_gb", 0),
            "used_gb": data.get("used_bytes", 0) / (1024**3),
            "expires_at": data.get("expires_at"),
            "active": data.get("active", True),
            "protocol": data.get("protocol", "vless-ws"),
            "vless_link": generate_vless_link(uid, data.get("username", "user"), data.get("protocol", "vless-ws")),
            "created_at": data.get("created_at")
        })
    return {"users": users}

@app.post("/api/users")
async def create_user(data: UserCreate, session: Optional[str] = Cookie(None)):
    if not session:
        raise HTTPException(status_code=401)
    uid = str(uuid.uuid4())
    expires_at = (datetime.now() + timedelta(days=data.expires_days)).isoformat() if data.expires_days > 0 else None
    state["users"][uid] = {
        "username": data.username,
        "password": hash_password(data.password),
        "limit_gb": data.limit_gb,
        "used_bytes": 0,
        "expires_at": expires_at,
        "active": True,
        "protocol": data.protocol,
        "note": data.note,
        "created_at": datetime.now().isoformat(),
        "connected_ips": []
    }
    save_state(state)
    return {"id": uid, "vless_link": generate_vless_link(uid, data.username, data.protocol)}

@app.patch("/api/users/{user_id}")
async def update_user(user_id: str, data: UserUpdate, session: Optional[str] = Cookie(None)):
    if not session or user_id not in state["users"]:
        raise HTTPException(status_code=401)
    user = state["users"][user_id]
    if data.username:
        user["username"] = data.username
    if data.password:
        user["password"] = hash_password(data.password)
    if data.limit_gb is not None:
        user["limit_gb"] = data.limit_gb
    if data.expires_days is not None and data.expires_days > 0:
        user["expires_at"] = (datetime.now() + timedelta(days=data.expires_days)).isoformat()
    if data.protocol:
        user["protocol"] = data.protocol
    if data.active is not None:
        user["active"] = data.active
    if data.note:
        user["note"] = data.note
    if data.reset_usage:
        user["used_bytes"] = 0
    save_state(state)
    return {"ok": True}

@app.delete("/api/users/{user_id}")
async def delete_user(user_id: str, session: Optional[str] = Cookie(None)):
    if not session or user_id not in state["users"]:
        raise HTTPException(status_code=401)
    del state["users"][user_id]
    save_state(state)
    return {"ok": True}

@app.get("/api/stats")
async def get_stats(session: Optional[str] = Cookie(None)):
    if not session:
        raise HTTPException(status_code=401)
    total_users = len(state["users"])
    active_users = sum(1 for u in state["users"].values() if u.get("active", True))
    total_traffic = sum(u.get("used_bytes", 0) for u in state["users"].values())
    return {
        "total_users": total_users,
        "active_users": active_users,
        "total_traffic_gb": total_traffic / (1024**3),
        "active_connections": sum(len(u.get("connected_ips", [])) for u in state["users"].values())
    }

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
