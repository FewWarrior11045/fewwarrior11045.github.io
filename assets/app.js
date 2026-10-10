/* AI 도감 동작 코드 — 모든 페이지가 같이 씀 */
const $ = id => document.getElementById(id);
const esc = s => String(s ?? "").replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
const store = {
  get(k, d){ try { const v = localStorage.getItem("dogam_" + k); return v ? JSON.parse(v) : d; } catch { return d; } },
  set(k, v){ try { localStorage.setItem("dogam_" + k, JSON.stringify(v)); } catch {} }
};
const TYPE_COLORS = {
  chat:["#8DB4F5","#3E6DC4"], image:["#F4A3C4","#C04E80"], video:["#F5AE7E","#BC6229"],
  audio:["#7FD6CB","#2D8B7F"], music:["#BFA4F0","#7150BC"], code:["#9ED69B","#418F3E"],
  slide:["#F5D97A","#B38B14"], study:["#E9BE8C","#9E6A2E"], trans:["#8FCFF0","#2F80B0"]
};
const catLabel = id => (CATEGORIES.find(c => c.id === id) || {}).label || "";
const dexNo = t => String(TOOLS.indexOf(t) + 1).padStart(3, "0");
const aiUrl = t => `/ai/${t.id}/`;
const DEFAULT_W = 2;
const weights = Object.assign(Object.fromEntries(CRITERIA.map(c => [c.key, DEFAULT_W])), store.get("weights", {}));
const seen = new Set(store.get("seen", []));
const favs = new Set(store.get("favs", []));

function total(t){
  let s = 0, w = 0;
  for (const c of CRITERIA){ s += (t.s[c.key] || 0) * weights[c.key]; w += weights[c.key]; }
  return w ? s / w : 0;
}
function ranked(cat){ return TOOLS.filter(t => t.cat === cat).map(t => ({t, v: total(t)})).sort((a, b) => b.v - a.v); }

/* 이름으로 정해지는 픽셀 캐릭터 (매번 같은 모양) */
function sprite(t, size, sil){
  let h = 2166136261;
  for (const ch of t.id) { h ^= ch.charCodeAt(0); h = Math.imul(h, 16777619); }
  const rnd = () => { h ^= h << 13; h ^= h >>> 17; h ^= h << 5; return ((h >>> 0) % 1000) / 1000; };
  const W = 8, H = 8, g = [];
  for (let y = 0; y < H; y++){
    g[y] = [];
    for (let x = 0; x < W / 2; x++){
      const core = y >= 2 && y <= 5 && x >= 2;
      const edge = (y === 0 || y === H - 1) ? .25 : x === 0 ? .3 : .6;
      g[y][x] = core || rnd() < edge ? 1 : 0;
    }
    for (let x = W / 2; x < W; x++) g[y][x] = g[y][W - 1 - x];
  }
  const [body, shade] = TYPE_COLORS[t.cat] || ["#ccc", "#888"];
  const cells = [];
  const filled = (x, y) => y >= 0 && y < H && x >= 0 && x < W && g[y][x];
  for (let y = -1; y <= H; y++) for (let x = -1; x <= W; x++){
    if (filled(x, y)) continue;
    if (filled(x+1,y) || filled(x-1,y) || filled(x,y+1) || filled(x,y-1)) cells.push(`<rect x="${x+1}" y="${y+1}" width="1" height="1" fill="#1E2A1B"/>`);
  }
  const mouth = rnd() < .6;
  for (let y = 0; y < H; y++) for (let x = 0; x < W; x++){
    if (!g[y][x]) continue;
    let c = y >= 6 ? shade : body;
    if (y === 3 && (x === 2 || x === 5)) c = "#1E2A1B";
    if (y === 2 && (x === 2 || x === 5)) c = "#FFFFFF";
    if (mouth && y === 5 && (x === 3 || x === 4)) c = shade;
    if (sil) c = "#8C9A84";
    cells.push(`<rect x="${x+1}" y="${y+1}" width="1" height="1" fill="${c}"/>`);
  }
  return `<svg class="sprite" width="${size}" height="${size}" viewBox="0 0 10 10" shape-rendering="crispEdges" aria-hidden="true">${cells.join("")}</svg>`;
}
/* 미리 만들어 둔 페이지 안의 캐릭터 자리(.sp)를 채움 */
function fillSprites(root){
  (root || document).querySelectorAll(".sp[data-id]").forEach(el => {
    const t = TOOLS.find(x => x.id === el.dataset.id);
    if (t) el.outerHTML = sprite(t, +el.dataset.size || 44, el.dataset.sil === "1");
  });
}

