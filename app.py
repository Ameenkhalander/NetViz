import random
import json
import pandas as pd
import plotly.express as px
import streamlit as st
from sqlalchemy import func
from database import init_db, SessionLocal
from models import Topic, Question, LessonProgress, QuizAttempt, UserQuestion, User
from auth import register_user, authenticate
import uuid
from content import MODULES, PROTOCOLS
from components.diagrams import flow_diagram, osi_diagram
from components.ai_tutor import explain_with_ai

st.set_page_config(page_title="NetViz", page_icon="🌐", layout="wide")
st.markdown("""
<style>
.stApp{background:radial-gradient(circle at 80% 0%,#132b43 0,#08111f 44%,#08111f 100%)}
.block-container{padding-top:1.5rem;max-width:1450px}
.hero{padding:1.4rem 1.6rem;border:1px solid #24445b;border-radius:18px;background:linear-gradient(120deg,#10263b,#0b1828);margin-bottom:1rem}
.hero h1{font-size:2.25rem;margin:0;color:#eaf7ff}.hero p{color:#a9bfd2;margin:.4rem 0 0}
div[data-testid="stMetric"]{background:#102338;border:1px solid #25465d;padding:14px;border-radius:12px}
</style>""",unsafe_allow_html=True)

@st.cache_resource
def startup():
    init_db()
startup()

def mark_complete(learner,name):
    with SessionLocal() as db:
        row=db.query(LessonProgress).filter_by(learner=learner,topic_name=name).first()
        if row: row.completed=True
        else: db.add(LessonProgress(learner=learner,topic_name=name,completed=True))
        db.commit()

def save_attempt(learner,topic,total,correct):
    with SessionLocal() as db:
        points=(correct*10)+(5 if total>0 and correct==total else 0)
        db.add(QuizAttempt(learner=learner,topic_name=topic,total=total,correct=correct,accuracy=correct/total*100,points=points))
        db.commit()
        return points

st.sidebar.markdown("## 🌐 NetViz")
st.sidebar.caption("Networking · Protocols · SOC · Pentesting")
if "learner_id" not in st.session_state: st.session_state.learner_id=None
if "learner_name" not in st.session_state: st.session_state.learner_name=None
if "auth_mode" not in st.session_state: st.session_state.auth_mode="Login"

if st.session_state.learner_id is None:
    auth_choice=st.sidebar.radio("Get started",["Login","Register","Continue as guest"],key="auth_choice")
    if auth_choice=="Login":
        with st.sidebar.form("login_form"):
            login_email=st.text_input("Email")
            login_password=st.text_input("Password",type="password")
            login_submit=st.form_submit_button("Login",use_container_width=True)
        if login_submit:
            user=authenticate(login_email,login_password)
            if user:
                st.session_state.learner_id=user.id; st.session_state.learner_name=user.username; st.rerun()
            else: st.sidebar.error("Email or password is incorrect.")
    elif auth_choice=="Register":
        with st.sidebar.form("register_form"):
            reg_name=st.text_input("Username")
            reg_email=st.text_input("Email")
            reg_password=st.text_input("Password (10+ characters)",type="password")
            reg_confirm=st.text_input("Confirm password",type="password")
            reg_submit=st.form_submit_button("Create account",use_container_width=True)
        if reg_submit:
            if reg_password!=reg_confirm: st.sidebar.error("Passwords do not match.")
            else:
                user,message=register_user(reg_name,reg_email,reg_password)
                if user:
                    st.session_state.learner_id=user.id; st.session_state.learner_name=user.username; st.success(message); st.rerun()
                else: st.sidebar.error(message)
    else:
        if st.sidebar.button("Start as guest",type="primary",use_container_width=True):
            st.session_state.learner_id="guest-"+str(uuid.uuid4())
            st.session_state.learner_name="Guest-"+st.session_state.learner_id[-4:]
            st.rerun()
else:
    st.sidebar.success(f"Signed in as {st.session_state.learner_name}")
    if st.sidebar.button("Log out",use_container_width=True):
        for key in ["learner_id","learner_name","quiz_bank","quiz_topic"]: st.session_state.pop(key,None)
        st.rerun()
