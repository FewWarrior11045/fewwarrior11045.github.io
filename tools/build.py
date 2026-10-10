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
EMAIL = 'aidogam.kr@gmail.com'
FOOT = f'''<p class="foot">점수는 직접 써 본 경험과 공개된 정보를 바탕으로 매기며, 계속 고쳐 나가요.</p>
    <p class="footlinks"><a href="/about/">소개</a><span>·</span><a href="/privacy/">개인정보 처리방침</a><span>·</span><a href="mailto:{EMAIL}">문의</a></p>'''

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
    {FOOT}
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
  {FOOT}
</div>
{TOAST}
{SCRIPTS}
</body>
</html>
'''
    os.makedirs(f"{OUT}/ai/{t['id']}", exist_ok=True)
    open(f"{OUT}/ai/{t['id']}/index.html", 'w', encoding='utf-8').write(page)


# ---------- 소개 · 개인정보 처리방침 ----------
CRIT_DESC = {
  'quality': '— 결과물이 얼마나 쓸 만한지. 글이면 정확하고 자연스러운지, 그림·영상이면 완성도가 높은지 봐요.',
  'free': '— 돈을 안 내도 어디까지 쓸 수 있는지. 무료 사용량이 넉넉할수록 점수가 높아요.',
  'korean': '— 한국어로 물어보고 한국어 결과를 받을 때 얼마나 자연스러운지 봐요.',
  'easy': '— 처음 써 보는 학생도 헤매지 않고 바로 쓸 수 있는지 봐요.',
}
def info_page(path, title, desc, body):
    return head(title, desc, path) + f"""
<body data-page="info">
<div class="wrap">
  <div class="dtop"><a class="back" href="/">◀ 도감으로</a></div>
  <article class="card px doc">{body}</article>
  {FOOT}
</div>
<script src="/assets/bit.js"></script>
<script>fillBits();</script>
</body>
</html>
"""
about = f"""
    <div class="doc-hero"><span class="bit" data-bit="wave" data-size="92" data-still="3"></span>
      <div><p class="crumb" style="color:var(--sub)">ABOUT</p><h1>AI 도감 소개</h1></div></div>
    <h2>어떤 곳인가요?</h2>
    <p>AI 도감은 챗봇, 그림, 영상, 음악, 발표자료 같은 분야별로 AI를 모아 두고, 한눈에 비교해서 나에게 맞는 걸 고를 수 있게 만든 사이트예요.</p>
    <h2>왜 만들었나요?</h2>
    <p>요즘은 학교에서도 AI를 적극적으로 써 보라고 권해요. 그런데 막상 쓰려고 하면 AI 종류가 너무 많아서 무엇부터 써야 할지 막막했어요. 게다가 글쓰기, 그림, 발표자료, 코딩처럼 하는 일이 다양한데, AI 하나로 모든 작업을 전문적으로 해내기는 어렵더라고요.</p>
    <p>그래서 하고 싶은 일에 맞춰 AI를 입맛대로 찾아 주는 곳이 필요하다고 생각했고, 그게 AI 도감의 시작이에요.</p>
    <h2>누가 만드나요?</h2>
    <p>AI를 직접 써 보는 고등학생이 만들고 운영해요. 학생 입장에서 실제로 필요한 기준으로 점수를 매기고, 직접 써 본 AI부터 후기를 채워 나가고 있어요. 아직 충분히 써 보지 못한 AI는 공개된 정보를 참고한 잠정 점수이고, 써 보면서 계속 고쳐요.</p>
    <h2>점수는 어떻게 매기나요?</h2>
    <p>AI마다 아래 네 가지를 5점 만점으로 채점하고, 총점은 네 점수의 평균이에요. 홈 화면의 <b>기준 바꾸기</b>로 나에게 중요한 기준의 비중을 높이면 순위가 바뀌어요.</p>
    <ul>{''.join(f'<li><b>{e(c["label"])}</b> {e(CRIT_DESC.get(c["key"], ""))}</li>' for c in CRIT)}</ul>
    <h2>알아 두면 좋은 점</h2>
    <ul>
      <li>AI 서비스의 가격과 기능은 자주 바뀌어요. 결제하기 전에는 꼭 공식 사이트에서 확인해 주세요.</li>
      <li>점수는 운영자의 경험과 판단이 담긴 의견이라, 같은 AI라도 쓰는 목적에 따라 느낌이 다를 수 있어요.</li>
      <li>지금은 어떤 회사에서도 돈이나 협찬을 받지 않아요. 나중에 광고나 제휴가 생기면 이 페이지에 알릴게요.</li>
    </ul>
    <h2>마스코트 비트</h2>
    <p>머리 위 별로 AI 점수를 콕콕 매기는 AI 도감지기, <b>비트</b>예요. 도감에서 써 본 AI를 다 모으면 비트가 깨어난대요.</p>
    <h2 id="contact">문의</h2>
    <p>링크가 깨졌거나, 추가했으면 하는 AI가 있거나, 제안하고 싶은 게 있으면 편하게 메일 주세요.</p>
    <p><a class="act go mail" href="mailto:{EMAIL}">{EMAIL}</a></p>
    <p class="updated">마지막 업데이트: {TODAY}</p>
"""
privacy = f"""
    <h1>개인정보 처리방침</h1>
    <p class="updated">시행일: 2026년 10월 10일</p>
    <p>AI 도감(aidogam.kr, 이하 "사이트")은 방문자의 개인정보를 소중하게 생각해요. 사이트가 어떤 정보를 어떻게 다루는지 알려 드려요.</p>
    <h2>1. 직접 받는 개인정보</h2>
    <p>사이트는 회원가입이 없고, 이름이나 연락처 같은 개인정보를 입력받지 않아요.</p>
    <h2>2. 방문 통계 (구글 애널리틱스)</h2>
    <p>사이트를 더 좋게 만들기 위해 Google LLC의 <b>구글 애널리틱스</b>를 사용해요. 이 과정에서 쿠키를 통해 다음 정보가 자동으로 수집될 수 있어요.</p>
    <ul>
      <li>방문한 페이지와 방문 시간</li>
      <li>기기 종류, 운영체제, 브라우저</li>
      <li>대략적인 지역(국가·도시 수준)과 사이트에 들어온 경로</li>
    </ul>
    <p>이 정보는 누가 방문했는지 알아내는 데 쓰지 않고, 전체 방문 통계를 보는 데만 써요. 구글 애널리틱스의 데이터 보존 설정에 따라 일정 기간(최대 14개월)이 지나면 자동으로 삭제돼요. 구글이 정보를 처리하는 방식은 <a href="https://policies.google.com/privacy" target="_blank" rel="noopener">구글 개인정보처리방침</a>에서 볼 수 있어요.</p>
    <h2>3. 내 기기에만 저장되는 정보</h2>
    <p>찜한 AI, 써봤어요 기록, 내 채점 기준, 마지막으로 본 탭은 <b>방문자 브라우저 안에만</b> 저장돼요. 운영자나 다른 곳으로 전송되지 않고, 브라우저의 사이트 데이터를 지우면 함께 사라져요.</p>
    <h2>4. 외부 서비스</h2>
    <p>글꼴을 보여 주기 위해 Google Fonts를 불러오며, 이때 방문자의 접속 정보(IP 주소 등)가 구글에 전달될 수 있어요. 사이트는 GitHub Pages에서 운영돼요.</p>
    <h2>5. 수집을 원하지 않을 때</h2>
    <ul>
      <li>브라우저 설정에서 쿠키를 차단할 수 있어요.</li>
      <li>구글이 제공하는 <a href="https://tools.google.com/dlpage/gaoptout" target="_blank" rel="noopener">애널리틱스 차단 부가기능</a>을 설치할 수 있어요.</li>
    </ul>
    <p>쿠키를 차단해도 사이트는 그대로 이용할 수 있어요.</p>
    <h2>6. 문의 메일</h2>
    <p>문의 메일을 보내면 보낸 사람의 이메일 주소와 내용은 답장을 위해서만 쓰고, 다른 곳에 제공하지 않아요.</p>
    <h2>7. 처리방침이 바뀔 때</h2>
    <p>내용이 바뀌면 이 페이지에 시행일과 함께 알려 드려요. 나중에 광고를 달게 되면 광고 쿠키에 관한 내용을 추가할 예정이에요.</p>
    <h2>8. 문의처</h2>
    <p>개인정보에 관한 문의: <a href="mailto:{EMAIL}">{EMAIL}</a></p>
"""
for path, title, desc, body in [
    ('/about/', 'AI 도감 소개 · 채점 기준 | AI 도감', '학생이 직접 써 보고 점수를 매기는 AI 도감 소개. 결과물 품질, 무료로 쓸 만함, 한국어, 쉬운 정도 네 가지 채점 기준과 문의 방법을 알려 드려요.', about),
    ('/privacy/', '개인정보 처리방침 | AI 도감', 'AI 도감이 방문 통계(구글 애널리틱스)와 쿠키를 어떻게 다루는지 알려 드려요.', privacy),
]:
    os.makedirs(OUT + path, exist_ok=True)
    open(OUT + path + 'index.html', 'w', encoding='utf-8').write(info_page(path, title, desc, body))

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
urls = ['/', '/about/', '/privacy/'] + [f"/ai/{t['id']}/" for t in TOOLS]
sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + \
     ''.join(f'  <url><loc>{SITE}{u}</loc><lastmod>{TODAY}</lastmod></url>\n' for u in urls) + '</urlset>\n'
open(f'{OUT}/sitemap.xml', 'w', encoding='utf-8').write(sm)
open(f'{OUT}/robots.txt', 'w', encoding='utf-8').write(f"User-agent: *\nAllow: /\nDisallow: /tools/\n\nSitemap: {SITE}/sitemap.xml\n")
print('pages', len(TOOLS)+1)
