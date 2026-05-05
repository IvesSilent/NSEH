// ════════════════════════════════════════
// NSEH Main v4 - Robustness & UX Enhanced
// ════════════════════════════════════════

let population_data = [];
let lastScrollTime = 0;
const SCROLL_INTERVAL = 15000;
let evolutionTimer = null;

// ── Toast 通知（堆叠版）───────────────────
const toasts = new Set();
function showToast(msg, type = 'info', duration = 3500) {
  // 清理重复的 toast
  toasts.forEach(t => { if (t.textContent === msg) { t.remove(); toasts.delete(t); } });

  const t = document.createElement('div');
  t.className = `toast ${type}`;
  t.textContent = msg;
  document.body.appendChild(t);
  toasts.add(t);

  // 等一帧确保 DOM 渲染完成，再排位
  requestAnimationFrame(() => repositionToasts());

  // 自动淡出
  setTimeout(() => {
    t.style.opacity = '0';
    t.style.transform = 'translateX(-50%) translateY(-10px)';
    setTimeout(() => {
      t.remove();
      toasts.delete(t);
      repositionToasts();
    }, 300);
  }, duration);
}

function repositionToasts() {
  const list = Array.from(toasts);
  let bottom = 30;
  list.forEach(t => {
    t.style.bottom = bottom + 'px';
    bottom += t.offsetHeight + 10;
  });
}

// ── DOM Ready ──────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  initTabs();
  initSettingPage();
  initEvolutionPage();
  initResultsPage();
  initKeyboardShortcuts();
  initLoadPopulationUI();

  setInterval(fetchPopulationData, 2000);
  setInterval(checkEvolutionStatus, 2000);
  setInterval(updateEvolutionTimer, 1000);

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
  if (saved) {
    document.documentElement.setAttribute('data-theme', saved);
    // 恢复主题图标
    const btn = document.getElementById('theme-toggle');
    if (btn) {
      btn.querySelector('.theme-sun').style.display = saved === 'light' ? 'none' : '';
      btn.querySelector('.theme-moon').style.display = saved === 'light' ? '' : 'none';
    }
  }

  // 尝试恢复上次配置
  restoreCachedConfig();
});

// ── 键盘快捷键 ────────────────────────────────
function initKeyboardShortcuts() {
  document.addEventListener('keydown', (e) => {
    // Ctrl+Enter 或 Cmd+Enter → 开始进化
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
      const settingPage = document.getElementById('setting-page');
      if (settingPage?.classList.contains('active')) {
        e.preventDefault();
        startEvolution();
      }
    }
    // Escape → 关闭所有弹窗
    if (e.key === 'Escape' || e.key === 'Esc') {
      closeDetailsCard();
      closePromptEditCard();
      closeSelfAdaptModal();
      closeFeatureTree();
    }
    // Ctrl+S → 保存配置
    if ((e.ctrlKey || e.metaKey) && e.key === 's') {
      e.preventDefault();
      showToast('配置保存在会话中，开始进化后自动生效', 'info');
    }
    // Escape → 关闭特征树
    if (e.key === 'Escape' || e.key === 'Esc') {
      const treeModal = document.getElementById('feature-tree-modal');
      if (treeModal && treeModal.style.display === 'flex') closeFeatureTree();
    }
  });
}

// ── 恢复缓存配置 ────────────────────────────
function restoreCachedConfig() {
  fetch('/api/get_cached_config')
    .then(r => r.json())
    .then(d => {
      const cfg = d.config;
      if (!cfg || !cfg.problem_path) return;
      // 只恢复非 API Key 的字段
      if (cfg.population_capacity) document.getElementById('population_capacity').value = cfg.population_capacity;
      if (cfg.num_generations) document.getElementById('num_generations').value = cfg.num_generations;
      if (cfg.num_mutation) document.getElementById('num_mutation').value = cfg.num_mutation;
      if (cfg.num_hybridization) document.getElementById('num_hybridization').value = cfg.num_hybridization;
      if (cfg.num_reflection) document.getElementById('num_reflection').value = cfg.num_reflection;
      if (cfg.base_url) document.getElementById('base_url').value = cfg.base_url;
      if (cfg.llm_model) {
        const sel = document.getElementById('llm_model_select');
        if (sel) {
          if ([...sel.options].some(o => o.value === cfg.llm_model)) {
            sel.value = cfg.llm_model;
          } else {
            document.getElementById('llm_model_custom').value = cfg.llm_model;
            document.getElementById('llm_model_custom').style.display = 'block';
          }
          onLLMModelChange();
        }
      }
    })
    .catch(() => {});
}