learner_id=st.session_state.learner_id or "anonymous-preview"
learner_name=st.session_state.learner_name or "Preview"
page=st.sidebar.radio("Navigation",["Dashboard","Learn modules","Protocol explorer","Packet simulator","Quiz arena","Leaderboard","Question builder","Practical labs","Progress & analytics","References"])
st.sidebar.divider()
st.sidebar.caption("Guest progress is stored for this browser session. Register to keep a named profile across visits on the same deployed database.")
st.sidebar.caption("Only test systems you own or are explicitly authorised to assess.")
st.markdown('<div class="hero"><h1>🌐 NetViz</h1><p>See the packets. Understand the protocols. Build defensive security skills.</p></div>',unsafe_allow_html=True)
if st.session_state.learner_id is None:
    st.info("You are previewing NetViz. Choose Login, Register or Continue as guest in the sidebar to save quiz progress and earn leaderboard points.")

def badge_for_points(points):
    tiers=[(1500,"Network Guardian","🏆"),(750,"SOC Defender","🛡️"),(300,"Protocol Pro","⚡"),(100,"Packet Explorer","🔎"),(0,"Newcomer","🌱")]
    for threshold,name,emoji in tiers:
        if points>=threshold: return name,emoji
    return "Newcomer","🌱"

if page=="Dashboard":
    with SessionLocal() as db:
        n_topics=db.query(Topic).count()
        completed=db.query(LessonProgress).filter_by(learner=learner_id,completed=True).count()
        attempts=db.query(QuizAttempt).filter_by(learner=learner_id).all()
        total=sum(x.total for x in attempts); correct=sum(x.correct for x in attempts)
    c=st.columns(4)
    c[0].metric("Learning modules",n_topics); c[1].metric("Protocol cards",len(PROTOCOLS))
    c[2].metric("Lessons completed",completed); c[3].metric("Quiz accuracy",f"{(correct/total*100 if total else 0):.1f}%")
    st.subheader("Networking ecosystem")
    flow_diagram("From application to the wire",[("Application","HTTP · DNS · SSH"),("Transport","TCP/UDP · ports"),("Network","IPv4/IPv6 · routing"),("Link","Ethernet · Wi-Fi · MAC"),("Physical","Signals · cable · radio")],"Encapsulation adds control information as data moves down the stack.")
    left,right=st.columns([1.1,1])
    with left:
        st.subheader("Curriculum")
        for i,(name,data) in enumerate(MODULES.items(),1):
            st.markdown(f"**{i:02d}. {name}**"); st.caption(data["intro"])
    with right:
        st.subheader("Recent quiz performance")
        if attempts:
            df=pd.DataFrame([{"Attempt":i+1,"Accuracy":a.accuracy,"Topic":a.topic_name} for i,a in enumerate(attempts[-8:])])
            st.plotly_chart(px.bar(df,x="Attempt",y="Accuracy",color="Topic",range_y=[0,100]),use_container_width=True)
        else: st.info("Complete a quiz to start your learning analytics.")
    with SessionLocal() as db:
        my_points=sum(a.points or 0 for a in db.query(QuizAttempt).filter_by(learner=learner_id).all())
    badge_name,badge_emoji=badge_for_points(my_points)
    st.metric("Your points",my_points)
    st.markdown(f"### {badge_emoji} {badge_name}")
    st.info("Suggested path: Networking fundamentals → TCP/UDP → DNS/DHCP/ARP → HTTP/TLS → SOC triage.")

