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
      errorMsg.textContent = T('login.needCredentials');
      errorMsg.classList.remove('error-shake');
      void errorMsg.offsetHeight;
      errorMsg.classList.add('error-shake');
      return;
    }

    const btn = document.getElementById('login-btn');
    btn.disabled = true;
    btn.textContent = T('login.loggingIn');

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
        errorMsg.textContent = data.message || T('login.failed');
        errorMsg.classList.remove('error-shake');
        void errorMsg.offsetHeight;
        errorMsg.classList.add('error-shake');
      }
    })
    .catch(() => {
      errorMsg.textContent = T('login.networkError');
      errorMsg.classList.add('error-shake');
    })
    .finally(() => {
      btn.disabled = false;
      btn.textContent = T('login.loginBtn');
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

      btn.setAttribute('aria-label', isPassword ? T('login.hidePwd') : T('login.showPwd'));
    });
  });

  // 注册
  document.getElementById('register-btn').addEventListener('click', () => {
    const userId = document.getElementById('regUserId').value.trim();
    const password = document.getElementById('regPassword').value.trim();
    const userName = document.getElementById('regUserName').value.trim();

    if (!userId || !password) {
      regError.textContent = T('login.needRegFields');
      regError.classList.add('error-shake');
      return;
    }
    if (password.length < 6) {
      regError.textContent = T('login.pwdTooShort');
      regError.classList.add('error-shake');
      return;
    }

    const btn = document.getElementById('register-btn');
    btn.disabled = true;
    btn.textContent = T('login.registering');

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
        regError.textContent = T('login.regSuccess');
        setTimeout(() => {
          document.getElementById('login-link').click();
          document.getElementById('userId').value = userId;
          document.getElementById('password').value = password;
          document.getElementById('login-btn').click();
        }, 1200);
      } else {
        regError.textContent = data.message || T('login.regFailed');
      }
    })
    .catch(() => { regError.textContent = T('login.networkError'); })
    .finally(() => {
      btn.disabled = false;
      btn.textContent = T('login.regBtn');
    });
  });

});