// ── Tab System ─────────────────────────────────
function initTabs() {
  const tabs = document.querySelectorAll('.tab');
  tabs.forEach((tab, i) => {
    tab.addEventListener('click', (e) => {
      if (tab.id !== 'setting-tab' && !validateSettings()) {
        e.preventDefault();
        showToast('请先完成设置再切换页面', 'warning');
        return;
      }
      tabs.forEach(t => t.classList.remove('active'));
      document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
      tab.classList.add('active');
      document.querySelectorAll('.page')[i].classList.add('active');

      if (tab.id === 'results-tab') {
        setTimeout(() => { renderChart(); renderTop3Chart(); }, 100);
      }
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
  return true;
}

// ── Problem Selector ────────────────────────────
function onProblemChange() {
  const sel = document.getElementById('problem_selector');
  if (!sel || !sel.value) return;
  const pid = sel.value;
  showToast(`正在加载 ${pid} 的配置...`, 'info');
  fetch('/api/get_problem_config', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ problem_id: pid })
  })
  .then(r => r.json())
  .then(d => {
    const cfg = d.config;
    if (!cfg) throw new Error(d.message || '获取配置失败');
    document.getElementById('problem').value = cfg.problem || '';
    document.getElementById('fun_name').value = cfg.fun_name || '';
    document.getElementById('fun_notes').value = cfg.fun_notes || '';
    document.getElementById('problem_path').value = cfg.problem_path || '';
    document.getElementById('train_data').value = cfg.train_data || '';
    document.getElementById('train_solution').value = cfg.train_solution || '';

    const asc = document.getElementById('ascend');
    if (asc) asc.value = cfg.ascend ? 'true' : 'false';

    const argsContainer = document.getElementById('fun_args_container');
    if (argsContainer && cfg.fun_args) {
      argsContainer.innerHTML = cfg.fun_args.map(a =>
        `<div class="arg-item" contenteditable="true">${escapeHtml(a)}</div>`
      ).join('');
    }

    const retContainer = document.getElementById('fun_return_container');
    if (retContainer && cfg.fun_return) {
      retContainer.innerHTML = cfg.fun_return.map(r =>
        `<div class="arg-item" contenteditable="true">${escapeHtml(r)}</div>`
      ).join('');
    }

    showToast(`已切换到 ${cfg.name || pid}`, 'success');
  })
  .catch(err => showToast('[FAIL] 加载问题配置失败: ' + err.message, 'error'));
}

// ── LLM Preset Loader ──────────────────────────
function initLLMPresets() {
  fetch('/api/get_llm_presets')
    .then(r => r.json())
    .then(d => {
      const sel = document.getElementById('llm_model_select');
      if (!sel || !d.presets) return;

      const groups = {};
      d.presets.forEach(p => {
        if (!groups[p.provider]) groups[p.provider] = [];
        groups[p.provider].push(p);
      });

      let html = '';
      for (const [provider, models] of Object.entries(groups)) {
        html += `<optgroup label="${escapeHtml(provider)}">`;
        models.forEach(m => {
          html += `<option value="${escapeHtml(m.id)}" data-url="${escapeHtml(m.base_url)}">${escapeHtml(m.name)}</option>`;
        });
        html += '</optgroup>';
      }
      sel.innerHTML = html;
      sel.value = 'deepseek-chat';
      onLLMModelChange();
    })
    .catch(() => {});
}

function onLLMModelChange() {
  const sel = document.getElementById('llm_model_select');
  const customInput = document.getElementById('llm_model_custom');
  const urlInput = document.getElementById('base_url');
  const hint = document.getElementById('llm_model_hint');
  if (!sel) return;

  const selected = sel.options[sel.selectedIndex];
  const isCustom = sel.value === 'custom';

  if (isCustom) {
    customInput.style.display = 'block';
    customInput.focus();
    if (hint) hint.textContent = '输入自定义模型名称，并手动填写 BASE_URL';
  } else {
    customInput.style.display = 'none';
    if (urlInput && selected) {
      const dataUrl = selected.getAttribute('data-url');
      if (dataUrl) urlInput.value = dataUrl;
    }
    if (hint) hint.textContent = `模型: ${selected?.text || ''}`;
  }
}

function getCurrentModelName() {
  const sel = document.getElementById('llm_model_select');
  const customInput = document.getElementById('llm_model_custom');
  if (sel.value === 'custom') return customInput.value.trim() || 'custom-model';
  return sel.value;
}

// ── Settings Page ──────────────────────────────
function initSettingPage() {
  fetch('/api/get_problems')
    .then(r => r.json())
    .then(d => {
      const sel = document.getElementById('problem_selector');
      if (!sel || !d.problems) return;
      sel.innerHTML = d.problems.map(p =>
        `<option value="${escapeHtml(p.id)}">${escapeHtml(p.name)}</option>`
      ).join('');
      if (d.problems.length > 0) onProblemChange();
    })
    .catch(() => {});

  initLLMPresets();

  document.getElementById('llm_model_select')?.addEventListener('change', onLLMModelChange);
  document.getElementById('self-adapt-btn')?.addEventListener('click', () => {
    document.getElementById('self-adapt-modal').style.display = 'flex';
  });

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

  document.addEventListener('click', e => {
    if (e.target.classList.contains('arg-item') && e.target.textContent.trim() === '') {
      e.target.remove();
    }
  });

  document.getElementById('browse_problem_path')?.addEventListener('click', () => {
    document.getElementById('problem_path_file')?.click();
  });
  document.getElementById('problem_path_file')?.addEventListener('change', e => {
    const files = e.target.files;
    if (files?.length > 0) {
      // 尝试获取目录路径
      let dirPath = files[0].path || files[0].webkitRelativePath || '';
      if (!dirPath && files[0].webkitRelativePath) {
        // webkitRelativePath 格式: "problems/tsp/somefile.py" → 取目录前缀
        const parts = files[0].webkitRelativePath.split('/');
        if (parts.length > 1) parts.pop();
        dirPath = parts.join('/');
      }
      if (dirPath) {
        // 尝试转为相对路径（项目根目录为 NSEH/）
        const nsehIdx = dirPath.indexOf('NSEH');
        if (nsehIdx >= 0) {
          dirPath = dirPath.substring(nsehIdx + 5).replace(/^[\\\/]+/, '');
        }
        document.getElementById('problem_path').value = dirPath;
        showToast('已选择目录: ' + dirPath, 'success');
      } else {
        showToast('无法获取目录路径，请手动输入', 'warning');
      }
    }
    // 重置 input 以便同一目录可再次选择
    e.target.value = '';
  });

  document.getElementById('start-evolution-btn')?.addEventListener('click', startEvolution);
  setInterval(updateScenarioBadge, 3000);
}

function selectArgText(el) {
  const range = document.createRange();
  range.selectNodeContents(el);
  const sel = window.getSelection();
  sel.removeAllRanges(); sel.addRange(range);
}

// ── Scenario Badge ─────────────────────────────
function updateScenarioBadge() {
  const badge = document.getElementById('scenario-name-display');
  if (!badge) return;
  fetch('/api/get_current_problem')
    .then(r => r.json())
    .then(d => {
      if (d.status === 'success') badge.textContent = d.problem_name || d.problem_id || '未知';
    })
    .catch(() => {});
}

// ── Evolution Timer ────────────────────────────
function updateEvolutionTimer() {
  const timerEl = document.getElementById('evolution-timer');
  if (!timerEl) return;
  fetch('/api/get_evolution_progress')
    .then(r => r.json())
    .then(d => {
      if (d.status !== 'success') return;
      const { current_gen, total_gens, elapsed } = d;
      if (total_gens === 0) { timerEl.textContent = ''; return; }

      const mins = Math.floor(elapsed / 60);
      const secs = Math.floor(elapsed % 60);
      const timeStr = `${mins}:${String(secs).padStart(2, '0')}`;

      if (current_gen > 0) {
        timerEl.textContent = `⏱ ${current_gen}/${total_gens} 代 耗时 ${timeStr}`;
      } else {
        timerEl.textContent = `⏱ 初始化中... 耗时 ${timeStr}`;
      }
    })
    .catch(() => {});
}

// ── Confirmation Dialog ────────────────────────
function showConfirmDialog(msg, onConfirm) {
  const overlay = document.createElement('div');
  overlay.className = 'modal-overlay';
  overlay.innerHTML = `
    <div class="confirm-dialog">
      <p>${escapeHtml(msg)}</p>
      <div class="confirm-actions">
        <button class="control-btn resume-btn" id="confirm-yes">确认</button>
        <button class="control-btn" id="confirm-no">取消</button>
      </div>
    </div>
  `;
  document.body.appendChild(overlay);
  overlay.querySelector('#confirm-yes').onclick = () => { overlay.remove(); onConfirm(); };
  overlay.querySelector('#confirm-no').onclick = () => overlay.remove();
}

// ── Evolution Flow ─────────────────────────────
function startEvolution() {
  if (!validateSettings()) return;

  const modelName = getCurrentModelName();
  const problemSelect = document.getElementById('problem_selector');
  const problemName = problemSelect?.selectedOptions?.[0]?.text || '自定义';
  const problemId = problemSelect?.value || 'custom';

  const config = {
    population_capacity: parseIntSafe('population_capacity', 7),
    num_generations: parseIntSafe('num_generations', 5),
    num_mutation: parseIntSafe('num_mutation', 3),
    num_hybridization: parseIntSafe('num_hybridization', 3),
    num_reflection: parseIntSafe('num_reflection', 3),
    api_key: val('api_key'),
    base_url: val('base_url'),
    llm_model: modelName,
    problem: val('problem'),
    fun_name: val('fun_name'),
    fun_args: collectArgs('fun_args_container'),
    fun_return: collectArgs('fun_return_container'),
    fun_notes: val('fun_notes'),
    ascend: document.getElementById('ascend')?.value === 'true',
    problem_path: val('problem_path'),
    train_data: val('train_data'),
    train_solution: val('train_solution'),
    problem_name: problemName,
    problem_id: problemId
  };

  // 前端校验
  if (!config.api_key.trim()) return showToast('请填写 API Key', 'error');
  if (!config.base_url.trim()) return showToast('请填写 BASE_URL', 'error');
  if (!config.llm_model.trim()) return showToast('请选择或输入 LLM 模型名称', 'error');
  if (!config.problem_path.trim()) return showToast('请填写问题目录', 'error');

  localStorage.setItem('nseh_config', JSON.stringify(config));

  const btn = document.getElementById('start-evolution-btn');
  if (btn) { btn.disabled = true; btn.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="spin" style="vertical-align:-2px;margin-right:4px;"><path stroke-linecap="round" stroke-linejoin="round" d="M16.023 9.348h4.992v-.001M2.985 19.644v-4.992m0 0h4.992m-4.993 0l3.181 3.183a8.25 8.25 0 0013.803-3.7M4.031 9.865a8.25 8.25 0 0113.803-3.7l3.181 3.182"/></svg> 正在启动...'; }

  showToast('正在保存配置并启动进化...', 'info');

  fetch('/api/save_config', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(config)
  })
  .then(r => r.json())
  .then(d => {
    if (d.status === 'success') {
      showToast('配置保存成功，正在启动进化...', 'success');
      document.getElementById('evolution-tab')?.click();
      return fetch('/api/start_evolution', { method: 'POST' });
    }
    throw new Error(d.message || '保存配置失败');
  })
  .then(r => r.json())
  .then(d => {
    if (d.status !== 'success') throw new Error(d.message);
    showToast('进化已启动 ✓', 'success');
    if (btn) { btn.disabled = false; btn.textContent = '开始进化'; }
  })
  .catch(err => {
    showToast('[ERROR] ' + err.message, 'error', 5000);
    if (btn) { btn.disabled = false; btn.textContent = '开始进化'; }
  });
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

  updateScenarioBadge();

  document.getElementById('pause-evolution-btn')?.addEventListener('click', () => {
    fetch('/api/pause_evolution', { method: 'POST' });
    showToast('进化已暂停', 'warning');
  });
  document.getElementById('resume-evolution-btn')?.addEventListener('click', () => {
    fetch('/api/resume_evolution', { method: 'POST' });
    showToast('进化继续中...', 'success');
  });
  document.getElementById('stop-evolution-btn')?.addEventListener('click', () => {
    showConfirmDialog('确定要终止当前进化吗？所有当前代的进度将丢失。', () => {
      fetch('/api/stop_evolution', { method: 'POST' }).then(() => {
        document.getElementById('setting-tab')?.click();
        showToast('进化已终止', 'warning');
      });
    });
  });
  document.getElementById('show-feature-tree-btn')?.addEventListener('click', showFeatureTree);
  document.getElementById('edit-prompt-btn')?.addEventListener('click', () => {
    fetch('/api/get_prompt_template')
      .then(r => r.json())
      .then(d => {
        showPromptEditCard(d);
        fetch('/api/pause_evolution', { method: 'POST' });
      })
      .catch(err => showToast('获取提示词模板失败: ' + err.message, 'error'));
  });
}

function fetchPopulationData() {
  fetch('/api/get_population_data')
    .then(r => r.json())
    .then(d => {
      const prevLen = population_data?.length || 0;
      population_data = d.population_data;
      renderPopulationData(d.population_data, d.current_population_index);

      // 自动滚动到最新一代
      if (d.population_data?.length > prevLen) {
        scrollToLatestGeneration();
      }
    })
    .catch(() => {});
}

function scrollToLatestGeneration() {
  const container = document.getElementById('population-container');
  if (!container) return;
  const now = Date.now();
  if (now - lastScrollTime < SCROLL_INTERVAL) return;
  lastScrollTime = now;
  container.scrollTop = container.scrollHeight;
}

function checkEvolutionStatus() {
  fetch('/api/check_evolution_status')
    .then(r => r.json())
    .then(d => {
      if (d.status === 'completed') {
        showToast('进化完成 ✓ 切换到结果页查看', 'success', 5000);
        document.getElementById('results-tab')?.click();
      } else if (d.status === 'idle') {
        // noop
      }
    })
    .catch(() => {});
}

// ── Render Population ──────────────────────────
function renderPopulationData(data, currentIdx) {
  const container = document.getElementById('population-container');
  if (!container || !data?.length) return;
  container.innerHTML = data.map((pop, gi) => renderPopCard(pop, gi)).join('');
  // 恢复展开状态
  restoreFeatureCollapseStates();
}

function renderPopCard(pop, genIdx) {
  const statusClass = getStatusClass(pop.status);
  const best = pop.best_objective !== null && pop.best_objective !== 'null'
    ? parseFloat(pop.best_objective).toFixed(2) : '—';

  const posFeats = pop.memory?.positive_features || [];
  const negFeats = pop.memory?.negative_features || [];

  const posCollapse = renderFeatureCollapse('positive', '积极特征', posFeats);
  const negCollapse = renderFeatureCollapse('negative', '消极特征', negFeats);

  return `
    <div class="population-card gen-${pop.index}">
      <div class="population-header">
        <h3>${pop.title || `第${pop.index}代`}</h3>
        <span class="population-status ${statusClass}">${pop.status || '等待中'}</span>
      </div>
      <div class="population-stats">
        <div class="stat"><strong>最优适应度：</strong><span class="best-fitness">${best}</span></div>
      </div>
      <div class="population-features">
        ${posCollapse}
        ${negCollapse}
      </div>
      <div class="heuristics-container">${renderHeuristics(pop.heuristics || [])}</div>
    </div>
  `;
}

function renderFeatureCollapse(type, label, features) {
  if (!features || features.length === 0) return '';

  const collapseId = `feat-${type}-${Math.random().toString(36).slice(2, 8)}`;
  const colorClass = type === 'positive' ? 'feat-positive' : 'feat-negative';
  const icon = type === 'positive' ? '📈' : '📉';

  const featureLines = features.map(f => {
    if (Array.isArray(f) && f.length > 0) {
      return f.map(t => `<span class="tag">${escapeHtml(t)}</span>`).join('<span class="tag-plus"> + </span>');
    }
    return `<span class="tag">${escapeHtml(String(f))}</span>`;
  }).join('<br>');

  return `
    <div class="feat-section ${colorClass}">
      <div class="feat-header" onclick="toggleFeatureCollapse('${collapseId}')">
        <span class="feat-icon">${icon}</span>
        <span class="feat-label">${label}</span>
        <span class="feat-count">${features.length}</span>
        <span class="feat-chevron" id="chevron-${collapseId}">▶</span>
      </div>
      <div class="feat-body" id="${collapseId}">
        <div class="feat-list">${featureLines}</div>
      </div>
    </div>
  `;
}

// ── 特征列表展开状态同步 ───────────────────
let _featureOpenState = {};

function toggleFeatureCollapse(id) {
  const body = document.getElementById(id);
  const chevron = document.getElementById('chevron-' + id);
  if (!body || !chevron) return;
  body.classList.toggle('feat-open');
  const open = body.classList.contains('feat-open');
  chevron.textContent = open ? '▼' : '▶';
  _featureOpenState[id] = open;
}

function restoreFeatureCollapseStates() {
  Object.keys(_featureOpenState).forEach(id => {
    if (_featureOpenState[id]) {
      const body = document.getElementById(id);
      const chevron = document.getElementById('chevron-' + id);
      if (body && chevron) {
        body.classList.add('feat-open');
        chevron.textContent = '▼';
      }
    }
  });
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

  const objectives = heuristics
    .filter(h => h.objective !== null && h.objective !== 'null' && h.objective !== Infinity)
    .map(h => parseFloat(h.objective));
  const bestObj = objectives.length ? Math.min(...objectives) : null;

  return heuristics.map((h, i) => {
    const obj = h.objective !== null && h.objective !== 'null' && h.objective !== Infinity
      ? parseFloat(h.objective).toFixed(2) : '∞';
    const isBest = bestObj !== null && parseFloat(h.objective) === bestObj;
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

  document.getElementById('heuristic-detail-title').textContent = '启发式 ' + index;
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
    .catch(() => showToast('无法访问剪贴板，请手动复制', 'warning'));
}

// ── Prompt Edit Card ───────────────────────────
function showPromptEditCard(data) {
  const existing = document.querySelector('.prompt-edit-card');
  if (existing) existing.remove();

  const html = `
    <div class="prompt-edit-card">
      <div class="details-header">
        <h3>自定义提示词</h3>
        <button class="close-btn" onclick="closePromptEditCard(this)">关闭</button>
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
      <div class="prompt-edit-actions">
        <button class="control-btn resume-btn" onclick="updatePromptTemplate()">确认更新</button>
        <button class="control-btn" onclick="closePromptEditCard(this)">取消</button>
      </div>
    </div>
  `;

  document.body.insertAdjacentHTML('beforeend', html);
  document.body.classList.add('prompt-edit-visible');
}

function closePromptEditCard(el) {
  const card = document.querySelector('.prompt-edit-card');
  if (card) card.remove();
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
// ── Results Page ───────────────────────────────
let resultsChart = null;
let top3Chart = null;
let chartRefreshInterval = null;
let currentChartType = 'line';

function initResultsPage() {
  document.getElementById('open-results-btn')?.addEventListener('click', () => {
    fetch('/api/open_results_directory', { method: 'GET' })
      .then(r => r.json())
      .then(d => { if (d.status !== 'success') showToast(d.message, 'error'); })
      .catch(() => showToast('无法打开结果目录', 'error'));
  });
  document.getElementById('open-rank-btn')?.addEventListener('click', () => {
    window.location.href = '/rank';
  });
  if (chartRefreshInterval) clearInterval(chartRefreshInterval);
  chartRefreshInterval = setInterval(() => {
    const resultsPage = document.getElementById('results-page');
    if (resultsPage?.classList.contains('active')) renderActiveChart();
  }, 3000);
}
function switchChart(type) {
  currentChartType = type;
  document.querySelectorAll('.chart-tab').forEach(t => t.classList.remove('active'));
  const tab = document.querySelector('.chart-tab[data-chart="' + type + '"]');
  if (tab) tab.classList.add('active');
  renderActiveChart();
}
function renderActiveChart() {
  if (!population_data?.length) return;
  const main = document.getElementById('chart-container-main');
  const secondary = document.getElementById('chart-container-secondary');
  switch (currentChartType) {
    case 'multi': main.style.display = 'block'; secondary.style.display = 'none'; renderMultiLineChart(); break;
    case 'top3': main.style.display = 'none'; secondary.style.display = 'block'; renderTop3Chart(); break;
    case 'all': main.style.display = 'block'; secondary.style.display = 'none'; renderAllHeuristicsChart(); break;
    case 'tokens': main.style.display = 'block'; secondary.style.display = 'none'; renderTokensChart(); break;
    default: main.style.display = 'block'; secondary.style.display = 'none'; renderChart();
  }
}
function getChartColors(count) {
  const p = ['#f0883e','#58a6ff','#3fb950','#d29922','#f85149','#bc8cff','#79c0ff','#ff7b72'];
  return count <= p.length ? p.slice(0, count) : Array.from({length: count}, (_, i) => 'hsl(' + ((i * 360 / count) % 360) + ',70%,55%)');
}

// ── 图表1: 最优值折线图 ──
function renderChart() {
  const gens = population_data.filter(p => p.best_objective != null && p.best_objective !== 'null');
  if (!gens.length) return;
  const labels = gens.map(p => '#' + (p.index != null ? p.index : ''));
  const values = gens.map(p => parseFloat(p.best_objective));
  if (resultsChart) resultsChart.destroy();
  const canvas = document.getElementById('results-chart');
  if (!canvas) return;
  const dark = !document.documentElement.getAttribute('data-theme');
  resultsChart = new Chart(canvas, {
    type: 'line',
    data: { labels, datasets: [{ label: '最优适应度', data: values, borderColor: '#f0883e', backgroundColor: 'rgba(240,136,62,0.08)', fill: true, tension: 0.3, pointRadius: 5, pointHoverRadius: 8, pointBackgroundColor: values.map((_, i, a) => i === a.length - 1 ? '#3fb950' : '#f0883e'), pointBorderColor: dark ? '#0d1117' : '#fff', pointBorderWidth: 2, borderWidth: 2.5 }] },
    options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { labels: { color: dark ? '#8b949e' : '#656d76', font: { size: 12 } } }, tooltip: { callbacks: { label: ctx => '最优: ' + ctx.parsed.y.toFixed(4) } } }, scales: { x: { title: { display: true, text: '进化代数', color: dark ? '#8b949e' : '#656d76' }, ticks: { color: dark ? '#8b949e' : '#656d76' }, grid: { color: dark ? 'rgba(48,54,61,0.3)' : 'rgba(208,215,222,0.3)' } }, y: { title: { display: true, text: '适应度', color: dark ? '#8b949e' : '#656d76' }, ticks: { color: dark ? '#8b949e' : '#656d76' }, grid: { color: dark ? 'rgba(48,54,61,0.3)' : 'rgba(208,215,222,0.3)' } } } }
  });
}

// ── 图表2: 最优/均值/方差 ──
function renderMultiLineChart() {
  const valid = population_data.filter(p => p.heuristics?.length > 0);
  if (!valid.length) return;
  const labels = [], best = [], avg = [], vari = [];
  valid.forEach(p => {
    labels.push('#' + (p.index != null ? p.index : ''));
    const vals = p.heuristics.map(h => h.objective).filter(v => v != null && v !== 'null' && v !== Infinity).map(Number);
    if (!vals.length) return;
    best.push(Math.min(...vals));
    const m = vals.reduce((a, b) => a + b, 0) / vals.length;
    avg.push(m);
    vari.push(vals.reduce((s, v) => s + (v - m) ** 2, 0) / vals.length);
  });
  if (!labels.length) return;
  if (resultsChart) resultsChart.destroy();
  const canvas = document.getElementById('results-chart');
  if (!canvas) return;
  const dark = !document.documentElement.getAttribute('data-theme');
  resultsChart = new Chart(canvas, {
    type: 'line',
    data: { labels, datasets: [
      { label: '最优值', data: best, borderColor: '#3fb950', backgroundColor: 'rgba(63,185,80,0.05)', fill: false, tension: 0.3, pointRadius: 4, borderWidth: 2.5 },
      { label: '均值', data: avg, borderColor: '#58a6ff', backgroundColor: 'rgba(88,166,255,0.05)', fill: false, tension: 0.3, pointRadius: 3, borderWidth: 2, borderDash: [5,3] },
      { label: '方差', data: vari, borderColor: '#d29922', backgroundColor: 'rgba(210,153,34,0.05)', fill: false, tension: 0.3, pointRadius: 3, borderWidth: 1.5, borderDash: [2,4] }
    ] },
    options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { labels: { color: dark ? '#8b949e' : '#656d76', font: { size: 11 } } }, tooltip: { callbacks: { label: ctx => ctx.dataset.label + ': ' + ctx.parsed.y.toFixed(4) } } }, scales: { x: { title: { display: true, text: '进化代数', color: dark ? '#8b949e' : '#656d76' }, ticks: { color: dark ? '#8b949e' : '#656d76' } }, y: { title: { display: true, text: '适应度', color: dark ? '#8b949e' : '#656d76' }, ticks: { color: dark ? '#8b949e' : '#656d76' } } } }
  });
}

