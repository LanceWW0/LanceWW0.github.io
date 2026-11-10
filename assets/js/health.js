/* /health page: load the aggregates, unlock them if the page is private,
   and draw the tiles and charts.

   The data is pre-computed daily/weekly/monthly numbers (see
   scripts/health); the page never sees raw Garmin data. Charts are inline
   SVG coloured through CSS variables, so the theme toggle needs no redraw;
   they redraw only when their width changes. Every chart has a "Show data"
   table, and the same readout on keyboard focus as on hover. */
(function () {
  'use strict';

  const root = document.getElementById('health');
  if (!root) return;

  const $ = (id) => document.getElementById(id);
  const statusEl = $('health-status');
  const lockForm = $('health-lock');
  const content = $('health-content');
  const SVG_NS = 'http://www.w3.org/2000/svg';
  const AAD = new TextEncoder().encode('health-v1');

  /* ------------------------------------------------------------------
     Formatting. Dates are parsed by hand and formatted in UTC, so a
     visitor's own time zone can never shift a day.
     ------------------------------------------------------------------ */
  const MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
  const MONTHS_LONG = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August',
    'September', 'October', 'November', 'December'];
  const WEEKDAYS = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
  const GROUP_NAMES = { run: 'Run', ride: 'Ride', swim: 'Swim', strength: 'Strength',
    walk: 'Walk & hike', climb: 'Climb', paddle: 'Paddle', other: 'Other' };
  const LEVEL_NAMES = ['Rest', 'Easy', 'Moderate', 'Hard', 'Hardest'];
  const nf = new Intl.NumberFormat('en-GB', { maximumFractionDigits: 0 });
  const nf1 = new Intl.NumberFormat('en-GB', { maximumFractionDigits: 1 });

  function parseDay(iso) {
    const [y, m, d] = iso.split('-').map(Number);
    return new Date(Date.UTC(y, m - 1, d));
  }
  const isoDay = (t) => t.toISOString().slice(0, 10);
  const addDays = (iso, n) => isoDay(new Date(parseDay(iso).getTime() + n * 86400000));
  const weekdayIndex = (t) => (t.getUTCDay() + 6) % 7; // Monday = 0
  const dayShort = (iso) => { const t = parseDay(iso); return `${t.getUTCDate()} ${MONTHS[t.getUTCMonth()]}`; };
  const dayLong = (iso) => `${WEEKDAYS[weekdayIndex(parseDay(iso))]} ${dayShort(iso)}`;
  const dayFull = (iso) => { const t = parseDay(iso); return `${t.getUTCDate()} ${MONTHS_LONG[t.getUTCMonth()]} ${t.getUTCFullYear()}`; };
  const monthLong = (m) => `${MONTHS[Number(m.slice(5)) - 1]} ${m.slice(0, 4)}`;
  const monthShort = (m) => (m.slice(5) === '01' ? m.slice(0, 4) : MONTHS[Number(m.slice(5)) - 1]);
  const weekLabel = (w) => `Week of ${dayShort(w)}`;

  function hm(minutes) {
    if (minutes == null) return '–';
    const h = Math.floor(minutes / 60);
    const m = Math.round(minutes - h * 60);
    return `${h}h ${String(m).padStart(2, '0')}m`;
  }
  const pace = (s) => (s == null ? '–' : `${Math.floor(s / 60)}:${String(Math.round(s % 60)).padStart(2, '0')}`);
  const num = (v, unit) => (v == null ? '–' : `${nf.format(v)}${unit ? ` ${unit}` : ''}`);
  const km = (v) => (v == null ? '–' : `${nf1.format(v)} km`);
  const plural = (n, word) => `${nf.format(n)} ${word}${n === 1 ? '' : 's'}`;

  function el(tag, className, text) {
    const node = document.createElement(tag);
    if (className) node.className = className;
    if (text != null) node.textContent = text;
    return node;
  }
  function svg(tag, attrs, parent) {
    const node = document.createElementNS(SVG_NS, tag);
    for (const key in attrs) node.setAttribute(key, attrs[key]);
    if (parent) parent.appendChild(node);
    return node;
  }
  function showStatus(text) {
    statusEl.textContent = text;
    statusEl.hidden = false;
  }

  /* ------------------------------------------------------------------
     Loading and unlocking
     ------------------------------------------------------------------ */
  function loadData() {
    const demo = new URLSearchParams(location.search).get('demo');
    if (demo !== null) {
      const url = demo === 'enc' ? root.dataset.demoEnc : root.dataset.demo;
      return fetch(url, { cache: 'no-store' }).then((r) => {
        if (!r.ok) throw new Error('demo data missing');
        return r.json();
      });
    }
    const inline = $('health-data');
    return Promise.resolve(JSON.parse(inline ? inline.textContent : 'null'));
  }

  function fromB64(text) {
    return Uint8Array.from(atob(text), (c) => c.charCodeAt(0));
  }

  function validEnvelope(env) {
    return env.enc === 1 && env.alg === 'AES-256-GCM' && env.kdf === 'PBKDF2-SHA256' &&
      Number.isInteger(env.iter) && env.iter >= 1000 && env.iter <= 10000000;
  }

  function deriveKey(passphrase, env) {
    return crypto.subtle.importKey('raw', new TextEncoder().encode(passphrase), 'PBKDF2', false, ['deriveKey'])
      .then((base) => crypto.subtle.deriveKey(
        { name: 'PBKDF2', hash: 'SHA-256', salt: fromB64(env.salt), iterations: env.iter },
        base, { name: 'AES-GCM', length: 256 }, false, ['decrypt']));
  }

  function decryptWith(key, env) {
    return crypto.subtle.decrypt({ name: 'AES-GCM', iv: fromB64(env.iv), additionalData: AAD }, key, fromB64(env.data))
      .then((plain) => JSON.parse(new TextDecoder().decode(plain)));
  }

  /* "Remember on this device" stores the derived key, not the passphrase.
     It is non-extractable, so even this page's own code can't read it back
     out. It's keyed by the file's salt, which only changes with the
     passphrase. Storage can be unavailable (private windows, blocked site
     data), so every call fails soft. */
  function keyStore(mode, action) {
    return new Promise((resolve) => {
      let request;
      try {
        request = indexedDB.open('health', 1);
      } catch (e) {
        resolve(null);
        return;
      }
      request.onupgradeneeded = () => request.result.createObjectStore('keys');
      request.onerror = () => resolve(null);
      request.onsuccess = () => {
        const db = request.result;
        try {
          const tx = db.transaction('keys', mode);
          const result = action(tx.objectStore('keys'));
          tx.oncomplete = () => { db.close(); resolve(result ? result.result : null); };
          tx.onerror = tx.onabort = () => { db.close(); resolve(null); };
        } catch (e) {
          db.close();
          resolve(null);
        }
      };
    });
  }
  const rememberedKey = (id) => keyStore('readonly', (store) => store.get(id));
  const rememberKey = (id, key) => keyStore('readwrite', (store) => { store.clear(); store.put(key, id); });
  const forgetKeys = () => keyStore('readwrite', (store) => { store.clear(); });

  function unlock(env) {
    if (!validEnvelope(env)) return showStatus('This data file is in a format this page doesn’t recognise.');
    if (!window.isSecureContext || !window.crypto || !crypto.subtle) {
      return showStatus('This page needs a secure (https) connection to unlock.');
    }
    return rememberedKey(env.salt).then((key) => {
      if (!key) return askForPassphrase(env);
      return decryptWith(key, env)
        .then((data) => render(data, { remembered: true }))
        .catch(() => forgetKeys().then(() => askForPassphrase(env)));
    });
  }

  function askForPassphrase(env) {
    statusEl.hidden = true;
    lockForm.hidden = false;
    const input = $('health-passphrase');
    const remember = $('health-remember');
    const error = $('health-lock-error');
    const button = $('health-unlock');
    input.focus();

    lockForm.addEventListener('submit', (event) => {
      event.preventDefault();
      if (!input.value || button.disabled) return;
      error.hidden = true;
      button.disabled = true;
      button.textContent = 'Unlocking…';
      deriveKey(input.value, env)
        .then((key) => decryptWith(key, env).then((data) => {
          input.value = '';
          lockForm.hidden = true;
          const keep = remember.checked;
          return (keep ? rememberKey(env.salt, key) : Promise.resolve())
            .then(() => render(data, { remembered: keep }));
        }))
        .catch(() => {
          error.textContent = 'That passphrase didn’t work.';
          error.hidden = false;
          input.select();
        })
        .finally(() => {
          button.disabled = false;
          button.textContent = 'Unlock';
        });
    });
  }

  /* ------------------------------------------------------------------
     Page
     ------------------------------------------------------------------ */
  function render(data, options) {
    statusEl.hidden = true;
    content.hidden = false;
    renderMeta(data, options || {});
    renderTiles(data);
    renderCharts(data);
  }

  function renderMeta(data, options) {
    const meta = $('health-meta');
    meta.textContent = '';
    meta.append(`Data through ${dayFull(data.through)} · from Garmin`);

    const now = new Date();
    const today = Date.UTC(now.getFullYear(), now.getMonth(), now.getDate());
    const behind = Math.round((today - parseDay(data.through).getTime()) / 86400000);
    if (behind > 4) meta.append(el('span', 'health-meta-note', ` · Updates paused since ${dayShort(data.through)}`));

    const names = { sleep: 'Sleep', hrv: 'HRV', rhr: 'Resting HR', body_battery: 'Body Battery', activities: 'Workouts' };
    for (const metric in data.sources) {
      if (data.sources[metric] < data.through) {
        meta.append(el('span', 'health-meta-note', ` · ${names[metric]} last updated ${dayShort(data.sources[metric])}`));
      }
    }
    if (options.remembered) {
      const forget = el('button', 'health-forget', 'Forget this device');
      forget.type = 'button';
      forget.addEventListener('click', () => forgetKeys().then(() => location.reload()));
      meta.append(' · ', forget);
    }
    meta.hidden = false;
  }

  function tile(label, value, unit, note) {
    const node = el('div', 'health-tile');
    node.append(el('p', 'health-tile-label', label));
    const v = el('p', 'health-tile-value', value == null ? '–' : value);
    if (value != null && unit) v.append(el('span', 'health-tile-unit', unit));
    node.append(v);
    if (note) node.append(el('p', 'health-tile-note', note));
    return node;
  }

  function renderTiles(data) {
    const d = data.summary.d30;
    const tiles = $('health-tiles');
    tiles.textContent = '';
    tiles.append(
      tile('Sleep', d.sleep_min == null ? null : hm(d.sleep_min), '', d.nights == null ? null : `Average of ${plural(d.nights, 'night')}`),
      tile('Sleep score', d.sleep_score == null ? null : nf.format(d.sleep_score), '', 'Average, out of 100'),
      tile('HRV', d.hrv == null ? null : nf.format(d.hrv), ' ms', 'Overnight average'),
      tile('Resting HR', d.rhr == null ? null : nf.format(d.rhr), ' bpm', 'Average'),
      tile('Body Battery', d.bb == null ? null : nf.format(d.bb), '', 'Average daily peak'),
      tile('Workouts', d.workouts == null ? null : nf.format(d.workouts), '', d.hours == null ? null : `${nf1.format(d.hours)} hours`),
    );

    const totals = data.summary.totals;
    const training = $('health-training-tiles');
    training.textContent = '';
    const allTime = $('health-alltime');
    allTime.textContent = '';
    if (!totals) {
      training.append(tile('Workouts', null, '', 'Not available right now'));
      return;
    }
    training.append(
      tile('Workouts', nf.format(totals.y1.workouts), '', 'Last 12 months'),
      tile('Time training', nf.format(totals.y1.hours), ' h', 'Last 12 months'),
      tile('Running', nf.format(totals.y1.run_km), ' km', 'Last 12 months'),
    );
    const since = data.months.length ? ` since ${monthLong(data.months[0].m)}` : '';
    allTime.textContent = `All time${since}: ${plural(totals.all.workouts, 'workout')} · ` +
      `${nf.format(totals.all.hours)} hours · ${nf.format(totals.all.run_km)} km run`;
  }

  /* ------------------------------------------------------------------
     Chart kit
     ------------------------------------------------------------------ */
  const drawers = [];

  function card(name, title, subtitle) {
    const figure = root.querySelector(`[data-chart="${name}"]`);
    figure.textContent = '';
    const head = el('figcaption', 'health-card-head');
    head.append(el('h3', 'health-card-title', title));
    if (subtitle) head.append(el('p', 'health-card-sub', subtitle));
    figure.append(head);
    return figure;
  }

  function empty(figure, text) {
    figure.append(el('p', 'health-empty', text || 'Not enough data yet.'));
  }

  const hasData = (values) => values.some((v) => v != null);

  function legend(items) {
    const list = el('ul', 'health-legend');
    for (const item of items) {
      const entry = el('li', 'health-legend-item');
      entry.append(el('span', `health-key health-key--${item.key}${item.cls ? ` ${item.cls}` : ''}`));
      entry.append(document.createTextNode(item.label));
      list.append(entry);
    }
    return list;
  }

  /* The table twin of every chart: the same numbers, no hovering needed. */
  function dataTable(figure, caption, head, rows) {
    const details = el('details', 'health-table');
    details.append(el('summary', null, 'Show data'));
    const wrap = el('div', 'health-table-wrap');
    const table = el('table');
    table.append(el('caption', 'health-sr', caption));
    const thead = el('thead');
    const headRow = el('tr');
    head.forEach((h) => {
      const th = el('th', null, h);
      th.scope = 'col';
      headRow.append(th);
    });
    thead.append(headRow);
    const tbody = el('tbody');
    rows.slice().reverse().forEach((row) => { // newest first
      const tr = el('tr');
      row.forEach((cell, i) => {
        const td = el(i === 0 ? 'th' : 'td', null, cell);
        if (i === 0) td.scope = 'row';
        tr.append(td);
      });
      tbody.append(tr);
    });
    table.append(thead, tbody);
    wrap.append(table);
    details.append(wrap);
    figure.append(details);
  }

  /* Charts draw at their real pixel width, so text never scales, and only
     redraw when that width changes. */
  function onWidth(node, draw) {
    drawers.push({ node, draw, width: 0 });
  }
  function redraw(entry) {
    const width = Math.floor(entry.node.clientWidth);
    if (!width || width === entry.width) return;
    entry.width = width;
    entry.draw(entry.node, width);
  }
  function startDrawing() {
    drawers.forEach(redraw);
    const all = () => requestAnimationFrame(() => drawers.forEach(redraw));
    if ('ResizeObserver' in window) {
      const observer = new ResizeObserver(all);
      drawers.forEach((entry) => observer.observe(entry.node));
    } else {
      window.addEventListener('resize', all);
    }
  }

  function niceStep(span, count) {
    const raw = span / Math.max(1, count);
    const magnitude = Math.pow(10, Math.floor(Math.log10(raw)));
    const n = raw / magnitude;
    return (n <= 1 ? 1 : n <= 2 ? 2 : n <= 2.5 ? 2.5 : n <= 5 ? 5 : 10) * magnitude;
  }

  function scaleY(values, options) {
    const finite = values.filter((v) => v != null && Number.isFinite(v));
    let lo = finite.length ? Math.min(...finite) : 0;
    let hi = finite.length ? Math.max(...finite) : 1;
    if (options.zero) lo = 0;
    if (hi === lo) hi = lo + 1;
    if (!options.zero) {
      const pad = (hi - lo) * 0.12;
      lo -= pad;
      hi += pad;
      if (finite.length && Math.min(...finite) >= 0) lo = Math.max(0, lo);
    }
    let step = options.step || niceStep(hi - lo, 4);
    if (options.steps) step = options.steps.find((s) => (hi - lo) / s <= 5) || options.steps[options.steps.length - 1];
    if (options.integer) step = Math.max(1, Math.round(step));
    lo = Math.floor(lo / step) * step;
    hi = Math.ceil(hi / step) * step;
    if (options.max != null) hi = Math.min(hi, options.max); // e.g. scores out of 100
    const ticks = [];
    for (let v = lo; v <= hi + step / 1000; v += step) ticks.push(Number(v.toFixed(6)));
    return { lo, hi, ticks };
  }

  function labelIndices(n, plotWidth, gap) {
    if (n <= 1) return [0];
    const step = Math.ceil(n / Math.max(2, Math.floor(plotWidth / gap)));
    const out = [];
    for (let i = n - 1; i >= 0; i -= step) out.unshift(i);
    return out;
  }

  function runs(n, present) {
    const out = [];
    let start = -1;
    for (let i = 0; i <= n; i++) {
      if (i < n && present(i)) {
        if (start < 0) start = i;
      } else if (start >= 0) {
        out.push([start, i - 1]);
        start = -1;
      }
    }
    return out;
  }

  function roundedTop(x, y, w, h, r) {
    r = Math.min(r, h, w / 2);
    return `M${x},${y + h}V${y + r}Q${x},${y} ${x + r},${y}H${x + w - r}Q${x + w},${y} ${x + w},${y + r}V${y + h}Z`;
  }

  function fillTip(tip, content) {
    tip.textContent = '';
    tip.append(el('p', 'health-tip-head', content.head));
    for (const row of content.rows) {
      const line = el('p', 'health-tip-row');
      if (row.key) line.append(el('span', `health-key health-key--${row.key}${row.cls ? ` ${row.cls}` : ''}`));
      line.append(el('strong', null, row.value));
      if (row.label) line.append(el('span', 'health-tip-label', row.label));
      tip.append(line);
    }
  }

  function placeTip(tip, x, top, width) {
    tip.hidden = false;
    const w = tip.offsetWidth;
    const left = x + 14 + w <= width ? x + 14 : x - 14 - w;
    tip.style.left = `${Math.max(0, Math.min(width - w, left))}px`;
    tip.style.top = `${top}px`;
  }

  /* Arrow keys move through the points; the readout matches hovering. */
  function keyboard(target, count, getActive, show, hide, moves) {
    target.addEventListener('focus', () => show(getActive() >= 0 ? getActive() : count - 1));
    target.addEventListener('blur', hide);
    target.addEventListener('keydown', (event) => {
      if (event.key === 'Escape') { hide(); return; }
      const current = getActive() >= 0 ? getActive() : count - 1;
      const delta = { ArrowLeft: -1, ArrowRight: 1, Home: -current, End: count - 1 - current, ...(moves || {}) }[event.key];
      if (delta === undefined) return;
      event.preventDefault();
      show(Math.max(0, Math.min(count - 1, current + delta)));
    });
  }

  /* Time series: columns (one bar series) or lines (an accent line, a grey
     context line and an optional band). Always one y-axis. */
  function seriesChart(figure, spec) {
    if (spec.legend) figure.append(legend(spec.legend));
    const plot = el('div', 'health-plot');
    figure.append(plot);
    onWidth(plot, (node, width) => drawSeries(node, width, spec));
    dataTable(figure, spec.title, spec.table.head, spec.table.rows);
  }

  function drawSeries(node, width, spec) {
    node.textContent = '';
    const columns = spec.type === 'columns';
    const n = spec.labels.length;
    const height = spec.height || 180;
    const m = { top: 10, right: spec.rightLabel ? 58 : 12, bottom: 24, left: 40 };
    const plotW = Math.max(60, width - m.left - m.right);
    const plotH = height - m.top - m.bottom;

    const values = [];
    for (const s of spec.series) {
      values.push(...(s.values || []));
      if (s.lo) values.push(...s.lo, ...s.hi);
    }
    if (spec.reference) values.push(spec.reference.value);
    const y = scaleY(values, spec.y);
    const yPos = (v) => m.top + plotH - ((v - y.lo) / (y.hi - y.lo)) * plotH;
    const band = plotW / n;
    const xPos = columns
      ? (i) => m.left + band * (i + 0.5)
      : (i) => m.left + (n === 1 ? plotW / 2 : (plotW * i) / (n - 1));

    const chart = svg('svg', {
      width, height, viewBox: `0 0 ${width} ${height}`, class: 'health-svg',
      role: 'img', tabindex: 0, 'aria-label': spec.summary,
    });

    for (const t of y.ticks) {
      const yy = Math.round(yPos(t)) + 0.5;
      svg('line', { x1: m.left, x2: m.left + plotW, y1: yy, y2: yy,
        class: columns && t === 0 ? 'viz-baseline' : 'viz-gridline' }, chart);
      svg('text', { x: m.left - 6, y: yy, class: 'viz-tick', 'text-anchor': 'end', 'dominant-baseline': 'middle' }, chart)
        .textContent = spec.y.format(t);
    }
    for (const i of labelIndices(n, plotW, spec.labelGap || 60)) {
      const text = spec.labels[i].short;
      const half = text.length * 3.2;
      let x = xPos(i);
      let anchor = 'middle';
      if (x - half < 2) { anchor = 'start'; x = Math.max(2, x - band / 2); }
      if (x + half > width - 2) { anchor = 'end'; x = Math.min(width - 2, x + band / 2); }
      svg('text', { x, y: height - 6, class: 'viz-tick', 'text-anchor': anchor }, chart).textContent = text;
    }

    const marks = svg('g', {}, chart);
    const bars = [];
    const barSeries = spec.series.find((s) => s.kind === 'bar');
    if (barSeries) {
      const w = Math.max(1, Math.min(24, band * 0.68));
      const base = yPos(0);
      barSeries.values.forEach((v, i) => {
        if (v == null || v <= 0) { bars.push(null); return; }
        const top = yPos(v);
        bars.push(svg('path', { d: roundedTop(xPos(i) - w / 2, top, w, base - top, 4), class: 'viz-bar' }, marks));
      });
    }
    for (const s of spec.series.filter((x) => x.kind === 'band')) {
      for (const [a, b] of runs(n, (i) => s.lo[i] != null && s.hi[i] != null)) {
        let d = '';
        for (let i = a; i <= b; i++) d += `${i === a ? 'M' : 'L'}${xPos(i)},${yPos(s.hi[i])}`;
        for (let i = b; i >= a; i--) d += `L${xPos(i)},${yPos(s.lo[i])}`;
        svg('path', { d: `${d}Z`, class: 'viz-band' }, marks);
      }
    }
    const lineSeries = spec.series.filter((s) => s.kind === 'context')
      .concat(spec.series.filter((s) => s.kind === 'line'));
    for (const s of lineSeries) {
      for (const [a, b] of runs(n, (i) => s.values[i] != null)) {
        if (a === b) {
          svg('circle', { cx: xPos(a), cy: yPos(s.values[a]), r: 1.5, class: `viz-dot--${s.kind}` }, marks);
          continue;
        }
        let d = '';
        for (let i = a; i <= b; i++) d += `${i === a ? 'M' : 'L'}${xPos(i)},${yPos(s.values[i])}`;
        svg('path', { d, class: s.kind === 'line' ? 'viz-line' : 'viz-context' }, marks);
      }
    }

    if (spec.reference) {
      const yy = Math.round(yPos(spec.reference.value)) + 0.5;
      svg('line', { x1: m.left, x2: m.left + plotW, y1: yy, y2: yy, class: 'viz-reference' }, chart);
      const label = svg('text', { x: m.left + plotW + 6, y: yy - 7, class: 'viz-label' }, chart);
      svg('tspan', { x: m.left + plotW + 6 }, label).textContent = spec.reference.label[0];
      svg('tspan', { x: m.left + plotW + 6, dy: 13, class: 'viz-label--strong' }, label).textContent = spec.reference.label[1];
    }
    if (spec.endLabel) {
      const s = spec.series.find((x) => x.kind === 'line' || x.kind === 'bar');
      let i = n - 1;
      while (i >= 0 && s.values[i] == null) i--;
      if (i >= 0) {
        if (s.kind === 'line') svg('circle', { cx: xPos(i), cy: yPos(s.values[i]), r: 4, class: 'viz-end' }, chart);
        svg('text', { x: m.left + plotW + 8, y: yPos(s.values[i]), class: 'viz-label viz-label--strong', 'dominant-baseline': 'middle' }, chart)
          .textContent = spec.endLabel(s.values[i]);
      }
    }

    const cross = svg('line', { y1: m.top, y2: m.top + plotH, class: 'viz-crosshair', visibility: 'hidden' }, chart);
    const focus = lineSeries.map((s) => svg('circle', { r: 4, class: `viz-focus viz-focus--${s.kind}`, visibility: 'hidden' }, chart));
    const hit = svg('rect', { x: m.left, y: m.top, width: plotW, height: plotH, class: 'viz-hit' }, chart);
    const tip = el('div', 'health-tip');
    tip.hidden = true;
    tip.setAttribute('aria-live', 'polite');
    node.append(chart, tip);

    let active = -1;
    const show = (i) => {
      active = i;
      const x = xPos(i);
      bars.forEach((bar, j) => bar && bar.classList.toggle('is-active', j === i));
      if (!columns) {
        cross.setAttribute('x1', x);
        cross.setAttribute('x2', x);
        cross.setAttribute('visibility', 'visible');
        lineSeries.forEach((s, k) => {
          const v = s.values[i];
          focus[k].setAttribute('visibility', v == null ? 'hidden' : 'visible');
          if (v != null) {
            focus[k].setAttribute('cx', x);
            focus[k].setAttribute('cy', yPos(v));
          }
        });
      }
      fillTip(tip, spec.tooltip(i));
      placeTip(tip, x, m.top, width);
    };
    const hide = () => {
      active = -1;
      tip.hidden = true;
      cross.setAttribute('visibility', 'hidden');
      focus.forEach((dot) => dot.setAttribute('visibility', 'hidden'));
      bars.forEach((bar) => bar && bar.classList.remove('is-active'));
    };
    const indexAt = (event) => {
      const px = event.clientX - chart.getBoundingClientRect().left - m.left;
      const i = columns ? Math.floor(px / band) : Math.round((px / plotW) * (n - 1));
      return Math.max(0, Math.min(n - 1, i));
    };
    hit.addEventListener('pointermove', (event) => show(indexAt(event)));
    hit.addEventListener('pointerdown', (event) => show(indexAt(event)));
    chart.addEventListener('pointerleave', () => { if (document.activeElement !== chart) hide(); });
    keyboard(chart, n, () => active, show, hide);
  }

  /* Training calendar: one square per day, Monday-first columns. */
  function calendarChart(figure, calendar) {
    const scale = el('div', 'health-scale');
    scale.append(el('span', null, 'Rest'));
    for (let level = 0; level <= 4; level++) {
      const swatch = el('span', `health-scale-swatch viz-cal-bg--${level}`);
      swatch.title = LEVEL_NAMES[level];
      scale.append(swatch);
    }
    scale.append(el('span', null, 'Hardest'));
    figure.append(scale);

    const days = calendar.levels.map((level, i) => ({ iso: addDays(calendar.start, i), level }));
    const plot = el('div', 'health-plot');
    figure.append(plot);
    onWidth(plot, (node, width) => drawCalendar(node, width, days));

    const byMonth = new Map();
    for (const d of days) {
      const key = d.iso.slice(0, 7);
      const row = byMonth.get(key) || { active: 0, hard: 0 };
      if (d.level > 0) row.active += 1;
      if (d.level >= 3) row.hard += 1;
      byMonth.set(key, row);
    }
    dataTable(figure, 'Training calendar by month', ['Month', 'Active days', 'Hard or hardest days'],
      [...byMonth].map(([month, row]) => [monthLong(month), nf.format(row.active), nf.format(row.hard)]));
  }

  function drawCalendar(node, width, allDays) {
    node.textContent = '';
    const last = allDays[allDays.length - 1].iso;
    const lastMonday = addDays(last, -weekdayIndex(parseDay(last)));
    const left = 30;
    const top = 16;
    const gap = 2;
    let weeks = 53;
    let size = Math.floor((width - left) / weeks) - gap;
    if (size < 9) {
      weeks = 26;
      size = Math.floor((width - left) / weeks) - gap;
    }
    size = Math.max(6, Math.min(14, size));
    const pitch = size + gap;
    const firstMonday = addDays(lastMonday, -7 * (weeks - 1));
    const days = allDays.filter((d) => d.iso >= firstMonday);
    const height = top + 7 * pitch;
    const active = days.filter((d) => d.level > 0).length;

    const chart = svg('svg', {
      width, height, viewBox: `0 0 ${width} ${height}`, class: 'health-svg', role: 'img', tabindex: 0,
      'aria-label': `Training calendar: ${active} active days in the last ${days.length} days.`,
    });
    for (const [label, row] of [['Mon', 0], ['Wed', 2], ['Fri', 4]]) {
      svg('text', { x: 0, y: top + row * pitch + size / 2, class: 'viz-tick', 'dominant-baseline': 'middle' }, chart).textContent = label;
    }
    const origin = parseDay(firstMonday).getTime();
    const cells = days.map((d) => {
      const offset = Math.round((parseDay(d.iso).getTime() - origin) / 86400000);
      const col = Math.floor(offset / 7);
      const x = left + col * pitch;
      const y = top + (offset % 7) * pitch;
      const rect = svg('rect', { x, y, width: size, height: size, rx: 2, class: `viz-cal viz-cal--${d.level}` }, chart);
      return { rect, x, y, d };
    });
    // Each month is labelled above the week that contains its 1st.
    let lastLabelCol = -10;
    for (let col = 0; col < weeks - 1; col++) {
      const monday = addDays(firstMonday, col * 7);
      const sunday = addDays(monday, 6);
      const startsMonth = monday.slice(8) === '01' || monday.slice(0, 7) !== sunday.slice(0, 7);
      if (startsMonth && col - lastLabelCol >= 3) {
        svg('text', { x: left + col * pitch, y: 10, class: 'viz-tick' }, chart).textContent = monthShort(sunday.slice(0, 7));
        lastLabelCol = col;
      }
    }

    const tip = el('div', 'health-tip');
    tip.hidden = true;
    tip.setAttribute('aria-live', 'polite');
    node.append(chart, tip);
    let current = -1;
    const show = (i) => {
      if (current >= 0) cells[current].rect.classList.remove('is-active');
      current = i;
      const cell = cells[i];
      cell.rect.classList.add('is-active');
      fillTip(tip, { head: dayLong(cell.d.iso), rows: [{ value: LEVEL_NAMES[cell.d.level], key: 'swatch', cls: `viz-cal-bg--${cell.d.level}` }] });
      placeTip(tip, cell.x + size / 2, Math.max(0, cell.y - 8), width);
    };
    const hide = () => {
      if (current >= 0) cells[current].rect.classList.remove('is-active');
      current = -1;
      tip.hidden = true;
    };
    cells.forEach((cell, i) => cell.rect.addEventListener('pointerenter', () => show(i)));
    chart.addEventListener('pointerleave', () => { if (document.activeElement !== chart) hide(); });
    keyboard(chart, cells.length, () => current, show, hide, { ArrowUp: -1, ArrowDown: 1, ArrowLeft: -7, ArrowRight: 7 });
  }

  /* One whole split into parts: a tall segmented bar with a legend. */
  function stagesChart(figure, stages) {
    const parts = [['deep', 'Deep'], ['light', 'Light'], ['rem', 'REM'], ['awake', 'Awake']];
    const bar = el('div', 'health-segbar');
    bar.setAttribute('role', 'img');
    bar.setAttribute('aria-label', `Sleep stages over the last 30 nights: ${parts.map(([k, name]) => `${name} ${stages[k]}%`).join(', ')}.`);
    const segments = [];
    parts.forEach(([key, name], i) => {
      if (!stages[key]) return;
      const segment = el('div', `health-seg viz-cat-${i + 1}`);
      segment.style.flexGrow = String(stages[key]);
      segment.title = `${name}: ${stages[key]}%`;
      segment.append(el('span', 'health-seg-label', `${stages[key]}%`));
      bar.append(segment);
      segments.push(segment);
    });
    figure.append(bar, legend(parts.map(([, name], i) => ({ key: 'swatch', cls: `viz-cat-${i + 1}`, label: name }))));
    onWidth(bar, () => {
      for (const segment of segments) {
        const label = segment.firstChild;
        label.hidden = false;
        label.hidden = label.offsetWidth + 12 > segment.clientWidth;
      }
    });
    dataTable(figure, 'Sleep stages', ['Stage', 'Share of the night'], parts.map(([key, name]) => [name, `${stages[key]}%`]).reverse());
  }

  /* Ranked horizontal bars, largest first, one hue. */
  function rankedChart(figure, rows, unit) {
    const max = rows.length ? rows[0][1] : 0;
    const list = el('ol', 'health-ranks');
    for (const [name, value] of rows) {
      const item = el('li', 'health-rank');
      item.append(el('span', 'health-rank-name', name));
      const track = el('span', 'health-rank-track');
      const fill = el('span', 'health-rank-bar');
      fill.style.width = `${max ? (value / max) * 100 : 0}%`;
      track.append(fill);
      item.append(track, el('span', 'health-rank-value', nf.format(value)));
      item.setAttribute('aria-label', `${name}: ${plural(value, unit)}`);
      list.append(item);
    }
    figure.append(list);
  }

  /* ------------------------------------------------------------------
     The charts
     ------------------------------------------------------------------ */
  function renderCharts(data) {
    const d30 = data.summary.d30;
    const days = data.days;
    const nights = days.slice(-30);
    const weeks = data.weeks;
    const months = data.months;
    const since = months.length ? `Since ${monthLong(months[0].m)}` : '';
    const dayLabels = (rows) => rows.map((d) => ({ short: dayShort(d.d) }));
    const monthLabels = months.map((r) => ({ short: monthShort(r.m) }));
    const weekLabels = weeks.map((w) => ({ short: dayShort(w.w) }));
    const hours = (v) => (v == null ? null : v / 60);

    // Sleep ----------------------------------------------------------
    let fig = card('sleep-hours', 'Time asleep', 'Last 30 nights');
    if (!hasData(nights.map((d) => d.sleep_min))) empty(fig);
    else {
      seriesChart(fig, {
        title: 'Time asleep, last 30 nights', type: 'columns',
        labels: dayLabels(nights),
        series: [{ kind: 'bar', values: nights.map((d) => hours(d.sleep_min)) }],
        y: { zero: true, step: 2, format: (v) => `${v}h` },
        reference: d30.sleep_min == null ? null : { value: d30.sleep_min / 60, label: ['average', hm(d30.sleep_min)] },
        rightLabel: true,
        tooltip: (i) => ({ head: dayLong(nights[i].d), rows: [
          { value: hm(nights[i].sleep_min), label: 'asleep', key: 'bar' },
          { value: num(nights[i].sleep_score), label: 'sleep score' }] }),
        summary: `Time asleep each night for the last 30 nights. 30-day average ${hm(d30.sleep_min)}.`,
        table: { head: ['Morning of', 'Asleep', 'Sleep score'], rows: nights.map((d) => [dayLong(d.d), hm(d.sleep_min), num(d.sleep_score)]) },
      });
    }

    fig = card('sleep-score', 'Sleep score', 'Last 30 nights, out of 100');
    if (!hasData(nights.map((d) => d.sleep_score))) empty(fig);
    else {
      seriesChart(fig, {
        title: 'Sleep score, last 30 nights', type: 'lines',
        labels: dayLabels(nights),
        series: [{ kind: 'line', values: nights.map((d) => d.sleep_score) }],
        y: { integer: true, max: 100, format: (v) => nf.format(v) },
        reference: d30.sleep_score == null ? null : { value: d30.sleep_score, label: ['average', nf.format(d30.sleep_score)] },
        rightLabel: true,
        tooltip: (i) => ({ head: dayLong(nights[i].d), rows: [{ value: num(nights[i].sleep_score), label: 'sleep score', key: 'line' }] }),
        summary: `Sleep score each night for the last 30 nights. 30-day average ${num(d30.sleep_score)}.`,
        table: { head: ['Morning of', 'Sleep score'], rows: nights.map((d) => [dayLong(d.d), num(d.sleep_score)]) },
      });
    }

    fig = card('sleep-stages', 'Sleep stages', 'Share of the night, last 30 nights');
    if (!data.summary.stages30) empty(fig);
    else stagesChart(fig, data.summary.stages30);

    fig = card('sleep-months', 'Average sleep by month', since);
    if (!hasData(months.map((r) => r.sleep_min))) empty(fig);
    else {
      seriesChart(fig, {
        title: 'Average sleep by month', type: 'lines', labels: monthLabels, labelGap: 48,
        series: [{ kind: 'line', values: months.map((r) => hours(r.sleep_min)) }],
        y: { format: (v) => `${nf1.format(v)}h` },
        rightLabel: true, endLabel: (v) => hm(v * 60),
        tooltip: (i) => ({ head: monthLong(months[i].m), rows: [
          { value: hm(months[i].sleep_min), label: 'average asleep', key: 'line' },
          { value: num(months[i].sleep_score), label: 'average score' }] }),
        summary: `Average time asleep per month, ${since.toLowerCase()}.`,
        table: { head: ['Month', 'Average asleep', 'Average score'], rows: months.map((r) => [monthLong(r.m), hm(r.sleep_min), num(r.sleep_score)]) },
      });
    }

    // Recovery -------------------------------------------------------
    const recovery = (name, title, subtitle, field, unit, extra) => {
      const figure = card(name, title, subtitle);
      if (!hasData(days.map((d) => d[field]))) { empty(figure); return; }
      const avg = `${field}7`;
      const series = [
        { kind: 'context', values: days.map((d) => d[field]) },
        { kind: 'line', values: days.map((d) => d[avg]) },
      ];
      const legendItems = [{ key: 'line', label: '7-day average' }, { key: 'context', label: 'Each day' }];
      if (extra) {
        series.unshift({ kind: 'band', lo: days.map((d) => d.hrv_lo), hi: days.map((d) => d.hrv_hi) });
        legendItems.push({ key: 'band', label: 'Garmin’s balanced range' });
      }
      const withUnit = (v) => num(v, unit);
      seriesChart(figure, {
        title: `${title}, last 90 days`, type: 'lines', labels: dayLabels(days), height: extra ? 200 : 170,
        series, legend: legendItems,
        y: { integer: true, max: field === 'bb' ? 100 : null, format: (v) => nf.format(v) },
        rightLabel: true, endLabel: (v) => withUnit(v),
        tooltip: (i) => {
          const day = days[i];
          const rows = [
            { value: withUnit(day[avg]), label: '7-day average', key: 'line' },
            { value: withUnit(day[field]), label: 'that day', key: 'context' },
          ];
          if (extra && day.hrv_lo != null) rows.push({ value: `${day.hrv_lo}–${day.hrv_hi} ${unit}`, label: 'balanced range', key: 'band' });
          return { head: dayLong(day.d), rows };
        },
        summary: `${title} over the last 90 days, with a 7-day average. 30-day average ${withUnit(d30[field])}.`,
        table: {
          head: ['Date', title, '7-day average'].concat(extra ? ['Balanced range'] : []),
          rows: days.map((day) => [dayLong(day.d), withUnit(day[field]), withUnit(day[avg])]
            .concat(extra ? [day.hrv_lo == null ? '–' : `${day.hrv_lo}–${day.hrv_hi} ${unit}`] : [])),
        },
      });
    };
    recovery('hrv', 'Heart rate variability', 'Overnight average, last 90 days, in milliseconds', 'hrv', 'ms', true);
    recovery('rhr', 'Resting heart rate', 'Last 90 days, in beats per minute', 'rhr', 'bpm');
    recovery('bb', 'Body Battery', 'Daily peak, last 90 days, out of 100', 'bb', '');

    // Training -------------------------------------------------------
    fig = card('calendar', 'Training calendar', 'Last 12 months, shaded by training load');
    if (!data.calendar) empty(fig, 'Not available right now.');
    else calendarChart(fig, data.calendar);

    fig = card('weekly-workouts', 'Workouts per week', 'Last 26 complete weeks');
    if (!hasData(weeks.map((w) => w.workouts))) empty(fig);
    else {
      seriesChart(fig, {
        title: 'Workouts per week', type: 'columns', labels: weekLabels,
        series: [{ kind: 'bar', values: weeks.map((w) => w.workouts) }],
        y: { zero: true, integer: true, format: (v) => nf.format(v) },
        tooltip: (i) => ({ head: weekLabel(weeks[i].w), rows: [
          { value: weeks[i].workouts == null ? '–' : plural(weeks[i].workouts, 'workout'), key: 'bar' },
          { value: weeks[i].hours == null ? '–' : `${nf1.format(weeks[i].hours)} h`, label: 'training' }] }),
        summary: 'Number of workouts in each of the last 26 complete weeks.',
        table: { head: ['Week of', 'Workouts', 'Hours'], rows: weeks.map((w) => [dayShort(w.w), num(w.workouts), w.hours == null ? '–' : nf1.format(w.hours)]) },
      });
    }

    const recent = months.slice(-12);
    fig = card('sports', 'By sport', recent.length ? `Sessions, ${monthLong(recent[0].m)} to ${monthLong(recent[recent.length - 1].m)}` : '');
    const counts = new Map();
    for (const month of recent) {
      for (const group in month.types || {}) counts.set(group, (counts.get(group) || 0) + month.types[group]);
    }
    const ranked = [...counts].sort((a, b) => b[1] - a[1]).map(([group, n]) => [GROUP_NAMES[group] || group, n]);
    if (!ranked.length) empty(fig);
    else {
      rankedChart(fig, ranked, 'session');
      dataTable(fig, 'Sessions by sport', ['Sport', 'Sessions'], ranked.map(([name, n]) => [name, nf.format(n)]).reverse());
    }

    fig = card('monthly-workouts', 'Workouts per month', since);
    if (!hasData(months.map((r) => r.workouts))) empty(fig);
    else {
      seriesChart(fig, {
        title: 'Workouts per month', type: 'columns', labels: monthLabels, labelGap: 44,
        series: [{ kind: 'bar', values: months.map((r) => r.workouts) }],
        y: { zero: true, integer: true, format: (v) => nf.format(v) },
        tooltip: (i) => ({ head: monthLong(months[i].m), rows: [
          { value: months[i].workouts == null ? '–' : plural(months[i].workouts, 'workout'), key: 'bar' },
          { value: months[i].hours == null ? '–' : `${nf1.format(months[i].hours)} h`, label: 'training' }] }),
        summary: `Number of workouts each month, ${since.toLowerCase()}.`,
        table: { head: ['Month', 'Workouts', 'Hours'], rows: months.map((r) => [monthLong(r.m), num(r.workouts), r.hours == null ? '–' : nf1.format(r.hours)]) },
      });
    }

    // Running --------------------------------------------------------
    fig = card('run-weekly-km', 'Running distance', 'Per week, last 26 complete weeks, in km');
    if (!hasData(weeks.map((w) => w.run_km))) empty(fig);
    else {
      seriesChart(fig, {
        title: 'Running distance per week', type: 'columns', labels: weekLabels,
        series: [{ kind: 'bar', values: weeks.map((w) => w.run_km) }],
        y: { zero: true, format: (v) => nf.format(v) },
        tooltip: (i) => ({ head: weekLabel(weeks[i].w), rows: [
          { value: km(weeks[i].run_km), label: 'run', key: 'bar' },
          { value: weeks[i].pace_s == null ? '–' : `${pace(weeks[i].pace_s)} /km`, label: 'average pace' }] }),
        summary: 'Kilometres run in each of the last 26 complete weeks.',
        table: { head: ['Week of', 'Distance', 'Average pace'], rows: weeks.map((w) => [dayShort(w.w), km(w.run_km), w.pace_s == null ? '–' : `${pace(w.pace_s)} /km`]) },
      });
    }

    fig = card('run-pace', 'Running pace', 'Weekly average, minutes per km (lower is faster)');
    if (!hasData(weeks.map((w) => w.pace_s))) empty(fig, 'Not enough running yet.');
    else {
      seriesChart(fig, {
        title: 'Average running pace per week', type: 'lines', labels: weekLabels,
        series: [{ kind: 'line', values: weeks.map((w) => w.pace_s) }],
        y: { steps: [15, 30, 60, 120], format: (v) => pace(v) },
        rightLabel: true, endLabel: (v) => `${pace(v)} /km`,
        tooltip: (i) => ({ head: weekLabel(weeks[i].w), rows: [
          { value: weeks[i].pace_s == null ? '–' : `${pace(weeks[i].pace_s)} /km`, label: 'average pace', key: 'line' },
          { value: km(weeks[i].run_km), label: 'run' }] }),
        summary: 'Average running pace in each of the last 26 complete weeks. Weeks under 3 km are left out.',
        table: { head: ['Week of', 'Average pace', 'Distance'], rows: weeks.map((w) => [dayShort(w.w), w.pace_s == null ? '–' : `${pace(w.pace_s)} /km`, km(w.run_km)]) },
      });
    }

    fig = card('run-monthly-km', 'Running distance by month', `${since}, in km`);
    if (!hasData(months.map((r) => r.run_km))) empty(fig);
    else {
      seriesChart(fig, {
        title: 'Running distance per month', type: 'columns', labels: monthLabels, labelGap: 44,
        series: [{ kind: 'bar', values: months.map((r) => r.run_km) }],
        y: { zero: true, format: (v) => nf.format(v) },
        tooltip: (i) => ({ head: monthLong(months[i].m), rows: [{ value: km(months[i].run_km), label: 'run', key: 'bar' }] }),
        summary: `Kilometres run each month, ${since.toLowerCase()}.`,
        table: { head: ['Month', 'Distance'], rows: months.map((r) => [monthLong(r.m), km(r.run_km)]) },
      });
    }

    startDrawing();
  }

  loadData()
    .then((data) => {
      if (!data) return showStatus('No data yet. Check back tomorrow.');
      if (data.enc) return unlock(data);
      return render(data);
    })
    .catch(() => showStatus('The data couldn’t be loaded.'));
})();
