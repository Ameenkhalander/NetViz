import os
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy import inspect, text

def database_url():
    try:
        import streamlit as st
        value = st.secrets.get("DATABASE_URL")
    except Exception:
        value = None
    return value or os.getenv("DATABASE_URL") or "sqlite:///netviz.db"

class Base(DeclarativeBase):
    pass

URL = database_url()
engine = create_engine(URL, connect_args={"check_same_thread": False} if URL.startswith("sqlite") else {}, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)

def init_db():
    from models import Topic, Question, LessonProgress, QuizAttempt, UserQuestion, User
    Base.metadata.create_all(engine)
    # create_all does not add columns to existing tables; migrate points safely.
    columns={c["name"] for c in inspect(engine).get_columns("quiz_attempts")}
    if "points" not in columns:
        with engine.begin() as conn:
            conn.execute(text("ALTER TABLE quiz_attempts ADD COLUMN points INTEGER NOT NULL DEFAULT 0"))
    topics = [
      ("Networking fundamentals","LAN/WAN, OSI and TCP/IP, addressing, subnetting, switching and VLANs."),
      ("Transport protocols","TCP, UDP, ports, handshakes, reliability and congestion."),
      ("Web protocols","HTTP, HTTPS, methods, headers, status codes and APIs."),
      ("Security protocols","TLS, certificates, encryption, hashing and HMAC."),
      ("Network services","DNS, DHCP, ARP, ICMP, NTP and SNMP."),
      ("File transfer and email","FTP, FTPS, SFTP, TFTP, SSH, Telnet, SMTP, POP3 and IMAP."),
      ("Routing and infrastructure","Routing, OSPF, BGP, NAT, firewalls, proxies and VPNs."),
      ("SOC Analyst training","SIEM, logs, alert triage, incident response and threat intelligence."),
      ("Penetration testing","Authorisation, reconnaissance, Nmap, enumeration, OWASP and reporting.")
    ]
    bank = [
      ("Networking fundamentals","OSI","Which OSI layer is responsible for logical addressing and routing?",["Physical","Data Link","Network","Transport"],2,"The Network layer (Layer 3) handles logical addressing and routing between networks.","Beginner"),
      ("Networking fundamentals","Switching","Which device forwards Ethernet frames using MAC address tables?",["Router","Switch","Repeater","Modem"],1,"A Layer 2 switch learns MAC addresses and forwards frames using its MAC table.","Beginner"),
      ("Transport protocols","TCP","What is the TCP three-way handshake sequence?",["ACK, SYN, FIN","SYN, SYN-ACK, ACK","SYN, ACK, RST","FIN, FIN-ACK, ACK"],1,"The client sends SYN, server replies SYN-ACK, and client completes with ACK.","Beginner"),
      ("Transport protocols","UDP","Which property is associated with UDP?",["Connection-oriented","Built-in retransmission","Connectionless datagrams","Guaranteed ordering"],2,"UDP is connectionless and has no built-in delivery or ordering guarantees.","Beginner"),
      ("Web protocols","HTTP","Which HTTP method is conventionally used to retrieve a representation?",["GET","POST","PATCH","DELETE"],0,"GET requests a representation of a resource.","Beginner"),
      ("Web protocols","Status codes","What does HTTP 404 indicate?",["Success","Unauthorised","Not Found","Server Error"],2,"404 means the server did not find a current representation for the target resource.","Beginner"),
      ("Security protocols","TLS","What does a TLS certificate primarily bind?",["A public key to an identity","An IP to a MAC","A user to a password","A port to a process"],0,"A certificate binds a public key to an identity and is validated through a trust chain.","Intermediate"),
      ("Network services","DNS","Which DNS record maps a hostname to IPv4?",["AAAA","MX","A","PTR"],2,"An A record maps a domain name to an IPv4 address; AAAA is for IPv6.","Beginner"),
      ("Network services","DHCP","What does D stand for in DHCP DORA?",["Discover","Deliver","Domain","Dynamic"],0,"DORA is Discover, Offer, Request and Acknowledge.","Beginner"),
      ("Network services","ARP","What does ARP resolve on a typical IPv4 LAN?",["Domain to IP","IPv4 address to MAC address","Port to process","MAC to public IP"],1,"ARP discovers the link-layer address associated with an IPv4 address on a local link.","Intermediate"),
      ("File transfer and email","SSH","What is the default TCP port for SSH?",["21","22","23","25"],1,"SSH commonly listens on TCP port 22.","Beginner"),
      ("Routing and infrastructure","NAT","What does PAT commonly allow?",["Many private hosts to share one public IP using ports","DNS encryption","Layer 2 switching","IPv6 address assignment"],0,"PAT uses transport ports to distinguish multiple flows sharing a public address.","Intermediate"),
      ("SOC Analyst training","Triage","What should an analyst do first with an unfamiliar alert?",["Delete the log","Validate context and collect evidence","Close it immediately","Isolate every host"],1,"Validate context, scope, telemetry and indicators before choosing a response action.","Intermediate"),
      ("Penetration testing","Ethics","What is essential before scanning a third-party system?",["A fast laptop","Written authorisation and scope","A public IP","A VPN"],1,"Testing must be explicitly authorised and constrained to agreed scope and rules.","Beginner"),
      ("Penetration testing","Nmap","Which Nmap option requests service/version detection?",["-sV","-O0","-p-","-sn"],0,"-sV probes open ports to identify services and versions; only scan authorised targets.","Intermediate")
    ]
    with SessionLocal() as db:
        for name, desc in topics:
            if not db.query(Topic).filter_by(name=name).first():
                db.add(Topic(name=name, description=desc))
        db.commit()
        for tn, sub, q, opts, ans, exp, diff in bank:
            topic = db.query(Topic).filter_by(name=tn).first()
            if not db.query(Question).filter_by(question=q).first():
                db.add(Question(topic_id=topic.id, subtopic=sub, question=q, options=opts, correct_index=ans, explanation=exp, difficulty=diff, source_url="https://www.rfc-editor.org/"))
        db.commit()
