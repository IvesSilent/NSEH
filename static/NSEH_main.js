// ════════════════════════════════════════
// NSEH Main v2 - Enhanced UX
// ════════════════════════════════════════

let population_data = [];
let lastScrollTime = 0;
const SCROLL_INTERVAL = 15000;

// ── Toast 通知 ─────────────────────────────────
function showToast(msg, type = 'info') {
  const existing = document.querySelector('.toast');
  if (existing) existing.remove();
  const t = document.createElement('div');
  t.className = `toast ${type}`;
  t.textContent = msg;
  document.body.appendChild(t);
  setTimeout(() => t.remove(), 3500);
}

// ── DOM Ready ──────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  initTabs();
  initSettingPage();
  initEvolutionPage();
  initResultsPage();

  setInterval(fetchPopulationData, 2000);
  setInterval(checkEvolutionStatus, 2000);

  document.getElementById('logout-btn')?.addEventListener('click', () => {
    fetch('/api/logout', { method: 'POST' })
      .then(r => r.json())
      .then(d => { if (d.status === 'success') window.location.href = '/login'; });
  });

  document.getElementById('theme-toggle')?.addEventListener('click', () => {
    const cur = document.documentElement.getAttribute('data-theme');
    const next = cur === 'light' ? null : 'light';
    document.documentElement.setAttribute('data-theme', next);
    localStorage.setItem('theme', next);
  });

  const saved = localStorage.getItem('theme');
  if (saved) document.documentElement.setAttribute('data-theme', saved);
});

// ── Tab System ─────────────────────────────────
function initTabs() {
  const tabs = document.querySelectorAll('.tab');
  tabs.forEach((tab, i) => {
    tab.addEventListener('click', (e) => {
      if (tab.id !== 'setting-tab' && !validateSettings()) {
        e.preventDefault();
        return;
      }
      tabs.forEach(t => t.classList.remove('active'));
      document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
      tab.classList.add('active');
      document.querySelectorAll('.page')[i].classList.add('active');
    });
  });
}

// ── Validation ─────────────────────────────────
function validateSettings() {
  const fields = {
    population_capacity: parseInt,
    num_generations: parseInt,
    num_mutation: parseInt,
    num_hybridization: parseInt,
    num_reflection: parseInt
  };
  for (const [id, fn] of Object.entries(fields)) {
    const val = fn(document.getElementById(id)?.value);
    if (isNaN(val) || val < 0) {
      showToast('进化参数需为非负整数，请检查设置', 'error');
      return false;
    }
  }
  const apiKey = document.getElementById('api_key')?.value.trim();
  const baseUrl = document.getElementById('base_url')?.value.trim();
  const model = document.getElementById('llm_model')?.value.trim();
  if (!apiKey || !baseUrl || !model) {
    showToast('LLM 配置不完整（API Key / Base URL / Model）', 'error');
    return false;
  }
  return true;
}

// ── Settings Page ──────────────────────────────
function initSettingPage() {
  // 添加参数/返回值
  document.getElementById('add_arg_btn')?.addEventListener('click', () => {
    const c = document.getElementById('fun_args_container');
    const el = document.createElement('div');
    el.className = 'arg-item'; el.contentEditable = true; el.textContent = '新参数';
    c.appendChild(el); el.focus();
    selectArgText(el);
  });
  document.getElementById('add_return_btn')?.addEventListener('click', () => {
    const c = document.getElementById('fun_return_container');
    const el = document.createElement('div');
    el.className = 'arg-item'; el.contentEditable = true; el.textContent = '新返回值';
    c.appendChild(el); el.focus();
    selectArgText(el);
  });

  // 空值删除
  document.addEventListener('click', e => {
    if (e.target.classList.contains('arg-item') && e.target.textContent.trim() === '') {
      e.target.remove();
    }
  });

  // 浏览
  document.getElementById('browse_problem_path')?.addEventListener('click', () => {
    document.getElementById('problem_path_file')?.click();
  });
  document.getElementById('problem_path_file')?.addEventListener('change', e => {
    if (e.target.files?.[0]) {
      document.getElementById('problem_path').value = e.target.files[0].path;
    }
  });

  // 开始进化
  document.getElementById('start-evolution-btn')?.addEventListener('click', startEvolution);
}

function selectArgText(el) {
  const range = document.createRange();
  range.selectNodeContents(el);
  const sel = window.getSelection();
  sel.removeAllRanges(); sel.addRange(range);
}

