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
with st.sidebar:
 st.image(str(ROOT/'assets/fac_ia_logo.jpeg'),use_container_width=True)
 st.markdown('**FAC-IA Saúde**  \nAvaliação de conformidade de IA responsável em saúde')
 page=st.radio('Navegação',['Visão geral','Sistemas cadastrados','Nova avaliação','Avaliar critérios','Resultados e scorecard','Relatório e exportação','Base de critérios','Metodologia e limites'],label_visibility='collapsed')
 st.caption('MVP acadêmico • 3 perspectivas • 5 domínios • 45 critérios')
st.markdown(f'''<div class="fac-header"><div class="fac-brand"><h1>FAC-IA <span>Saúde</span></h1><p>Framework de Avaliação e Conformidade de Inteligência Artificial em Saúde</p></div><div class="fac-institutions"><img alt="UFMG" src="{image_data(ROOT/'assets/ufmg.png')}"><span class="separator"></span><img alt="PPGIT UFMG" src="{image_data(ROOT/'assets/ppgit.png')}"></div></div>''',unsafe_allow_html=True)
st.markdown('''<div class="fac-hero"><h3>IA responsável, segurança e governança em saúde</h3><p>Instrumento computacional acadêmico para avaliação estruturada e acompanhamento de requisitos de conformidade de sistemas de inteligência artificial em saúde, fundamentado em três perspectivas, cinco domínios e 45 critérios.</p></div>''',unsafe_allow_html=True)
systems=fetch('SELECT * FROM systems ORDER BY id DESC');assessments=fetch('SELECT a.*,s.name system_name FROM assessments a JOIN systems s ON a.system_id=s.id ORDER BY a.id DESC')
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