elif page=="Learn modules":
    chosen=st.selectbox("Choose a module",list(MODULES))
    d=MODULES[chosen]
    st.title(chosen)
    st.markdown("### What is it?"); st.write(d["intro"])
    st.markdown("### Why does it matter?"); st.write(d["why"])
    st.markdown("### Topics covered")
    for item in d["topics"]: st.markdown("- "+item)
    st.markdown("### How it works"); st.write(d["details"])
    if chosen=="Networking fundamentals": osi_diagram()
    if chosen=="Transport protocols":
        flow_diagram("TCP three-way handshake",[("Client","SYN →"),("Server","← SYN + ACK"),("Client","ACK →")])
        flow_diagram("Typical TCP close",[("Host A","FIN"),("Host B","ACK"),("Host B","FIN"),("Host A","ACK")])
    if chosen=="Network services":
        flow_diagram("DHCP DORA",[("Client","Discover"),("Server","Offer"),("Client","Request"),("Server","Acknowledge")])
        flow_diagram("DNS lookup",[("Stub resolver","asks resolver"),("Recursive resolver","checks cache / hierarchy"),("Authoritative DNS","returns record"),("Client","uses answer")])
    if chosen=="Web protocols": flow_diagram("HTTP request/response",[("Browser","Method + headers"),("Network","Transport"),("Server","Status + headers + body")])
    if chosen=="Security protocols": flow_diagram("TLS 1.3 (simplified)",[("Client","ClientHello + key share"),("Server","ServerHello + key share"),("Peers","Encrypted handshake"),("Both","Protected data")])
    st.markdown("### Guided lab"); st.write(d["lab"])
    st.markdown("### Interview practice"); st.write(d["interview"])
    if st.button("Mark module completed",type="primary"): mark_complete(learner_id,chosen); st.success("Completion saved.")
    st.markdown("### Ask the AI tutor")
    prompt=st.text_area("Your question",key="lesson_prompt")
    level=st.select_slider("Explanation level",["Beginner","Intermediate","Advanced","Expert"],value="Beginner")
    if st.button("Ask AI",key="lesson_ai"):
        if prompt.strip(): st.markdown(explain_with_ai(prompt,chosen,level))
        else: st.warning("Enter a question first.")
    st.markdown("### References")
    for url in d["refs"]: st.markdown(f"- [{url}]({url})")

elif page=="Protocol explorer":
    st.title("Protocol explorer")
    st.caption("Ports shown are common defaults/conventions, not proof that a service is running there.")
    df=pd.DataFrame(PROTOCOLS,columns=["Protocol","Default port / identifier","Transport","Layer","Purpose"])
    term=st.text_input("Search protocol, port or purpose")
    if term:
        df=df[df.astype(str).apply(lambda col:col.str.contains(term,case=False,na=False)).any(axis=1)]
    st.dataframe(df,use_container_width=True,hide_index=True)
    name=st.selectbox("Inspect protocol",[x[0] for x in PROTOCOLS])
    p=next(x for x in PROTOCOLS if x[0]==name)
    a,b=st.columns(2); a.metric("Default port / identifier",p[1]); b.metric("Transport",p[2])
    st.write("**Layer:**",p[3]); st.write("**Purpose:**",p[4])
    st.info("Use the linked IETF RFC or official protocol specification for exact, version-specific behaviour.")

elif page=="Packet simulator":
    st.title("Interactive packet journey simulator")
    st.warning("Educational simulation only: this page does not send packets or capture live traffic.")
    a,b,c=st.columns(3)
    transport=a.selectbox("Transport",["TCP","UDP"])
    src_ip=a.text_input("Source IP","192.168.1.10")
    dst_ip=b.text_input("Destination IP","93.184.216.34")
    src_port=b.number_input("Source port",1024,65535,51514)
    proto=c.selectbox("Application protocol",["HTTPS","HTTP","DNS","SSH","Custom"])
    dst_port=c.number_input("Destination port",1,65535,443)
    st.code(f"{transport} | {src_ip}:{src_port} → {dst_ip}:{dst_port} | {proto}")
    if st.button("Simulate packet flow",type="primary"):
        if transport=="TCP":
            flow_diagram("TCP connection setup",[("Client","SYN"),("Server","SYN-ACK"),("Client","ACK"),("Application",f"{proto} data → port {dst_port}")])
            st.write("TCP provides connection state and an ordered byte stream.")
        else:
            flow_diagram("UDP datagram",[("Client","Build datagram"),("Network","Best-effort forwarding"),("Server","Deliver if reachable")])
            st.write("UDP has no transport handshake or built-in retransmission/ordering.")
        st.json({"source_ip":src_ip,"destination_ip":dst_ip,"source_port":int(src_port),"destination_port":int(dst_port),"transport":transport,"application":proto,"simulation":"educational"})
    sim=st.selectbox("Additional simulation",["DNS resolution","DHCP DORA","ARP resolution","HTTP request/response","TLS handshake","NAT/PAT"])
    diagrams={
      "DNS resolution":[("Client","query"),("Recursive resolver","cache / recursion"),("Authoritative DNS","answer"),("Client","uses record")],
      "DHCP DORA":[("Client","Discover"),("Server","Offer"),("Client","Request"),("Server","ACK")],
      "ARP resolution":[("Host","broadcast: who has IP?"),("Target","reply with MAC"),("Host","caches mapping")],
      "HTTP request/response":[("Client","request"),("Server","status + headers + body")],
      "TLS handshake":[("Client","ClientHello"),("Server","ServerHello + key share"),("Peers","Finished messages"),("Both","encrypted application data")],
      "NAT/PAT":[("Private host","192.168.1.10:51514"),("NAT router","rewrites tuple"),("Internet","203.0.113.5:40001"),("Reply","mapping reverses translation")]
    }
    flow_diagram(sim,diagrams[sim])