// ── Evolution Flow ─────────────────────────────
function startEvolution() {
  if (!validateSettings()) return;

  const config = {
    population_capacity: parseIntSafe('population_capacity', 7),
    num_generations: parseIntSafe('num_generations', 5),
    num_mutation: parseIntSafe('num_mutation', 3),
    num_hybridization: parseIntSafe('num_hybridization', 3),
    num_reflection: parseIntSafe('num_reflection', 3),
    api_key: val('api_key'),
    base_url: val('base_url'),
    llm_model: val('llm_model'),
    problem: val('problem'),
    fun_name: val('fun_name'),
    fun_args: collectArgs('fun_args_container'),
    fun_return: collectArgs('fun_return_container'),
    fun_notes: val('fun_notes'),
    ascend: document.getElementById('ascend')?.value === 'true',
    problem_path: val('problem_path'),
    train_data: val('train_data'),
    train_solution: val('train_solution')
  };

  localStorage.setItem('nseh_config', JSON.stringify(config));

  fetch('/api/save_config', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(config)
  })
  .then(r => r.json())
  .then(d => {
    if (d.status === 'success') {
      showToast('配置保存成功，开始进化', 'success');
      document.getElementById('evolution-tab')?.click();
      return fetch('/api/start_evolution', { method: 'POST' });
    }
    throw new Error(d.message || '保存配置失败');
  })
  .then(r => r.json())
  .then(d => {
    if (d.status !== 'success') throw new Error(d.message);
  })
  .catch(err => showToast(err.message, 'error'));
}

function parseIntSafe(id, def) {
  const v = parseInt(document.getElementById(id)?.value);
  return isNaN(v) ? def : v;
}
function val(id) { return document.getElementById(id)?.value || ''; }
function collectArgs(id) {
  return Array.from(document.querySelectorAll(`#${id} .arg-item`)).map(el => el.textContent.trim());
}

// ── Evolution Page ─────────────────────────────
function initEvolutionPage() {
  fetch('/api/get_population_data')
    .then(r => r.json())
    .then(d => { population_data = d.population_data; renderPopulationData(d.population_data, d.current_population_index); })
    .catch(() => {});

  document.getElementById('pause-evolution-btn')?.addEventListener('click', () => {
    fetch('/api/pause_evolution', { method: 'POST' });
  });
  document.getElementById('resume-evolution-btn')?.addEventListener('click', () => {
    fetch('/api/resume_evolution', { method: 'POST' });
  });
  document.getElementById('stop-evolution-btn')?.addEventListener('click', () => {
    fetch('/api/stop_evolution', { method: 'POST' }).then(() => {
      document.getElementById('setting-tab')?.click();
      showToast('进化已终止', 'warning');
    });
  });
  document.getElementById('edit-prompt-btn')?.addEventListener('click', () => {
    fetch('/api/get_prompt_template')
      .then(r => r.json())
      .then(d => {
        showPromptEditCard(d);
        fetch('/api/pause_evolution', { method: 'POST' });
      });
  });
}

function fetchPopulationData() {
  fetch('/api/get_population_data')
    .then(r => r.json())
    .then(d => {
      population_data = d.population_data;
      renderPopulationData(d.population_data, d.current_population_index);
    })
    .catch(() => {});
}

function checkEvolutionStatus() {
  fetch('/api/check_evolution_status')
    .then(r => r.json())
    .then(d => {
      if (d.status === 'completed') {
        showToast('🎉 进化完成！', 'success');
        document.getElementById('results-tab')?.click();
      }
    })
    .catch(() => {});
}

// ── Render Population ──────────────────────────
function renderPopulationData(data, currentIdx) {
  const container = document.getElementById('population-container');
  if (!container || !data?.length) return;

  container.innerHTML = data.map((pop, gi) => renderPopCard(pop, gi)).join('');
}

function renderPopCard(pop, genIdx) {
  const statusClass = getStatusClass(pop.status);
  const best = pop.best_objective !== null && pop.best_objective !== 'null'
    ? parseFloat(pop.best_objective).toFixed(2) : '—';

  const posFeats = (pop.memory?.positive_features || []).map(f => formatFeature(f)).join('\n');
  const negFeats = (pop.memory?.negative_features || []).map(f => formatFeature(f)).join('\n');

  return `
    <div class="population-card">
      <div class="population-header">
        <h3>${pop.title || `第${pop.index}代`}</h3>
        <span class="population-status ${statusClass}">${pop.status || '等待中'}</span>
      </div>
      <div class="population-stats">
        <div class="stat"><strong>最优适应度：</strong>${best}</div>
        ${posFeats ? `<div class="stat"><strong>积极特征：</strong><br>${posFeats}</div>` : ''}
        ${negFeats ? `<div class="stat"><strong>消极特征：</strong><br>${negFeats}</div>` : ''}
      </div>
      <div class="heuristics-container">${renderHeuristics(pop.heuristics || [])}</div>
    </div>
  `;
}

