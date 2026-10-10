"""
AI 도감 페이지 만들기 프로그램
- assets/data.js(AI 목록·점수·후기)를 읽어서 홈, AI별 페이지, 404, sitemap.xml, robots.txt를 다시 만들어요.
- 사용법: 사이트 폴더 맨 위에서  python3 tools/build.py   (node가 설치되어 있어야 해요)
- Claude에게 부탁할 때: 이 파일과 assets/data.js를 함께 주고 "다시 만들어 줘"라고 하면 돼요.
"""
import json, html, os, subprocess, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # 사이트 폴더 맨 위
OUT = ROOT

# data.js를 node로 읽어서 데이터로 바꿈
_js = open(os.path.join(ROOT, 'assets', 'data.js'), encoding='utf-8').read()
_js += "\nprocess.stdout.write(JSON.stringify({CRITERIA, CATEGORIES, TOOLS}));"
D = json.loads(subprocess.run(['node', '-e', _js], capture_output=True, text=True, check=True).stdout)
TODAY = datetime.date.today().isoformat()
CRIT, CATS, TOOLS = D['CRITERIA'], D['CATEGORIES'], D['TOOLS']
SITE = 'https://aidogam.kr'
TC = {"chat":"#8DB4F5","image":"#F4A3C4","video":"#F5AE7E","audio":"#7FD6CB","music":"#BFA4F0",
      "code":"#9ED69B","slide":"#F5D97A","study":"#E9BE8C","trans":"#8FCFF0"}
e = lambda s: html.escape(str(s or ''), quote=True)
cat_label = {c['id']: c['label'] for c in CATS}
dexno = {t['id']: f"{i+1:03d}" for i, t in enumerate(TOOLS)}
def total(t): return sum(t['s'].get(c['key'], 0) for c in CRIT) / len(CRIT)
def ranked(cat): return sorted([t for t in TOOLS if t['cat'] == cat], key=lambda t: -total(t))
def f1(v): return f"{v + 1e-9:.1f}"

GA = '''<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-4PGZ1RDWYT"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());

  gtag('config', 'G-4PGZ1RDWYT');
</script>'''

def head(title, desc, path):
    url = SITE + path
    return f'''<!DOCTYPE html>
<html lang="ko">
<head>
{GA}
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{url}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="AI 도감">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{url}">
<meta property="og:locale" content="ko_KR">
<meta name="theme-color" content="#262A5C">
<link rel="icon" href="/assets/bit.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/assets/bit-icon.png">
<meta property="og:image" content="{SITE}/assets/og.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Do+Hyeon&family=Noto+Sans+KR:wght@500;700&family=Press+Start+2P&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/style.css">
</head>'''

SCRIPTS = '<script src="/assets/data.js"></script>\n<script src="/assets/bit.js"></script>\n<script src="/assets/app.js"></script>'
TOAST = '<div class="toast" id="toast" role="status" aria-live="polite"></div>'

def entry(t, rank):
    return f'''<li><a class="entry" href="/ai/{t['id']}/">
    <span class="rank {'first' if rank == 1 else ''}">{rank or ''}</span>
    <span class="sp" data-id="{t['id']}" data-size="44"></span>
    <span style="min-width:0"><span class="nm">{e(t['name'])}</span>
      <span class="meta"><span class="ds">{e(t['desc'])}</span></span></span>
    <span class="score">{f1(total(t))}</span></a></li>'''

def allnav():
    rows = ''.join(f'<dt>{e(c["label"])}</dt><dd>' + ' '.join(f'<a href="/ai/{t["id"]}/">{e(t["name"])}</a>' for t in ranked(c['id'])) + '</dd>' for c in CATS)
    return f'<nav class="allnav" aria-label="전체 AI 목록"><h2>AI 도감 전체 목록</h2><dl>{rows}</dl></nav>'