// ── 图表3: TOP3 条形图 ──
function renderTop3Chart() {
  const last = population_data[population_data.length - 1];
  if (!last?.heuristics?.length) return;
  const top3 = last.heuristics.slice(0, 3).filter(h => h.objective != null && h.objective !== 'null' && h.objective !== Infinity);
  if (!top3.length) return;
  if (top3Chart) top3Chart.destroy();
  const canvas = document.getElementById('top3-chart');
  if (!canvas) return;
  const dark = !document.documentElement.getAttribute('data-theme');
  top3Chart = new Chart(canvas, {
    type: 'bar',
    data: { labels: top3.map((_, i) => '#' + (i + 1)), datasets: [{ label: '最新代 TOP' + top3.length, data: top3.map(h => parseFloat(h.objective)), backgroundColor: ['#f0883e','#58a6ff','#3fb950'], borderColor: dark ? '#0d1117' : '#fff', borderWidth: 1.5, borderRadius: 4, barPercentage: 0.5 }] },
    options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { labels: { color: dark ? '#8b949e' : '#656d76', font: { size: 12 } } }, tooltip: { callbacks: { label: ctx => '适应度: ' + ctx.parsed.y.toFixed(4) } } }, scales: { x: { title: { display: true, text: '排名', color: dark ? '#8b949e' : '#656d76' }, ticks: { color: dark ? '#8b949e' : '#656d76' } }, y: { title: { display: true, text: '适应度', color: dark ? '#8b949e' : '#656d76' }, ticks: { color: dark ? '#8b949e' : '#656d76' } } } }
  });
}

