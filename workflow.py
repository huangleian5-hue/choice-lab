"""Executable local source-ingest -> wiki-retrieval -> evidence -> HTML graph.
No external LLM API is called. Rejects unsupported claims and records actual retries.
"""
import json,re,sys,argparse
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parent
CAT=json.loads((ROOT/'sources/catalog.json').read_text(encoding='utf-8'))
NOW=lambda:datetime.now(timezone.utc).isoformat()

def retrieve(query):
    tokens=[x for x in re.split(r'\s+',query.strip()) if x]
    out=[]
    for f in sorted((ROOT/'wiki').glob('W*.md')):
        t=f.read_text(encoding='utf-8')
        score=sum(t.lower().count(x.lower()) for x in tokens)
        if score:out.append({'page':f.name,'score':score,'source_ids':re.findall(r'S\d+',re.search(r'^source_ids:.*$',t,re.M).group())})
    return sorted(out,key=lambda x:-x['score'])

def run_graph(query='選擇架構',claim='選擇架構可能影響選擇',inject_bad_claim=False):
    log={'at_utc':NOW(),'query':query,'steps':[],'rejections':[],'retry_count':0,'mode':'本地可執行檢索與證據規則檢查，無 LLM API'}
    def step(name,ok,detail):log['steps'].append({'node':name,'pass':bool(ok),'detail':detail});return ok
    notes=list((ROOT/'sources/notes').glob('S*.md'))
    ingested=[c for c in CAT if (ROOT/'sources/notes'/f"{c['id']}.md").exists() and '已核對' in c.get('ingest_status','')]
    if not step('ingest_sources',len(ingested)>=5,f'{len(ingested)} 份公開摘要／網頁中文轉述筆記；非全文'):
        log['status']='FAIL';return log
    results=retrieve(query)
    if not step('retrieve_wiki',bool(results),[x['page'] for x in results]):log['status']='FAIL';return log
    ids={c['id'] for c in CAT};valid=all(set(x['source_ids'])<=ids for x in results)
    if not step('check_source_links',valid,'檢索頁面所列 source_ids 必須存在於 catalog'):
        log['status']='FAIL';return log
    text=claim if not inject_bad_claim else '只要放在最顯眼的位置，銷量一定增加100%'
    unsupported=['一定增加100%','保證銷量','所有人都會','必然購買']
    for attempt in range(3):
        ok=not any(x in text for x in unsupported)
        step('check_claim',ok,{'attempt':attempt+1,'claim':text})
        if ok:break
        log['rejections'].append({'node':'check_claim','reason':'絕對化且缺乏來源支持','rejected_claim':text})
        if attempt==2:log['status']='FAIL';return log
        log['retry_count']+=1
        text='商品位置與資訊呈現可能影響注意力，但銷量效果仍需驗證。'
        step('revise_claim',True,{'revision':text,'method':'規則式替換，非 LLM 改寫'})
    html=(ROOT/'index.html').read_text(encoding='utf-8')
    checks={'12_slides':len(re.findall(r'<section class="slide',html))==12,'wiki_refs':all(f'data-wiki="W{i:02}"' in html for i in range(1,6)),'interactive_menu':'function pickMeal' in html and 'function clue' in html,'interactive_machine':'function drawMachine' in html and 'function showDesign' in html,'quiz':'function answerQuiz' in html}
    step('validate_html_static',all(checks.values()),checks)
    log['status']='PASS' if all(checks.values()) else 'FAIL'
    log['final_claim']=text
    return log

if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('--query',default='選擇架構');a.add_argument('--inject-bad-claim',action='store_true');a.add_argument('--show-retrieval',action='store_true');args=a.parse_args()
    if args.show_retrieval:print(json.dumps(retrieve(args.query),ensure_ascii=False,indent=2));sys.exit(0)
    result=run_graph(args.query,inject_bad_claim=args.inject_bad_claim)
    (ROOT/'logs').mkdir(exist_ok=True)
    name='graph-rejection.json' if args.inject_bad_claim else 'graph-normal.json'
    (ROOT/'logs'/name).write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(result,ensure_ascii=False,indent=2));sys.exit(result['status']!='PASS')