# ---------- 홈 ----------
home_desc = f"학생이 직접 써보고 점수를 매긴 AI 도감. 챗봇, 그림, 영상, 음악, 발표자료 등 {len(TOOLS)}개 AI를 타입별 순위와 후기로 비교하고, 질문 4개로 나에게 맞는 AI를 찾아보세요."
home = head("AI 도감 | 학생이 직접 써보고 매긴 AI 순위", home_desc, "/") + f'''
<body data-page="home">
<div class="wrap">
  <section id="home">
    <header class="top">
      <h1 class="logo"><small>NO.001~{len(TOOLS):03d}</small>AI 도감</h1>
      <button class="meter" id="openDex" aria-label="내 도감 열기"><span class="lbl">써본 AI <b id="cnt">0/{len(TOOLS)}</b><span class="go" aria-hidden="true">▶</span></span><span class="bar" id="bar" aria-hidden="true"></span></button>
    </header>
    <label class="search px"><span aria-hidden="true">▶</span>
      <input id="q" type="search" placeholder="AI 이름이나 하고 싶은 일 검색" autocomplete="off" aria-label="AI 검색">
    </label>
    <button class="quest" id="openQuiz"><span class="bit" data-bit="wave" data-size="68" data-still="3"></span>
      <span><b>나에게 맞는 AI 찾기</b><span class="s">질문 4개에 답하면 딱 맞는 AI를 골라 줘요</span></span><span class="arrow" aria-hidden="true">▶</span></button>
    <div class="types" id="types" role="toolbar" aria-label="타입"></div>
    <div class="board px">
      <div class="board-head">
        <h2 id="title">챗봇 타입 순위</h2>
        <button class="tool-btn" id="openW">기준 바꾸기</button>
      </div>
      <ul class="list" id="list">{''.join(entry(t, i+1) for i, t in enumerate(ranked('chat')))}</ul>
    </div>
    <p class="foot">점수와 후기는 직접 써본 경험을 바탕으로 합니다.</p>
    {allnav()}
  </section>
  <section id="dex" hidden></section>
  <section id="quiz" hidden></section>
</div>
<div class="modal-bg" id="mbg"></div>
<div class="modal px" id="modal" role="dialog" aria-modal="true" aria-labelledby="mTitle">
  <h2 id="mTitle">내 채점 기준</h2>
  <p>중요한 기준일수록 높이세요. 0이면 점수에서 빠져요.</p>
  <div id="wrows"></div>
  <div class="modal-foot">
    <button class="tool-btn plain" id="resetW">기본값으로</button>
    <button class="tool-btn" id="closeW">적용하기</button>
  </div>
</div>
{TOAST}
{SCRIPTS}
</body>
</html>
'''
open(f'{OUT}/index.html', 'w', encoding='utf-8').write(home)

