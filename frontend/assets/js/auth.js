/* Login page handler. Jillani SofTech. */
document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("loginForm");
  if (!form) return;

  // Verify the browser allows localStorage (private mode / blocked cookies break auth).
  let storageOk = true;
  try { localStorage.setItem("fs_probe", "1"); localStorage.removeItem("fs_probe"); }
  catch (e) { storageOk = false; }

  const err = document.getElementById("loginError");
  if (!storageOk) {
    err.textContent = "Your browser is blocking local storage. Disable private/incognito mode or allow site data, then reload.";
  }

  if (storageOk && FinServeAPI.token()) { location.href = "/dashboard"; return; }

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    err.textContent = "";
    const email = document.getElementById("email").value.trim();
    const password = document.getElementById("password").value;
    const btn = document.getElementById("loginBtn");
    btn.disabled = true; btn.textContent = "Signing in\u2026";
    try {
      const r = await FinServeAPI.login(email, password);
      FinServeAPI.setToken(r.access_token);
      localStorage.setItem("fs_name", r.name);
      btn.textContent = "Success \u2014 redirecting\u2026";
      window.location.replace("/dashboard");
    } catch (ex) {
      err.textContent = "Invalid email or password. Use the demo credentials shown below.";
      btn.disabled = false; btn.textContent = "Sign in";
    }
  });
});