// ── 图表4: 全部启发式条形图 ──
function renderAllHeuristicsChart() {
  const last = population_data[population_data.length - 1];
  if (!last?.heuristics?.length) return;
  const valid = last.heuristics.filter(h => h.objective != null && h.objective !== 'null' && h.objective !== Infinity);
  if (!valid.length) return;
  const labels = valid.map((_, i) => '#' + (i + 1));
  const values = valid.map(h => parseFloat(h.objective));
  if (resultsChart) resultsChart.destroy();
  const canvas = document.getElementById('results-chart');
  if (!canvas) return;
  const dark = !document.documentElement.getAttribute('data-theme');
  resultsChart = new Chart(canvas, {
    type: 'bar',
    data: { labels, datasets: [{ label: '当前代全部启发式', data: values, backgroundColor: getChartColors(valid.length), borderColor: dark ? '#0d1117' : '#fff', borderWidth: 1, borderRadius: 3, barPercentage: 0.7 }] },
    options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { labels: { color: dark ? '#8b949e' : '#656d76', font: { size: 12 } } }, tooltip: { callbacks: { label: ctx => '适应度: ' + ctx.parsed.y.toFixed(4) } } }, scales: { x: { title: { display: true, text: '启发式排名', color: dark ? '#8b949e' : '#656d76' }, ticks: { color: dark ? '#8b949e' : '#656d76' } }, y: { title: { display: true, text: '适应度', color: dark ? '#8b949e' : '#656d76' }, ticks: { color: dark ? '#8b949e' : '#656d76' } } } }
  });
}

