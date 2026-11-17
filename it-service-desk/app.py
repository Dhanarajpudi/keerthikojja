import os, sqlite3
from flask import Flask, jsonify, request, render_template_string

app = Flask(__name__)
DB_PATH = os.environ.get("DB_PATH", "data/tickets.db")
PAGE = '''
<!doctype html><html><head><meta name="viewport" content="width=device-width,initial-scale=1">
<title>IT Service Desk</title><style>
body{font-family:Arial;background:#f2f5fa;color:#172033;margin:0}header{background:#172b4d;color:white;padding:24px 5%}
main{max-width:950px;margin:28px auto;padding:0 18px}.card{background:white;padding:22px;border-radius:12px;margin-bottom:20px}
input,textarea,select,button{font:inherit;padding:11px;border:1px solid #ccd4e0;border-radius:7px;width:100%;box-sizing:border-box;margin:6px 0}
button{background:#1769aa;color:white;border:0;cursor:pointer}.ticket{border-top:1px solid #ddd;padding:14px 0}
small{color:#667085}.status{font-weight:bold;color:#1769aa}
</style></head><body><header><h1>IT Service Desk</h1>Support ticket management portal</header><main>
<section class="card"><h2>Create a support ticket</h2><form id="f">
<input name="title" placeholder="Issue title" required><input name="requester" placeholder="Your name" required>
<textarea name="description" placeholder="Describe the issue" required></textarea><button>Submit ticket</button></form><p id="msg"></p></section>
<section class="card"><h2>Support tickets</h2><button onclick="loadTickets()">Refresh</button><div id="tickets">Loading...</div></section>
</main><script>
async function loadTickets(){let r=await fetch('/api/tickets'),d=await r.json();document.getElementById('tickets').innerHTML=d.map(t=>`<div class="ticket"><b>#${t.id} — ${t.title}</b><p>${t.description}</p><small>${t.requester} · ${t.created_at}</small><p class="status">${t.status}</p><select id="s${t.id}"><option>Open</option><option>In Progress</option><option>Resolved</option></select><button onclick="upd(${t.id})">Update status</button></div>`).join('')||'No tickets yet.'}
async function upd(id){let status=document.getElementById('s'+id).value;await fetch('/api/tickets/'+id,{method:'PATCH',headers:{'Content-Type':'application/json'},body:JSON.stringify({status})});loadTickets()}
document.getElementById('f').onsubmit=async e=>{e.preventDefault();let d=Object.fromEntries(new FormData(e.target));let r=await fetch('/api/tickets',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(d)});let x=await r.json();document.getElementById('msg').textContent=r.ok?'Ticket #'+x.id+' created':x.error;if(r.ok){e.target.reset();loadTickets()}};loadTickets();
</script></body></html>
'''

def db():
    os.makedirs(os.path.dirname(DB_PATH) or ".", exist_ok=True)
    c=sqlite3.connect(DB_PATH); c.row_factory=sqlite3.Row; return c

def init_db():
    with db() as c:
        c.execute('CREATE TABLE IF NOT EXISTS tickets(id INTEGER PRIMARY KEY AUTOINCREMENT,title TEXT NOT NULL,description TEXT NOT NULL,requester TEXT NOT NULL,status TEXT NOT NULL DEFAULT "Open",created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)')

@app.get("/")
def home(): return render_template_string(PAGE)

@app.get("/health")
def health():
    try:
        with db() as c: c.execute("SELECT 1")
        return jsonify(status="healthy",service="it-service-desk"),200
    except sqlite3.Error: return jsonify(status="unhealthy"),500

@app.get("/api/tickets")
def tickets():
    with db() as c: rows=c.execute("SELECT * FROM tickets ORDER BY id DESC").fetchall()
    return jsonify([dict(x) for x in rows])

@app.post("/api/tickets")
def create():
    d=request.get_json(silent=True) or {}
    vals=[str(d.get(k,"")).strip() for k in ("title","description","requester")]
    if not all(vals): return jsonify(error="title, description and requester are required"),400
    with db() as c: cur=c.execute("INSERT INTO tickets(title,description,requester) VALUES(?,?,?)",vals)
    return jsonify(id=cur.lastrowid,message="Ticket created"),201

@app.patch("/api/tickets/<int:ticket_id>")
def update(ticket_id):
    status=(request.get_json(silent=True) or {}).get("status")
    if status not in ["Open","In Progress","Resolved"]: return jsonify(error="Invalid status"),400
    with db() as c:
        cur=c.execute("UPDATE tickets SET status=? WHERE id=?",(status,ticket_id))
        if cur.rowcount==0: return jsonify(error="Ticket not found"),404
    return jsonify(message="Ticket updated",id=ticket_id,status=status)

init_db()
if __name__=="__main__": app.run(host="0.0.0.0",port=int(os.environ.get("PORT","5000")))
