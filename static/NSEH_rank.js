// NSEH Rank v2
document.addEventListener('DOMContentLoaded', () => {
  const savedTheme = localStorage.getItem('theme');
  if (savedTheme) document.documentElement.setAttribute('data-theme', savedTheme);

  fetch('/api/get_user_rank')
    .then(r => r.json())
    .then(data => {
      const tbody = document.getElementById('rank-body');
      if (!tbody) return;

      if (data.users?.length) {
        data.users.forEach((user, i) => {
          const tr = document.createElement('tr');
          const isMe = user.user_id === getUserId();

          const medal = i === 0 ? '🥇' : i === 1 ? '🥈' : i === 2 ? '🥉' : '';
          const rankHtml = medal
            ? `<span class="rank-medal">${medal}</span>`
            : `<span class="rank-num">${i + 1}</span>`;

          tr.innerHTML = `
            <td>${rankHtml}</td>
            <td>${escapeHtml(user.user_name || user.user_id)}</td>
            <td>${user.best_score !== null ? parseFloat(user.best_score).toFixed(4) : '—'}</td>
          `;
          if (isMe) tr.className = 'me-row';
          tbody.appendChild(tr);
        });
      } else {
        tbody.innerHTML = '<tr><td colspan="3" style="text-align:center;padding:32px;color:var(--text-secondary)">暂无排行数据</td></tr>';
      }
    })
    .catch(() => {
      document.getElementById('rank-body').innerHTML = '<tr><td colspan="3" style="text-align:center;padding:32px;color:var(--danger)">加载失败</td></tr>';
    });
});

function getUserId() {
  try {
    const m = document.cookie.match(/session=([^;]+)/);
    return m ? atob(m[1]).match(/"user_id":"([^"]+)"/)?.[1] : null;
  } catch { return null; }
}

function escapeHtml(str) {
  if (!str) return '';
  const d = document.createElement('div');
  d.textContent = str;
  return d.innerHTML;
}