// ── 图表5: Token消耗 ──
function renderTokensChart() {
  const canvas = document.getElementById('results-chart');
  if (!canvas) return;
  if (resultsChart) resultsChart.destroy();
  const count = population_data.filter(p => p.heuristics?.length > 0).length;
  const mut = count * 3 * 800, hyb = count * 3 * 1200, opt = count * 7 * 500;
  const dark = !document.documentElement.getAttribute('data-theme');
  resultsChart = new Chart(canvas, {
    type: 'doughnut',
    data: { labels: ['突变','杂交','优化'], datasets: [{ data: [mut, hyb, opt], backgroundColor: ['#f0883e','#58a6ff','#3fb950'], borderColor: dark ? '#0d1117' : '#fff', borderWidth: 2 }] },
    options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { position: 'bottom', labels: { color: dark ? '#8b949e' : '#656d76', font: { size: 12 }, padding: 16 } }, tooltip: { callbacks: { label: ctx => { const t = ctx.dataset.data.reduce((a, b) => a + b, 0); return ctx.label + ': ' + Math.round(ctx.parsed) + ' tokens (' + (ctx.parsed / t * 100).toFixed(1) + '%)'; } } } } }
  });
}
// ── Scenario Self-Adaptation ───────────────────
function closeSelfAdaptModal() {
  document.getElementById('self-adapt-modal').style.display = 'none';
  document.getElementById('generate-progress').style.display = 'none';
  document.getElementById('generate-result').style.display = 'none';
  document.getElementById('generate-scenario-btn').disabled = false;
  document.getElementById('generate-scenario-btn').innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M15.59 14.37a6 6 0 01-5.84 7.38v-4.8m5.84-2.58a14.98 14.98 0 006.16-12.12A14.98 14.98 0 009.631 8.41m5.96 5.96a14.926 14.926 0 01-5.841 2.58m-.119-8.54a6 6 0 00-7.381 5.84h4.8m2.581-5.84a14.927 14.927 0 00-2.58 5.84m2.699 2.7c-.103.021-.207.041-.311.06a15.09 15.09 0 01-2.448-2.448 14.9 14.9 0 01.06-.312m-2.24 2.39a4.493 4.493 0 00-1.757 4.306 4.493 4.493 0 004.306-1.758M16.5 9a1.5 1.5 0 11-3 0 1.5 1.5 0 013 0z"/></svg> 生成场景';
}

