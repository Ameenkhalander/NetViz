import streamlit as st
def flow_diagram(title, steps, caption=None):
    st.markdown("#### "+title)
    cols=st.columns(len(steps))
    for i,(name,detail) in enumerate(steps):
        with cols[i]:
            st.markdown(f"""<div style="background:#102338;border:1px solid #2a526b;border-radius:12px;padding:14px;min-height:110px;text-align:center"><small style="color:#35d0ba">STEP {i+1}</small><br><b>{name}</b><br><span style="color:#a9bfd2">{detail}</span></div>""",unsafe_allow_html=True)
    if caption: st.caption(caption)
def osi_diagram():
    for name,desc in [("7 · Application","HTTP, DNS, SMTP"),("6 · Presentation","Encoding, encryption"),("5 · Session","Dialog coordination"),("4 · Transport","TCP, UDP, ports"),("3 · Network","IP, routing"),("2 · Data Link","Ethernet, MAC, VLAN"),("1 · Physical","Signals, cables, radio")]:
        st.markdown(f'<div style="display:flex;justify-content:space-between;padding:10px 14px;margin:5px 0;border-radius:8px;background:#10283b;border-left:5px solid #35d0ba"><b>{name}</b><span>{desc}</span></div>',unsafe_allow_html=True)