function getStatusClass(status) {
  if (!status) return '';
  if (status.includes('完成') || status === '已完成') return 'completed';
  if (status === '已暂停') return 'paused';
  if (status.includes('进行') || status === '正在生成') return 'running';
  return '';
}

function formatFeature(f) {
  if (Array.isArray(f)) {
    return f.map(t => `<span class="tag">${escapeHtml(t)}</span>`).join(' + ');
  }
  return escapeHtml(String(f));
}

function renderHeuristics(heuristics) {
  if (!heuristics?.length) return '<div class="empty-heuristics">暂无启发式</div>';

  const bestObj = Math.min(...heuristics.filter(h => h.objective !== null && h.objective !== 'null' && h.objective !== Infinity).map(h => parseFloat(h.objective)));

  return heuristics.map((h, i) => {
    const obj = h.objective !== null && h.objective !== 'null' && h.objective !== Infinity
      ? parseFloat(h.objective).toFixed(2) : '∞';
    const isBest = parseFloat(h.objective) === bestObj;
    const tags = h.tags || [];
    const tagsHtml = tags.length > 0
      ? tags.map(t => `<span class="tag">${escapeHtml(t)}</span>`).join('')
      : (h.feature ? `<span class="tag">${escapeHtml(h.feature)}</span>` : '');

    return `
      <div class="heuristic-card ${isBest ? 'best' : ''}" onclick="showHeuristicDetails(${h.index || i + 1})">
        <div class="rank-badge">${i + 1}</div>
        <h4>启发式 ${h.index || i + 1}</h4>
        <div class="heuristic-feature">${tagsHtml || '—'}</div>
        <div class="heuristic-objective">适应度: ${obj}</div>
      </div>
    `;
  }).join('');
}

function showHeuristicDetails(index) {
  const pop = population_data[population_data.length - 1];
  if (!pop) return;
  const h = pop.heuristics?.find(x => x.index === index);
  if (!h) { showToast('未找到启发式详情', 'error'); return; }

  document.getElementById('detail-concept').textContent = h.concept || '—';
  document.getElementById('detail-objective').textContent =
    (h.objective !== null && h.objective !== 'null' && h.objective !== Infinity)
      ? parseFloat(h.objective).toFixed(4) : '∞';
  document.getElementById('detail-feature').textContent = (h.tags?.length ? h.tags.join(' + ') : h.feature) || '—';
  document.getElementById('detail-algorithm').textContent = h.algorithm || '—';

  document.getElementById('heuristic-details-container').style.display = 'block';
  document.body.classList.add('details-visible');
}

function closeDetailsCard() {
  document.getElementById('heuristic-details-container').style.display = 'none';
  document.body.classList.remove('details-visible');
}

function copyAlgorithm() {
  const code = document.getElementById('detail-algorithm')?.textContent;
  if (!code) return;
  navigator.clipboard.writeText(code)
    .then(() => {
      const msg = document.getElementById('copy-success');
      if (msg) { msg.style.opacity = '1'; setTimeout(() => msg.style.opacity = '0', 2000); }
    })
    .catch(() => showToast('复制失败', 'error'));
}

// ── Prompt Edit Card ───────────────────────────
function showPromptEditCard(data) {
  const existing = document.querySelector('.prompt-edit-card');
  if (existing) existing.remove();

  const html = `
    <div class="prompt-edit-card">
      <div class="details-header">
        <h3>自定义提示词</h3>
        <button class="close-btn" onclick="closePromptEditCard()">关闭</button>
      </div>
      <div class="form-group">
        <label>函数要求</label>
        <textarea id="fun_requirement" rows="3">${escapeHtml(data.fun_requirement)}</textarea>
      </div>
      <div class="form-group">
        <label>MUTATION 突变</label>
        <textarea id="strategy_MUT" rows="3">${escapeHtml(data.strategy_MUT)}</textarea>
      </div>
      <div class="form-group">
        <label>HYBRIDIZATION 杂交</label>
        <textarea id="strategy_HYB" rows="3">${escapeHtml(data.strategy_HYB)}</textarea>
      </div>
      <div class="form-group">
        <label>OPTIMIZATION 优化</label>
        <textarea id="strategy_OPT" rows="3">${escapeHtml(data.strategy_OPT)}</textarea>
      </div>
      <div class="form-group">
        <label>分析过程</label>
        <textarea id="analyze" rows="3">${escapeHtml(data.analyze)}</textarea>
      </div>
      <div style="display:flex;justify-content:center;gap:12px;margin-top:16px;">
        <button class="control-btn resume-btn" onclick="updatePromptTemplate()">确认</button>
        <button class="control-btn" onclick="closePromptEditCard()">取消</button>
      </div>
    </div>
  `;

  document.body.insertAdjacentHTML('beforeend', html);
  document.body.classList.add('prompt-edit-visible');
}