elif page=="Quiz arena":
    st.title("Quiz arena")
    if st.session_state.learner_id is None: st.warning("Sign in or continue as guest to take a quiz and save results."); st.stop()
    st.caption("16,000-question practice bank · 4,000 questions per difficulty level.")
    with open("data/question_bank.json", encoding="utf-8") as f:
        full_bank=json.load(f)
    topic_names=sorted({q["topic"] for q in full_bank})
    topic=st.selectbox("Topic",["All topics"]+topic_names)
    difficulty=st.selectbox("Difficulty",["All","Beginner","Intermediate","Advanced","Expert"])
    count_mode=st.selectbox("Question count",["5","10","20","30","40","50","100","200","500","1000","2000","3000","4000","Custom"])
    count=st.number_input("Custom count",1,4000,100) if count_mode=="Custom" else int(count_mode)
    st.caption("Format: single-answer MCQ. Each question includes answer feedback and a technical reference. The expanded bank contains scenario-framed variants built around 50 core knowledge targets per difficulty, not 16,000 independently authored concepts.")
    filtered=[q for q in full_bank if (topic=="All topics" or q["topic"]==topic) and (difficulty=="All" or q["difficulty"]==difficulty)]
    with SessionLocal() as db:
        custom=db.query(UserQuestion).filter_by(learner=learner_id).all()
        if topic!="All topics": custom=[q for q in custom if q.topic_name==topic]
        if difficulty!="All": custom=[q for q in custom if q.difficulty==difficulty]
        for q in custom:
            filtered.append({"id":f"CUSTOM-{q.id}","topic":q.topic_name,"subtopic":q.subtopic,"difficulty":q.difficulty,
                "question":q.question,"options":q.options,"correct_index":q.correct_index,
                "explanation":q.explanation,"source_url":""})
    st.metric("Questions available for this selection",len(filtered))
    if st.button("Generate quiz",type="primary"):
        if not filtered:
            st.error("No questions match these filters. Change the topic or difficulty.")
        else:
            actual=min(int(count),len(filtered))
            st.session_state.quiz_bank=random.sample(filtered,actual)
            st.session_state.quiz_topic=topic if topic!="All topics" else ("Mixed topics" if difficulty=="All" else difficulty)
            if actual<int(count):
                st.warning(f"You requested {count}; only {actual} questions are available for this selection.")
            else:
                st.success(f"Generated {actual} questions at the selected level.")
    quiz=st.session_state.get("quiz_bank",[])
    if quiz:
        st.subheader(f"Quiz · {len(quiz)} questions")
        with st.form("quiz_answers"):
            answers=[]
            for i,q in enumerate(quiz):
                st.markdown(f"**Q{i+1}. [{q['topic']} · {q['subtopic']}]**")
                st.write(q["question"])
                answers.append(st.radio("Select answer",q["options"],key=f"answer_{i}",index=None,label_visibility="collapsed"))
            submit=st.form_submit_button("Submit answers")
        if submit:
            score=0
            for i,(q,chosen) in enumerate(zip(quiz,answers),1):
                ok=chosen==q["options"][q["correct_index"]]
                score+=int(ok)
                st.markdown(f"#### Q{i}: {'✅ Correct' if ok else '❌ Incorrect'}")
                st.write("Your answer:",chosen or "Not answered")
                st.write("Correct answer:",q["options"][q["correct_index"]])
                st.write(q["explanation"])
                if q.get("source_url"): st.caption("Reference: "+q["source_url"])
                if not ok: st.info("Revision tip: revisit the matching module and explain the concept in your own words.")
            earned=save_attempt(learner_id,st.session_state.quiz_topic,len(quiz),score)
            accuracy=score/len(quiz)*100
            st.success(f"Score: {score}/{len(quiz)} · Accuracy: {accuracy:.1f}% · +{earned} points")
            with SessionLocal() as db:
                total_points=sum(a.points or 0 for a in db.query(QuizAttempt).filter_by(learner=learner_id).all())
            badge_name,badge_emoji=badge_for_points(total_points)
            st.markdown(f"### {badge_emoji} {badge_name} · {total_points} total points")
            del st.session_state["quiz_bank"]

