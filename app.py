# ============================================
# پنل عاشقانه — Love Panel v1.0
# ============================================
import os
import secrets
import random
from datetime import datetime
from fastapi import FastAPI, HTTPException, Request, Response, Cookie
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from pydantic import BaseModel
import uvicorn

app = FastAPI(title="Love Panel", version="1.0")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "love2025")
SECRET_KEY = os.environ.get("SECRET_KEY", secrets.token_hex(32))

# ── پیام‌های عاشقانه ──
LOVE_MESSAGES = [
    "❤️ امروز هم مثل همیشه، تو زیباترین بخش روز منی.",
    "🌹 وقتی به تو فکر می‌کنم، دلم برایت تنگ می‌شود.",
    "✨ عشق تو مثل ستاره‌ای است که شب‌هایم را روشن می‌کند.",
    "💫 نگاهت آرامش‌بخش‌ترین حس دنیاست.",
    "🌸 تو معنی قشنگ عشق را به من یاد دادی.",
    "🌙 حتی ماه هم به تو غبطه می‌خورد.",
    "💝 عشق تو بهترین بخش زندگی‌ام است.",
    "🍃 نسیم صبحگاهی، یادآور عطر توست.",
    "☀️ وقتی می‌خندی، دنیا روشن‌تر می‌شود.",
    "🌟 تو ستاره‌ی درخشان آسمان قلب منی.",
    "💞 عشق تو مثل یک رویای شیرین است.",
    "🌺 هیچ‌چیز به اندازه‌ی لبخندت قشنگ نیست.",
    "💕 هر روز با تو، بهترین روز زندگی‌ام است.",
    "🌿 عشق تو مثل باران بهاری، تازه و آرامش‌بخش است.",
    "✨ وجودت، زیباترین هدیه‌ی زندگی به من است.",
    "💖 امروز هم دلم برایت پر می‌زند.",
    "🌙 شب‌های من با فکر تو، پرستاره می‌شوند.",
    "🌸 عشق تو مثل یک گل، هر روز زیباتر می‌شود."
]

# ── صفحات HTML ──
LOGIN_HTML = """<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>ورود · پنل عاشقانه</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{background:linear-gradient(135deg,#1a0011,#2d001a);display:flex;align-items:center;justify-content:center;min-height:100vh;font-family:'Vazirmatn',sans-serif;padding:20px}
.card{background:rgba(255,255,255,0.03);backdrop-filter:blur(24px);border:1px solid rgba(255,255,255,0.06);border-radius:28px;padding:44px 36px;max-width:400px;width:100%;box-shadow:0 16px 56px rgba(255,255,255,0.05)}
h1{color:#ffd1e8;font-size:24px;font-weight:800;text-align:center;margin-bottom:12px}
h1 i{color:#ff6b9d;margin-left:10px}
.sub{text-align:center;color:#ffb3c6;font-size:14px;margin-bottom:32px}
input{width:100%;padding:15px 18px;border-radius:16px;border:1.5px solid rgba(255,255,255,0.06);background:rgba(255,255,255,0.02);color:#ffd1e8;font-size:14px;outline:none;transition:all .3s;margin-bottom:20px;text-align:center}
input:focus{border-color:#ff6b9d;box-shadow:0 0 0 5px rgba(255,107,157,0.1)}
input::placeholder{color:rgba(255,255,255,0.3)}
button{width:100%;padding:15px;border-radius:16px;border:none;background:linear-gradient(135deg,#ff6b9d,#ff3d7f);color:#fff;font-size:14px;font-weight:700;cursor:pointer;transition:all .3s}
button:hover{transform:translateY(-2px);box-shadow:0 10px 40px rgba(255,107,157,0.3)}
.heart{color:#ff6b9d;font-size:12px;text-align:center;margin-top:20px;opacity:0.5}
</style>
</head>
<body>
<div class="card">
<h1><i class="ti ti-heart"></i> ورود به پنل</h1>
<p class="sub">🌹 برای دیدن پیام امروز، وارد شو</p>
<form id="login">
<input type="password" id="pw" placeholder="••••••••" autofocus required>
<button type="submit">✨ وارد شو</button>
</form>
<div class="heart">❤️ عاشقانه‌های من برای تو</div>
</div>
<script>
document.getElementById('login').addEventListener('submit',async e=>{
e.preventDefault();const r=await fetch('/api/login',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({password:document.getElementById('pw').value})});
if(r.ok)location.href='/panel';else alert('💔 رمز اشتباه است');
});
</script>
</body>
</html>"""

