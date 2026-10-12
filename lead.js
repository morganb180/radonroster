/* Radon Roster: quote form (progressive enhancement) + anonymous contact-link click counts. */
(function(){var API="https://leads.radonroster.com";
function beacon(f,t){try{var b=JSON.stringify({f:f,t:t});if(navigator.sendBeacon)navigator.sendBeacon(API+"/api/click",new Blob([b],{type:"text/plain"}));else fetch(API+"/api/click",{method:"POST",body:b,keepalive:true,mode:"no-cors"})}catch(e){}}
document.addEventListener("click",function(e){var a=e.target.closest&&e.target.closest("a[data-fid]");if(a)beacon(a.getAttribute("data-fid"),a.getAttribute("data-ct"))},true);
var forms=document.querySelectorAll("form[data-lead]");if(!forms.length)return;
var s=document.createElement("script");s.src="https://challenges.cloudflare.com/turnstile/v0/api.js";s.async=true;s.defer=true;document.head.appendChild(s);
var q=new URLSearchParams(location.search),pl=window.RR_PLACES||{},pre=pl[q.get("county")]||pl[q.get("city")];
function esc(x){return String(x==null?"":x).replace(/[&<>"]/g,function(c){return{"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]})}
forms.forEach(function(f){var src=f.querySelector("[name=source]");if(src)src.value=location.pathname;
 var cs=f.querySelector("select[name=county]");if(cs&&pre&&!cs.value)cs.value=pre;
 f.addEventListener("submit",function(e){if(!window.fetch)return;e.preventDefault();var out=f.querySelector(".lf-out"),btn=f.querySelector("button[type=submit]"),d={};
  new FormData(f).forEach(function(v,k){d[k]=v});d.consent=!!f.querySelector("[name=consent]").checked;btn.disabled=true;out.textContent="Sending...";
  fetch(f.action,{method:"POST",headers:{"content-type":"application/json",accept:"application/json"},body:JSON.stringify(d)}).then(function(r){return r.json()}).then(function(j){
   if(j.ok){f.innerHTML='<div class="lf-done"><h2 class="lf-h">Request sent</h2><p>We sent your request to '+j.firms.length+' DEP-certified firm'+(j.firms.length==1?'':'s')+':</p><ul>'+j.firms.map(function(x){return'<li><strong>'+esc(x.name)+'</strong>'+(x.phone?' · '+esc(x.phone):'')+'</li>'}).join('')+'</ul><p class="muted">They will contact you directly.'+(d.email?' We emailed you this list.':'')+'</p></div>';return}
   btn.disabled=false;out.textContent=j.fields?Object.keys(j.fields).map(function(k){return j.fields[k]}).join(" "):(j.error||"Something went wrong.");if(window.turnstile)try{turnstile.reset()}catch(x){}
  }).catch(function(){btn.disabled=false;f.submit()})})})})();