# ---------- AI별 페이지 ----------
for t in TOOLS:
    r = ranked(t['cat']); rank = r.index(t) + 1; v = total(t); cl = cat_label[t['cat']]
    pros = ', '.join(t.get('pros') or [])
    desc = f"{t['name']} 점수 {f1(v)}/5 · {cl} {rank}위. {t['desc']}."
    if pros: desc += f" 좋은 점: {pros}."
    desc += " 학생이 직접 써보고 매긴 AI 도감."
    if len(desc) > 158: desc = desc[:157] + '…'
    stats = ''.join(f'''<div class="stat"><span>{e(c['label'])}</span>
      <span class="seg" aria-hidden="true">{''.join(f'<i class="{"on" if i < round(t["s"].get(c["key"],0)*2) else ""}"></i>' for i in range(10))}</span>
      <b>{t["s"].get(c["key"],0):.1f}</b></div>''' for c in CRIT)
    lst = lambda a: ('<ul>' + ''.join(f'<li>{e(x)}</li>' for x in a) + '</ul>') if a else ''
    review = f'<p>{e(t["review"]).replace(chr(10), "<br>")}</p>' if t.get('review') else '<p>아직 후기가 없어요. 직접 써보고 채울 예정이에요.</p>'
    talk = ''
    if t.get('pros'): talk += f'<h3>좋은 점</h3>{lst(t["pros"])}'
    if t.get('cons'): talk += f'<h3>아쉬운 점</h3>{lst(t["cons"])}'
    if t.get('who'): talk += f'<h3>이런 사람에게</h3><p>{e(t["who"])}</p>'
    talk += f'<h3>직접 써본 후기</h3>{review}'
    others = ''.join(entry(x, i+1) for i, x in enumerate(r) if x is not t)
    page = head(f"{t['name']} 점수·후기 | AI 도감", desc, f"/ai/{t['id']}/") + f'''
<body data-page="ai" data-id="{t['id']}">
<div class="wrap">
  <div class="dtop">
    <a class="back" id="back" href="/">◀ 도감으로</a>
    <div class="icons">
      <button class="icon-btn" id="share">공유</button>
      <button class="icon-btn fav" id="fav" aria-pressed="false">찜하기</button>
    </div>
  </div>
  <p class="crumb"><a href="/">AI 도감</a> › {e(cl)} › {e(t['name'])}</p>
  <article class="card px">
    <div class="stage pop" style="--tc:{TC[t['cat']]}">
      <span class="dexno">No.{dexno[t['id']]}</span>
      <span class="rankbadge" id="rankbadge">{e(cl)} {rank}위</span>
      <span class="sp" data-id="{t['id']}" data-size="160"></span>
    </div>
    <div class="id">
      <div><h1>{e(t['name'])}</h1><p class="desc">{e(t['desc'])}</p></div>
      <div class="big" id="bigscore">{f1(v)}<small>5점 만점</small></div>
    </div>
    <div class="stats">{stats}</div>
    <div class="talk px">{talk}<span class="more" aria-hidden="true">▼</span></div>
    <div class="actions">
      <button class="act collect" id="collect" aria-pressed="false">써봤어요</button>
      <a class="act go" href="{e(t['url'])}" target="_blank" rel="noopener">사이트 가기</a>
    </div>
  </article>
  <div class="board px others">
    <div class="board-head"><h2>{e(cl)} 타입 다른 AI</h2></div>
    <ul class="list" id="others">{others}</ul>
  </div>
  <p class="foot">점수와 후기는 직접 써본 경험을 바탕으로 합니다.</p>
</div>
{TOAST}
{SCRIPTS}
</body>
</html>
'''
    os.makedirs(f"{OUT}/ai/{t['id']}", exist_ok=True)
    open(f"{OUT}/ai/{t['id']}/index.html", 'w', encoding='utf-8').write(page)

# ---------- 404 ----------
open(f'{OUT}/404.html', 'w', encoding='utf-8').write(head("페이지를 찾을 수 없어요 | AI 도감", "AI 도감에서 찾는 페이지가 없어요.", "/404.html").replace('<link rel="canonical" href="https://aidogam.kr/404.html">', '<meta name="robots" content="noindex">') + '''
<body data-page="404">
<div class="wrap" style="text-align:center; padding-top:80px">
  <div class="qbox px lost">
    <span class="bit" data-bit="sleepy" data-size="150" data-still="2"></span>
    <p class="qstep" style="font-size:1.2rem; margin:0 0 10px">404</p>
    <h1 class="qtitle">앗, 이 페이지는 도감에 없어요</h1>
    <p style="color:var(--sub); margin:-6px 0 16px">비트가 깜빡 졸았나 봐요. 도감으로 돌아가서 다시 찾아봐요!</p>
    <a class="act go" href="/" style="max-width:240px; margin:0 auto">도감으로 돌아가기</a>
  </div>
</div>
<script src="/assets/bit.js"></script>
<script>fillBits();</script>
</body>
</html>
''')

# ---------- sitemap / robots ----------
urls = ['/'] + [f"/ai/{t['id']}/" for t in TOOLS]
sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + \
     ''.join(f'  <url><loc>{SITE}{u}</loc><lastmod>{TODAY}</lastmod></url>\n' for u in urls) + '</urlset>\n'
open(f'{OUT}/sitemap.xml', 'w', encoding='utf-8').write(sm)
open(f'{OUT}/robots.txt', 'w', encoding='utf-8').write(f"User-agent: *\nAllow: /\nDisallow: /tools/\n\nSitemap: {SITE}/sitemap.xml\n")
print('pages', len(TOOLS)+1)