PANEL_HTML = """<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>پنل عاشقانه</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{background:linear-gradient(135deg,#1a0011,#2d001a);min-height:100vh;display:flex;align-items:center;justify-content:center;font-family:'Vazirmatn',sans-serif;padding:20px}
.container{max-width:600px;width:100%}
.card{background:rgba(255,255,255,0.03);backdrop-filter:blur(24px);border:1px solid rgba(255,255,255,0.06);border-radius:28px;padding:44px 36px;text-align:center;box-shadow:0 16px 56px rgba(255,255,255,0.05)}
h1{color:#ffd1e8;font-size:28px;font-weight:800;margin-bottom:8px}
h1 i{color:#ff6b9d;margin-left:10px}
.sub{color:#ffb3c6;font-size:14px;margin-bottom:30px}
.btn{background:linear-gradient(135deg,#ff6b9d,#ff3d7f);color:#fff;border:none;padding:15px 40px;border-radius:16px;font-size:18px;font-weight:700;cursor:pointer;transition:all .3s;display:inline-flex;align-items:center;gap:10px;margin-bottom:20px}
.btn:hover{transform:translateY(-3px);box-shadow:0 10px 40px rgba(255,107,157,0.3)}
.btn i{font-size:20px}
.message-box{background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.06);border-radius:20px;padding:30px;margin-top:20px;min-height:120px;display:flex;align-items:center;justify-content:center;transition:all .5s}
.message-box .msg{color:#ffd1e8;font-size:22px;font-weight:500;line-height:1.8}
.message-box .heart-icon{color:#ff6b9d;font-size:30px;margin-bottom:10px;display:block}
.logout{color:rgba(255,255,255,0.3);background:none;border:none;cursor:pointer;font-size:12px;margin-top:30px;transition:all .3s}
.logout:hover{color:#ff6b9d}
.quote{color:rgba(255,255,255,0.2);font-size:12px;margin-top:16px}
</style>
</head>
<body>
<div class="container">
<div class="card">
<h1><i class="ti ti-heart"></i> پنل عاشقانه</h1>
<p class="sub">🌹 هر روز یک پیام جدید از قلب من برای تو</p>
<button class="btn" onclick="getMessage()"><i class="ti ti-sparkles"></i> پیام امروز</button>
<div class="message-box" id="messageBox">
<span class="msg" style="color:rgba(255,255,255,0.2);font-size:16px">❤️ برای دیدن پیام، دکمه رو بزن</span>
</div>
<button class="logout" onclick="logout()">🚪 خروج</button>
<div class="quote">✨ هر روز عاشق‌تر از دیروز</div>
</div>
</div>
<script>
async function getMessage(){
const box=document.getElementById('messageBox');
box.innerHTML='<span class="msg" style="color:#ffb3c6">🌹 در حال بارگذاری...</span>';
try{
const r=await fetch('/api/message');
const data=await r.json();
box.innerHTML=`<div><span class="heart-icon">❤️</span><span class="msg">${data.message}</span></div>`;
}catch(e){
box.innerHTML='<span class="msg" style="color:#ff6b9d">💔 خطا در دریافت پیام</span>';
}
}
async function logout(){await fetch('/api/logout',{method:'POST'});location.href='/'}
</script>
</body>
</html>"""

# ── مدل‌ها ──
class LoginData(BaseModel):
    password: str

# ── مسیرها ──
@app.post("/api/login")
async def login(data: LoginData, response: Response):
    if data.password == ADMIN_PASSWORD:
        session_token = secrets.token_hex(32)
        response = JSONResponse({"authenticated": True})
        response.set_cookie(key="session", value=session_token, httponly=True, max_age=7*24*3600)
        return response
    raise HTTPException(status_code=401, detail="رمز اشتباه است")

@app.get("/api/me")
async def me(session: Optional[str] = Cookie(None)):
    return {"authenticated": bool(session)}

@app.post("/api/logout")
async def logout():
    response = JSONResponse({"ok": True})
    response.delete_cookie("session")
    return response

@app.get("/api/message")
async def get_message(session: Optional[str] = Cookie(None)):
    if not session:
        raise HTTPException(status_code=401)
    # انتخاب یک پیام تصادفی از لیست
    message = random.choice(LOVE_MESSAGES)
    return {"message": message, "date": datetime.now().strftime("%Y/%m/%d")}

@app.get("/panel", response_class=HTMLResponse)
async def panel_page(session: Optional[str] = Cookie(None)):
    if not session:
        return RedirectResponse(url="/")
    return HTMLResponse(PANEL_HTML)

@app.get("/", response_class=HTMLResponse)
async def login_page():
    return HTMLResponse(LOGIN_HTML)

# ── راه‌اندازی ──
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
