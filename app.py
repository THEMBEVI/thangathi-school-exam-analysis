import os, sqlite3
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash

app=Flask(__name__)
app.secret_key=os.environ.get("SECRET_KEY","CHANGE_THIS_SECRET_KEY")
DB="thangathi.db"
SUBJECTS=["Mathematics","English","Kiswahili","Science","Social Studies","CRE","Agriculture","Computer","Creative Arts"]

def con():
    c=sqlite3.connect(DB); c.row_factory=sqlite3.Row; return c

def init():
    c=con()
    c.execute("CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY,username TEXT UNIQUE,password TEXT)")
    c.execute("""CREATE TABLE IF NOT EXISTS students(
      id INTEGER PRIMARY KEY,name TEXT,admission TEXT,class_name TEXT,gender TEXT,parent_phone TEXT,balance REAL,
      Mathematics REAL,English REAL,Kiswahili REAL,Science REAL,Social_Studies REAL,CRE REAL,Agriculture REAL,Computer REAL,Creative_Arts REAL)""")
    if c.execute("SELECT count(*) FROM users").fetchone()[0]==0:
        u=os.environ.get("ADMIN_USERNAME","admin"); p=os.environ.get("ADMIN_PASSWORD","ChangeMe123!")
        c.execute("INSERT INTO users(username,password) VALUES(?,?)",(u,generate_password_hash(p)))
    c.commit(); c.close()

def login_required(f):
    def w(*a,**k):
        if "uid" not in session:return redirect(url_for("login"))
        return f(*a,**k)
    w.__name__=f.__name__; return w

def band(t):
    return "Exceeded Expectations" if t>=350 else "Meeting Expectations" if t>=200 else "Approaching Expectations" if t>=101 else "Below Expectations"

@app.route("/")
def home(): return redirect(url_for("dashboard") if "uid" in session else url_for("login"))

@app.route("/login",methods=["GET","POST"])
def login():
    if request.method=="POST":
        c=con(); u=c.execute("SELECT * FROM users WHERE username=?",(request.form["username"],)).fetchone(); c.close()
        if u and check_password_hash(u["password"],request.form["password"]):
            session["uid"]=u["id"]; return redirect(url_for("dashboard"))
        flash("Invalid username or password.")
    return render_template("login.html")

@app.route("/logout")
def logout(): session.clear(); return redirect(url_for("login"))

@app.route("/dashboard")
@login_required
def dashboard():
    c=con(); rows=c.execute("SELECT * FROM students ORDER BY name").fetchall(); c.close()
    data=[]; means=[]
    for s in rows:
        scores=[float(s[x.replace(" ","_")] or 0) for x in SUBJECTS]; total=sum(scores); b=band(total)
        data.append(dict(id=s["id"],name=s["name"],class_name=s["class_name"],total=round(total,2),average=round(total/9,2),band=b,phone=s["parent_phone"],balance=s["balance"] or 0))
    for x in SUBJECTS:
        vals=[float(s[x.replace(" ","_")] or 0) for s in rows]
        means.append(round(sum(vals)/len(vals),2) if vals else 0)
    counts={b:sum(1 for s in data if s["band"]==b) for b in ["Exceeded Expectations","Meeting Expectations","Approaching Expectations","Below Expectations"]}
    return render_template("dashboard.html",students=data,subjects=SUBJECTS,means=means,counts=counts)

@app.route("/student/add",methods=["GET","POST"])
@login_required
def add():
    if request.method=="POST":
        fields=["name","admission","class_name","gender","parent_phone","balance"]+[x.replace(" ","_") for x in SUBJECTS]
        vals=[request.form.get(x,"") for x in fields]
        c=con(); c.execute("INSERT INTO students("+",".join(fields)+") VALUES("+",".join(["?"]*len(fields))+")",vals); c.commit(); c.close()
        return redirect(url_for("dashboard"))
    return render_template("form.html",subjects=SUBJECTS)

@app.route("/report/<int:sid>")
@login_required
def report(sid):
    c=con(); s=c.execute("SELECT * FROM students WHERE id=?",(sid,)).fetchone(); rows=c.execute("SELECT * FROM students").fetchall(); c.close()
    if not s:return "Not found",404
    scores=[float(s[x.replace(" ","_")] or 0) for x in SUBJECTS]; total=sum(scores); b=band(total)
    totals=[sum(float(r[x.replace(" ","_")] or 0) for x in SUBJECTS) for r in rows]
    pos=1+sum(t>total for t in totals)
    subs=[]
    for x,score in zip(SUBJECTS,scores):
        vals=[float(r[x.replace(" ","_")] or 0) for r in rows]; mean=sum(vals)/len(vals) if vals else 0
        grade="Exceeded" if score>=35 else "Meeting" if score>=20 else "Approaching" if score>=11 else "Below"
        subs.append((x,score,round(mean,2),1+sum(v>score for v in vals),grade))
    return render_template("report.html",s=s,subs=subs,total=round(total,2),avg=round(total/9,2),band=b,pos=pos)

if __name__=="__main__":
    init(); app.run(host="0.0.0.0",port=int(os.environ.get("PORT",5000)))