function generateScenario() {
  const name = document.getElementById('scenario_name_input').value.trim();
  const desc = document.getElementById('scenario_desc_input').value.trim();

  if (!name) { showToast('请输入场景名称', 'error'); return; }
  if (!desc) { showToast('请输入场景描述', 'error'); return; }
  if (!/^[a-zA-Z][a-zA-Z0-9_]*$/.test(name)) {
    showToast('场景名只能包含字母、数字和下划线，且必须以字母开头', 'error');
    return;
  }

  document.getElementById('generate-progress').style.display = 'block';
  document.getElementById('generate-result').style.display = 'none';
  const btn = document.getElementById('generate-scenario-btn');
  btn.disabled = true;
  btn.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="spin" style="vertical-align:-2px;margin-right:4px;"><path stroke-linecap="round" stroke-linejoin="round" d="M16.023 9.348h4.992v-.001M2.985 19.644v-4.992m0 0h4.992m-4.993 0l3.181 3.183a8.25 8.25 0 0013.803-3.7M4.031 9.865a8.25 8.25 0 0113.803-3.7l3.181 3.182"/></svg> 正在生成...';

  ['step-config', 'step-heuristic', 'step-datagen', 'step-traineval', 'step-finish'].forEach(id => {
    const el = document.getElementById(id);
    if (el) {
      el.className = 'progress-step';
      el.querySelector('.step-pending').style.display = '';
      el.querySelector('.step-spinner').style.display = 'none';
      el.querySelector('.step-done').style.display = 'none';
      el.querySelector('.step-error').style.display = 'none';
    }
  });

  setStepActive('step-config');

  fetch('/api/generate_scenario', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ scenario_name: name, description: desc })
  })
  .then(r => r.json())
  .then(d => {
    if (d.status === 'success') {
      setStepDone('step-config');
      setStepDone('step-heuristic');
      setStepDone('step-datagen');
      setStepDone('step-traineval');
      setStepDone('step-finish');

      const resultEl = document.getElementById('generate-result');
      resultEl.className = 'generate-result success';
      resultEl.style.display = 'block';
      resultEl.innerHTML = `
        <strong style="color:var(--success);">${d.message}</strong><br><br>
        <strong>场景信息：</strong><br>
        名称：${escapeHtml(name)}<br>
        目录：problems/${escapeHtml(name)}/<br><br>
        <button class="control-btn resume-btn" onclick="applyGeneratedScenario('${escapeHtml(name)}')">应用此场景</button>
        <button class="control-btn" onclick="closeSelfAdaptModal()">关闭</button>
      `;
    } else {
      throw new Error(d.message || '生成失败');
    }
  })
  .catch(err => {
    showToast('[ERROR] ' + err.message, 'error', 5000);
    const resultEl = document.getElementById('generate-result');
    resultEl.className = 'generate-result error';
    resultEl.style.display = 'block';
    resultEl.innerHTML = `<strong style="color:var(--danger);">生成失败: </strong>${escapeHtml(err.message)}`;
    setStepError('step-config');
  })
  .finally(() => {
    btn.disabled = false;
    btn.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M15.59 14.37a6 6 0 01-5.84 7.38v-4.8m5.84-2.58a14.98 14.98 0 006.16-12.12A14.98 14.98 0 009.631 8.41m5.96 5.96a14.926 14.926 0 01-5.841 2.58m-.119-8.54a6 6 0 00-7.381 5.84h4.8m2.581-5.84a14.927 14.927 0 00-2.58 5.84m2.699 2.7c-.103.021-.207.041-.311.06a15.09 15.09 0 01-2.448-2.448 14.9 14.9 0 01.06-.312m-2.24 2.39a4.493 4.493 0 00-1.757 4.306 4.493 4.493 0 004.306-1.758M16.5 9a1.5 1.5 0 11-3 0 1.5 1.5 0 013 0z"/></svg> 生成场景';
  });
}

function setStepActive(id) {
  const el = document.getElementById(id);
  if (el) {
    el.className = 'progress-step active';
    el.querySelector('.step-pending').style.display = 'none';
    el.querySelector('.step-spinner').style.display = '';
    el.querySelector('.step-done').style.display = 'none';
    el.querySelector('.step-error').style.display = 'none';
  }
}
function setStepDone(id) {
  const el = document.getElementById(id);
  if (el) {
    el.className = 'progress-step done';
    el.querySelector('.step-pending').style.display = 'none';
    el.querySelector('.step-spinner').style.display = 'none';
    el.querySelector('.step-done').style.display = '';
    el.querySelector('.step-error').style.display = 'none';
  }
}
function setStepError(id) {
  const el = document.getElementById(id);
  if (el) {
    el.className = 'progress-step error';
    el.querySelector('.step-pending').style.display = 'none';
    el.querySelector('.step-spinner').style.display = 'none';
    el.querySelector('.step-done').style.display = 'none';
    el.querySelector('.step-error').style.display = '';
  }
}

