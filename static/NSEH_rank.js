// NSEH Rank v3 — Enhanced
document.addEventListener('DOMContentLoaded', () => {
  const savedTheme = localStorage.getItem('theme');
  if (savedTheme) document.documentElement.setAttribute('data-theme', savedTheme);

  function loadRank() {
    fetch('/api/get_user_rank')
      .then(r => r.json())
      .then(data => {
        const tbody = document.getElementById('rank-body');
        if (!tbody) return;

        if (data.users?.length) {
          tbody.innerHTML = '';
          data.users.forEach((user, i) => {
            const tr = document.createElement('tr');
            const isMe = user.user_id === getUserId();

            // Rank badges
            const rankBadge = i === 0
              ? '<span class="rank-badge rank-1">🥇</span>'
              : i === 1
                ? '<span class="rank-badge rank-2">🥈</span>'
                : i === 2
                  ? '<span class="rank-badge rank-3">🥉</span>'
                  : `<span class="rank-other">${i + 1}</span>`;

            tr.innerHTML = `
              <td>${rankBadge}</td>
              <td>${escapeHtml(user.user_name || user.user_id)}${isMe ? ' <span style="color:var(--accent);font-size:0.75rem;">' + T('rank.me') + '</span>' : ''}</td>
              <td style="font-family:var(--font-mono);">${user.best_score !== null ? Number(user.best_score).toFixed(4) : '—'}</td>
            `;
            if (isMe) {
              tr.style.background = 'var(--accent-subtle)';
              tr.style.borderLeft = '3px solid var(--accent)';
            }
            // Staggered entrance animation
            tr.style.opacity = '0';
            tr.style.transform = 'translateX(-10px)';
            tr.style.transition = 'opacity 0.3s ease, transform 0.3s ease, background 0.2s ease';
            tbody.appendChild(tr);
            requestAnimationFrame(() => {
              setTimeout(() => {
                tr.style.opacity = '1';
                tr.style.transform = 'translateX(0)';
              }, i * 50);
            });
          });
        } else {
          tbody.innerHTML = `<tr><td colspan="3" style="text-align:center;padding:32px;color:var(--text-muted)">${escapeHtml(T('rank.empty'))}</td></tr>`;
        }
      })
      .catch(() => {
        const tbody = document.getElementById('rank-body');
        if (tbody) {
          tbody.innerHTML = `<tr><td colspan="3" style="text-align:center;padding:32px;color:var(--danger)">${escapeHtml(T('rank.loadFailed'))}</td></tr>`;
        }
      });
  }

  loadRank();

  // 语言切换后重新渲染（表头/数据由 i18n.apply 处理，这里刷新数据文本）
  document.addEventListener('i18n:changed', () => loadRank());
});

function getUserId() {
  try {
    const m = document.cookie.match(/session=([^;]+)/);
    if (!m) return null;
    return JSON.parse(atob(m[1]))?.user_id || null;
  } catch { return null; }
}

function escapeHtml(str) {
  if (!str) return '';
  const d = document.createElement('div');
  d.textContent = str;
  return d.innerHTML;
}
