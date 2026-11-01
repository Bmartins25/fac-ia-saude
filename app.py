import streamlit as st
import pandas as pd
import sqlite3, json, io
from pathlib import Path
from datetime import datetime
ROOT=Path(__file__).parent
DB=ROOT/'fac_ia.db'
CRITERIA=json.loads((ROOT/'criteria.json').read_text(encoding='utf-8'))
DOMAINS=list(dict.fromkeys(x['dominio'] for x in CRITERIA))
st.set_page_config(page_title='FAC-IA Saúde | Avaliação de Conformidade',page_icon='⚕️',layout='wide')
st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
html,body,[class*=css],.stApp{font-family:Inter,Arial,sans-serif}
.stApp{background:#f7faff;color:#0c2348}
[data-testid="stSidebar"]{background:linear-gradient(155deg,#061e44 0%,#082b58 78%,#0c5672 100%);border-right:1px solid #103e6e}
[data-testid="stSidebar"] *{color:#e8f7ff!important}
[data-testid="stSidebar"] [role="radiogroup"] label{padding:9px 10px;border-radius:10px;margin:3px 0;transition:background .15s}
[data-testid="stSidebar"] [role="radiogroup"] label:hover{background:#174a77}
[data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked){background:linear-gradient(90deg,#078f9c,#10b4b0)}
.block-container{padding-top:1.35rem;max-width:1500px}
h1,h2,h3{color:#0b2145;letter-spacing:-.035em}
h1{font-size:2.1rem!important}
[data-testid="stMetric"]{border:1px solid #e1eaf5;border-radius:17px;padding:15px 17px;background:linear-gradient(135deg,#fff,#eff8ff);box-shadow:0 5px 20px #0c2c5010}
[data-testid="stMetricLabel"]{color:#3c5677}
[data-testid="stMetricValue"]{color:#0c2853}
[data-testid="stForm"]{border:1px solid #e2eaf3;border-radius:18px;background:white;padding:20px}
.stButton>button[kind="primary"],.stDownloadButton>button{border-radius:11px;background:#087e9c;color:white;border:0}
.fac-header{display:flex;align-items:center;justify-content:space-between;gap:20px;padding:4px 0 20px}
.fac-brand h1{margin:0;font-size:2.2rem;font-weight:800;color:#0b234a}
.fac-brand h1 span{color:#0aa8a3}
.fac-brand p{font-size:.84rem;color:#48617c;margin:6px 0 0;max-width:650px}
.fac-institutions{display:flex;align-items:center;gap:17px;flex-shrink:0}
.fac-institutions img{object-fit:contain;max-height:68px;width:auto;max-width:165px}
.fac-institutions .separator{height:51px;width:1px;background:#9fb7c8}
.fac-hero{padding:26px 29px;border:1px solid #d6e9f2;border-radius:19px;background:radial-gradient(circle at 90% 15%,#9ce8ec 0,transparent 29%),linear-gradient(110deg,#edf8fc,#e7f3fb 68%,#d5eefa);margin:0 0 20px;box-shadow:0 8px 24px #1537560b}
.fac-hero h3{margin:0 0 8px;font-size:1.25rem}.fac-hero p{color:#244665;margin:0;max-width:850px;font-size:.91rem;line-height:1.65}
.fac-panel{background:white;border:1px solid #e1eaf4;border-radius:18px;padding:21px;box-shadow:0 5px 18px #0b2c4a0b;margin:8px 0 16px}
.fac-panel h3{font-size:1.1rem;margin:0 0 16px}
.fac-domains{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:9px}
.fac-domain{padding:16px 8px;border-radius:14px;text-align:center;background:linear-gradient(145deg,#eff7ff,#f8fbff);min-height:115px}
.fac-domain:nth-child(2){background:#f4f1ff}.fac-domain:nth-child(3){background:#fff0f5}.fac-domain:nth-child(4){background:#e9fbf5}.fac-domain:nth-child(5){background:#fff8ea}
.fac-domain .ico{font-size:27px}.fac-domain b{display:block;font-size:.76rem;margin-top:10px;line-height:1.3}.fac-domain small{display:block;color:#54708c;margin-top:6px}
.fac-steps{display:grid;grid-template-columns:repeat(4,1fr);gap:10px}.fac-step{background:#f0f6ff;border-radius:12px;padding:17px 12px;text-align:center;font-size:.81rem;line-height:1.55}.fac-step strong{display:block;font-size:1.35rem;color:#0a9dba;margin-bottom:7px}
.fac-note{padding:13px 17px;background:#eef6ff;border-radius:13px;color:#234a70;font-size:.83rem;margin:14px 0}
@media(max-width:1050px){.fac-header{flex-wrap:wrap}.fac-domains{grid-template-columns:repeat(2,1fr)}.fac-steps{grid-template-columns:repeat(2,1fr)}}

/* Landing page e mobile */
.fac-topnav{display:flex;gap:7px;flex-wrap:wrap;margin:0 0 18px;align-items:center}
.fac-topnav span{background:#edf5fb;border:1px solid #d8e8f3;color:#123c62;padding:9px 13px;border-radius:22px;font-size:.78rem;font-weight:700}
.fac-landing{background:linear-gradient(115deg,#061d3e,#0b4166);border-radius:24px;padding:48px 42px;color:#fff;margin:0 0 20px;position:relative;overflow:hidden}
.fac-landing:after{content:'';position:absolute;right:-90px;top:-90px;width:340px;height:340px;border:65px solid #19c7cc22;border-radius:50%}
.fac-eyebrow{color:#67e6ed!important;font-size:.75rem;font-weight:800;letter-spacing:.16em;text-transform:uppercase}
.fac-landing h2{color:#fff!important;font-size:clamp(2rem,4.3vw,3.5rem);max-width:800px;line-height:1.12;margin:14px 0}
.fac-landing h2 em{color:#53dce8;font-style:normal}
.fac-landing p{color:#dceaf4;max-width:740px;font-size:1.03rem;line-height:1.7}
.fac-tag{display:inline-block;background:#ffffff16;color:#e8fbff;border:1px solid #ffffff35;border-radius:25px;padding:8px 14px;font-size:.78rem;margin:6px 7px 0 0}
.fac-section{margin:26px 0 12px}.fac-section h2{font-size:1.65rem!important;margin-bottom:8px}.fac-section p{line-height:1.8;color:#34516d}
.fac-cards{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:13px;margin:16px 0}
.fac-card{background:white;border:1px solid #deebf4;border-radius:17px;padding:21px;box-shadow:0 5px 16px #0824440a}
.fac-card b{display:block;color:#092b4e;font-size:1.05rem;margin-bottom:7px}.fac-card p{color:#47647c;font-size:.88rem;line-height:1.65;margin:0}
.fac-profile{display:grid;grid-template-columns:minmax(180px,260px) 1fr;gap:28px;align-items:center;background:white;border:1px solid #e0eaf2;border-radius:20px;padding:20px}
.fac-profile img{width:100%;height:290px;object-fit:cover;object-position:center 25%;border-radius:14px}
.fac-profile h3{font-size:1.5rem;margin:0 0 8px}.fac-profile p{line-height:1.75;color:#3b5873}
.fac-footer{border-top:1px solid #dce7f0;margin-top:30px;padding:20px 0;color:#4c6780;font-size:.79rem}
@media(max-width:768px){
 .block-container{padding:1rem .8rem 3rem!important}
 .fac-header{gap:8px;padding:0 0 13px;flex-direction:column;align-items:flex-start}
 .fac-brand h1{font-size:1.6rem!important}.fac-brand p{font-size:.74rem}
 .fac-institutions{gap:10px}.fac-institutions img{max-height:39px;max-width:105px}.fac-institutions .separator{height:30px}
 .fac-hero{padding:18px 15px}.fac-hero p{font-size:.84rem}
 .fac-landing{padding:29px 20px;border-radius:18px}.fac-landing h2{font-size:2rem!important}.fac-landing p{font-size:.9rem}
 .fac-cards{grid-template-columns:1fr}.fac-profile{grid-template-columns:1fr}.fac-profile img{height:280px;max-width:260px}
 .fac-domains{grid-template-columns:1fr 1fr}.fac-steps{grid-template-columns:1fr 1fr}
 [data-testid="stMetric"]{padding:10px!important}
 [data-testid="stHorizontalBlock"]{flex-wrap:wrap}
 [data-testid="stColumn"]{min-width: min(100%, 230px)!important}
 .fac-topnav span{font-size:.72rem;padding:7px 10px}
}
@media(max-width:390px){.fac-domains,.fac-steps{grid-template-columns:1fr}.fac-landing h2{font-size:1.7rem!important}}

/* FAC-IA Saúde — identidade inspirada na arquitetura visual da Veritas, sem marca comercial */
.fac-nav-caption{color:#627c91;font-size:.72rem;font-weight:800;letter-spacing:.12em;margin:4px 0 9px}
.fac-landing{background:linear-gradient(110deg,#071e34 0%,#0b3451 58%,#096579 100%);border-radius:20px;box-shadow:0 20px 48px #071e3424}
.fac-card{transition:transform .2s ease,box-shadow .2s ease;border-top:3px solid #0b9cae}
.fac-card:hover{transform:translateY(-3px);box-shadow:0 12px 28px #0b2c4a19}
.stButton>button{min-height:42px;font-weight:650;border-radius:10px}
[data-testid="stSidebar"] .stButton>button{justify-content:flex-start;text-align:left}
.fac-footer{border-top:2px solid #0c9bad}
@media(max-width:900px){
 .fac-landing{padding:30px 23px}
 div[data-testid="stHorizontalBlock"]:has(button[key^="nav_"]){flex-wrap:wrap}
}
@media(max-width:768px){
 .fac-landing{padding:27px 19px}
 .fac-landing h2{font-size:clamp(1.8rem,7vw,2.5rem)!important}
 .fac-header{align-items:center;text-align:center}
 .fac-institutions{justify-content:center;width:100%}
 .fac-nav-caption{text-align:center}
 [data-testid="stHorizontalBlock"]{gap:.35rem}
 [data-testid="stColumn"]{min-width:calc(50% - .35rem)!important;flex:1 1 calc(50% - .35rem)!important}
 [data-testid="stColumn"] .stButton>button{font-size:.77rem;padding:.45rem .4rem;white-space:normal;line-height:1.15}
 .fac-card{padding:18px}
}
@media(max-width:440px){.fac-profile img{max-width:100%;height:260px}.fac-domains{grid-template-columns:1fr}.fac-steps{grid-template-columns:1fr}}

/* Identidade clara FAC-IA: substitui controles escuros do tema Streamlit */
.stApp {background:#f5f9fc!important;color:#123250!important}
[data-testid="stHeader"] {background:#edf5f9!important}
[data-testid="stToolbar"] {color:#18415d!important}
.stButton>button[kind="secondary"],.stButton>button[data-testid="stBaseButton-secondary"] {background:#ffffff!important;color:#16476a!important;border:1px solid #bed9e6!important;box-shadow:0 2px 8px #12516a0b!important}
.stButton>button[kind="secondary"]:hover,.stButton>button[data-testid="stBaseButton-secondary"]:hover {background:#e5f7fa!important;color:#006c85!important;border-color:#21a5b5!important}
.stButton>button[kind="primary"],.stButton>button[data-testid="stBaseButton-primary"] {background:#087f9c!important;color:#ffffff!important;border:1px solid #087f9c!important;box-shadow:0 4px 12px #087f9c25!important}
.stButton>button[kind="primary"]:hover {background:#06667f!important;color:#fff!important}
[data-testid="stSidebar"] .stButton>button[kind="secondary"] {background:#174c70!important;color:#f3fbff!important;border:1px solid #5684a1!important}
[data-testid="stSidebar"] .stButton>button[kind="primary"] {background:#0aa1af!important;color:#fff!important}
.fac-landing {background:linear-gradient(118deg,#e7f6fc 0%,#d4eef6 65%,#b8e5ee 100%)!important;border:1px solid #b6dce8!important;box-shadow:0 12px 32px #15415b12!important}
.fac-landing h2 {color:#0c3457!important}.fac-landing h2 em {color:#008c9c!important}
.fac-landing p {color:#284d66!important}.fac-eyebrow {color:#047c92!important}
.fac-tag {background:#ffffffaa!important;color:#0a5269!important;border:1px solid #9fd1dc!important}
.fac-feature {background:white;border:1px solid #dceaf0;border-radius:18px;padding:24px;margin:18px 0;box-shadow:0 6px 20px #16415a0b}
.fac-feature h2 {font-size:1.55rem!important;color:#0a3556!important;margin:0 0 12px}
.fac-feature h3 {font-size:1.1rem!important;color:#0a5771!important;margin:15px 0 8px}
.fac-feature p {color:#35556d;line-height:1.75;margin:8px 0}
.fac-feature ul {color:#35556d;line-height:1.85;padding-left:22px}
.fac-publications {display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px;margin:15px 0}
.fac-publications .fac-card {border-top-color:#13a8b3}
@media(max-width:760px){.fac-feature{padding:18px 15px}.fac-publications{grid-template-columns:1fr}.fac-landing{padding:26px 18px!important}}

/* Ajustes de apresentação, cabeçalho compacto e ocultação dos controles de compartilhamento */
[data-testid="stToolbar"], [data-testid="stDecoration"], [data-testid="stStatusWidget"]{display:none!important}
[data-testid="stHeader"]{height:2.2rem!important;min-height:2.2rem!important;background:#f5f9fc!important}
[data-testid="stSidebar"]{width:238px!important;min-width:238px!important}
[data-testid="stSidebar"] [data-testid="stImage"]{max-width:165px;margin:0 auto 8px}
[data-testid="stSidebar"] .stButton>button{min-height:36px!important;padding:.4rem .75rem!important;font-size:.82rem!important}
.block-container{padding-top:.65rem!important;max-width:1280px!important}
.fac-header{padding-bottom:8px!important;margin-bottom:8px!important}
.fac-brand h1{font-size:clamp(2.15rem,3.3vw,3.15rem)!important;line-height:1.14!important;letter-spacing:-.035em!important;margin-bottom:8px!important}
.fac-brand p{font-size:clamp(.83rem,1.05vw,1rem)!important;line-height:1.45!important}
.fac-header{align-items:center!important;min-height:112px!important}
@media(max-width:650px){.fac-brand h1{font-size:2rem!important}.fac-brand p{font-size:.8rem!important}.fac-header{min-height:0!important}}
.fac-institutions img{max-height:42px!important}
.fac-data-intro{padding:25px 0 14px}
.fac-data-eyebrow{color:#b18423;font-size:.75rem;font-weight:800;letter-spacing:.15em}
.fac-data-intro h2{font-size:clamp(1.35rem,2.1vw,1.95rem)!important;color:#0c2f50;margin:8px 0 12px}
.fac-data-intro p{color:#49647c;line-height:1.65;max-width:920px}
.fac-stats-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px;margin:8px 0 15px}
.fac-stat-card{display:flex;flex-direction:column;min-width:0;background:#fff;border:1px solid #dce8f0;border-top:4px solid #0c99aa;border-radius:16px;padding:20px;box-shadow:0 8px 24px #0c31540c}
.fac-stat-kicker{font-size:.76rem;color:#54718a;text-transform:uppercase;letter-spacing:.07em;font-weight:800}
.fac-stat-card h3{font-size:1.65rem!important;margin:12px 0 6px;color:#0b3557}
.fac-stat-card p{font-size:.85rem;color:#526b80;line-height:1.55;min-height:70px}
.fac-stat-card a{margin-top:auto;font-size:.75rem;color:#087b98;text-decoration:none;font-weight:700;padding-top:12px;overflow-wrap:anywhere}
.fac-stat-number{font-size:3.3rem;line-height:1.2;color:#b58b2c;font-weight:800;margin:12px 0 6px}
.fac-stat-number span{font-size:2rem}
.fac-bar-group{margin:14px 0 8px}.fac-bar-label{display:flex;justify-content:space-between;color:#214963;font-size:.78rem;margin:9px 0 4px}
.fac-bar-track{background:#eaf2f7;height:10px;border-radius:20px;overflow:hidden}.fac-bar-fill{height:100%;background:#91c9d5;border-radius:20px}.fac-bar-fill-strong{background:#079caf}
.fac-stat-reading{background:#f0f8fb;border-left:3px solid #0b9dad;border-radius:6px;padding:10px;margin-top:14px;color:#254d66;font-size:.78rem;line-height:1.5}
.fac-ring{width:104px;height:104px;margin:12px auto;background:conic-gradient(#b58b2c 0 68%,#e7eff5 68% 100%);border-radius:50%;display:grid;place-items:center}.fac-ring>div{display:grid;place-items:center;background:#fff;border-radius:50%;width:76px;height:76px;color:#0b3557;font-size:1.25rem;font-weight:800}
.fac-device-visual{display:flex;gap:15px;align-items:center;justify-content:center;margin:12px 0;height:103px;color:#0a8b9e;font-weight:800;font-size:1.6rem}.fac-device-bars{display:flex;gap:7px;align-items:flex-end;height:85px}.fac-device-bars i{display:block;width:19px;border-radius:6px 6px 0 0;background:#b58b2c}
.fac-evidence-note{font-size:.76rem;color:#647b8e;line-height:1.6;margin-bottom:23px}
@media(max-width:980px){.fac-stats-grid{grid-template-columns:1fr 1fr}.fac-stat-card:last-child{grid-column:1/-1}}
@media(max-width:650px){.fac-stats-grid{grid-template-columns:1fr}.fac-stat-card:last-child{grid-column:auto}.fac-stat-card p{min-height:0}.fac-data-intro{padding-top:15px}.fac-stat-card{padding:17px}.fac-brand h1{font-size:1.45rem!important}[data-testid="stSidebar"]{width:230px!important;min-width:230px!important}}

/* Páginas institucionais — FAC-IA Saúde */
.fac-method-grid{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:12px;margin:18px 0}
.fac-method-card{background:#fff;border:1px solid #d8e7f0;border-top:4px solid #089eb0;border-radius:14px;padding:17px 14px;min-height:155px}
.fac-method-card strong{display:block;color:#092f53;font-size:.94rem;line-height:1.4}
.fac-method-card p{font-size:.84rem;line-height:1.6;color:#43627b}
.fac-contact-title{font-size:1.12rem;font-weight:800;color:#0b3658;margin:12px 0 14px}
.fac-section .fac-eyebrow{color:#008b9f!important}
@media(max-width:1050px){.fac-method-grid{grid-template-columns:repeat(2,minmax(0,1fr))}}
@media(max-width:650px){.fac-method-grid{grid-template-columns:1fr}.fac-method-card{min-height:auto}}

/* Formulário Contato: campos claros, legíveis e consistentes com a identidade FAC-IA */
[data-testid="stForm"] [data-testid="stTextInput"] input,
[data-testid="stForm"] [data-testid="stTextArea"] textarea,
[data-testid="stForm"] [data-baseweb="select"] > div,
[data-testid="stForm"] [data-baseweb="input"] > div {
  background-color:#ffffff!important;
  color:#123250!important;
  border:1px solid #b9d6e4!important;
  border-radius:10px!important;
  box-shadow:none!important;
}
[data-testid="stForm"] input::placeholder,
[data-testid="stForm"] textarea::placeholder{color:#6a8396!important;opacity:1!important}
[data-testid="stForm"] label,
[data-testid="stForm"] label p,
[data-testid="stForm"] [data-testid="stWidgetLabel"] p,
[data-testid="stForm"] [data-testid="stCheckbox"] p{color:#153b59!important;font-weight:600!important}
[data-testid="stForm"] [data-baseweb="select"] span,
[data-testid="stForm"] [data-baseweb="select"] svg{color:#123250!important;fill:#123250!important}
[data-testid="stForm"] input:focus,
[data-testid="stForm"] textarea:focus,
[data-testid="stForm"] [data-baseweb="select"] > div:focus-within{border-color:#079cac!important;box-shadow:0 0 0 2px #079cac25!important}
[data-testid="stForm"] button[kind="primary"],
[data-testid="stForm"] button[data-testid="stBaseButton-primary"]{background:#07879e!important;border:1px solid #07879e!important;color:white!important;border-radius:10px!important}
[data-testid="stForm"] button[kind="primary"]:hover{background:#056d84!important}
/* Menu de opções do select, quando aberto */
[data-baseweb="popover"] [role="listbox"],
[data-baseweb="popover"] [role="option"]{background:#ffffff!important;color:#123250!important}
[data-baseweb="popover"] [role="option"]:hover{background:#e6f6fa!important}

</style>""",unsafe_allow_html=True)
def connect():
 c=sqlite3.connect(DB);c.row_factory=sqlite3.Row;return c
def init():
 with connect() as c:
  c.executescript("""CREATE TABLE IF NOT EXISTS systems(id INTEGER PRIMARY KEY,name TEXT NOT NULL,institution TEXT,purpose TEXT,population TEXT,version TEXT,owner TEXT,context TEXT,created TEXT);
CREATE TABLE IF NOT EXISTS assessments(id INTEGER PRIMARY KEY,system_id INTEGER,title TEXT,evaluator TEXT,scope TEXT,created TEXT,FOREIGN KEY(system_id) REFERENCES systems(id));
CREATE TABLE IF NOT EXISTS answers(assessment_id INTEGER,code TEXT,status TEXT NOT NULL DEFAULT 'NV',score INTEGER,evidence TEXT,justification TEXT,verification TEXT,reviewer TEXT,reviewed_at TEXT,recommendation TEXT,PRIMARY KEY(assessment_id,code));""")
def fetch(sql,args=()):
 with connect() as c:return [dict(r) for r in c.execute(sql,args).fetchall()]
def save(sql,args):
 with connect() as c:c.execute(sql,args)
def now():return datetime.now().strftime('%Y-%m-%d %H:%M')
def data_for(aid):
 ans={a['code']:a for a in fetch('SELECT * FROM answers WHERE assessment_id=?',(aid,))}
 return [{**x,**ans.get(x['codigo'],{'status':'NV','score':None,'evidence':'','justification':'','verification':'','reviewer':'','reviewed_at':'','recommendation':''})} for x in CRITERIA]
def calc(rows):
 av=[x for x in rows if x['status']=='AV' and x['score'] is not None]
 nv=sum(x['status']=='NV' for x in rows);na=sum(x['status']=='NA' for x in rows)
 conf=100*sum(x['score'] for x in av)/(4*len(av)) if av else None
 cov=100*len(av)/(len(av)+nv) if len(av)+nv else None
 return conf,cov,len(av),nv,na
def classification(c):
 if c is None:return 'Não calculável'
 return ('Conformidade muito baixa' if c<20 else 'Conformidade baixa' if c<40 else 'Conformidade parcial' if c<60 else 'Conformidade elevada' if c<80 else 'Conformidade muito elevada')
init()
def image_data(path):
    suffix=path.suffix.lower().replace('.','')
    mime='jpeg' if suffix in ('jpg','jpeg') else 'png'
    return f"data:image/{mime};base64,{base64.b64encode(path.read_bytes()).decode()}"
import base64
PUBLIC_PAGES=['Início','O Projeto','Metodologia','Plataforma','Pesquisador','Contato']
APP_PAGES=['Visão geral','Sistemas cadastrados','Nova avaliação','Avaliar critérios','Resultados e scorecard','Relatório e exportação','Base de critérios','Metodologia e limites']
if 'page' not in st.session_state:st.session_state.page='Início'
def navigate(target):
 st.session_state.page=target
with st.sidebar:
 st.image(str(ROOT/'assets/fac_ia_logo.jpeg'),width=165)
 st.markdown('**FAC-IA Saúde**  \nFramework Acadêmico • PPGIT/UFMG')
 st.caption('MENU DA PLATAFORMA')
 for item in APP_PAGES:
  if st.button(item,key='side_'+item,use_container_width=True,type='primary' if st.session_state.page==item else 'secondary'):
   navigate(item);st.rerun()
 st.divider()
 st.caption('3 perspectivas • 5 domínios • 45 critérios')
page=st.session_state.page
if page in APP_PAGES:
 if st.button('← Voltar ao site institucional',key='back_home'):
  navigate('Início');st.rerun()
st.markdown(f'''<div class="fac-header"><div class="fac-brand"><h1>FAC-IA <span>Saúde</span></h1><p>Framework de Avaliação e Conformidade de Inteligência Artificial em Saúde</p></div><div class="fac-institutions"><img alt="UFMG" src="{image_data(ROOT/'assets/ufmg.png')}"><span class="separator"></span><img alt="PPGIT UFMG" src="{image_data(ROOT/'assets/ppgit.png')}"></div></div>''',unsafe_allow_html=True)
if page not in ['Início','O Projeto','Metodologia','Plataforma','Pesquisador','Contato']:
 st.markdown('''<div class="fac-hero"><h3>IA responsável, segurança e governança em saúde</h3><p>Instrumento computacional acadêmico para avaliação estruturada e acompanhamento de requisitos de conformidade de sistemas de inteligência artificial em saúde, fundamentado em três perspectivas, cinco domínios e 45 critérios.</p></div>''',unsafe_allow_html=True)
systems=fetch('SELECT * FROM systems ORDER BY id DESC');assessments=fetch('SELECT a.*,s.name system_name FROM assessments a JOIN systems s ON a.system_id=s.id ORDER BY a.id DESC')

PUBLICATIONS=[
 ('Artigo 1','FAC-IA Saúde: framework multidimensional para avaliação de conformidade de IA responsável em saúde'),
 ('Artigo 2','Análise exploratória com dados clínicos da MIMIC-IV: evidências e limitações'),
 ('Artigo 3','Percepção de profissionais de saúde sobre IA responsável: ética, confiança e governança'),
 ('Artigo 4','Transparência e explicabilidade em IA na saúde: diretrizes e evidências')]
if page in ['Início','O Projeto','Metodologia','Plataforma','Pesquisador','Contato']:
 st.markdown('<div class="fac-nav-caption">EXPLORE O PROJETO</div>',unsafe_allow_html=True)
 navcols=st.columns([1,1.3,1.3,1.2,1.3,1.1])
 for col,item in zip(navcols,PUBLIC_PAGES):
  with col:
   if st.button(item,key='nav_'+item,use_container_width=True,type='primary' if page==item else 'secondary'):
    navigate(item);st.rerun()
 if page=='Início':
  st.markdown('''<section class="fac-landing"><div class="fac-eyebrow">Pesquisa · Inovação · Inteligência Artificial Responsável</div><h2>Uma nova perspectiva para avaliar a <em>IA na saúde.</em></h2><p>Conheça o FAC-IA Saúde: um framework acadêmico de avaliação e conformidade que conecta tecnologia, ética e governança para apoiar análises estruturadas de modelos de inteligência artificial.</p><span class="fac-tag">3 perspectivas</span><span class="fac-tag">5 domínios</span><span class="fac-tag">45 critérios</span></section>''',unsafe_allow_html=True)
  cta1,cta2=st.columns(2)
  with cta1:
   if st.button('Experimentar a plataforma →',type='primary',use_container_width=True,key='cta_home'):navigate('Visão geral');st.rerun()
  with cta2:
   if st.button('Conhecer a metodologia',use_container_width=True,key='cta_method'):navigate('Metodologia');st.rerun()
  st.markdown("""<section class="fac-data-intro"><div class="fac-data-eyebrow">IA NA SAÚDE · DADOS E EVIDÊNCIAS</div><h2>A inteligência artificial avança na prática clínica — e exige avaliação responsável</h2><p>Indicadores de pesquisas com médicos nos Estados Unidos e de dispositivos médicos autorizados pela FDA. Os dados mostram adoção, percepção de benefícios e expansão regulatória; não representam estimativas brasileiras.</p></section>""",unsafe_allow_html=True)
  st.markdown("""<div class="fac-stats-grid">
   <article class="fac-stat-card"><div class="fac-stat-kicker">Uso de IA por médicos · EUA</div><h3>De 38% para 66%</h3><p>Profissionais que declararam utilizar IA na prática, segundo levantamentos da AMA referentes a 2023 e 2024.</p><div class="fac-bar-group"><div class="fac-bar-label"><span>2023</span><b>38%</b></div><div class="fac-bar-track"><div class="fac-bar-fill" style="width:38%"></div></div><div class="fac-bar-label"><span>2024</span><b>66%</b></div><div class="fac-bar-track"><div class="fac-bar-fill fac-bar-fill-strong" style="width:66%"></div></div></div><div class="fac-stat-reading">+28 pontos percentuais na amostra pesquisada.</div><a href="https://www.ama-assn.org/press-center/ama-press-releases/ama-physician-enthusiasm-grows-health-care-ai" target="_blank" rel="noopener noreferrer">Fonte: American Medical Association (2025) ↗</a></article>
   <article class="fac-stat-card"><div class="fac-stat-kicker">Percepção médica · EUA</div><div class="fac-stat-number">68<span>%</span></div><p>Dos médicos entrevistados em 2024 perceberam alguma vantagem ou vantagem clara no uso de ferramentas de IA.</p><div class="fac-ring" style="--pct:68"><div>68%</div></div><div class="fac-stat-reading">Indicador de percepção, não de eficácia clínica.</div><a href="https://www.ama-assn.org/press-center/ama-press-releases/ama-physician-enthusiasm-grows-health-care-ai" target="_blank" rel="noopener noreferrer">Fonte: American Medical Association (2025) ↗</a></article>
   <article class="fac-stat-card"><div class="fac-stat-kicker">Dispositivos médicos · EUA</div><div class="fac-stat-number">+1.600</div><p>Dispositivos médicos habilitados por IA autorizados para comercialização pela FDA até setembro de 2026.</p><div class="fac-device-visual"><span>IA</span><div class="fac-device-bars"><i style="height:28%"></i><i style="height:43%"></i><i style="height:63%"></i><i style="height:85%"></i><i style="height:100%"></i></div></div><div class="fac-stat-reading">Total acumulado informado pela agência; não é medida de uso clínico.</div><a href="https://www.fda.gov/medical-devices/digital-health-center-excellence/artificial-intelligence-enabled-medical-devices" target="_blank" rel="noopener noreferrer">Fonte: FDA (setembro de 2026) ↗</a></article>
  </div><div class="fac-evidence-note">Nota metodológica: dados de fontes e populações distintas, apresentados apenas como contexto. A pesquisa FAC-IA Saúde não produziu esses indicadores. A autorização regulatória de um dispositivo não garante adequação de qualquer aplicação específica.</div>""",unsafe_allow_html=True)
  st.markdown('''<section class="fac-feature"><h2>FAC-IA Saúde — Ciência, tecnologia e responsabilidade</h2><p><strong>Tecnologia, ciência e responsabilidade para uma Inteligência Artificial mais segura, transparente e confiável na saúde.</strong></p><p>O FAC-IA Saúde é uma iniciativa acadêmica desenvolvida no Programa de Pós-Graduação em Inovação Tecnológica (PPGIT), da Universidade Federal de Minas Gerais (UFMG), para contribuir com a avaliação multidimensional da conformidade de modelos de Inteligência Artificial aplicados à saúde.</p><p>A proposta integra aspectos técnicos, éticos e regulatórios em um instrumento estruturado de avaliação, apoiando a identificação de riscos, lacunas de governança, necessidades de transparência e oportunidades de melhoria.</p><p><strong>Explore o framework, conheça sua fundamentação científica e experimente a plataforma interativa.</strong></p></section>''',unsafe_allow_html=True)
  st.markdown('''<section class="fac-feature"><h2>Sobre o projeto</h2><h3>Da pesquisa científica à aplicação prática</h3><p>O FAC-IA Saúde foi desenvolvido como artefato de pesquisa com a metodologia <strong>Design Science Research (DSR)</strong>, no contexto da dissertação de mestrado <em>“Avaliação e Conformidade de Modelos de IA Responsável em Saúde”</em>.</p><ul><li><strong>3 pilares:</strong> técnico, ético e regulatório.</li><li><strong>5 domínios:</strong> governança; dados e LGPD; segurança e risco clínico; transparência e explicabilidade; robustez e monitoramento.</li><li><strong>45 critérios de avaliação</strong> organizados em matriz operacional.</li><li><strong>Escala de 0 a 4</strong>, com estados AV, NA e NV, evidências e indicadores de cobertura.</li></ul><p>A plataforma permite explorar critérios, registrar avaliações e visualizar resultados por domínio e dimensão. O instrumento está em desenvolvimento acadêmico e aplicação exploratória; não constitui certificação regulatória ou validação de segurança clínica.</p></section>''',unsafe_allow_html=True)
  st.markdown('''<section class="fac-feature"><h2>Experimente o FAC-IA Saúde</h2><h3>Da metodologia à experiência interativa</h3><p>Conheça os domínios, explore os 45 critérios de conformidade e compreenda como o instrumento pode apoiar avaliações estruturadas de modelos de Inteligência Artificial em saúde.</p></section>''',unsafe_allow_html=True)
  if st.button('Iniciar avaliação na plataforma →',type='primary',key='cta_start_bottom',use_container_width=True):navigate('Visão geral');st.rerun()
 elif page=='O Projeto':
  st.markdown("""<div class="fac-section"><div class="fac-eyebrow">O PROJETO</div><h2>Da pesquisa científica à aplicação prática</h2><p>O FAC-IA Saúde é um artefato acadêmico desenvolvido na dissertação <em>“Avaliação e Conformidade de Modelos de IA Responsável em Saúde”</em>, no PPGIT/UFMG, sob orientação do <strong>Prof. Dr. Wagner Meira Jr.</strong> (DCC/UFMG), com apoio acadêmico da <strong>Prof.ª Dr.ª Patrícia Martins Parreiras</strong> (Instituto René Rachou — Fiocruz Minas).</p><p>A proposta integra dimensões técnicas, éticas e regulatórias para apoiar a identificação de riscos, lacunas de governança, transparência e oportunidades de melhoria na IA aplicada à saúde.</p></div>""",unsafe_allow_html=True)
  st.image(str(ROOT/'assets/fac_estrutura.png'),caption='Estrutura conceitual do FAC-IA Saúde: três pilares, cinco domínios e 45 critérios.',use_container_width=True)
  st.markdown('<div class="fac-cards"><div class="fac-card"><b>3 pilares</b><p>Técnico, ético e regulatório.</p></div><div class="fac-card"><b>5 domínios</b><p>Governança; Dados e LGPD; Segurança e risco clínico; Transparência e explicabilidade; Robustez e monitoramento.</p></div><div class="fac-card"><b>45 critérios</b><p>Nove por domínio; escala de 0 a 4, estados AV, NA e NV e registro de evidências.</p></div></div>',unsafe_allow_html=True)
  st.info('O FAC-IA Saúde é um instrumento acadêmico de apoio à avaliação; não constitui certificação regulatória, comprovação de segurança clínica ou validação empírica integral.')
 elif page=='Metodologia':
  st.markdown('<div class="fac-section"><div class="fac-eyebrow">METODOLOGIA</div><h2>Percurso metodológico da pesquisa</h2><p>A pesquisa utiliza <strong>Design Science Research (DSR)</strong>, articulando fundamentação, construção do artefato, aplicação exploratória, análise e síntese das contribuições.</p></div>',unsafe_allow_html=True)
  st.image(str(ROOT/'assets/fac_percurso.png'),caption='Síntese visual das cinco etapas metodológicas.',use_container_width=True)
  st.markdown('<div class="fac-method-grid"><div class="fac-method-card"><strong>01 · Problema e fundamentação</strong><p>Identificação do problema, revisão teórica e referências éticas e regulatórias.</p></div><div class="fac-method-card"><strong>02 · Desenvolvimento</strong><p>Construção da matriz operacional do FAC-IA Saúde: 3 pilares, 5 domínios e 45 critérios.</p></div><div class="fac-method-card"><strong>03 · Aplicação exploratória</strong><p>Uso conceitual no contexto de dados clínicos MIMIC-IV, sem avaliação de um sistema implantado.</p></div><div class="fac-method-card"><strong>04 · Análise e resultados</strong><p>Identificação de evidências, lacunas, limitações e oportunidades de melhoria.</p></div><div class="fac-method-card"><strong>05 · Síntese e contribuições</strong><p>Consolidação das contribuições e perspectivas de validação empírica futura.</p></div></div>',unsafe_allow_html=True)
  st.info('A aplicação exploratória com MIMIC-IV não equivale à validação integral do framework em um sistema de IA implantado.')
 elif page=='Plataforma':
  st.markdown('<div class="fac-section"><h2>Experimente a plataforma</h2><p>Cadastre sistemas e modelos, inicie avaliações, registre evidências para os 45 critérios, visualize indicadores de conformidade e cobertura e exporte relatórios. Utilize o menu lateral para acessar as funcionalidades.</p></div>',unsafe_allow_html=True)
  # A navegação para o aplicativo ocorre diretamente pelo menu lateral.
  st.markdown('<div class="fac-cards"><div class="fac-card"><b>1 · Cadastrar</b><p>Identifique o sistema ou modelo.</p></div><div class="fac-card"><b>2 · Avaliar</b><p>Registre pontuações, status e evidências.</p></div><div class="fac-card"><b>3 · Analisar</b><p>Consulte resultados e exporte relatórios.</p></div></div>',unsafe_allow_html=True)
 elif page=='Pesquisador':
  st.markdown(f'''<div class="fac-profile"><img alt="Fotografia do pesquisador" src="{image_data(ROOT/'assets/pesquisador.jpeg')}"><div><div class="fac-eyebrow">Pesquisador responsável</div><h3>Bruno Martins Bartolomeu</h3><p>Mestrando no Programa de Pós-Graduação em Inovação Tecnológica da Universidade Federal de Minas Gerais (PPGIT/UFMG), sob orientação do <strong>Prof. Dr. Wagner Meira Jr.</strong>, do Departamento de Ciência da Computação (DCC/UFMG), com apoio acadêmico da <strong>Prof.ª Dr.ª Patrícia Martins Parreiras</strong>, do Instituto René Rachou (Fiocruz Minas).</p><p>Profissional de Tecnologia da Informação e Dados, com atuação em análise de dados, inteligência de negócios, liderança técnica e docência no ensino superior. Sua pesquisa aborda avaliação, governança, ética e conformidade da IA em saúde.</p></div></div>''',unsafe_allow_html=True)
  st.link_button('Consultar Currículo Lattes ↗','http://lattes.cnpq.br/4479037178271028')
 elif page=='Contato':
  st.markdown("""<div class="fac-section"><div class="fac-eyebrow">CONTATO E COLABORAÇÃO</div><h2>Vamos conversar sobre IA responsável em saúde?</h2><p>Para colaboração científica, esclarecimentos sobre o framework, atividades acadêmicas ou propostas de pesquisa, utilize o formulário abaixo. O FAC-IA Saúde é uma iniciativa acadêmica, não um serviço de certificação ou consultoria regulatória.</p></div>""",unsafe_allow_html=True)
  a,b=st.columns([1.15,1],gap='large')
  with a:
   st.markdown('<div class="fac-contact-title">Entre em contato</div>',unsafe_allow_html=True)
   st.markdown('**Pesquisador:** Bruno Martins Bartolomeu  \n**Instituição:** PPGIT / Universidade Federal de Minas Gerais  \n**Localização:** Belo Horizonte — MG  \n**Área:** IA responsável, governança, avaliação e conformidade em saúde')
   st.link_button('Consultar Currículo Lattes ↗','http://lattes.cnpq.br/4479037178271028')
  with b:
   st.markdown('<div class="fac-contact-title">Temas para colaboração</div>',unsafe_allow_html=True)
   st.markdown('• Pesquisa e desenvolvimento do FAC-IA Saúde  \n• Governança e avaliação de IA em saúde  \n• Transparência e explicabilidade  \n• Aplicações acadêmicas e estudos exploratórios  \n• Parcerias e produção científica')
  st.markdown('### Envie sua mensagem')
  st.caption('Preencha o formulário para preparar uma mensagem no seu aplicativo de e-mail. Nenhum dado é enviado ou armazenado pelo site.')
  with st.form('fac_contato',clear_on_submit=False):
   ca,cb=st.columns(2)
   with ca:
    nome=st.text_input('Nome *',placeholder='Seu nome')
    email=st.text_input('E-mail *',placeholder='seuemail@exemplo.com')
    instituicao=st.text_input('Instituição / organização',placeholder='Universidade ou instituição')
   with cb:
    funcao=st.text_input('Cargo / função',placeholder='Pesquisador(a), docente, estudante...')
    assunto=st.selectbox('Assunto *',['Colaboração científica','Dúvida sobre o FAC-IA Saúde','Pesquisa acadêmica','Convite para palestra','Outro'])
   mensagem=st.text_area('Como podemos colaborar? *',height=135,placeholder='Descreva sua mensagem ou proposta...')
   consentimento=st.checkbox('Concordo em utilizar os dados informados exclusivamente para compor esta mensagem de contato.')
   enviar=st.form_submit_button('Preparar mensagem',type='primary',use_container_width=True)
  if enviar:
   if not nome.strip() or not email.strip() or '@' not in email or not mensagem.strip() or not consentimento:
    st.error('Preencha nome, e-mail e mensagem, e confirme o consentimento.')
   else:
    corpo=f'Nome: {nome}\nE-mail: {email}\nInstituição: {instituicao}\nCargo: {funcao}\nAssunto: {assunto}\n\n{mensagem}'
    # A página não dispõe de serviço de e-mail configurado; não afirmar envio.
    st.success('Mensagem preparada. Copie o texto abaixo e encaminhe pelo canal de contato acadêmico de sua preferência.')
    st.code(corpo,language=None)
    st.caption('O formulário não envia e-mails automaticamente. Para envio direto, é necessário configurar um serviço de e-mail e um destinatário autorizado.')
 st.markdown('<div class="fac-footer">FAC-IA Saúde · Framework Acadêmico · Projeto de mestrado · PPGIT / Universidade Federal de Minas Gerais · Belo Horizonte, 2026<br>Instrumento de apoio à avaliação; não constitui certificação regulatória nem comprovação de segurança clínica.</div>',unsafe_allow_html=True)

if page=='Visão geral':
 a,b,c,d=st.columns(4)
 a.metric('◈ Sistemas cadastrados',len(systems));b.metric('☑ Avaliações realizadas',len(assessments));c.metric('▤ Critérios do framework',45);d.metric('⬡ Domínios',5)
 latest=assessments[0] if assessments else None
 if latest:
  lr=data_for(latest['id']);lc,lk,lav,lnv,lna=calc(lr)
 else:lc=lk=None;lav=lnv=lna=0
 left,right=st.columns([1,1.18],gap='medium')
 with left:
  st.markdown('<div class="fac-panel"><h3>Conformidade · última avaliação</h3></div>',unsafe_allow_html=True)
  x,y=st.columns(2)
  x.metric('Conformidade',f'{lc:.1f}%' if lc is not None else '—')
  y.metric('Cobertura (AV)',f'{lk:.1f}%' if lk is not None else '—')
  if lc is not None:st.progress(min(1,max(0,lc/100)),text=classification(lc))
  else:st.caption('Crie uma avaliação e registre evidências para calcular o índice.')
  st.caption(f'Critérios: {lav} AV · {lnv} NV · {lna} NA')
 with right:
  st.markdown('<div class="fac-panel"><h3>Desempenho por domínio</h3></div>',unsafe_allow_html=True)
  icons=['🏛️','▤','🛡️','◉','▥']
  html='<div class="fac-domains">'
  for i,dom in enumerate(DOMAINS):
   sub=[x for x in lr if x['dominio']==dom] if latest else []
   score=calc(sub)[0] if sub else None
   html+=f'<div class="fac-domain"><span class="ico">{icons[i]}</span><b>{dom}</b><small>{f"{score:.0f}%" if score is not None else "—"}</small></div>'
  st.markdown(html+'</div>',unsafe_allow_html=True)
 st.markdown('<div class="fac-panel"><h3>Fluxo operacional do FAC-IA Saúde</h3><div class="fac-steps"><div class="fac-step"><strong>①</strong>Cadastrar<br>sistema / modelo</div><div class="fac-step"><strong>②</strong>Avaliar os<br>45 critérios</div><div class="fac-step"><strong>③</strong>Analisar<br>conformidade e cobertura</div><div class="fac-step"><strong>④</strong>Gerar relatório<br>com recomendações</div></div></div>',unsafe_allow_html=True)
 st.markdown('<div class="fac-note">ⓘ O FAC-IA Saúde é um instrumento acadêmico de avaliação de conformidade. Não constitui certificação regulatória nem comprovação automática de segurança clínica. A aplicação MIMIC-IV na dissertação é exploratória.</div>',unsafe_allow_html=True)
if page=='Sistemas cadastrados':
 st.subheader('Cadastro de sistemas e modelos de IA')
 with st.form('sys'):
  name=st.text_input('Nome do sistema/modelo *');institution=st.text_input('Instituição');purpose=st.text_area('Finalidade e uso pretendido');population=st.text_input('População-alvo');version=st.text_input('Versão do modelo');owner=st.text_input('Responsável');context=st.selectbox('Contexto',['Sistema implantado','Protótipo / pesquisa','Estudo exploratório / conceitual'])
  if st.form_submit_button('Cadastrar sistema',type='primary'):
   if name.strip():save('INSERT INTO systems(name,institution,purpose,population,version,owner,context,created) VALUES(?,?,?,?,?,?,?,?)',(name,institution,purpose,population,version,owner,context,now()));st.success('Sistema cadastrado.');st.rerun()
   else:st.error('Informe o nome.')
 if systems:st.dataframe(pd.DataFrame(systems)[['id','name','institution','version','context']],use_container_width=True,hide_index=True)
if page=='Nova avaliação':
 st.subheader('Definir escopo de avaliação')
 if not systems:st.warning('Cadastre um sistema antes de criar uma avaliação.')
 else:
  with st.form('assessment'):
   sid=st.selectbox('Sistema',options=[s['id'] for s in systems],format_func=lambda i:next(s['name'] for s in systems if s['id']==i))
   title=st.text_input('Título da avaliação',value='Avaliação de conformidade FAC-IA Saúde');evaluator=st.text_input('Avaliador');scope=st.text_area('Escopo, finalidade, limites e fontes de evidência')
   if st.form_submit_button('Criar avaliação',type='primary'):
    save('INSERT INTO assessments(system_id,title,evaluator,scope,created) VALUES(?,?,?,?,?)',(sid,title,evaluator,scope,now()));st.success('Avaliação criada.');st.rerun()
if page in ['Avaliar critérios','Resultados e scorecard','Relatório e exportação']:
 if not assessments:st.warning('Crie uma avaliação para continuar.')
 else:
  aid=st.selectbox('Avaliação',options=[a['id'] for a in assessments],format_func=lambda i:next(f"#{a['id']} • {a['system_name']} • {a['title']}" for a in assessments if a['id']==i))
  rows=data_for(aid);conf,cov,nav,nnv,nna=calc(rows)
  if page=='Avaliar critérios':
   st.subheader('Matriz operacional — Apêndice A')
   st.caption('AV: aplicável e verificável, com pontuação 0–4. NA: não aplicável. NV: aplicável, mas evidência insuficiente. NA/NV não recebem nota.')
   dom=st.selectbox('Domínio',DOMAINS)
   for item in [x for x in rows if x['dominio']==dom]:
    with st.expander(f"{item['codigo']} — {item['criterio']} • {item['status']}"):
     st.write('**Requisito e pilares:**',item['requisito']);st.write('**Evidências esperadas:**',item['evidencias_esperadas']);st.write('**Procedimento de verificação:**',item['procedimento'])
     with st.form('criterion_'+item['codigo']):
      status=st.selectbox('Condição',['NV','AV','NA'],index=['NV','AV','NA'].index(item['status']))
      score=st.selectbox('Pontuação AV',['Selecione',0,1,2,3,4],index=([ 'Selecione',0,1,2,3,4].index(item['score']) if item['score'] is not None else 0),help='0 exige evidência suficiente de não atendimento. Ausência de evidências corresponde a NV.') if status=='AV' else None
      evidence=st.text_area('Evidências encontradas / referências',value=item['evidence'] or '')
      justification=st.text_area('Justificativa da classificação e pontuação',value=item['justification'] or '')
      verification=st.text_area('Procedimento realizado / limitações',value=item['verification'] or '')
      recommendation=st.text_area('Fragilidades e recomendações',value=item['recommendation'] or '')
      reviewer=st.text_input('Responsável pela verificação',value=item['reviewer'] or '')
      if st.form_submit_button('Salvar critério',type='primary'):
       if status=='AV' and score=='Selecione':st.error('Critério AV exige pontuação de 0 a 4.')
       elif not justification.strip():st.error('Registre a justificativa para AV, NA ou NV.')
       elif status=='AV' and not evidence.strip():st.error('Registre evidência para atribuir pontuação AV, inclusive quando a nota for zero.')
       else:
        save('INSERT INTO answers(assessment_id,code,status,score,evidence,justification,verification,reviewer,reviewed_at,recommendation) VALUES(?,?,?,?,?,?,?,?,?,?) ON CONFLICT(assessment_id,code) DO UPDATE SET status=excluded.status,score=excluded.score,evidence=excluded.evidence,justification=excluded.justification,verification=excluded.verification,reviewer=excluded.reviewer,reviewed_at=excluded.reviewed_at,recommendation=excluded.recommendation',(aid,item['codigo'],status,score if status=='AV' else None,evidence,justification,verification,reviewer,now(),recommendation));st.success('Critério registrado.');st.rerun()
  if page=='Resultados e scorecard':
   st.subheader('Scorecard de conformidade e cobertura')
   a,b,c,d,e=st.columns(5);a.metric('Conformidade',f'{conf:.1f}%' if conf is not None else 'N/D');b.metric('Cobertura',f'{cov:.1f}%' if cov is not None else 'N/D');c.metric('AV',nav);d.metric('NV',nnv);e.metric('NA',nna)
   st.info('Classificação proposta: '+classification(conf)+'. Faixas descritivas não validadas empiricamente nem definidas por regulador.')
   summary=[]
   for dom in DOMAINS:
    subset=[x for x in rows if x['dominio']==dom];c,k,av,nv,na=calc(subset)
    summary.append({'Domínio':dom,'Conformidade (%)':round(c,1) if c is not None else None,'Cobertura (%)':round(k,1) if k is not None else None,'AV':av,'NV':nv,'NA':na})
   st.dataframe(pd.DataFrame(summary),use_container_width=True,hide_index=True)
   st.subheader('Critérios e evidências')
   st.dataframe(pd.DataFrame(rows)[['codigo','dominio','criterio','status','score','evidence','justification','recommendation']],use_container_width=True,hide_index=True)
   st.warning('Conformidade é calculada somente com critérios AV. Cobertura = AV/(AV+NV). Um percentual elevado com baixa cobertura exige cautela.')
  if page=='Relatório e exportação':
   st.subheader('Relatório técnico de avaliação')
   assessment=next(a for a in assessments if a['id']==aid)
   st.write('**Sistema:**',assessment['system_name']);st.write('**Avaliador:**',assessment['evaluator']);st.write('**Escopo:**',assessment['scope']);st.write('**Data de criação:**',assessment['created'])
   st.write('**Conformidade:**',f'{conf:.2f}%' if conf is not None else 'Não calculável');st.write('**Cobertura:**',f'{cov:.2f}%' if cov is not None else 'Não calculável');st.write('**Classificação:**',classification(conf))
   st.caption('O relatório não é certificado regulatório, auditoria clínica independente ou comprovação integral de conformidade.')
   df=pd.DataFrame(rows)
   st.download_button('Baixar matriz CSV',df.to_csv(index=False).encode('utf-8-sig'),file_name=f'fac_ia_matriz_{aid}.csv',mime='text/csv')
   report={'framework':'FAC-IA Saúde','versao_metodologica':'Dissertação PPGIT/UFMG 2026','avaliacao':assessment,'conformidade_percentual':conf,'cobertura_percentual':cov,'classificacao':classification(conf),'AV':nav,'NV':nnv,'NA':nna,'criterios':rows,'limite':'Instrumento de apoio; não certifica segurança clínica ou conformidade regulatória integral.'}
   st.download_button('Baixar relatório JSON',json.dumps(report,ensure_ascii=False,indent=2,default=str).encode('utf-8'),file_name=f'fac_ia_relatorio_{aid}.json',mime='application/json')
   txt=['FAC-IA SAÚDE — RELATÓRIO DE AVALIAÇÃO',f"Sistema: {assessment['system_name']}",f"Avaliação: {assessment['title']}",f"Avaliador: {assessment['evaluator']}",f"Escopo: {assessment['scope']}",f"Conformidade: {conf:.2f}%" if conf is not None else 'Conformidade: N/D',f"Cobertura: {cov:.2f}%" if cov is not None else 'Cobertura: N/D',f'Classificação: {classification(conf)}','', 'LIMITES: Avaliação metodológica baseada em evidências; não equivale a certificação ou validação clínica integral.']
   for x in rows:txt.extend(['',f"{x['codigo']} — {x['criterio']} [{x['status']}]",f"Pontuação: {x['score'] if x['score'] is not None else 'Não atribuída'}",f"Evidência: {x['evidence']}",f"Justificativa: {x['justification']}",f"Recomendação: {x['recommendation']}"])
   st.download_button('Baixar relatório TXT','\n'.join(txt).encode('utf-8'),file_name=f'fac_ia_relatorio_{aid}.txt',mime='text/plain')
if page=='Metodologia e limites':
 st.subheader('Fundamentação e regras da dissertação')
 st.markdown('**Três perspectivas:** técnica, ética e regulatória. **Cinco domínios:** governança; dados e LGPD; segurança e risco clínico; transparência e explicabilidade; robustez e monitoramento.')
 st.markdown('**Escala ordinal:** 0 = não atendido demonstrado; 1 = incipiente; 2 = parcial; 3 = substancial; 4 = integralmente demonstrado.')
 st.latex(r'C = \frac{\sum_{i \in V} s_i}{4n_V} \times 100')
 st.latex(r'K = \frac{n_{AV}}{n_{AV}+n_{NV}} \times 100')
 st.markdown('**Classificação proposta:** 0–<20 muito baixa; 20–<40 baixa; 40–<60 parcial; 60–<80 elevada; 80–100 muito elevada.')
 st.warning('NA e NV são excluídos do índice de conformidade. Pontuação 0 não deve ser atribuída automaticamente por falta de evidência. O scorecard não mede diretamente probabilidade ou gravidade de risco.')
 st.info('O estudo MIMIC-IV v3.1 da dissertação é uma aplicação exploratória de evidências clínicas, não uma avaliação operacional de IA implantada. A validação empírica integral permanece futura.')
 st.caption('Fonte: Dissertação final, seções 4.3.3–4.3.6 e Apêndice A. Critérios transcritos das tabelas originais.')

if page=='Base de critérios':
 st.subheader('Base de critérios · Apêndice A')
 st.caption('Consulta à matriz operacional dos 45 critérios, preservada do projeto original.')
 domain_filter=st.selectbox('Filtrar domínio',['Todos']+DOMAINS)
 filtered=[x for x in CRITERIA if domain_filter=='Todos' or x['dominio']==domain_filter]
 st.dataframe(pd.DataFrame(filtered),use_container_width=True,hide_index=True)
 st.download_button('Exportar base de critérios CSV',pd.DataFrame(filtered).to_csv(index=False).encode('utf-8-sig'),file_name='fac_ia_criterios.csv',mime='text/csv')
