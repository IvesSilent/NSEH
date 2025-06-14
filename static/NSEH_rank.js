// NSEH_rank.js
document.addEventListener('DOMContentLoaded', function() {
    // 主题切换功能
    const themeToggle = document.getElementById('theme-toggle');
    const currentTheme = localStorage.getItem('theme');
    if (currentTheme === 'light') {
        document.documentElement.setAttribute('data-theme', 'light');
    }

    themeToggle.addEventListener('click', function() {
        const currentTheme = document.documentElement.getAttribute('data-theme');
        const newTheme = currentTheme === 'light' ? null : 'light';
        document.documentElement.setAttribute('data-theme', newTheme);

        // 可选：保存到 localStorage
        localStorage.setItem('theme', newTheme);
    });

    // 获取用户数据并渲染排行榜
    fetch('/api/get_user_rank')
        .then(response => response.json())
        .then(data => {
            renderUserRank(data.users);
        })
        .catch(error => {
            console.error('Error fetching user rank data:', error);
        });

    // 返回进化页面按钮
    document.getElementById('back-btn').addEventListener('click', function() {
        window.location.href = '/';
    });
});

function renderUserRank(users) {
    const userCardsContainer = document.getElementById('user-cards');
    userCardsContainer.innerHTML = '';

    users.forEach(user => {
        const userCard = document.createElement('div');
        userCard.className = 'user-card';
        userCard.innerHTML = `
            <h3>${user.user_name}</h3>
            <p>账号: ${user.user_id}</p>
            <p>最佳适应度: <span class="best-score">${user.best_score !== 'null' ? user.best_score : '无'}</span></p>
        `;
        userCardsContainer.appendChild(userCard);
    });
}