/* FinServe AI Copilot - API client (token-aware). Jillani SofTech. */
const FinServeAPI = {
  base: "",
  token() { return localStorage.getItem("fs_token") || ""; },
  setToken(t) { localStorage.setItem("fs_token", t); },
  clear() { localStorage.removeItem("fs_token"); localStorage.removeItem("fs_name"); },

  headers(json) {
    const h = {};
    if (json) h["Content-Type"] = "application/json";
    const t = this.token();
    if (t) h["Authorization"] = "Bearer " + t;
    return h;
  },

  async req(path, opts) {
    const res = await fetch(this.base + path, opts);
    if (res.status === 401) { this.clear(); location.href = "/login"; throw new Error("unauthorized"); }
    if (!res.ok) throw new Error("HTTP " + res.status);
    return res.json();
  },

  login(email, password) {
    return this.req("/auth/login", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    });
  },

  health() { return this.req("/health", { headers: this.headers() }); },
  metrics() { return this.req("/dashboard/metrics", { headers: this.headers() }); },
  charts() { return this.req("/dashboard/charts", { headers: this.headers() }); },
  documents() { return this.req("/documents", { headers: this.headers() }); },
  history() { return this.req("/analysis/history", { headers: this.headers() }); },
  query(q) { return this.req("/rag/query", { method: "POST", headers: this.headers(true), body: JSON.stringify({ query: q, top_k: 4 }) }); },
  risk(text, subject) { return this.req("/risk/analyze", { method: "POST", headers: this.headers(true), body: JSON.stringify({ text, subject }) }); },
  compliance(text) { return this.req("/compliance/review", { method: "POST", headers: this.headers(true), body: JSON.stringify({ text, framework: "ALL" }) }); },

  upload(file, category) {
    const fd = new FormData();
    fd.append("file", file);
    fd.append("category", category || "General");
    return this.req("/documents/upload", { method: "POST", headers: this.headers(), body: fd });
  },
};
