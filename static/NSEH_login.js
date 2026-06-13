// NSEH Login v2
document.addEventListener('DOMContentLoaded', () => {

  const loginForm = document.querySelector('.login-form');
  const regForm = document.querySelector('.register-form');
  const errorMsg = document.getElementById('error-message');
  const regError = document.getElementById('register-error');

  // 切换注册/登录
  document.getElementById('register-link').addEventListener('click', (e) => {
    e.preventDefault();
    loginForm.style.display = 'none';
    regForm.style.display = 'block';
    errorMsg.textContent = '';
  });

  document.getElementById('login-link').addEventListener('click', (e) => {
    e.preventDefault();
    regForm.style.display = 'none';
    loginForm.style.display = 'block';
    regError.textContent = '';
  });

  // 登录
  document.getElementById('login-btn').addEventListener('click', () => {
    const userId = document.getElementById('userId').value.trim();
    const password = document.getElementById('password').value.trim();

    if (!userId || !password) {
      errorMsg.textContent = '请输入用户ID和密码';
      return;
    }

    const btn = document.getElementById('login-btn');
    btn.disabled = true;
    btn.textContent = '登录中...';

    fetch('/api/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ userId, password })
    })
    .then(res => res.json())
    .then(data => {
      if (data.status === 'success') {
        window.location.href = '/';
      } else {
        errorMsg.textContent = data.message || '登录失败，请重试';
      }
    })
    .catch(() => { errorMsg.textContent = '网络错误，请稍后重试'; })
    .finally(() => {
      btn.disabled = false;
      btn.textContent = '登 录';
    });
  });

  // 回车登录
  document.getElementById('password').addEventListener('keydown', (e) => {
    if (e.key === 'Enter') document.getElementById('login-btn').click();
  });

  // ── 密码显示/隐藏切换 ─────────────────────
  document.querySelectorAll('.password-toggle').forEach(btn => {
    btn.addEventListener('click', () => {
      const targetId = btn.getAttribute('data-target');
      const input = document.getElementById(targetId);
      if (!input) return;

      const isPassword = input.type === 'password';
      input.type = isPassword ? 'text' : 'password';

      // 切换图标
      const eyeOpen = btn.querySelector('.eye-open');
      const eyeSlash = btn.querySelector('.eye-slash');
      if (eyeOpen) eyeOpen.style.display = isPassword ? 'none' : '';
      if (eyeSlash) eyeSlash.style.display = isPassword ? '' : 'none';

      btn.setAttribute('aria-label', isPassword ? '隐藏密码' : '显示密码');
    });
  });

  // 注册
  document.getElementById('register-btn').addEventListener('click', () => {
    const userId = document.getElementById('regUserId').value.trim();
    const password = document.getElementById('regPassword').value.trim();
    const userName = document.getElementById('regUserName').value.trim();

    if (!userId || !password) {
      regError.textContent = '用户ID和密码不能为空';
      return;
    }
    if (password.length < 6) {
      regError.textContent = '密码至少6位';
      return;
    }

    const btn = document.getElementById('register-btn');
    btn.disabled = true;
    btn.textContent = '注册中...';

    fetch('/api/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ userId, password, userName })
    })
    .then(res => res.json())
    .then(data => {
      if (data.status === 'success') {
        regError.textContent = '';
        regError.style.color = '#3fb950';
        regError.textContent = '注册成功！即将跳转登录...';
        setTimeout(() => {
          document.getElementById('login-link').click();
          document.getElementById('userId').value = userId;
          document.getElementById('password').value = password;
          document.getElementById('login-btn').click();
        }, 1200);
      } else {
        regError.textContent = data.message || '注册失败';
      }
    })
    .catch(() => { regError.textContent = '网络错误，请稍后重试'; })
    .finally(() => {
      btn.disabled = false;
      btn.textContent = '注 册';
    });
  });

});