function closePromptEditCard() {
  document.querySelector('.prompt-edit-card')?.remove();
  document.body.classList.remove('prompt-edit-visible');
}

function updatePromptTemplate() {
  const data = {
    fun_requirement: document.getElementById('fun_requirement')?.value || '',
    strategy_MUT: document.getElementById('strategy_MUT')?.value || '',
    strategy_HYB: document.getElementById('strategy_HYB')?.value || '',
    strategy_OPT: document.getElementById('strategy_OPT')?.value || '',
    analyze: document.getElementById('analyze')?.value || ''
  };

  fetch('/api/update_prompt_template', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  })
  .then(r => r.json())
  .then(d => {
    if (d.status === 'success') {
      showToast('提示词已更新', 'success');
      closePromptEditCard();
    } else throw new Error(d.message);
  })
  .catch(err => showToast(err.message, 'error'));
}

// ── Results Page ───────────────────────────────
let resultsChart = null;

function initResultsPage() {
  document.getElementById('open-results-btn')?.addEventListener('click', () => {
    fetch('/api/open_results_directory', { method: 'GET' })
      .then(r => r.json())
      .then(d => { if (d.status !== 'success') showToast(d.message, 'error'); })
      .catch(() => showToast('无法打开目录', 'error'));
  });

  document.getElementById('open-rank-btn')?.addEventListener('click', () => {
    window.location.href = '/rank';
  });
}

function renderChart() {
  if (!population_data?.length) return;

  const labels = population_data.map(p => `${p.index}`);
  const objectives = population_data.map(p => {
    const o = p.best_objective;
    return (o !== null && o !== 'null' && o !== undefined) ? parseFloat(o) : null;
  }).filter(o => o !== null);

  if (!objectives.length) return;

  const canvas = document.getElementById('results-chart');
  if (!canvas) return;

  if (resultsChart) resultsChart.destroy();

  const isDark = !document.documentElement.getAttribute('data-theme');

  resultsChart = new Chart(canvas, {
    type: 'line',
    data: {
      labels: population_data.filter((_, i) => objectives[i] !== undefined).map((_, i) => i),
      datasets: [{
        label: '最优适应度',
        data: objectives,
        borderColor: '#f0883e',
        backgroundColor: 'rgba(240,136,62,0.1)',
        fill: true,
        tension: 0.3,
        pointRadius: 5,
        pointHoverRadius: 7,
        pointBackgroundColor: objectives.map((o, i, arr) =>
          i === arr.length - 1 ? '#3fb950' : '#f0883e'
        ),
        pointBorderColor: isDark ? '#0d1117' : '#ffffff',
        pointBorderWidth: 2,
        borderWidth: 2.5
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { labels: { color: isDark ? '#8b949e' : '#656d76', font: { size: 12 } } }
      },
      scales: {
        x: {
          title: { display: true, text: '进化代数', color: isDark ? '#8b949e' : '#656d76' },
          ticks: { color: isDark ? '#8b949e' : '#656d76' },
          grid: { color: isDark ? 'rgba(48,54,61,0.3)' : 'rgba(208,215,222,0.3)' }
        },
        y: {
          title: { display: true, text: '适应度', color: isDark ? '#8b949e' : '#656d76' },
          ticks: { color: isDark ? '#8b949e' : '#656d76' },
          grid: { color: isDark ? 'rgba(48,54,61,0.3)' : 'rgba(208,215,222,0.3)' }
        }
      }
    }
  });
}

// ── Helpers ────────────────────────────────────
function escapeHtml(str) {
  if (!str) return '';
  const d = document.createElement('div');
  d.textContent = str;
  return d.innerHTML;
}

// 当切换结果标签页时更新图表
const origInit = initResultsPage;
initResultsPage = () => {
  origInit();
  renderChart();
};