function applyGeneratedScenario(scenarioId) {
  closeSelfAdaptModal();
  fetch('/api/get_problem_config', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ problem_id: scenarioId })
  })
  .then(r => r.json())
  .then(d => {
    if (d.status === 'success' || d.config) {
      fetch('/api/get_problems')
        .then(r => r.json())
        .then(pd => {
          const sel = document.getElementById('problem_selector');
          if (sel && pd.problems) {
            sel.innerHTML = pd.problems.map(p =>
              `<option value="${escapeHtml(p.id)}">${escapeHtml(p.name)}</option>`
            ).join('');
            sel.value = scenarioId;
            onProblemChange();
            showToast(`已切换到场景: ${scenarioId}`, 'success');
          }
        });
    }
  })
  .catch(err => showToast('加载新场景失败: ' + err.message, 'error'));
}

// ── 特征树可视化 ─────────────────────────
function showFeatureTree() {
  const modal = document.getElementById('feature-tree-modal');
  if (!modal) return;
  modal.style.display = 'flex';
  document.getElementById('feature-tree-content').innerHTML = '<div style="text-align:center;padding:40px;color:var(--text-secondary);">正在加载特征树...</div>';

  fetch('/api/get_feature_tree')
    .then(r => r.json())
    .then(d => {
      if (d.status !== 'success') throw new Error(d.message);
      document.getElementById('feature-tree-desc').textContent =
        `场景: ${d.scenario.name || '自定义'} — ${d.scenario.description || ''}`;
      document.getElementById('feature-tree-content').innerHTML = renderFeatureTree(d);
    })
    .catch(err => {
      document.getElementById('feature-tree-content').innerHTML =
        `<div style="text-align:center;padding:40px;color:var(--danger);">加载失败: ${escapeHtml(err.message)}</div>`;
    });
}

function closeFeatureTree() {
  document.getElementById('feature-tree-modal').style.display = 'none';
}

