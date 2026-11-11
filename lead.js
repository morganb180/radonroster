/* Radon Roster: quote form (progressive enhancement) + anonymous contact-link click counts. */
(function(){var API="https://leads.radonroster.com";
function beacon(f,t){try{var b=JSON.stringify({f:f,t:t});if(navigator.sendBeacon)navigator.sendBeacon(API+"/api/click",new Blob([b],{type:"text/plain"}));else fetch(API+"/api/click",{method:"POST",body:b,keepalive:true,mode:"no-cors"})}catch(e){}}
document.addEventListener("click",function(e){var a=e.target.closest&&e.target.closest("a[data-fid]");if(a)beacon(a.getAttribute("data-fid"),a.getAttribute("data-ct"))},true);
var forms=document.querySelectorAll("form[data-lead]");if(!forms.length)return;
var ts=false;function loadTS(){if(ts)return;ts=true;var s=document.createElement("script");s.src="https://challenges.cloudflare.com/turnstile/v0/api.js";s.async=true;s.defer=true;document.head.appendChild(s)}
var q=new URLSearchParams(location.search),pl=window.RR_PLACES||{},pre=pl[q.get("county")]||pl[q.get("city")];
function esc(x){return String(x==null?"":x).replace(/[&<>"]/g,function(c){return{"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]})}
function uid(){try{return crypto.randomUUID()}catch(e){return "k"+Date.now().toString(36)+Math.random().toString(36).slice(2,12)}}
function emit(f,x){try{f.dispatchEvent(new CustomEvent("lead:result",{bubbles:true,detail:x}))}catch(e){}}
function cslug(c){return String(c||"").toLowerCase().replace(/[^a-z]+/g,"-")}
function nextSteps(email){return '<h3 class="lf-h">What happens next</h3><ol><li>'+(email?'Their names are listed here. The same list is also sent to the address you gave, from leads@radonroster.com.':'Their names are listed here. Save this page or note the reference.')+'</li><li>We connected you with these firms. They contact you directly. We don\'t call or text you.</li><li>Compare their PA DEP certification IDs and written quotes before you hire. For mitigation, ask what post-install test is included. PA DEP Radon Hotline: 800-237-2366.</li></ol><p class="muted">To delete our copy, email <a href="mailto:hello@radonroster.com">hello@radonroster.com</a>. Firms keep what they received under their own policies.</p>'}
forms.forEach(function(f){var src=f.querySelector("[name=source]");if(src)src.value=location.pathname;
 var id=f.querySelector("[name=idem]");if(id&&!id.value)id.value=uid();
 f.addEventListener("focusin",loadTS,{once:true});f.addEventListener("change",loadTS,{once:true}); /* Turnstile loads on first focus or change, never on hover */
 var cs=f.querySelector("select[name=county]");if(cs&&pre&&!cs.value)cs.value=pre;
 var fi=f.querySelector("input[name=firm]"),fid=q.get("firm"),fn=fid&&(window.RR_FIRMS||{})[fid];
 if(fi&&fn&&/^F[0-9]{1,6}$/.test(fid)){fi.value=fid;var fl=f.querySelector(".lf-firm");if(fl){fl.innerHTML='Your request goes to <strong>'+esc(fn)+'</strong> and up to 2 other nearby certified pros.';fl.hidden=false}}
 f.addEventListener("submit",function(e){if(!window.fetch)return;e.preventDefault();var out=f.querySelector(".lf-out"),btn=f.querySelector("button[type=submit]"),d={},sent=false,st=0;
  new FormData(f).forEach(function(v,k){d[k]=v});d.consent=!!f.querySelector("[name=consent]").checked;var mk=f.querySelector("[name=marketing_opt_in]");d.marketing_opt_in=!!(mk&&mk.checked);
  if(!String(d.email||"").trim()&&!String(d.phone||"").trim()){emit(f,{ok:false,type:"missing_contact"});out.textContent="Please enter an email address or a phone number so firms can reach you.";(f.querySelector("[name=email]")||{focus:function(){}}).focus();return}
  btn.disabled=true;out.textContent="Sending...";
  fetch(f.action,{method:"POST",headers:{"content-type":"application/json",accept:"application/json"},body:JSON.stringify(d)}).then(function(r){sent=true;st=r.status;return r.json()}).then(function(j){
   if(j.ok){emit(f,{ok:true,duplicate:!!j.duplicate,firms:(j.firms||[]).length,county:j.county||d.county||"",need:d.need||""});var place=j.county||d.county||"";f.innerHTML='<div class="lf-done" tabindex="-1"><h2 class="lf-h">'+(j.duplicate?'We already have your request':'Request sent')+'</h2><p>We connected you with '+j.firms.length+' DEP-certified firm'+(j.firms.length==1?'':'s')+':</p><ul>'+j.firms.map(function(x){return'<li><strong>'+esc(x.name)+'</strong></li>'}).join('')+'</ul><p class="muted">They will contact you directly.'+(d.email?' The same names are sent to the address you gave.':' Keep this page or note the reference below.')+'</p>'+nextSteps(!!String(d.email||"").trim())+'<p class="muted">Reference: '+esc(j.lead_id||"")+'</p>'+(place?'<p><a href="/pa/county/'+cslug(place)+'/">See every certified firm in '+esc(place)+' County</a></p>':'')+'</div>';
    try{history.replaceState(null,"",location.pathname+"?sent=1"+location.hash)}catch(x){}var dn=f.querySelector(".lf-done");if(dn)dn.focus();return}
   btn.disabled=false;emit(f,{ok:false,status:st,duplicate:!!j.duplicate,fields:j.fields?Object.keys(j.fields):[]});
   if(j.error&&/couldn't find a certified firm/.test(j.error)){out.innerHTML=esc(j.error)+' <a href="/pa/counties/">Browse certified firms by county</a>, call the PA DEP Radon Hotline (800-237-2366), or order a mail-in test kit from a DEP-certified lab (labs are listed on every <a href="/pa/counties/">county page</a>).';}
   else out.textContent=j.fields?Object.keys(j.fields).map(function(k){return j.fields[k]}).join(" "):(j.error||"Something went wrong.");
   if(window.turnstile)try{turnstile.reset()}catch(x){}
  }).catch(function(){btn.disabled=false;emit(f,{ok:false,type:sent?"unconfirmed":"network"});
   /* Same idem key: the Worker won't route this request twice even if the first post got through. */
   if(!sent)f.submit();else out.innerHTML='We couldn\'t confirm your request. Please don\'t resend it. <a href="/pa/counties/">Browse certified firms by county</a> or call the PA DEP Radon Hotline: 800-237-2366.'})})})})();
