/* The captain's bridge for a touch screen held sideways. Everything it shows comes from
 * Game.view(), which holds no hidden value, so nothing here can leak one. */
(function () {
  'use strict';
  const SAVE_KEY = 'depths-within:save:v1';
  const app = document.getElementById('app');
  const state = { game: null, sheet: null, pick: null, sound: false, shownAt: 0, started: false, tabL: 'ledger', tabC: 'chart' };

  const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  const pct = (x) => Math.round(x * 100);
  const guard = (fn) => { try { return fn(); } catch (e) { return undefined; } };

  // ------------------------------------------------------------------ storage (per viewer, optional)
  const store = {
    read() { return guard(() => JSON.parse(localStorage.getItem(SAVE_KEY) || 'null')); },
    write(g) { guard(() => localStorage.setItem(SAVE_KEY, JSON.stringify(g.serialize()))); },
    clear() { guard(() => localStorage.removeItem(SAVE_KEY)); },
  };

  // ------------------------------------------------------------------ sound: the sonar is the horror
  const Sound = {
    ctx: null, drone: null,
    start() {
      if (this.ctx) { if (this.ctx.state === 'suspended') this.ctx.resume(); this.fade(0.035, 1.5); return; }
      const AC = window.AudioContext || window.webkitAudioContext;
      if (!AC) return;
      this.ctx = new AC();
      const lp = this.ctx.createBiquadFilter(); lp.type = 'lowpass'; lp.frequency.value = 220;
      const gain = this.ctx.createGain(); gain.gain.value = 0;
      [47, 49.5, 71].forEach((f, i) => {
        const o = this.ctx.createOscillator(); o.type = i === 2 ? 'triangle' : 'sine'; o.frequency.value = f;
        const g = this.ctx.createGain(); g.gain.value = i === 2 ? 0.25 : 1; o.connect(g); g.connect(lp); o.start();
      });
      lp.connect(gain); gain.connect(this.ctx.destination);
      this.drone = gain;
      this.fade(0.035, 2);
    },
    fade(v, s) { if (this.drone) { const t = this.ctx.currentTime; this.drone.gain.cancelScheduledValues(t); this.drone.gain.linearRampToValueAtTime(v, t + s); } },
    ping() {
      if (!this.ctx || !state.sound) return;
      const t = this.ctx.currentTime, o = this.ctx.createOscillator(), g = this.ctx.createGain();
      o.type = 'sine'; o.frequency.setValueAtTime(1180, t);
      g.gain.setValueAtTime(0.0001, t); g.gain.exponentialRampToValueAtTime(0.06, t + 0.02); g.gain.exponentialRampToValueAtTime(0.0001, t + 1.6);
      o.connect(g); g.connect(this.ctx.destination); o.start(t); o.stop(t + 1.7);
    },
    hush() { this.fade(0, 3); },          // the ending: the hydrophones go quiet
    mute() { this.fade(0, 0.3); },
  };

  // ------------------------------------------------------------------ small helpers
  function vibrate(ms) { guard(() => navigator.vibrate && navigator.vibrate(ms)); }
  let wake = null;
  function keepAwake() { guard(() => navigator.wakeLock && navigator.wakeLock.request('screen').then((l) => { wake = l; }).catch(() => {})); }

  function newSeed() {
    const a = new Uint32Array(1);
    guard(() => crypto.getRandomValues(a));
    return (a[0] || Math.floor(Math.random() * 2147483647)) % 2147483647;
  }

  // ------------------------------------------------------------------ actions
  function begin(game) {
    state.game = game; state.sheet = null; state.pick = null; state.started = true;
    store.write(game); keepAwake();
    if (state.sound) Sound.start();
    render();
  }
  function act(input) {
    const g = state.game;
    const hadPending = !!g.w.pending;
    g.do(input);
    store.write(g);
    const v = g.view();
    if (!hadPending && v.pending) { state.shownAt = Date.now(); vibrate(40); Sound.ping(); }
    if (v.over) { Sound.hush(); vibrate([60, 80, 60]); }
    state.sheet = null; state.pick = null;
    render();
  }
  function setSound(on) {
    state.sound = on;
    if (on) Sound.start(); else Sound.mute();
    render();
  }

  // ------------------------------------------------------------------ views
  function ledgerRow(label, value, extra, higherIsBetter) {
    const level = value <= 0.2 ? 'crit' : value <= 0.4 ? 'low' : '';
    const flag = level === 'crit' ? ' <span class="flag">critical</span>' : level === 'low' ? ' <span class="flag">low</span>' : '';
    return `<div class="r ${level}"><span class="k">${label}</span><span class="bar"><i style="width:${pct(value)}%"></i></span>` +
      `<span class="v">${pct(value)}%</span>${extra ? `<span class="sub">${extra}${flag}</span>` : (flag ? `<span class="sub">${flag}</span>` : '')}</div>`;
  }
  function ledgerView(v) {
    const L = v.ledger;
    return `<div class="led">
      ${ledgerRow('Hull', L.hull)}
      ${ledgerRow('Food', L.food, `−${L.food_day.toFixed(0)}%/day`)}
      ${ledgerRow('Water', L.water, `−${L.water_day.toFixed(0)}%/day`)}
      ${ledgerRow('Diesel', L.fuel)}
      ${ledgerRow('Air', L.scrubber, 'absorbent left')}
      <div class="air ${L.air}"><span>CO₂ <span class="num">${(L.co2 * 100).toFixed(1)}%</span></span><span>${L.air}</span></div>
      <div class="air"><span>Rations <span class="num">${pct(L.rations)}%</span></span><span>Men aboard <span class="num">${L.men}</span></span></div>
    </div>`;
  }
  // ------------------------------------------------------------------ the chart, the instruments, the hull
  function chartSvg(v) {
    const N = v.nav;
    let g = '';
    for (let i = 0; i <= 11; i++) g += `<line class="gl" x1="${i * 10}" y1="0" x2="${i * 10}" y2="80"/>`;
    for (let j = 0; j <= 8; j++) g += `<line class="gl" x1="0" y1="${j * 10}" x2="110" y2="${j * 10}"/>`;
    for (let i = 0; i < 11; i++) g += `<text class="gt" x="${i * 10 + 5}" y="3.4" text-anchor="middle">${'ABCDEFGHIJK'[i]}</text>`;
    for (let j = 0; j < 8; j++) g += `<text class="gt" x="1.2" y="${j * 10 + 6.5}">${j + 1}</text>`;
    let t = '';
    v.tracks.forEach((tr) => {
      if (!tr.points.length) return;
      const d = tr.points.map((p) => `${p[0]},${p[1]}`).join(' ');
      t += `<polyline class="trk ${tr.state}" points="${d}"/>`;
      tr.points.forEach((p, i) => {
        if (i === 0) return;
        const reached = i <= tr.reached, next = tr.state === 'current' && i === tr.reached + 1;
        t += `<circle class="wp ${reached ? 'hit' : next ? 'next' : ''}" cx="${p[0]}" cy="${p[1]}" r="${next ? 2.1 : 1.4}"/>`;
        if (next || (tr.state === 'current' && reached && i === tr.reached)) t += `<text class="wl" x="${p[0]}" y="${p[1] + (p[1] > 66 ? -3.4 : 5)}" text-anchor="${p[0] > 85 ? 'end' : 'middle'}">${esc(p[2])}</text>`;
      });
    });
    const boat = `<g class="boat ${v.surfaced ? 'up' : ''}" transform="translate(${N.x} ${N.y}) rotate(${N.heading})"><circle class="halo" r="4.2"/><path d="M0 -4.6 L2.4 3.4 L0 2.2 L-2.4 3.4 Z"/></g>`;
    return `<svg class="chart" viewBox="0 0 110 80" role="img" aria-label="Chart: ${esc(N.grid)}, heading ${N.heading}">
      <rect class="sea" width="110" height="80"/>${g}
      <path class="land" d="M90 0 L110 0 L110 21 L101 19 L95 9 Z"/><text class="wl" x="108" y="26" text-anchor="end">Base</text>${t}${boat}</svg>`;
  }
  function gauge(k, val, unit, extra) {
    return `<div class="gg"><span class="gk">${k}</span><span class="gv">${val}<small>${unit || ''}</small></span>${extra || ''}</div>`;
  }
  function chartView(v) {
    const N = v.nav;
    const nxt = N.next ? `${esc(N.next)} · ${N.range_nm} nm${N.eta_h ? ` · ${N.eta_h} h` : ''}` : 'On station';
    return `${chartSvg(v)}<div class="gauges">
      ${gauge('Heading', String(N.heading).padStart(3, '0'), '°')}${gauge('Speed', N.speed.toFixed(1), ' kn')}
      ${gauge('Depth', N.depth, ' m')}${gauge('Grid', N.grid, '')}
      ${gauge('Signature', pct(N.noise), '%', `<span class="bar sm"><i style="width:${pct(N.noise)}%"></i></span>`)}
      <div class="gg wide"><span class="gk">Next</span><span class="gv sm">${nxt}</span></div></div>`;
  }
  function hullView(v) {
    const segs = v.hull.map((h, i) => {
      const x = 4 + i * 20.4;
      return `<rect class="cp ${h.state}" x="${x}" y="15" width="19.6" height="14" rx="${i === 0 || i === 4 ? 6 : 1.5}" style="opacity:${(0.35 + 0.65 * h.integrity).toFixed(2)}"/>`;
    }).join('');
    const rows = v.hull.map((h) => `<li class="${h.state}"><span class="n">${esc(h.name)}</span><span class="bar"><i style="width:${pct(h.integrity)}%"></i></span><span class="v">${pct(h.integrity)}%</span>` +
      `<span class="st">${h.state === 'flooding' ? 'taking water' : h.state}</span></li>`).join('');
    return `<svg class="hullsvg" viewBox="0 0 110 40" aria-hidden="true"><path class="tower" d="M27 15 L29 8 L37 8 L39 15 Z"/>${segs}</svg><ul class="comp">${rows}</ul>`;
  }
  const SAID = { 'says he is fine': '“fine”', 'says he is tired': '“tired”', 'says it has been hard': '“it’s been hard”', 'says nothing good': '“nothing good”' };
  function menView(v) {
    const rows = v.men.map((m) => {
      if (m.missing) return `<li class="gone"><span class="n">${esc(m.name)}<span class="role">${esc(m.role)}</span></span><span class="says">missing</span></li>`;
      const seen = m.seen.length ? `<span class="seen">${esc(m.seen.join('; '))}</span>` : '';
      return `<li class="${m.seen.length ? 'sym' : ''}"><span class="n">${esc(m.name)}<span class="role">${esc(m.role)}</span>${m.confined ? '<span class="badge">confined</span>' : ''}</span>` +
        `<span class="says">${esc(SAID[m.says] || m.says)}</span>${seen}</li>`;
    }).join('');
    const rep = v.sonar.reports.map((r) => `<p>${esc(r)}</p>`).join('') || (v.sonar.on ? '<p class="dim">The sonar room has nothing to report.</p>' : '');
    return `<ul class="men">${rows}</ul>
      <div class="sonar ${v.sonar.on ? '' : 'off'}"><b>SONAR ${v.sonar.on ? 'ON' : 'OFF'}</b>${rep}</div>`;
  }
  const tabBtn = (key, id, label, cur) => `<button class="tab ${cur === id ? 'on' : ''}" data-a="${key}:${id}" aria-pressed="${cur === id}">${label}</button>`;
  function logView(v) {
    return v.log.map((l) => {
      const m = l.match(/^(\[\d+\])\s?(.*)$/);
      const tk = m ? m[1] : '', body = m ? m[2] : l;
      const cls = /^ORDERS:/.test(body) ? 'ord' : /^>/.test(body) ? 'ch' : /^Mission /.test(body) ? 'mis' : '';
      return `<p><span class="tk">${esc(tk)}</span> <span class="${cls}">${esc(body)}</span></p>`;
    }).join('');
  }
  /** The mission's next step as the first thing to do; nothing advances unless it is ordered. */
  function stepView(v) {
    const m = v.mission;
    if (!m) return '';
    const st = m.step, o = v.orders.find((x) => x.kind === 'act');
    if (!st.of) return `<div class="step hold"><span class="k">Station</span><span class="t">Hold position. Nothing is asked of you but to stay.</span></div>`;
    const off = v.pending || v.over;
    if (!o) return `<div class="step done"><span class="k">${st.of} of ${st.of}</span><span class="t">Every step ordered. What comes now is not up to the sea.</span></div>`;
    const cls = st.working ? 'step going' : o.why ? 'step blocked' : 'step ready';
    const sub = st.working ? `Under way · ${esc(o.hint)}${o.why ? ' · ' + esc(o.why) : ''}` : o.why ? esc(o.why) : esc(o.hint);
    return `<button class="${cls}" data-a="act" ${off ? 'disabled' : ''}><span class="k">Step ${st.n + 1} of ${st.of}</span>` +
      `<span class="t">${esc(o.label.replace(/^Under way: /, ''))}</span><span class="s">${sub}</span></button>`;
  }
  function pips(m) {
    if (!m || !m.step.of) return '';
    let out = '';
    for (let i = 0; i < m.step.of; i++) out += i < m.step.n ? '●' : i === m.step.n && m.step.working ? '◐' : '○';
    return `<span class="pips" aria-label="Steps ordered: ${m.step.n} of ${m.step.of}">${out}</span>`;
  }
  function topView(v) {
    const m = v.mission;
    const cal = v.clocks.calendar ? `<small>log: day ${v.clocks.calendar.log} · chronometer: day ${v.clocks.calendar.chrono} · the cook says later</small>`
      : v.clocks.drift ? '<small>control-room clock: eleven minutes slow</small>' : '';
    return `<div class="top">
      <button class="orders-chip" data-a="sheet:briefing" aria-label="Show the orders">
        <span class="t">${m ? `${m.index}/${m.total} · ${esc(m.title)}` : 'No orders'} ${pips(m)}</span>
        <span class="p">${m ? esc(m.provenance) : ''}</span></button>
      <div class="clock">Day ${v.day} · ${String(v.hour).padStart(2, '0')}:00${cal}</div>
      <button class="icon-btn ${state.sound ? '' : 'off'}" data-a="sound" aria-pressed="${state.sound}" aria-label="${state.sound ? 'Sound on' : 'Sound off'}">♪</button>
      <button class="icon-btn" data-a="sheet:help" aria-label="How to play">?</button>
    </div>`;
  }

  function sheetBriefing(v) {
    const m = v.mission;
    return `<div class="sheet" role="dialog" aria-modal="true" aria-label="Orders"><header><h2>${m ? esc(m.title) : 'Orders'}</h2><button class="icon-btn" data-a="close" aria-label="Close">✕</button></header>
      <div class="body">${m ? `<p style="font:400 17px/1.5 var(--display)">${esc(m.briefing)}</p>
        <p class="smcaps">Received</p><p>${esc(m.provenance)}</p>
        <p class="note">Where an order comes from is never settled. You see how it reached you, not who sent it.</p>` : '<p>No orders.</p>'}</div></div>`;
  }
  function sheetHelp() {
    return `<div class="sheet" role="dialog" aria-modal="true" aria-label="How to play"><header><h2>How to read the boat</h2><button class="icon-btn" data-a="close" aria-label="Close">✕</button></header>
      <div class="body"><div class="title-card" style="max-width:none"><div class="rule">
        <span><b>The ledger is exact.</b> Hull, stores, air and diesel are what they say they are.</span>
        <span><b>The men are not.</b> Each says how he is; you can also see his symptoms. When the two disagree, believe the symptoms.</span>
        <span><b>Nothing advances while you wait.</b> The mission is carried out by ordering its steps, one at a time. Each takes hours, and the clock on the orders keeps running.</span>
        <span><b>Wait 1 h</b> advances an hour. <b>News ▶▶</b> waits until something happens (at most 12 hours).</span>
        <span><b>Decisions stop the clock.</b> Each option shows what it costs, not what it does.</span>
        <span><b>Orders are never free.</b> Most of what they cost, you learn later.</span>
        <span><b>There is no battle.</b> Nothing aboard will ever be confirmed as anything but possible.</span>
      </div></div></div></div>`;
  }
  function sheetOrders(v) {
    if (state.pick) {
      const item = v.orders.find((o) => o.id === state.pick);
      const men = (v.pickable[state.pick] || []);
      return `<div class="sheet" role="dialog" aria-modal="true" aria-label="Which man?"><header><h2>${esc(item ? item.label : 'Which man?')}</h2><button class="icon-btn" data-a="close" aria-label="Close">✕</button></header>
        <div class="body"><div class="pick">${men.map((c) => `<button class="opt" data-a="order:${esc(state.pick)}:${c.id}"><b>${esc(c.name)}</b><span>${esc(c.role)}</span></button>`).join('') || '<p class="dim">Nobody to choose.</p>'}</div></div>
        <footer><button class="btn" data-a="orders">Back</button></footer></div>`;
    }
    return `<div class="sheet" role="dialog" aria-modal="true" aria-label="Orders"><header><h2>Orders</h2><button class="icon-btn" data-a="close" aria-label="Close">✕</button></header>
      <div class="body"><div class="orders-grid">${v.orders.filter((o) => o.kind !== 'act').map((o) => `<button class="opt" data-a="${o.needsCrew ? 'pick:' : 'order:'}${o.id}"><b>${esc(o.label)}${o.needsCrew ? ' …' : ''}</b>${o.hint ? `<span>${esc(o.hint)}</span>` : ''}</button>`).join('')}</div>
        <p class="note">Orders are not free. Most of what they cost, you will learn later.</p></div></div>`;
  }
  function sheetDecision(v) {
    const d = v.pending;
    return `<div class="sheet decision" role="dialog" aria-modal="true" aria-label="Decision"><header><h2>CAPTAIN: ${esc(d.title)}</h2><span class="smcaps">the clock is stopped</span></header>
      <div class="body"><div class="grid"><div class="story">${esc(d.text)}</div>
        <div class="opts">${d.choices.map((c, i) => `<button class="opt" data-a="choose:${i}"><b>${esc(c.label)}</b>${c.cost ? `<span>${esc(c.cost)}</span>` : ''}</button>`).join('')}</div></div></div></div>`;
  }
  function sheetEnding(v) {
    const pairs = v.reports.official.map((o, i) => `<div class="row"><div class="c">${esc(o)}</div><div class="c log">${esc(v.reports.log[i])}</div></div>`).join('');
    return `<div class="sheet" role="dialog" aria-modal="true" aria-label="The end"><header><h2>The end</h2><span class="smcaps">${esc(v.ending.replace(/_/g, ' '))}</span></header>
      <div class="body"><div class="epi">${v.epilogue.map((l, i) => `<p class="${i === v.epilogue.length - 1 ? 'hush' : ''}">${esc(l)}</p>`).join('')}</div>
        <p class="smcaps" style="margin-top:14px">Two accounts of the same patrol. Nobody has been asked to reconcile them.</p>
        <div class="reports"><h3>Report of proceedings</h3><h3>Captain's log</h3>${pairs}</div></div>
      <footer><button class="btn primary" data-a="new">New patrol</button></footer></div>`;
  }
  function titleView() {
    const saved = store.read();
    const can = saved && saved.inputs && saved.inputs.length > 0;
    return `<div class="sheet" role="dialog" aria-modal="true" aria-label="Depths Within"><div class="body" style="padding:20px 14px"><div class="title-card">
      <span class="smcaps">A patrol in five orders</span>
      <h1>Depths Within</h1>
      <p>You command a submarine whose orders arrive from somewhere nobody can name. The war is real. What breaks the boat is the crew under pressure, and perhaps something else.</p>
      <div class="rule"><span><b>The ledger tells the truth.</b> The men do not always.</span><span><b>Nothing is ever confirmed.</b> Every strange thing has an ordinary explanation, and another.</span></div>
      <div class="row">
        ${can ? `<button class="btn primary" data-a="continue">Continue<small>${saved.inputs.length} moves played</small></button>` : ''}
        <button class="btn ${can ? '' : 'primary'}" data-a="new">${can ? 'New patrol' : 'Begin patrol'}<small>a new seed every time</small></button>
      </div>
      <p class="note">Hold the phone sideways. Sound is optional (♪ in the corner).</p></div></div></div>`;
  }

  // ------------------------------------------------------------------ render
  function render() {
    if (!state.game) { app.innerHTML = `<div class="veil">${titleView()}</div>`; return; }
    const v = state.game.view();
    const sheet = v.over ? sheetEnding(v) : v.pending ? sheetDecision(v)
      : state.sheet === 'briefing' ? sheetBriefing(v) : state.sheet === 'help' ? sheetHelp()
        : state.sheet === 'orders' ? sheetOrders(v) : '';
    const logEl = document.querySelector('.log-scroll');
    const stick = !logEl || logEl.scrollHeight - logEl.scrollTop - logEl.clientHeight < 60;
    app.innerHTML = `${topView(v)}
      <div class="cols">
        <section class="col" aria-label="${state.tabL === 'hull' ? 'Hull' : 'Ledger'}"><header class="tabs">${tabBtn('tabL', 'ledger', 'Ledger', state.tabL)}${tabBtn('tabL', 'hull', 'Hull', state.tabL)}</header><div class="scroll">${state.tabL === 'hull' ? hullView(v) : ledgerView(v)}</div></section>
        <section class="col" aria-label="${state.tabC === 'men' ? 'The men' : 'Chart'}"><header class="tabs">${tabBtn('tabC', 'chart', 'Chart', state.tabC)}${tabBtn('tabC', 'men', 'The men', state.tabC)}</header><div class="scroll">${state.tabC === 'men' ? menView(v) : chartView(v)}</div></section>
        <section class="col logcol" aria-label="Log"><header><span class="smcaps">Log</span><span class="smcaps">tick ${v.tick}</span></header>
          <div class="scroll log log-scroll">${logView(v)}</div>
          <div class="notice" aria-live="polite">${esc(v.notice || '')}</div>
          ${stepView(v)}
          <div class="actions">
            <button class="btn primary" data-a="orders" ${v.pending || v.over ? 'disabled' : ''}>Orders<small>${v.orders.filter((o) => o.kind !== 'act').length} more</small></button>
            <button class="btn" data-a="wait" ${v.pending || v.over ? 'disabled' : ''}>Wait 1h</button>
            <button class="btn" data-a="news" ${v.pending || v.over ? 'disabled' : ''}>News ▶▶<small class="wide">until something happens</small></button>
          </div></section>
      </div>
      ${sheet ? `<div class="veil" data-veil="1">${sheet}</div>` : ''}`;
    const sc = document.querySelector('.log-scroll');
    if (sc && stick) sc.scrollTop = sc.scrollHeight;
    const veil = document.querySelector('.veil[data-veil]');
    const first = veil && veil.querySelector('button.opt, .btn, .icon-btn');
    if (first && v.pending) first.blur();
  }

  // ------------------------------------------------------------------ input (touch and mouse)
  app.addEventListener('click', (e) => {
    const t = e.target.closest('[data-a]');
    if (!t) {
      const veil = e.target.closest('.veil[data-veil]');
      if (veil && e.target === veil && state.game && !state.game.view().pending && !state.game.over) { state.sheet = null; state.pick = null; render(); }
      return;
    }
    const a = t.getAttribute('data-a');
    const g = state.game;
    if (a === 'new') { store.clear(); begin(new Dread.Game(newSeed())); return; }
    if (a === 'continue') { const s = store.read(); if (s) begin(Dread.Game.restore(s)); return; }
    if (!g) return;
    if (a.startsWith('tabL:')) { state.tabL = a.slice(5); return render(); }
    if (a.startsWith('tabC:')) { state.tabC = a.slice(5); return render(); }
    if (a === 'act') return act('o:act');
    if (a === 'wait') return act('t');
    if (a === 'news') return act('w');
    if (a === 'orders') { state.sheet = 'orders'; state.pick = null; return render(); }
    if (a === 'close') { state.sheet = null; state.pick = null; return render(); }
    if (a === 'sound') return setSound(!state.sound);
    if (a.startsWith('sheet:')) { state.sheet = a.slice(6); return render(); }
    if (a.startsWith('pick:')) { state.pick = a.slice(5); return render(); }
    if (a.startsWith('order:')) return act(`o:${a.slice(6)}`);
    if (a.startsWith('choose:')) {
      if (Date.now() - state.shownAt < 350) return;          // a stray tap while it appears is not an answer
      return act(`c:${a.slice(7)}`);
    }
  });
  document.addEventListener('keydown', (e) => {                // a keyboard works too (desktop, tablets with one)
    if (!state.game) return;
    const v = state.game.view();
    if (v.pending && /^[1-9]$/.test(e.key) && Number(e.key) <= v.pending.choices.length) { act(`c:${Number(e.key) - 1}`); return; }
    if (v.pending || v.over) return;
    if (e.key === ' ' || e.key === 'Enter') { e.preventDefault(); act('t'); }
    else if (e.key === 'w' || e.key === 'W') act('w');
    else if (e.key === 'o' || e.key === 'O') { state.sheet = 'orders'; render(); }
    else if (e.key === 'Escape') { state.sheet = null; state.pick = null; render(); }
  });
  document.addEventListener('visibilitychange', () => { if (document.visibilityState === 'visible' && state.started) keepAwake(); });

  // test and demo hook. It also exposes the world to the console: this is a single-player game, and
  // nothing hidden is ever drawn, which is what the tests check.
  window.dreadDebug = { state, render, act, begin, Dread };
  render();
})();
