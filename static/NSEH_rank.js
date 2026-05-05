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

          const medalSvg = i === 0
            ? '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="#ffd700" stroke="#b8860b" stroke-width="1"><path d="M16.5 18.75h-9m9 0a3 3 0 013 3h-15a3 3 0 013-3m9 0v-3.375c0-.621-.503-1.125-1.125-1.125h-.871M7.5 18.75v-3.375c0-.621.504-1.125 1.125-1.125h.872m5.007 0H9.497m5.007 0a7.454 7.454 0 01-.982-3.172M9.497 14.25a7.454 7.454 0 00.981-3.172M5.25 4.236c-.982.143-1.954.317-2.916.52A6.003 6.003 0 007.73 9.728M5.25 4.236V4.5c0 2.108.966 3.99 2.48 5.228M5.25 4.236V2.721A7.456 7.456 0 0112 2.25c1.16 0 2.27.13 3.31.38M5.25 9.728h.01m0 0a.01.01 0 01-.01-.01m13.5-5.492c-.982.143-1.954.317-2.916.52A6.003 6.003 0 0016.27 9.728M18.75 4.236V4.5c0 2.108-.966 3.99-2.48 5.228m0 0h.01a.01.01 0 00.01-.01"/></svg>'
            : i === 1
              ? '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="#c0c0c0" stroke="#808080" stroke-width="1"><path d="M16.5 18.75h-9m9 0a3 3 0 013 3h-15a3 3 0 013-3m9 0v-3.375c0-.621-.503-1.125-1.125-1.125h-.871M7.5 18.75v-3.375c0-.621.504-1.125 1.125-1.125h.872m5.007 0H9.497m5.007 0a7.454 7.454 0 01-.982-3.172M9.497 14.25a7.454 7.454 0 00.981-3.172M5.25 4.236c-.982.143-1.954.317-2.916.52A6.003 6.003 0 007.73 9.728M5.25 4.236V4.5c0 2.108.966 3.99 2.48 5.228M5.25 4.236V2.721A7.456 7.456 0 0112 2.25c1.16 0 2.27.13 3.31.38M5.25 9.728h.01m0 0a.01.01 0 01-.01-.01m13.5-5.492c-.982.143-1.954.317-2.916.52A6.003 6.003 0 0016.27 9.728M18.75 4.236V4.5c0 2.108-.966 3.99-2.48 5.228m0 0h.01a.01.01 0 00.01-.01"/></svg>'
            : i === 2
              ? '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="#cd7f32" stroke="#8b4513" stroke-width="1"><path d="M16.5 18.75h-9m9 0a3 3 0 013 3h-15a3 3 0 013-3m9 0v-3.375c0-.621-.503-1.125-1.125-1.125h-.871M7.5 18.75v-3.375c0-.621.504-1.125 1.125-1.125h.872m5.007 0H9.497m5.007 0a7.454 7.454 0 01-.982-3.172M9.497 14.25a7.454 7.454 0 00.981-3.172M5.25 4.236c-.982.143-1.954.317-2.916.52A6.003 6.003 0 007.73 9.728M5.25 4.236V4.5c0 2.108.966 3.99 2.48 5.228M5.25 4.236V2.721A7.456 7.456 0 0112 2.25c1.16 0 2.27.13 3.31.38M5.25 9.728h.01m0 0a.01.01 0 01-.01-.01m13.5-5.492c-.982.143-1.954.317-2.916.52A6.003 6.003 0 0016.27 9.728M18.75 4.236V4.5c0 2.108-.966 3.99-2.48 5.228m0 0h.01a.01.01 0 00.01-.01"/></svg>'
            : '';
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