elif page=="Leaderboard":
    st.title("🏅 NetViz leaderboard")
    st.caption("Rankings are based on quiz participation and points earned. Guests appear with temporary guest names.")
    with SessionLocal() as db:
        rows=db.query(QuizAttempt.learner,func.count(QuizAttempt.id).label("quizzes"),func.coalesce(func.sum(QuizAttempt.points),0).label("points"),func.coalesce(func.sum(QuizAttempt.correct),0).label("correct"),func.coalesce(func.sum(QuizAttempt.total),0).label("total")).group_by(QuizAttempt.learner).all()
        users={u.id:u.username for u in db.query(User).all()}
    leaderboard=[]
    for row in rows:
        label=users.get(row.learner, row.learner if row.learner.startswith("Guest-") else "Guest-"+row.learner[-4:])
        badge_name,badge_emoji=badge_for_points(int(row.points or 0))
        leaderboard.append({"Learner":label,"Quizzes attended":int(row.quizzes),"Points":int(row.points or 0),"Accuracy":round((row.correct/row.total*100) if row.total else 0,1),"Badge":f"{badge_emoji} {badge_name}"})
    if leaderboard:
        by_points=sorted(leaderboard,key=lambda x:(x["Points"],x["Quizzes attended"]),reverse=True)
        by_attendance=sorted(leaderboard,key=lambda x:(x["Quizzes attended"],x["Points"]),reverse=True)
        left,right=st.columns(2)
        with left:
            st.subheader("⭐ Top learners by points")
            st.dataframe(by_points[:10],use_container_width=True,hide_index=True)
        with right:
            st.subheader("📚 Most quizzes attended")
            st.dataframe(by_attendance[:10],use_container_width=True,hide_index=True)
    else:
        st.info("No quiz attempts yet. Complete a quiz to appear on the leaderboard.")

elif page=="Question builder":
    st.title("Question builder")
    if st.session_state.learner_id is None: st.warning("Sign in or continue as guest to build questions."); st.stop()
    st.caption("Custom questions are stored in your local collection. Public deployments need authentication and moderation.")
    with st.form("new_question"):
        topic=st.selectbox("Topic",list(MODULES))
        sub=st.text_input("Subtopic","My practice")
        q=st.text_area("Question")
        opts=[st.text_input(f"Option {i+1}",key=f"option_{i}") for i in range(4)]
        answer=st.selectbox("Correct option",[1,2,3,4])
        explanation=st.text_area("Detailed explanation")
        difficulty=st.selectbox("Difficulty",["Beginner","Intermediate","Advanced","Expert"])
        source=st.text_input("Reference URL (optional)")
        submit=st.form_submit_button("Save question")
    if submit:
        if not q.strip() or not explanation.strip() or any(not x.strip() for x in opts): st.error("Complete question, four options and explanation.")
        elif len({x.strip().casefold() for x in opts})<4: st.error("All four options must be distinct.")
        else:
            with SessionLocal() as db:
                exists=db.query(UserQuestion).filter_by(learner=learner_id,question=q.strip()).first()
                if exists: st.error("This question already exists in your collection.")
                else:
                    db.add(UserQuestion(learner=learner_id,topic_name=topic,subtopic=sub.strip(),question=q.strip(),options=opts,correct_index=answer-1,explanation=explanation.strip(),difficulty=difficulty))
                    db.commit(); st.success("Question added to your quiz bank.")
    with SessionLocal() as db: mine=db.query(UserQuestion).filter_by(learner=learner_id).order_by(UserQuestion.id.desc()).all()
    st.subheader("Your questions")
    for item in mine:
        with st.expander(f"{item.topic_name} · {item.question[:90]}"):
            st.write(item.explanation)
            if st.button("Delete",key=f"delete_{item.id}"):
                with SessionLocal() as db:
                    obj=db.query(UserQuestion).filter_by(id=item.id,learner=learner_id).first()
                    if obj: db.delete(obj); db.commit()
                st.rerun()

