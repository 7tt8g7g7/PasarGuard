# ============================================
# X4G VPN Panel — آماده‌ی دیپلوی روی Railway
# ============================================
import os
import json
import uuid
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from fastapi import FastAPI, HTTPException, Request, Response, Cookie
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from pydantic import BaseModel
import uvicorn

# ── تنظیمات ──
app = FastAPI(title="X4G VPN Panel", version="9.8")
DATA_FILE = "vpn_state.json"
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "X4GKING")
SECRET_KEY = os.environ.get("SECRET_KEY", secrets.token_hex(32))

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
def load_state() -> Dict:
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
        "stats": {
            "total_traffic": 0,
            "active_connections": 0,
            "created_at": datetime.now().isoformat()
        }
    }

def save_state(state: Dict):
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
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>ورود · X4G VPN</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{background:#080c18;display:flex;align-items:center;justify-content:center;min-height:100vh;font-family:'Vazirmatn',sans-serif;padding:20px}
.card{background:rgba(255,255,255,0.03);backdrop-filter:blur(24px);border:1px solid rgba(255,255,255,0.06);border-radius:28px;padding:44px 36px;max-width:400px;width:100%;box-shadow:0 16px 56px rgba(0,0,0,0.55)}
h1{color:#edf2ff;font-size:24px;font-weight:800;text-align:center;margin-bottom:32px}
h1 i{color:#5b8def;margin-left:10px}
input{width:100%;padding:15px 18px;border-radius:16px;border:1.5px solid rgba(255,255,255,0.06);background:rgba(255,255,255,0.02);color:#edf2ff;font-size:14px;outline:none;transition:all .3s;margin-bottom:20px}
input:focus{border-color:#5b8def;box-shadow:0 0 0 5px rgba(91,141,239,0.04)}
button{width:100%;padding:15px;border-radius:16px;border:none;background:linear-gradient(135deg,#5b8def,#7a5cf0);color:#fff;font-size:14px;font-weight:700;cursor:pointer;transition:all .3s}
button:hover{transform:translateY(-2px);box-shadow:0 10px 40px rgba(91,141,239,0.3)}
</style>
</head>
<body>
<div class="card">
<h1><i class="ti ti-shield-lock"></i> ورود به پنل</h1>
<form id="login">
<input type="password" id="pw" placeholder="••••••••" autofocus required>
<button type="submit">ورود</button>
</form>
</div>
<script>
document.getElementById('login').addEventListener('submit',async e=>{
e.preventDefault();const r=await fetch('/api/login',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({password:document.getElementById('pw').value})});
if(r.ok)location.href='/dashboard';else alert('رمز اشتباه است');
});
</script>
</body>
</html>"""

DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>X4G VPN · داشبورد</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{background:#080c18;color:#edf2ff;font-family:'Vazirmatn',sans-serif;padding:20px}
.container{max-width:900px;margin:0 auto}
.header{display:flex;justify-content:space-between;align-items:center;margin-bottom:30px}
.header h1{font-size:24px;font-weight:800}
.header h1 i{color:#5b8def;margin-left:10px}
.btn{background:linear-gradient(135deg,#5b8def,#7a5cf0);color:#fff;border:none;padding:8px 16px;border-radius:10px;cursor:pointer}
.stats{display:grid;grid-template-columns:repeat(4,1fr);gap:13px;margin-bottom:30px}
.stat{background:rgba(255,255,255,0.03);backdrop-filter:blur(16px);border:1px solid rgba(255,255,255,0.05);border-radius:16px;padding:17px}
.stat-label{font-size:10px;color:#8aa0c4;text-transform:uppercase;letter-spacing:.05em;margin-bottom:6px}
.stat-val{font-size:25px;font-weight:700}
.card{background:rgba(255,255,255,0.03);backdrop-filter:blur(24px);border:1px solid rgba(255,255,255,0.05);border-radius:16px;padding:18px 20px;margin-bottom:16px}
.card-title{font-size:12.5px;font-weight:700;margin-bottom:15px;display:flex;align-items:center;gap:7px}
.card-title i{color:#5b8def}
table{width:100%;border-collapse:collapse;font-size:13px}
th{text-align:right;padding:8px 0;color:#8aa0c4;font-weight:600;border-bottom:1px solid rgba(255,255,255,0.05)}
td{padding:8px 0;border-bottom:1px solid rgba(255,255,255,0.03)}
.status-active{color:#3FD79C}
.status-inactive{color:#FB8585}
.actions{display:flex;gap:5px}
.actions button{background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.05);color:#8aa0c4;padding:4px 8px;border-radius:6px;cursor:pointer;font-size:11px}
.actions button:hover{background:rgba(91,141,239,0.08)}
</style>
</head>
<body>
<div class="container">
<div class="header"><h1><i class="ti ti-layout-dashboard"></i> پنل VPN</h1><button class="btn" onclick="logout()">خروج</button></div>
<div class="stats" id="stats"></div>
<div class="card"><div class="card-title"><i class="ti ti-users"></i> کاربران</div>
<table><thead><tr><th>نام</th><th>سهمیه</th><th>مصرف</th><th>وضعیت</th><th>عملیات</th></tr></thead><tbody id="users"></tbody></table>
</div>
<div class="card"><div class="card-title"><i class="ti ti-user-plus"></i> افزودن کاربر</div>
<form id="addUser" style="display:flex;gap:10px;flex-wrap:wrap;align-items:end">
<input name="username" placeholder="نام کاربری" required style="flex:1;padding:8px 12px;border-radius:8px;border:1px solid rgba(255,255,255,0.05);background:rgba(255,255,255,0.02);color:#edf2ff">
<input name="password" type="password" placeholder="رمز" required style="flex:1;padding:8px 12px;border-radius:8px;border:1px solid rgba(255,255,255,0.05);background:rgba(255,255,255,0.02);color:#edf2ff">
<input name="limit_gb" type="number" placeholder="سهمیه (GB)" style="flex:0 0 100px;padding:8px 12px;border-radius:8px;border:1px solid rgba(255,255,255,0.05);background:rgba(255,255,255,0.02);color:#edf2ff">
<button type="submit" class="btn" style="padding:8px 20px">افزودن</button>
</form>
</div>
</div>
<script>
async function loadData(){
const r=await fetch('/api/users');const data=await r.json();
document.getElementById('users').innerHTML=data.users.map(u=>
`<tr><td>${u.username}</td><td>${u.limit_gb}GB</td><td>${u.used_gb.toFixed(2)}GB</td><td class="${u.active?'status-active':'status-inactive'}">${u.active?'فعال':'غیرفعال'}</td><td class="actions"><button onclick="toggleUser('${u.id}')">${u.active?'غیرفعال':'فعال'}</button><button onclick="copyLink('${u.id}')">لینک</button><button onclick="deleteUser('${u.id}')">حذف</button></td></tr>`
).join('');
const s=await fetch('/api/stats');const stats=await s.json();
document.getElementById('stats').innerHTML=`
<div class="stat"><div class="stat-label">کل کاربران</div><div class="stat-val">${stats.total_users}</div></div>
<div class="stat"><div class="stat-label">فعال</div><div class="stat-val">${stats.active_users}</div></div>
<div class="stat"><div class="stat-label">ترافیک کل</div><div class="stat-val">${stats.total_traffic_gb.toFixed(2)}GB</div></div>
<div class="stat"><div class="stat-label">اتصالات</div><div class="stat-val">${stats.active_connections}</div></div>
`;
}
document.getElementById('addUser').addEventListener('submit',async e=>{
e.preventDefault();const form=e.target;const data={username:form.username.value,password:form.password.value,limit_gb:parseFloat(form.limit_gb.value)||0};
const r=await fetch('/api/users',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(data)});
if(r.ok){form.reset();loadData();}else alert('خطا');
});
async function toggleUser(id){const r=await fetch('/api/users/'+id,{method:'PATCH',headers:{'Content-Type':'application/json'},body:JSON.stringify({active:false})});if(r.ok)loadData();}
async function deleteUser(id){if(!confirm('حذف این کاربر؟'))return;const r=await fetch('/api/users/'+id,{method:'DELETE'});if(r.ok)loadData();}
async function copyLink(id){const r=await fetch('/api/users');const data=await r.json();const user=data.users.find(u=>u.id===id);if(user)await navigator.clipboard.writeText(user.vless_link);alert('لینک کپی شد');}
async function logout(){await fetch('/api/logout',{method:'POST'});location.href='/'}
loadData();
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
