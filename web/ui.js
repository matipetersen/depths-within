/* The captain's bridge for a touch screen held sideways. Everything it shows comes from
 * Game.view(), which holds no hidden value, so nothing here can leak one. */
(function () {
  'use strict';
  const SAVE_KEY = 'depths-within:save:v1';
  const app = document.getElementById('app');
  const TUTORIAL_KEY = 'depths-within:tutorial:v1';
  const state = { advIdx: 0, game: null, sheet: null, pick: null, sound: false, shownAt: 0, started: false, tabL: 'ledger', tabC: 'chart', train: 0 };

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
    state.game = game; state.sheet = guard(() => localStorage.getItem(TUTORIAL_KEY)) ? null : 'tutorial'; state.pick = null; state.started = true; state.advIdx = 0;
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
    if (state.sheet !== 'periscope') state.sheet = null;
    state.pick = null;
    render();
  }
  function openWays(v) {
    const ways = v.orders.filter((o) => o.kind === 'act');
    if (ways.length > 1 && !(v.mission && v.mission.step.working)) { state.sheet = 'ways'; render(); return; }
    act('o:act');
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
      ${ledgerRow('Battery', L.battery, v.helm.snorkel ? 'on the snorkel' : v.surfaced ? 'charging' : '')}
      ${ledgerRow('Spares', L.spares, v.helm.dc ? 'damage control at work' : '')}
      ${ledgerRow('Air', L.scrubber, 'absorbent left')}
      <div class="air ${L.air}"><span>CO₂ <span class="num">${(L.co2 * 100).toFixed(1)}%</span></span><span>${L.air}</span></div>
      <div class="air"><span>Rations <span class="num">${pct(L.rations)}%</span></span><span>Men aboard <span class="num">${L.men}</span></span></div>
      <div class="air"><span>Torpedoes <span class="num">${L.torpedoes}</span></span><span>aboard</span></div>
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
    const err = `<circle class="errc" cx="${N.x}" cy="${N.y}" r="${Math.max(1.2, N.err_nm / 0.9).toFixed(1)}"/>`;
    const boat = `<g class="boat ${v.surfaced ? 'up' : ''}" transform="translate(${N.x} ${N.y}) rotate(${N.heading})"><circle class="halo" r="4.2"/><path d="M0 -4.6 L2.4 3.4 L0 2.2 L-2.4 3.4 Z"/></g>`;
    return `<svg class="chart" viewBox="0 0 110 80" role="img" aria-label="Chart: ${esc(N.grid)}, heading ${N.heading}">
      <rect class="sea" width="110" height="80"/>${g}
      <path class="land" d="M90 0 L110 0 L110 21 L101 19 L95 9 Z"/><text class="wl" x="108" y="26" text-anchor="end">Base</text>${t}${err}${boat}</svg>`;
  }
  function gauge(k, val, unit, extra) {
    return `<div class="gg"><span class="gk">${k}</span><span class="gv">${val}<small>${unit || ''}</small></span>${extra || ''}</div>`;
  }
  function chartView(v) {
    const N = v.nav;
    const nxt = N.next ? `${esc(N.next)} · ${N.range_nm} nm${N.eta_h ? ` · ${N.eta_h} h` : ''}` : 'On station';
    return `${chartSvg(v)}<div class="gauges">
      ${gauge('Heading', String(N.heading).padStart(3, '0'), '°')}${gauge('Speed', N.speed.toFixed(1), ' kn', `<span class="gk">ordered ${v.helm.speed}${v.helm.lag ? ' …' : ''}</span>`)}
      ${gauge('Depth', N.depth, ' m', `<span class="gk">${N.keel === null ? (v.surfaced ? 'on the surface' : 'no return from the sounder') : N.keel + ' m under the keel'}</span>`)}${gauge('Grid', N.grid, '', `<span class="gk">within ${N.err_nm.toFixed(1)} nm</span>`)}
      ${gauge('Signature', pct(N.noise), '%', `<span class="bar sm"><i style="width:${pct(N.noise)}%"></i></span>`)}
      <div class="gg wide"><span class="gk">Next</span><span class="gv sm">${nxt}</span></div></div>`;
  }
  /** The scope: sonar under water, radar on the surface. Every contact is drawn the same way. */
  function scopeView(v) {
    const R = 46, up = v.surfaced;
    const live = v.sonar.on || up;
    let g = [1, 2, 3].map((i) => `<circle class="ring" cx="50" cy="50" r="${(R * i / 3).toFixed(1)}"/>`).join('');
    g += '<line class="ring" x1="50" y1="4" x2="50" y2="96"/><line class="ring" x1="4" y1="50" x2="96" y2="50"/>';
    g += '<text class="gt" x="50" y="8" text-anchor="middle">N</text><text class="gt" x="94" y="52" text-anchor="end">E</text><text class="gt" x="50" y="97" text-anchor="middle">S</text><text class="gt" x="6" y="52">W</text>';
    const blips = live ? v.contacts.map((c) => {
      const r = Math.min(R, c.range_nm / 30 * R), a = c.bearing * Math.PI / 180;
      const x = 50 + r * Math.sin(a), y = 50 - r * Math.cos(a);
      return `<g class="blip"><circle cx="${x.toFixed(1)}" cy="${y.toFixed(1)}" r="1.8"/><text x="${(x + 2.6).toFixed(1)}" y="${(y + 1).toFixed(1)}">${c.tag}</text></g>`;
    }).join('') : '';
    const rows = live ? v.contacts.map((c) => `<li><b>${c.tag}</b><span>${String(c.bearing).padStart(3, '0')}° · ${c.range_nm.toFixed(1)} nm</span><span class="dim">${esc(c.label)}</span></li>`).join('') : '';
    const msg = !live ? 'Sonar is off. You hear nothing, and nothing is told to you.' : v.contacts.length ? '' : (up ? 'Radar clear.' : 'Nothing on the scope.');
    return `<div class="scopehead"><b>${up ? 'RADAR' : 'SONAR'}</b><span>${live ? 'range 30 nm · north up' : 'off'}</span></div>
      <svg class="scope ${live ? '' : 'dark'}" viewBox="0 0 100 100" role="img" aria-label="${up ? 'Radar' : 'Sonar'} scope, ${v.contacts.length} contacts">
        <circle class="face" cx="50" cy="50" r="${R}"/>${g}${live ? '<line class="sweep" x1="50" y1="50" x2="50" y2="4"/>' : ''}${blips}
        <path class="me" d="M50 46.5 L52 52.5 L50 51.5 L48 52.5 Z" transform="rotate(${v.nav.heading} 50 50)"/></svg>
      ${msg ? `<p class="dim scopemsg">${msg}</p>` : `<ul class="cts">${rows}</ul>`}
      <p class="note">A contact is something the room heard. The scope does not say what it was.</p>`;
  }
  const mmss = (s) => `${Math.floor(s / 60)}:${String(s % 60).padStart(2, '0')}`;
  /** The torpedo room's readings. The stock is the ledger's; the rest is what the room reports. */
  function weaponsView(v) {
    const W = v.weapons;
    const tubes = W.tubes.map((t, i) => `<div class="tube ${t.replace(' ', '-')}"><span class="tn">${i + 1}<small>${i < 4 ? 'bow' : 'stern'}</small></span><span class="ts">${esc(t)}</span></div>`).join('');
    const sols = !W.manned ? '<p class="dim">The torpedo room does not answer.</p>'
      : W.solutions.length ? `<table class="sol"><tr><th></th><th>Brg</th><th>Range</th><th>Run</th><th>Gyro</th></tr>${W.solutions.map((x) =>
        `<tr><td><b>${x.tag}</b></td><td>${String(x.bearing).padStart(3, '0')}°</td><td>${x.range_yd} yd</td><td>${mmss(x.run_s)}</td><td>${x.gyro > 0 ? '+' : ''}${x.gyro}°</td></tr>`).join('')}</table>`
        : '<p class="dim">No solution. Nothing on the scope.</p>';
    return `<div class="wpn"><div class="gg wide"><span class="gk">Torpedoes aboard</span><span class="gv">${W.stock}<small> exact · loaded: ${esc(W.loaded)}</small></span><span class="gk">${Object.entries(W.types).map(([k, n]) => `${k} ${n}`).join(' · ')}</span></div>
      <p class="smcaps">Tubes · as reported</p><div class="tubes">${tubes}</div>
      <p class="smcaps">Fire solutions · one per contact</p>${sols}
      <p class="note">The room reports what it sees. The stock is the ledger's.</p></div>`;
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
    const look = v.lookout.length ? `<div class="sonar"><b>LOOKOUT</b>${v.lookout.map((r) => `<p>${esc(r)}</p>`).join('')}</div>` : '';
    return `<ul class="men">${rows}</ul>
      <div class="sonar ${v.sonar.on ? '' : 'off'}"><b>SONAR ${v.sonar.on ? 'ON' : 'OFF'}</b>${rep}</div>${look}`;
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
    const sub = st.working ? `Under way · ${esc(o.hint)}${o.why && o.why !== 'The hours must pass.' ? ' · ' + esc(o.why) : ''}` : o.why ? esc(o.why) : esc(o.hint);
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
      <button class="icon-btn" data-a="sheet:periscope" aria-label="Periscope">◉</button>
      <button class="icon-btn ${state.sound ? '' : 'off'}" data-a="sound" aria-pressed="${state.sound}" aria-label="${state.sound ? 'Sound on' : 'Sound off'}">♪</button>
      <button class="icon-btn" data-a="sheet:help" aria-label="How to play">?</button>
    </div>`;
  }

  // ------------------------------------------------------------------ the periscope
  function hullShape(kind, markings) {
    if (kind === 'capital') return `<path class="hull" d="M-26 0 L-24 -4 L22 -4 L28 -8 L28 0 Z"/><rect class="sup" x="-7" y="-13" width="11" height="9"/><rect class="sup" x="-14" y="-12" width="3" height="8"/><rect class="sup" x="8" y="-12" width="3" height="8"/><line class="mast" x1="-1.5" y1="-13" x2="-1.5" y2="-24"/>`;
    const cross = markings ? '<rect class="red" x="-1" y="-6.4" width="2" height="5.2"/><rect class="red" x="-2.6" y="-4.8" width="5.2" height="2"/>' : '';
    return `<path class="hull ${markings ? 'white' : ''}" d="M-20 0 L-19 -4 L16 -4 L20 -7 L20 0 Z"/><rect class="sup ${markings ? 'white' : ''}" x="-4" y="-10" width="9" height="6"/><rect class="sup" x="-12" y="-9" width="2.6" height="5"/>${cross}`;
  }
  const KIND = { capital: 'a capital ship', convoy: 'a convoy', steamer: 'a steamer' };
  function periscopeSvg(ps) {
    const Y = 47;
    if (ps.mode === 'down') return `<svg class="eye" viewBox="0 0 160 90" role="img" aria-label="The periscope is housed"><rect width="160" height="90" fill="#05090c"/><text x="80" y="48" text-anchor="middle" class="gt" style="font-size:5px">PERISCOPE HOUSED</text></svg>`;
    const sh = ps.ship, k = sh ? Math.max(0.35, Math.min(2.2, 9 / sh.range_nm)) : 1;
    const X = sh && sh.in_field ? 80 + sh.rel / 25 * 70 : 80;
    let scene = '';
    if (sh && sh.in_field) {
      let body = '';
      if (sh.kind === 'convoy') for (let i = 0; i < sh.ships; i++) body += `<g transform="translate(${(i - (sh.ships - 1) / 2) * 38} ${(i % 2) * -2}) scale(.7)">${hullShape('steamer', false)}</g>`;
      else {
        body = hullShape(sh.kind, sh.markings);
        for (let i = 0; i < sh.escorts; i++) body += `<g transform="translate(${(i % 2 ? 1 : -1) * (46 + 18 * i)} -1) scale(.5)">${hullShape('steamer', false)}</g>`;
      }
      scene += `<g class="vessel" transform="translate(${X.toFixed(1)} ${Y}) scale(${k.toFixed(2)})">${body}<path class="wake" d="M-30 1 L30 1" /></g>`;
    }
    (ps.others || []).forEach((o) => {
      if (!o.in_field) return;
      const k2 = Math.max(0.3, Math.min(1.6, 7 / Math.max(1, o.range_nm)));
      scene += `<g class="vessel other" transform="translate(${(80 + o.rel / 25 * 70).toFixed(1)} ${Y}) scale(${k2.toFixed(2)})">${o.kind === 'fishing' ? '<path class="hull" d="M-8 0 L-7 -3 L7 -3 L9 -5 L9 0 Z"/><line class="mast" x1="0" y1="-3" x2="0" y2="-11"/>' : hullShape('steamer', false)}</g>`;
    });
    ps.ghosts.forEach((rel) => { scene += `<g class="ghostv" transform="translate(${(80 + rel / 25 * 70).toFixed(1)} ${Y}) scale(.9)">${hullShape('steamer', false)}</g>`; });
    const hx = sh && sh.in_field ? X : 80, hs = sh && sh.in_field ? k : 1;
    ps.distortions.forEach((d, i) => {
      const o = i * 6;
      if (d === 'figures_on_rail') { let f = ''; for (let j = 0; j < 8; j++) f += `<rect class="fig" x="${-18 + j * 4.6}" y="-9" width=".9" height="3.2"/>`; scene += `<g transform="translate(${hx.toFixed(1)} ${Y}) scale(${hs.toFixed(2)})">${f}</g>`; }
      else if (d === 'cross_on_hull') scene += `<g transform="translate(${(hx + 6).toFixed(1)} ${Y}) scale(${hs.toFixed(2)})"><rect class="red" x="-1" y="-6.4" width="2" height="5.2"/><rect class="red" x="-2.6" y="-4.8" width="5.2" height="2"/></g>`;
      else if (d === 'second_hull') scene += `<g class="ghostv" transform="translate(${(hx + 20 + o).toFixed(1)} ${Y}) scale(${(hs * 0.9).toFixed(2)})">${hullShape('capital', false)}</g>`;
      else if (d === 'lamp') scene += `<circle class="lamp" cx="${(hx + 5).toFixed(1)}" cy="${(Y - 10 * hs).toFixed(1)}" r="1.1"/>`;
      else if (d === 'wake_wrong') scene += `<path class="wake" d="M${(hx + 30 * hs).toFixed(1)} ${Y + 1.5} l12 1.6 M${(hx + 30 * hs).toFixed(1)} ${Y + 1.5} l12 -0.6"/>`;
    });
    let edge = '';
    if (sh && !sh.in_field) edge = sh.rel > 0 ? '<path class="edge" d="M148 45 l-6 -4 v8 z"/>' : '<path class="edge" d="M12 45 l6 -4 v8 z"/>';
    let ticks = '';
    for (let d = -20; d <= 20; d += 10) ticks += `<line class="rt" x1="${80 + d * 2.8}" y1="${d % 20 === 0 ? 70 : 72}" x2="${80 + d * 2.8}" y2="76"/>`;
    return `<svg class="eye" viewBox="0 0 160 90" role="img" aria-label="${ps.mode === 'bridge' ? 'Bridge' : 'Periscope'} view, centre ${ps.centre}">
      <defs><clipPath id="eyeclip"><circle cx="80" cy="45" r="43"/></clipPath></defs><rect width="160" height="90" fill="#05090c"/>
      <g clip-path="url(#eyeclip)"><rect class="sky" y="0" width="160" height="${Y}"/><rect class="water" y="${Y}" width="160" height="${90 - Y}"/><line class="horizon" x1="0" y1="${Y}" x2="160" y2="${Y}"/>${scene}</g>
      ${ps.visibility < 5 ? '<rect class="mist" width="160" height="90" clip-path="url(#eyeclip)"/>' : ''}<circle class="rim" cx="80" cy="45" r="43"/><line class="ret" x1="80" y1="6" x2="80" y2="84"/><line class="ret" x1="40" y1="${Y}" x2="120" y2="${Y}"/>${ticks}${edge}</svg>`;
  }
  function sheetPeriscope(v) {
    const ps = Dread.periscope(state.game.w, state.train), sh = ps.ship;
    const up = v.orders.find((o) => o.id === 'raise_periscope' || o.id === 'lower_periscope');
    const read = ps.mode === 'down' ? 'The periscope is housed. You see nothing, and are seen by nothing.'
      : sh ? `${sh.in_field ? 'In the field' : (sh.rel > 0 ? 'To starboard' : 'To port')}: ${esc(KIND[sh.kind] || sh.kind)}${sh.kind === 'convoy' ? ` of ${sh.ships} ships` : sh.escorts ? ` with ${sh.escorts} escorts` : ''} · bearing ${String(sh.bearing).padStart(3, '0')}° · ${sh.range_nm.toFixed(1)} nm`
        : 'An empty horizon.';
    return `<div class="sheet scopesheet" role="dialog" aria-modal="true" aria-label="Periscope"><header><h2>${ps.mode === 'bridge' ? 'Bridge' : 'Periscope'}</h2><button class="icon-btn" data-a="close" aria-label="Close">✕</button></header>
      <div class="body"><div class="eyegrid"><div>${periscopeSvg(ps)}<p class="eyeread">${read}</p><p class="eyeread dim">Centre ${String(ps.centre).padStart(3, '0')}° · trained ${ps.train > 0 ? '+' : ''}${ps.train}° · you can see ${ps.visibility.toFixed(1)} nm</p></div>
        <div class="eyebtns"><button class="btn" data-a="train:-15">◀ Train left</button><button class="btn" data-a="train:15">Train right ▶</button>
          ${up ? `<button class="btn primary" data-a="order:${up.id}">${esc(up.label)}<small>${esc(up.hint)}</small></button>` : '<p class="dim">On the surface: the bridge glasses.</p>'}
          <button class="btn" data-a="wait">Watch an hour</button><p class="note">What the eye sees is not always what is there.</p></div></div></div></div>`;
  }
  function sheetBriefing(v) {
    const m = v.mission;
    return `<div class="sheet" role="dialog" aria-modal="true" aria-label="Orders"><header><h2>${m ? esc(m.title) : 'Orders'}</h2><button class="icon-btn" data-a="close" aria-label="Close">✕</button></header>
      <div class="body">${m ? `<p style="font:400 17px/1.5 var(--display)">${esc(m.briefing)}</p>
        <p class="smcaps">Received</p><p>${esc(m.provenance)}</p>
        <p class="note">Where an order comes from is never settled. You see how it reached you, not who sent it.</p>` : '<p>No orders.</p>'}</div></div>`;
  }
  function sheetHelp(first) {
    const steps = [
      ['You are the captain.', 'Orders come from a source nobody can name. Tap the orders chip (top left) any time to read them again.'],
      ['Nothing happens while you wait.', 'The gold <b>step</b> button, bottom right, is your next move. Tap it and choose <b>how</b> to do it: every way has a price (time, noise, batteries, nerves).'],
      ['Look after the boat.', 'Left: the exact ledger, the hull, the torpedoes. Middle: the chart, the sonar and the men. A strip above the buttons says <b>what needs doing</b>; tap it and the order is given.'],
      ['The men are not exact.', 'Each says how he is, and you can see his symptoms. When the two disagree, believe the symptoms. What a man reports, an instrument may not show.'],
      ['Decisions stop the clock.', 'Each option shows what it costs, not what it does. There is no right answer. Wait <b>1 h</b>, or <b>▶▶</b> until something happens.'],
      ['Nothing is ever confirmed.', 'Whatever strange thing happens aboard has an ordinary explanation, and another.'],
    ];
    return `<div class="sheet" role="dialog" aria-modal="true" aria-label="How to play"><header><h2>${first ? 'Before you take command' : 'How to play'}</h2><button class="icon-btn" data-a="close" aria-label="Close">✕</button></header>
      <div class="body"><ol class="tut">${steps.map(([h, t]) => `<li><b>${h}</b><span>${t}</span></li>`).join('')}</ol></div>
      <footer><button class="btn primary" data-a="close">${first ? 'Take command' : 'Got it'}</button></footer></div>`;
  }
  /** How will you do it? The step's ways, each with its hours and what it costs. */
  function sheetWays(v) {
    const ways = v.orders.filter((o) => o.kind === 'act');
    return `<div class="sheet" role="dialog" aria-modal="true" aria-label="How will you do it?"><header><h2>How will you do it?</h2><button class="icon-btn" data-a="close" aria-label="Close">✕</button></header>
      <div class="body"><div class="orders-grid">${ways.map((o, i) => `<button class="opt" data-a="order:${esc(o.id)}"><b>${esc(o.label)}${i === 0 ? ' · plain' : ''}</b><span>${esc(o.hint)}</span>${o.why ? `<span class="why">${esc(o.why)}</span>` : ''}</button>`).join('')}</div>
        <p class="note">None of them is free. The hours are what it would take now: tired men, the dark and a hurt engine make them longer.</p></div></div>`;
  }
  /** What needs doing: the top tip, one tap to do it, and a button for the next one. */
  function adviceRow(v) {
    if (!v.advice.length || v.pending || v.over) return '';
    const i = state.advIdx % v.advice.length, t = v.advice[i];
    return `<div class="adv"><button class="advtxt ${t.order ? 'go' : ''}" data-a="adv:run" aria-label="Do it"><span class="k">${i === 0 ? 'What needs doing' : `Tip ${i + 1}`}</span><span class="t">${esc(t.text)}</span></button>` +
      (v.advice.length > 1 ? `<button class="advnext" data-a="adv:next" aria-label="Next tip">${i + 1}/${v.advice.length} ›</button>` : '') + '</div>';
  }
  const GROUPS = [
    ['Helm and navigation', /^(speed_|depth_|snorkel_|silent_running|normal_running|surface|dive|raise_periscope|lower_periscope|take_fix|active_ping)/],
    ['Torpedoes', /^load_/],
    ['Sensors and radio', /^(silence_sonar|restore_sonar|listen_radio|verify_orders)/],
    ['The boat', /^(damage_control|scrub_air|force_compartment)/],
    ['The men', /^(cancel_rest|grant_rest|stand_down|hold_ritual|address_crew|rations|isolate|release|sick_call|call_council|write_log)/],
    ['Station', /^(check_world|leave_station)/],
  ];
  function ordersGrouped(orders) {
    const btn = (o) => `<button class="opt" data-a="${o.needsCrew ? 'pick:' : 'order:'}${o.id}"><b>${esc(o.label)}${o.needsCrew ? ' …' : ''}</b>${o.hint ? `<span>${esc(o.hint)}</span>` : ''}</button>`;
    const used = new Set();
    let out = '';
    for (const [name, re] of GROUPS) {
      const items = orders.filter((o) => re.test(o.id));
      if (!items.length) continue;
      items.forEach((o) => used.add(o.id));
      out += `<p class="smcaps grp">${name}</p><div class="orders-grid">${items.map(btn).join('')}</div>`;
    }
    const rest = orders.filter((o) => !used.has(o.id));
    if (rest.length) out += `<p class="smcaps grp">Other</p><div class="orders-grid">${rest.map(btn).join('')}</div>`;
    return out;
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
      <div class="body">${ordersGrouped(v.orders.filter((o) => o.kind !== 'act'))}
        <p class="note">Orders are not free. Most of what they cost, you will learn later.</p></div></div>`;
  }
  function sheetDecision(v) {
    const d = v.pending;
    return `<div class="sheet decision ${d.id === 'engagement_turn' ? 'attack' : ''}" role="dialog" aria-modal="true" aria-label="Decision"><header><h2>CAPTAIN: ${esc(d.title)}</h2><span class="smcaps">the clock is stopped</span></header>
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
      : state.sheet === 'briefing' ? sheetBriefing(v) : state.sheet === 'periscope' ? sheetPeriscope(v) : state.sheet === 'help' ? sheetHelp(false) : state.sheet === 'tutorial' ? sheetHelp(true) : state.sheet === 'ways' ? sheetWays(v)
        : state.sheet === 'orders' ? sheetOrders(v) : '';
    const logEl = document.querySelector('.log-scroll');
    const stick = !logEl || logEl.scrollHeight - logEl.scrollTop - logEl.clientHeight < 60;
    app.innerHTML = `${topView(v)}
      <div class="cols">
        <section class="col" aria-label="${state.tabL === 'hull' ? 'Hull' : state.tabL === 'tubes' ? 'Tubes' : 'Ledger'}"><header class="tabs">${tabBtn('tabL', 'ledger', 'Ledger', state.tabL)}${tabBtn('tabL', 'hull', 'Hull', state.tabL)}${tabBtn('tabL', 'tubes', 'Tubes', state.tabL)}</header><div class="scroll">${state.tabL === 'hull' ? hullView(v) : state.tabL === 'tubes' ? weaponsView(v) : ledgerView(v)}</div></section>
        <section class="col" aria-label="${state.tabC === 'men' ? 'The men' : state.tabC === 'scope' ? 'Scope' : 'Chart'}"><header class="tabs">${tabBtn('tabC', 'chart', 'Chart', state.tabC)}${tabBtn('tabC', 'scope', 'Scope', state.tabC)}${tabBtn('tabC', 'men', 'The men', state.tabC)}</header><div class="scroll">${state.tabC === 'men' ? menView(v) : state.tabC === 'scope' ? scopeView(v) : chartView(v)}</div></section>
        <section class="col logcol" aria-label="Log"><header><span class="smcaps">Log</span><span class="smcaps">tick ${v.tick}</span></header>
          <div class="scroll log log-scroll">${logView(v)}</div>
          <div class="notice" aria-live="polite">${esc(v.notice || '')}</div>
          ${adviceRow(v)}
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
    if (a.startsWith('train:')) { state.train = Math.max(-180, Math.min(180, state.train + Number(a.slice(6)))); return render(); }
    if (a.startsWith('tabL:')) { state.tabL = a.slice(5); return render(); }
    if (a.startsWith('tabC:')) { state.tabC = a.slice(5); return render(); }
    if (a === 'act') return openWays(g.view());
    if (a === 'wait') return act('t');
    if (a === 'news') return act('w');
    if (a === 'orders') { state.sheet = 'orders'; state.pick = null; return render(); }
    if (a === 'close') { if (state.sheet === 'tutorial') guard(() => localStorage.setItem(TUTORIAL_KEY, '1')); state.sheet = null; state.pick = null; return render(); }
    if (a === 'adv:next') { state.advIdx += 1; return render(); }
    if (a === 'adv:run') {
      const v = g.view(), t = v.advice[state.advIdx % Math.max(1, v.advice.length)];
      if (!t || !t.order) { state.advIdx += 1; return render(); }
      if (t.order === 'act') return openWays(v);
      if (!v.orders.some((o) => o.id === t.order)) { state.advIdx += 1; return render(); }
      return act(`o:${t.order}`);
    }
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
