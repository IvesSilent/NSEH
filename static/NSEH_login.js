// NSEH_login.js
document.addEventListener('DOMContentLoaded', function() {

//    // 清除会话存储
//    sessionstorage.clear();

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

    // 登录功能
    const loginBtn = document.getElementById('login-btn');
    loginBtn.addEventListener('click', function() {
        const userId = document.getElementById('user_id').value;
        const password = document.getElementById('password').value;

        if (!userId || !password) {
            alert('账号和密码不能为空');
            return;
        }

        // 发送登录请求
        fetch('/api/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ userId, password }),
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                // 登录成功，跳转到主页面
                window.location.href = '/';
            } else {
                // 登录失败，显示错误信息
                alert(data.message);
            }
        })
        .catch(error => {
            console.error('Error during login:', error);
            alert('登录过程中出错，请稍后再试');
        });
    });
});