/* 픽셀 하트: filled면 꽉 찬 하트, 아니면 빈 하트 */
function heart(size, color, filled){
  const full = [".XX.XX.","XXXXXXX","XXXXXXX",".XXXXX.","..XXX..","...X..."];
  const line = [".XX.XX.","X..X..X","X.....X",".X...X.","..X.X..","...X..."];
  const rows = filled ? full : line, r = [];
  rows.forEach((row, y) => [...row].forEach((ch, x) => { if (ch === "X") r.push(`<rect x="${x}" y="${y}" width="1" height="1"/>`); }));
  return `<svg class="pxheart" width="${size}" height="${Math.round(size * 6 / 7)}" viewBox="0 0 7 6" fill="${color}" shape-rendering="crispEdges" aria-hidden="true">${r.join("")}</svg>`;
}
const favLabel = on => on ? `${heart(14, "#fff", true)}찜했어요` : `${heart(14, "#F04452", false)}찜하기`;

function toast(msg){
  const el = $("toast"); if (!el) return;
  el.textContent = msg; el.classList.add("show");
  clearTimeout(toast.t); toast.t = setTimeout(() => el.classList.remove("show"), 1600);
}

/* 공유: 휴대폰은 공유 창, 안 되면 링크 복사 */
async function shareLink(url, title, text){
  if (navigator.share){
    try { await navigator.share({title, text, url}); return; }
    catch (e) { if (e && e.name === "AbortError") return; }
  }
  try { await navigator.clipboard.writeText(url); toast("링크를 복사했어요"); return; } catch {}
  try {
    const ta = document.createElement("textarea"); ta.value = url; ta.setAttribute("readonly", "");
    ta.style.position = "fixed"; ta.style.opacity = "0"; document.body.appendChild(ta); ta.select();
    const ok = document.execCommand("copy"); ta.remove();
    toast(ok ? "링크를 복사했어요" : "주소창의 링크를 복사해 주세요");
  } catch { toast("주소창의 링크를 복사해 주세요"); }
}

/* 목록 한 줄 (진짜 링크라서 검색엔진도 따라갈 수 있음) */
function entry(t, v, rank, showChip){
  const tc = TYPE_COLORS[t.cat][0];
  const fav = favs.has(t.id) ? `<span class="heart" role="img" aria-label="찜함">${heart(16, "#F04452", true)}</span>` : "";
  return `<li><a class="entry" href="${aiUrl(t)}">
    <span class="rank ${rank === 1 ? "first" : ""}">${rank ? rank : ""}</span>
    ${sprite(t, 44)}
    <span style="min-width:0"><span class="nm">${esc(t.name)}${fav}</span>
      <span class="meta">${showChip ? `<span class="chip" style="--tc:${tc}">${esc(catLabel(t.cat))}</span>` : ""}${seen.has(t.id) ? '<span class="seen">써봄</span>' : ""}<span class="ds">${esc(t.desc)}</span></span></span>
    <span class="score">${v.toFixed(1)}</span></a></li>`;
}