function renderFeatureTree(data) {
  const tree = data.tree || {};
  const tags = data.tags || {};
  const posTags = data.positive_tags || {};
  const negTags = data.negative_tags || {};
  const coOccurrence = data.co_occurrence || [];

  const totalExplored = Object.keys(tags).filter(t => tags[t].count > 0).length;
  const posCount = Object.values(posTags).reduce((a, b) => a + b, 0);
  const negCount = Object.values(negTags).reduce((a, b) => a + b, 0);

  let html = '<div class="ftree-container">';

  // Summary bar
  html += `<div class="ftree-summary">
    <div class="ftree-summary-item"><span class="num info">${totalExplored}</span> 标签被探索</div>
    <div class="ftree-summary-item"><span class="num success">${posCount}</span> 积极特征</div>
    <div class="ftree-summary-item"><span class="num danger">${negCount}</span> 消极特征</div>
    <div class="ftree-summary-item"><span class="num info">${coOccurrence.length}</span> 标签组合</div>
  </div>';

  // Render tree
  for (const [cat, catData] of Object.entries(tree)) {
    const catId = 'ft-' + cat.replace(/[^a-zA-Z0-9]/g, '');
    const children = catData.children || {};
    const allLeaves = [];
    for (const [, sd] of Object.entries(children)) { (sd.leaf || []).forEach(l => allLeaves.push(l)); }
    const exploredCount = allLeaves.filter(l => tags[l] && tags[l].count > 0).length;

    html += `<div class="ftree-node">
      <div class="ftree-node-header clickable" onclick="toggleFtree('${catId}')">
        <svg class="ftree-chevron open" xmlns="http://www.w3.org/2000/svg" width="14" height="14" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M8.25 4.5l7.5 7.5-7.5 7.5"/></svg>
        <svg class="ftree-icon" xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" style="color:var(--info);"><path stroke-linecap="round" stroke-linejoin="round" d="M2.25 12.75V12A2.25 2.25 0 014.5 9.75h15A2.25 2.25 0 0121.75 12v.75m-8.69-6.44l-2.12-2.12a1.5 1.5 0 00-1.061-.44H4.5A2.25 2.25 0 002.25 6v12a2.25 2.25 0 002.25 2.25h15A2.25 2.25 0 0021.75 18V9a2.25 2.25 0 00-2.25-2.25h-5.379a1.5 1.5 0 01-1.06-.44z"/></svg>
        <span class="ftree-label">${escapeHtml(cat)}</span>
        ${exploredCount > 0 ? `<span class="ftree-badge" style="background:var(--accent-dim);color:var(--accent);">${exploredCount} 个发现</span>` : ''}
      </div>
      <div class="ftree-children" id="${catId}">`;

    for (const [subcat, subData] of Object.entries(children)) {
      const subId = catId + '-' + subcat.replace(/[^a-zA-Z0-9]/g, '');
      const leaves = subData.leaf || [];
      const exploredLeaves = leaves.filter(l => tags[l] && tags[l].count > 0);

      html += `<div class="ftree-node">
        <div class="ftree-node-header clickable" onclick="toggleFtree('${subId}')">
          <svg class="ftree-chevron open" xmlns="http://www.w3.org/2000/svg" width="13" height="13" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M8.25 4.5l7.5 7.5-7.5 7.5"/></svg>
          <svg class="ftree-icon" xmlns="http://www.w3.org/2000/svg" width="14" height="14" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" style="color:var(--text-secondary);"><path stroke-linecap="round" stroke-linejoin="round" d="M4 6h16M4 10h16M4 14h16M4 18h16"/></svg>
          <span class="ftree-label" style="font-size:0.85rem;">${escapeHtml(subcat)}</span>
          <span class="ftree-badge" style="background:rgba(88,166,255,0.1);color:${exploredLeaves.length > 0 ? 'var(--info)' : 'var(--text-secondary)'};font-size:0.68rem;">${exploredLeaves.length}/${leaves.length}</span>
        </div>
        <div class="ftree-children" id="${subId}">
          <div class="ftree-leaf-area">`;

      for (const leaf of leaves) {
        const tagInfo = tags[leaf];
        const count = tagInfo ? (tagInfo.count || 0) : 0;
        const isPos = posTags[leaf] > 0;
        const isNeg = negTags[leaf] > 0;
        let cls = 'ftree-tag';
        if (count > 0) cls += ' explored';
        if (isPos && !isNeg) cls += ' positive';
        else if (isNeg && !isPos) cls += ' negative';
        else if (isPos && isNeg) cls += ' explored';

        html += `<span class="${cls}">${escapeHtml(leaf)}${count > 0 ? `<span class="count">${count}</span>` : ''}</span>`;
      }

      html += '</div></div></div>';
    }

    html += '</div></div>';
  }

  // Co-occurrence section
  if (coOccurrence.length > 0) {
    html += `<div class="ftree-node" style="margin-top:16px;">
      <div class="ftree-node-header">
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" style="color:var(--accent);"><path stroke-linecap="round" stroke-linejoin="round" d="M13.19 8.688a4.5 4.5 0 011.242 7.244l-4.5 4.5a4.5 4.5 0 01-6.364-6.364l1.757-1.757m9.86-2.566a4.5 4.5 0 01-1.242-7.244l-4.5-4.5a4.5 4.5 0 00-6.364 6.364M15.75 12a3.75 3.75 0 11-7.5 0 3.75 3.75 0 017.5 0z"/></svg>
        <span class="ftree-label">高频共现组合</span>
        <span style="font-size:0.72rem;color:var(--text-secondary);margin-left:auto;">出现次数</span>
      </div>
      <div class="ftree-leaf-area" style="padding-left:24px;">
        ${coOccurrence.map(p => {
          return `<span class="ftree-tag" style="border-style:dashed;">
            ${p.tags.map(t => escapeHtml(t)).join('<span style="color:var(--text-secondary);margin:0 3px;">+</span>')}
            <span class="count">${p.count}</span>
          </span>`;
        }).join('')}
      </div>
    </div>`;
  }

  html += '</div>';
  return html;
}

function toggleFtree(id) {
  const el = document.getElementById(id);
  if (!el) return;
  const header = el.previousElementSibling;
  const isHidden = el.style.display === 'none';
  el.style.display = isHidden ? '' : 'none';
  const chevron = header?.querySelector('.ftree-chevron');
  if (chevron) chevron.classList.toggle('open', isHidden);
}

// ── 加载已有种群 ────────────────────────────
function initLoadPopulationUI() {
  document.getElementById('load-population-btn')?.addEventListener('click', () => {
    const pathInput = document.getElementById('problem_path');
    const pathDisplay = document.getElementById('load-pop-path-display');
    if (pathDisplay && pathInput) pathDisplay.textContent = pathInput.value || 'problems/tsp';
    document.getElementById('load-population-modal').style.display = 'flex';
    listSavedPopulations();
  });
}

function closeLoadPopulationModal() {
  document.getElementById('load-population-modal').style.display = 'none';
  document.getElementById('load-population-summary').style.display = 'none';
}

function listSavedPopulations() {
  const pathVal = document.getElementById('problem_path')?.value || 'problems/tsp';
  const loading = document.getElementById('population-list-loading');
  const list = document.getElementById('population-list');
  const empty = document.getElementById('population-list-empty');

  loading.style.display = 'block';
  loading.textContent = '正在扫描所有问题的已保存种群...';
  list.style.display = 'none';
  empty.style.display = 'none';

  // 先扫描当前问题，再尝试扫描所有可用问题
  fetch('/api/list_saved_populations', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ problem_path: pathVal, scan_all: true })
  })
  .then(r => r.json())
  .then(d => {
    loading.style.display = 'none';
    const pops = d.populations;
    if (!pops || pops.length === 0) {
      empty.style.display = 'block';
      return;
    }
    list.style.display = 'block';
    list.innerHTML = pops.map(p => {
      const problemTag = p.problem ? `<span class="tag" style="margin-right:8px;">${escapeHtml(p.problem)}</span>` : '';
      return `<div class="pop-file-card" onclick="selectPopulationFile('${escapeHtml(p.path)}')">
        <div style="display:flex;justify-content:space-between;align-items:center;">
          <div>
            ${problemTag}
            <strong style="color:var(--accent);">第 ${p.generation} 代</strong>
            <span style="color:var(--text-secondary);margin-left:8px;">${escapeHtml(p.date)}</span>
          </div>
          <div style="color:var(--text-secondary);font-size:0.82rem;">
            ${escapeHtml(p.mtime)} · ${p.size_kb}KB
          </div>
        </div>
        <div style="font-size:0.82rem;color:var(--text-secondary);margin-top:4px;">${escapeHtml(p.filename)}</div>
      </div>`;
    }).join('');
  })
  .catch(err => {
    loading.style.display = 'none';
    showToast('加载种群列表失败: ' + err.message, 'error');
  });
}

function selectPopulationFile(path) {
  showToast('正在加载种群...', 'info');
  fetch('/api/load_population', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ path: path })
  })
  .then(r => r.json())
  .then(d => {
    if (d.status === 'success') {
      const summary = document.getElementById('load-population-summary');
      summary.style.display = 'block';
      summary.innerHTML = `
        <strong style="color:var(--success);">${escapeHtml(d.message)}</strong><br><br>
        <table style="width:100%;border-collapse:collapse;">
          <tr><td style="padding:4px 8px;color:var(--text-secondary);">起始代数</td>
              <td style="padding:4px 8px;">第 ${d.generation} 代</td></tr>
          <tr><td style="padding:4px 8px;color:var(--text-secondary);">启发式数量</td>
              <td style="padding:4px 8px;">${d.heuristic_count} 个</td></tr>
          <tr><td style="padding:4px 8px;color:var(--text-secondary);">积极特征</td>
              <td style="padding:4px 8px;">${d.memory_summary.positive_count} 条</td></tr>
          <tr><td style="padding:4px 8px;color:var(--text-secondary);">消极特征</td>
              <td style="padding:4px 8px;">${d.memory_summary.negative_count} 条</td></tr>
        </table>
        <div style="margin-top:12px;text-align:center;">
          <button class="control-btn resume-btn" onclick="closeLoadPopulationModal();startEvolution();">
            <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" style="vertical-align:-2px;margin-right:4px;"><path stroke-linecap="round" stroke-linejoin="round" d="M5.25 5.653c0-.856.917-1.398 1.667-.986l11.54 6.348a1.125 1.125 0 010 1.971l-11.54 6.347a1.125 1.125 0 01-1.667-.985V5.653z"/></svg>
            用此种群开始进化</button>
          <button class="control-btn" onclick="closeLoadPopulationModal()">取消</button>
        </div>
      `;
      showToast('✓ ' + d.message, 'success');
    } else {
      throw new Error(d.message);
    }
  })
  .catch(err => showToast('[ERROR] ' + err.message, 'error', 5000));
}

// ── Helpers ────────────────────────────────────
function escapeHtml(str) {
  if (!str) return '';
  const d = document.createElement('div');
  d.textContent = str;
  return d.innerHTML;
}