elif page=="Practical labs":
    st.title("Practical labs")
    labs=[
      ("Wireshark: TCP handshake","Capture your own browser traffic; filter `tcp.flags.syn == 1`.","Find SYN, SYN-ACK and ACK and note ports."),
      ("Wireshark: DNS","Run `nslookup example.com` while capturing your own interface.","Identify query name, record type and response."),
      ("Wireshark: TLS","Inspect a TLS handshake generated by a site you are allowed to access.","Locate ClientHello and ServerHello metadata where visible."),
      ("DHCP and ARP","Inspect `ipconfig /all` and, where supported, `arp -a`.","Explain the gateway, DHCP lease and neighbour cache."),
      ("Nmap localhost","Run `nmap -sV 127.0.0.1` on your own machine if Nmap is installed.","Record open ports; an open port alone is not a vulnerability."),
      ("Firewall log review","Use a sample log or your own system's firewall logs.","Group events by source, destination, port and time.")
    ]
    for title,steps,expected in labs:
        with st.expander(title):
            st.write("**Objective:** Practise interpreting network/security telemetry safely.")
            st.write("**Instructions:**",steps)
            st.write("**Expected output:**",expected)
            st.checkbox("Mark complete for this session",key=f"lab_{title}")
    st.error("Safety: capture only traffic you own or are authorised to inspect. Scan only localhost or explicitly authorised targets.")

elif page=="Progress & analytics":
    st.title("Progress & analytics")
    with SessionLocal() as db:
        completed=db.query(LessonProgress).filter_by(learner=learner_id,completed=True).all()
        attempts=db.query(QuizAttempt).filter_by(learner=learner_id).order_by(QuizAttempt.id).all()
    st.metric("Completed modules",len(completed)); st.progress(min(len(completed)/len(MODULES),1.0))
    st.caption(f"{len(completed)} of {len(MODULES)} modules completed")
    if attempts:
        df=pd.DataFrame([{"Attempt":i+1,"Topic":x.topic_name,"Accuracy":x.accuracy,"Questions":x.total} for i,x in enumerate(attempts)])
        st.plotly_chart(px.line(df,x="Attempt",y="Accuracy",color="Topic",markers=True,range_y=[0,100]),use_container_width=True)
        st.dataframe(df,use_container_width=True,hide_index=True)
        st.subheader("Revision priorities")
        st.dataframe(df.groupby("Topic")["Accuracy"].mean().sort_values().reset_index(name="Average accuracy"),use_container_width=True,hide_index=True)
    else: st.info("Take a quiz to unlock your performance charts.")

elif page=="References":
    st.title("Trusted references")
    refs=[
      ("IETF RFC Editor","https://www.rfc-editor.org/","Protocol standards and RFCs"),
      ("Python documentation","https://docs.python.org/3/","Python language"),
      ("PostgreSQL documentation","https://www.postgresql.org/docs/","Database"),
      ("Wireshark documentation","https://www.wireshark.org/docs/","Packet analysis"),
      ("Scapy documentation","https://scapy.readthedocs.io/","Packet analysis library"),
      ("Nmap reference guide","https://nmap.org/book/man.html","Authorised discovery and auditing"),
      ("OWASP Top 10","https://owasp.org/www-project-top-ten/","Web application security"),
      ("MITRE ATT&CK","https://attack.mitre.org/","Adversary tactics and techniques"),
      ("OpenAI API docs","https://platform.openai.com/docs/","AI tutor"),
      ("Streamlit docs","https://docs.streamlit.io/","App development and deployment")]
    for name,url,desc in refs: st.markdown(f"- **[{name}]({url})** — {desc}")
    st.caption("Use protocol-specific RFCs linked within each module for exact specifications.")
st.sidebar.divider(); st.sidebar.caption("NetViz · Learn ethically. Verify standards. Practise safely.")