/* ================= 홈 (목록 · 내 도감 · 퀴즈) ================= */
function initHome(){
  let current = store.get("type", "chat");
  let query = "";

  function renderMeter(){
    $("cnt").textContent = `${seen.size}/${TOOLS.length}`;
    const on = Math.round(seen.size / TOOLS.length * 12);
    $("bar").innerHTML = Array.from({length:12}, (_, i) => `<i class="${i < on ? "on" : ""}"></i>`).join("");
  }
  function renderTypes(){
    const all = [{id:"fav", label:`찜 ${favs.size}`}, {id:"all", label:"전체"}, ...CATEGORIES];
    const tcOf = id => id === "all" ? "var(--lcd)" : id === "fav" ? "#F7A1AC" : TYPE_COLORS[id][0];
    $("types").innerHTML = all.map(c => `<button class="type" data-c="${c.id}" aria-pressed="${!query && c.id === current}"
      style="--tc:${tcOf(c.id)}">${c.id === "fav" ? heart(14, "#F04452", true) : ""}${esc(c.label)}</button>`).join("");
    $("types").querySelectorAll(".type").forEach(b => b.onclick = () => {
      current = b.dataset.c; store.set("type", current);
      query = ""; $("q").value = ""; renderTypes(); renderList();
    });
  }
  function renderList(){
    const q = query.trim().toLowerCase();
    let rows;
    if (q){
      $("title").textContent = `"${query.trim()}" 검색 결과`;
      rows = TOOLS.filter(t => [t.name, t.desc, catLabel(t.cat), t.who, ...(t.pros || [])].join(" ").toLowerCase().includes(q))
        .map(t => ({t, v: total(t)})).sort((a, b) => b.v - a.v).map(r => entry(r.t, r.v, null, true));
    } else if (current === "fav"){
      $("title").textContent = "찜한 AI";
      rows = TOOLS.filter(t => favs.has(t.id)).map(t => ({t, v: total(t)})).sort((a, b) => b.v - a.v).map(r => entry(r.t, r.v, null, true));
    } else if (current === "all"){
      $("title").textContent = "전체 도감";
      rows = TOOLS.map(t => entry(t, total(t), null, true));
    } else {
      if (!CATEGORIES.some(c => c.id === current)) current = "chat";
      $("title").textContent = `${catLabel(current)} 타입 순위`;
      rows = ranked(current).map((r, i) => entry(r.t, r.v, i + 1));
    }
    const emptyMsg = q ? "찾는 AI가 없어요. 다른 단어로 검색해 보세요." : current === "fav" ? "아직 찜한 AI가 없어요.<br>AI 페이지에서 찜하기를 눌러 보세요." : "이 타입에 아직 AI가 없어요.";
    $("list").innerHTML = rows.length ? rows.join("") : `<li class="empty">${emptyMsg}</li>`;
  }

  /* 내 도감 */
  function renderDex(){
    const bar = TOOLS.map((t, i) => `<i class="${i < seen.size ? "on" : ""}"></i>`).join("");
    const secs = CATEGORIES.map(c => {
      const items = TOOLS.filter(t => t.cat === c.id);
      const got = items.filter(t => seen.has(t.id)).length;
      return `<section class="dexsec"><h2 style="--tc:${TYPE_COLORS[c.id][0]}"><i></i>${esc(c.label)}<span class="n">${got}/${items.length}</span></h2>
        <div class="grid">${items.map(t => {
          const on = seen.has(t.id);
          return `<a class="cell ${on ? "" : "locked"}" href="${aiUrl(t)}" aria-label="${esc(t.name)}${on ? ", 써봄" : ", 아직 안 써봄"}">
            <span class="no">No.${dexNo(t)}</span>${sprite(t, 52, !on)}<span class="nm">${on ? esc(t.name) : "???"}</span></a>`;
        }).join("")}</div></section>`;
    }).join("");
    $("dex").innerHTML = `
      <div class="dtop"><button class="back" id="dexBack">◀ 목록으로</button></div>
      <div class="dexhead px">
        <h1>내 도감</h1>
        <div class="count"><span>써본 AI</span><b>${seen.size} / ${TOOLS.length}</b></div>
        <div class="bigbar" aria-hidden="true">${bar}</div>
      </div>${secs}`;
    $("dexBack").onclick = () => { location.hash = "#/"; };
  }

  /* 퀴즈 */
  let qStep = 0, qAns = [];
  function quizResult(){
    let cat = "chat"; const w = { quality:2, free:1, korean:1, easy:1 };
    qAns.forEach(a => { if (a.set.cat) cat = a.set.cat; Object.assign(w, a.set.w || {}); });
    const score = t => { let s = 0, sw = 0; for (const k in w){ s += (t.s[k] || 0) * w[k]; sw += w[k]; } return sw ? s / sw : 0; };
    return { list: TOOLS.filter(t => t.cat === cat).map(t => ({t, fit: score(t)})).sort((a, b) => b.fit - a.fit), w };
  }
  function renderQuiz(){
    const el = $("quiz");
    const top = `<div class="dtop"><button class="back" id="qBack">◀ 목록으로</button></div>`;
    if (qStep < QUIZ.length){
      const Q = QUIZ[qStep];
      el.innerHTML = `${top}<div class="qbox px">
        <div class="qtop"><span class="qstep">Q${qStep + 1}/${QUIZ.length}</span>
          <span class="qprog" aria-hidden="true">${QUIZ.map((_, i) => `<i class="${i <= qStep ? "on" : ""}"></i>`).join("")}</span></div>
        <h1 class="qtitle">${esc(Q.q)}</h1>
        <div class="qopts ${Q.grid ? "two" : ""}">${Q.opts.map((o, i) =>
          `<button class="qopt" data-i="${i}"><span class="em" aria-hidden="true">${o.em}</span>${esc(o.t)}</button>`).join("")}</div>
        ${qStep > 0 ? `<button class="qprev" id="qPrev">◀ 이전 질문</button>` : ""}
      </div>`;
      el.querySelectorAll(".qopt").forEach(b => b.onclick = () => { qAns[qStep] = Q.opts[+b.dataset.i]; qStep++; renderQuiz(); window.scrollTo(0, 0); });
      if ($("qPrev")) $("qPrev").onclick = () => { qStep--; renderQuiz(); };
      const first = el.querySelector(".qopt"); if (first) first.focus({ preventScroll:true });
    } else {
      const { list, w } = quizResult();
      const best = list[0] && list[0].t;
      if (!best){ el.innerHTML = `${top}<div class="qbox px"><p>이 분야에 아직 AI가 없어요.</p></div>`; }
      else {
        const reasons = Object.keys(w).filter(k => w[k] >= 1.5 && (best.s[k] || 0) >= 4).sort((a, b) => w[b] - w[a]).map(k => WHY[k]);
        if (!reasons.length) reasons.push("고른 조건에서 가장 점수가 높아요");
        if (best.who) reasons.push(`${best.who}에게 잘 맞아요`);
        el.innerHTML = `${top}
        <article class="card px found">
          <div class="stage pop" style="--tc:${TYPE_COLORS[best.cat][0]}"><span class="dexno">No.${dexNo(best)}</span>${sprite(best, 140)}</div>
          <p class="hello">찾았다!</p>
          <h1>${esc(best.name)}</h1><p>${esc(best.desc)}</p>
          <div class="talk px" style="text-align:left"><h3>추천하는 이유</h3><ul>${reasons.map(r => `<li>${esc(r)}</li>`).join("")}</ul></div>
          <div class="found-btns">
            <a class="act go" href="${aiUrl(best)}">${esc(best.name)} 자세히 보기</a>
            <div class="two"><button class="act plain" id="qShare">결과 공유</button><button class="act plain" id="qAgain">다시 하기</button></div>
          </div>
        </article>
        ${list.length > 1 ? `<div class="board px subboard"><h2>이것도 잘 맞아요</h2><ul class="list">${list.slice(1, 3).map(r => entry(r.t, total(r.t), null, false)).join("")}</ul></div>` : ""}`;
        $("qAgain").onclick = () => { qStep = 0; qAns = []; renderQuiz(); window.scrollTo(0, 0); };
        $("qShare").onclick = () => shareLink(location.origin + "/#/quiz", "AI 추천 퀴즈", `AI 추천 퀴즈 결과, 나에게 딱 맞는 AI는 ${best.name}! 너도 해봐`);
      }
    }
    $("qBack").onclick = () => { location.hash = "#/"; };
  }

  /* 기준 창 */
  function renderW(){
    $("wrows").innerHTML = CRITERIA.map(c => `
      <div class="wrow"><span>${esc(c.label)}</span>
        <button class="step" data-k="${c.key}" data-d="-1" aria-label="${esc(c.label)} 낮추기" ${weights[c.key] <= 0 ? "disabled" : ""}>-</button>
        <output>x${weights[c.key]}</output>
        <button class="step" data-k="${c.key}" data-d="1" aria-label="${esc(c.label)} 높이기" ${weights[c.key] >= 3 ? "disabled" : ""}>+</button></div>`).join("");
    $("wrows").querySelectorAll(".step").forEach(b => b.onclick = () => {
      const k = b.dataset.k; weights[k] = Math.min(3, Math.max(0, weights[k] + +b.dataset.d));
      store.set("weights", weights); renderW(); renderList();
      const again = $("wrows").querySelector(`.step[data-k="${k}"][data-d="${b.dataset.d}"]`);
      if (again && !again.disabled) again.focus();
    });
  }
  function modal(open){
    $("modal").classList.toggle("open", open); $("mbg").classList.toggle("open", open);
    if (open) $("modal").querySelector("button").focus(); else $("openW").focus();
  }
  $("openW").onclick = () => { renderW(); modal(true); };
  $("closeW").onclick = $("mbg").onclick = () => modal(false);
  $("resetW").onclick = () => { CRITERIA.forEach(c => weights[c.key] = DEFAULT_W); store.set("weights", weights); renderW(); renderList(); toast("기본 기준으로 돌아왔어요"); };
  document.addEventListener("keydown", e => { if (e.key === "Escape" && $("modal").classList.contains("open")) modal(false); });

  $("q").oninput = () => { query = $("q").value; renderTypes(); renderList(); };
  $("openDex").onclick = () => { location.hash = "#/dex"; };
  $("openQuiz").onclick = () => { qStep = 0; qAns = []; location.hash = "#/quiz"; };

  function route(){
    const h = location.hash;
    const old = h.match(/^#\/ai\/([\w-]+)/);           // 예전 주소(#/ai/chatgpt)로 들어오면 새 주소로 이동
    if (old && TOOLS.some(t => t.id === old[1])) { location.replace(`/ai/${old[1]}/`); return; }
    const dex = h === "#/dex", quiz = h === "#/quiz";
    $("home").hidden = dex || quiz; $("dex").hidden = !dex; $("quiz").hidden = !quiz;
    if (dex){ renderDex(); document.title = "내 도감 | AI 도감"; window.scrollTo(0, 0); }
    else if (quiz){ renderQuiz(); document.title = "AI 추천 퀴즈 | AI 도감"; window.scrollTo(0, 0); }
    else { document.title = HOME_TITLE; renderMeter(); renderTypes(); renderList(); }
  }
  const HOME_TITLE = document.title;
  window.addEventListener("hashchange", route);
  route();
}

/* ================= AI 상세 페이지 ================= */
function initDetail(id){
  const t = TOOLS.find(x => x.id === id);
  if (!t) return;
  fillSprites();

  // 내 채점 기준에 맞춰 점수·순위 다시 계산
  const r = ranked(t.cat), rank = r.findIndex(x => x.t === t) + 1;
  $("rankbadge").textContent = `${catLabel(t.cat)} ${rank}위`;
  $("bigscore").firstChild.nodeValue = total(t).toFixed(1);

  // 같은 타입 다른 AI
  $("others").innerHTML = r.map((x, i) => x.t === t ? "" : entry(x.t, x.v, i + 1)).join("");

  // 뒤로 가기: 사이트 안에서 왔으면 그 화면으로, 아니면 홈으로
  $("back").onclick = e => {
    try { if (document.referrer && new URL(document.referrer).origin === location.origin){ e.preventDefault(); history.back(); } } catch {}
  };

  const fav = $("fav");
  fav.setAttribute("aria-pressed", favs.has(t.id)); fav.innerHTML = favLabel(favs.has(t.id));
  fav.onclick = () => {
    const on = !favs.has(t.id);
    on ? favs.add(t.id) : favs.delete(t.id);
    store.set("favs", [...favs]);
    fav.setAttribute("aria-pressed", on); fav.innerHTML = favLabel(on);
    toast(on ? "찜 목록에 담았어요" : "찜을 취소했어요");
  };

  const col = $("collect");
  const setCol = on => { col.setAttribute("aria-pressed", on); col.textContent = on ? "써봤어요 ✓" : "써봤어요"; };
  setCol(seen.has(t.id));
  col.onclick = () => {
    const on = !seen.has(t.id);
    on ? seen.add(t.id) : seen.delete(t.id);
    store.set("seen", [...seen]); setCol(on);
    toast(on ? `도감에 기록했어요: ${t.name}` : "기록을 지웠어요");
  };

  $("share").onclick = () => shareLink(location.origin + aiUrl(t), `${t.name} | AI 도감`, `${t.name}: ${t.desc} (AI 도감)`);
}

/* 시작 */
(function(){
  const page = document.body.dataset.page;
  if (page === "home") initHome();
  else if (page === "ai") initDetail(document.body.dataset.id);
})();
