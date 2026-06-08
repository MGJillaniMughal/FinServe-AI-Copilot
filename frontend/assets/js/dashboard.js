/* Dashboard controller. Jillani SofTech. */
function tagClass(c){c=(c||"").toLowerCase();return c==="high"?"tag-high":c==="medium"?"tag-medium":"tag-low";}
function ringColor(score,invert){ // invert=true: high score is good (compliance)
  const good = invert ? score>=80 : score<45;
  const bad  = invert ? score<60 : score>=70;
  return bad ? "#d13b3b" : good ? "#1fae72" : "#c98a00";
}
function setRing(el,score,invert){
  el.style.setProperty("--pct",score);
  el.style.setProperty("--col",ringColor(score,invert));
  el.querySelector(".num").textContent=Math.round(score);
}
function fmt(ts){try{return new Date(ts).toLocaleString();}catch(e){return ts;}}

async function loadHealth(){
  try{
    const h=await FinServeAPI.health();
    const b=document.getElementById("aiModeBadge");
    if(b) b.innerHTML='<span class="dot"></span> AI Engine: '+h.ai_status+' \u00b7 '+h.ai_mode;
    const ht=document.getElementById("healthText");
    if(ht) ht.textContent="Online \u00b7 "+h.ai_mode;
  }catch(e){}
}
async function loadKpis(){
  const m=await FinServeAPI.metrics();
  const set=(id,v)=>{const el=document.getElementById(id);if(el)el.textContent=v;};
  set("kpiDocs",m.total_documents);set("kpiComp",m.compliance_score);
  set("kpiAlerts",m.compliance_alerts);set("kpiQueries",m.ai_queries);
}
async function loadDocs(){
  const docs=await FinServeAPI.documents();
  const box=document.getElementById("docList");if(!box)return;
  box.innerHTML=docs.map(d=>`<div class="fs-doc"><span>${d.filename}</span><span class="cat">${d.category} \u00b7 ${d.chunks} chunks</span></div>`).join("")
    || '<div class="text-muted small">No documents yet.</div>';
}
async function loadHistory(){
  const items=await FinServeAPI.history();
  const body=document.getElementById("historyBody");if(!body)return;
  body.innerHTML=items.map(h=>`<tr>
    <td><span class="fs-pill-type pt-${h.type}">${h.type}</span></td>
    <td>${h.title}</td><td class="text-muted">${h.summary}</td>
    <td>${h.score!=null?h.score:"\u2014"}</td><td class="text-muted">${fmt(h.created_at)}</td></tr>`).join("");
}
function addMsg(text,who,cites){
  const box=document.getElementById("chatBox");const d=document.createElement("div");
  d.className="fs-msg "+who;d.innerHTML=text;
  if(cites)cites.forEach(c=>d.innerHTML+=`<span class="cite">\u{1F4C4} ${c.filename} (score ${c.score})</span>`);
  box.appendChild(d);box.scrollTop=box.scrollHeight;
}
function wireChat(){
  const send=document.getElementById("chatSend"),input=document.getElementById("chatInput");
  const ask=async()=>{const q=input.value.trim();if(!q)return;addMsg(q,"user");input.value="";
    addMsg("Analyzing\u2026","ai");const box=document.getElementById("chatBox");
    try{const r=await FinServeAPI.query(q);box.lastChild.remove();
      addMsg(r.answer+` <span class="cite">Confidence: ${(r.confidence*100).toFixed(0)}% \u00b7 ${r.model}</span>`,"ai",r.citations);
    }catch(e){box.lastChild.remove();addMsg("Request failed. Please try again.","ai");}
    loadHistory();loadKpis();};
  send.onclick=ask;input.addEventListener("keydown",e=>{if(e.key==="Enter")ask();});
}
function wireUpload(){
  const drop=document.getElementById("dropZone"),input=document.getElementById("fileInput"),
        btn=document.getElementById("uploadBtn"),msg=document.getElementById("uploadMsg");
  if(!drop)return;const open=()=>input.click();
  drop.onclick=open;btn.onclick=e=>{e.stopPropagation();open();};
  input.onchange=async()=>{if(!input.files.length)return;msg.textContent="Ingesting\u2026";
    try{const r=await FinServeAPI.upload(input.files[0],"General");msg.textContent=r.message;}
    catch(e){msg.textContent="Upload failed.";}
    loadDocs();loadKpis();loadHistory();};
}
function wireRisk(){
  document.getElementById("riskBtn").onclick=async()=>{
    const text=document.getElementById("riskText").value.trim();if(!text)return;
    const r=await FinServeAPI.risk(text,"Portfolio");
    const ring=document.getElementById("riskRing");if(ring)setRing(ring,r.risk_score,false);
    const cat=document.getElementById("riskCatTag");if(cat){cat.textContent=r.risk_category;cat.className="fs-tag "+tagClass(r.risk_category);}
    document.getElementById("riskResult").innerHTML=
      `<div class="line"><span>Risk Score</span><strong>${r.risk_score}/100</strong></div>
       <div class="line"><span>Category</span><span class="fs-tag ${tagClass(r.risk_category)}">${r.risk_category}</span></div>
       <div class="line"><span>Confidence</span><strong>${(r.confidence*100).toFixed(0)}%</strong></div>
       <strong class="d-block mt-2">Risk Drivers</strong><ul>${r.risk_drivers.map(d=>`<li>${d}</li>`).join("")}</ul>
       <strong class="d-block mt-2">Mitigation</strong><ul>${r.mitigation.map(d=>`<li>${d}</li>`).join("")}</ul>`;
    loadHistory();loadKpis();};
}
function wireCompliance(){
  document.getElementById("compBtn").onclick=async()=>{
    const text=document.getElementById("compText").value.trim();if(!text)return;
    const r=await FinServeAPI.compliance(text);
    const fw=r.frameworks.map(f=>`<div class="fs-fwbar"><span class="lbl">${f.name}</span>
      <div class="track"><div class="fill" style="width:${f.coverage}%"></div></div>
      <span class="text-muted">${f.coverage}%</span></div>`).join("");
    document.getElementById("compResult").innerHTML=
      `<div class="line"><span>Compliance Score</span><strong>${r.compliance_score}/100</strong></div>
       <div class="line"><span>Risk Level</span><span class="fs-tag ${tagClass(r.risk_level)}">${r.risk_level}</span></div>
       <div class="line"><span>Human Review</span><strong>${r.human_review?"Recommended":"Not required"}</strong></div>
       <strong class="d-block mt-2">Framework Coverage</strong>${fw}
       <strong class="d-block mt-2">Recommendations</strong><ul>${r.recommendations.map(d=>`<li>${d}</li>`).join("")}</ul>`;
    loadHistory();loadKpis();};
}

document.addEventListener("DOMContentLoaded",async()=>{
  // Hard auth guard: if there is no token, leave immediately before any API call.
  if(!FinServeAPI.token()){window.location.replace("/login");return;}
  const nm=localStorage.getItem("fs_name");
  if(nm){const el=document.getElementById("userName");if(el)el.textContent=nm;}
  document.getElementById("logoutBtn")?.addEventListener("click",()=>{FinServeAPI.clear();location.href="/login";});
  await loadHealth();await loadKpis();await loadDocs();await loadHistory();
  try{fsRenderCharts(await FinServeAPI.charts());}catch(e){}
  wireChat();wireUpload();wireRisk();wireCompliance();
  // Pre-run risk + compliance so the dashboard is populated for screenshots
  document.getElementById("riskBtn").click();
  document.getElementById("compBtn").click();
  setTimeout(()=>{ // seed a friendly first chat exchange
    addMsg("Hello. I am the FinServe AI Copilot by Jillani SofTech. Ask me about your indexed financial or compliance documents \u2014 I answer with source citations.","ai");
  },200);
});
