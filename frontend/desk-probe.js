/** Opt-in desk probe: display refresh + keyboard/pointer timing. Never records key characters. */
(function (global) {
  const state = {
    active: false,
    samples: [],
    frames: [],
    lastKeyTs: null,
    rafId: null,
    summary: null,
  };

  function estimateRefresh(deltas) {
    if (!deltas.length) return null;
    const mid = deltas.slice().sort((a, b) => a - b)[Math.floor(deltas.length / 2)];
    return mid > 0 ? 1000 / mid : null;
  }

  function onFrame(ts) {
    if (!state.active) return;
    const prev = state.frames.length ? state.frames[state.frames.length - 1] : null;
    state.frames.push(ts);
    if (prev != null) {
      const delta = ts - prev;
      const hz = estimateRefresh(state.frames.slice(-120).map((t, i, arr) => (i ? t - arr[i - 1] : null)).filter(Boolean));
      state.samples.push({ kind: 'frame', t: ts, frame_delta_ms: delta, refresh_hz: hz });
    }
    if (state.lastKeyTs != null) {
      const keyToFrame = ts - state.lastKeyTs;
      state.samples.push({ kind: 'keydown', t: ts, key_to_frame_ms: keyToFrame, refresh_hz: estimateRefresh(state.frames.slice(-60).map((t, i, arr) => (i ? t - arr[i - 1] : null)).filter(Boolean)) });
      state.lastKeyTs = null;
      const flash = document.getElementById('deskFlash');
      if (flash) {
        flash.classList.add('on');
        requestAnimationFrame(() => flash.classList.remove('on'));
      }
    }
    state.rafId = requestAnimationFrame(onFrame);
  }

  function onKeyDown(e) {
    if (!state.active) return;
    // Timing only — never store e.key / e.code.
    if (e.repeat) return;
    state.lastKeyTs = performance.now();
  }

  async function onTradeClick() {
    if (!state.active) return;
    const t0 = performance.now();
    state.samples.push({ kind: 'pointerdown', t: t0 });
    try {
      await fetch('/api/hardware-latency/ack', { method: 'POST' });
      const rtt = performance.now() - t0;
      state.samples.push({ kind: 'ack', t: performance.now(), click_to_ack_ms: rtt });
    } catch (_) {
      /* ack failure still leaves pointer sample */
    }
  }

  function start() {
    if (state.active) return;
    state.active = true;
    state.samples = [];
    state.frames = [];
    state.lastKeyTs = null;
    window.addEventListener('keydown', onKeyDown, { passive: true });
    state.rafId = requestAnimationFrame(onFrame);
  }

  function stop() {
    state.active = false;
    window.removeEventListener('keydown', onKeyDown);
    if (state.rafId) cancelAnimationFrame(state.rafId);
    state.rafId = null;
  }

  async function submit(runId) {
    const payload = {
      samples: state.samples.slice(-5000),
      run_id: runId || null,
      workstation: (navigator.userAgentData && navigator.userAgentData.platform) || navigator.platform || 'browser',
    };
    const r = await fetch('/api/hardware-latency', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    if (!r.ok) {
      const e = await r.json().catch(() => ({}));
      throw Error(typeof e.detail === 'string' ? e.detail : 'Hardware probe upload failed');
    }
    state.summary = await r.json();
    return state.summary;
  }

  function liveStats() {
    const deltas = [];
    for (let i = 1; i < state.frames.length; i++) deltas.push(state.frames[i] - state.frames[i - 1]);
    const hz = estimateRefresh(deltas.slice(-90));
    const keySamples = state.samples.filter(s => s.key_to_frame_ms != null).map(s => s.key_to_frame_ms);
    const ackSamples = state.samples.filter(s => s.click_to_ack_ms != null).map(s => s.click_to_ack_ms);
    const median = arr => arr.length ? arr.slice().sort((a, b) => a - b)[Math.floor(arr.length / 2)] : null;
    return {
      active: state.active,
      samples: state.samples.length,
      refresh_hz: hz,
      frame_budget_ms: hz ? 1000 / hz : null,
      key_to_frame_p50: median(keySamples),
      click_to_ack_p50: median(ackSamples),
    };
  }

  global.DeskProbe = { start, stop, submit, onTradeClick, liveStats, get summary() { return state.summary; } };
})(window);
