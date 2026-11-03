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
/* Thank-you state (quote-trust v1). Keeps .lf-done (analytics: link_location=lead_success) and the lead:result event. */
var OKI='<i aria-hidden="true"><svg width="20" height="20" viewBox="0 0 16 16"><path d="M3.8 8.4l2.7 2.7 5.7-5.9" fill="none" stroke="#fff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg></i>';
function done(j,d){var n=(j.firms||[]).length,place=j.county||d.county||"",em=String(d.email||"").trim();
 return '<div class="lf-done qt-done" tabindex="-1"><div class="qt-ok">'+OKI+'<div><h2 class="lf-h">'+(j.duplicate?'We already have your request':'Your request is on its way')+'</h2><p class="muted" style="margin:.2rem 0 0">'+(j.duplicate?'We didn\'t send it again. ':'')+'We sent it to '+n+' PA DEP-certified firm'+(n==1?'':'s')+' near you:</p></div></div>'
 +'<ul class="qt-firms">'+j.firms.map(function(x){return'<li><strong>'+esc(x.name)+'</strong>'+(x.phone?' · <a href="tel:'+esc(String(x.phone).replace(/[^0-9+]/g,""))+'">'+esc(x.phone)+'</a>':'')+'</li>'}).join('')+'</ul>'
 +'<h3 class="lf-h">What happens next</h3><ol class="qt-next">'
 +(em?'<li><strong>Check your inbox.</strong> We emailed this list to '+esc(em)+' from leads@radonroster.com.</li>':'<li><strong>Save this page.</strong> You didn\'t give an email, so this list is your only copy.</li>')
 +'<li><strong>The firms contact you directly</strong> by email or phone. Replies come from the firms, not from Radon Roster. You can also call them now.</li>'
 +'<li><strong>Compare before you hire.</strong> Ask each for its PA DEP certification ID and a written quote. For mitigation, ask what post-mitigation test is included. You don\'t have to hire anyone.</li></ol>'
 +'<p class="muted">Questions about radon? PA DEP Radon Hotline: 800-237-2366. Want our copy of your request deleted? Email <a href="mailto:hello@radonroster.com">hello@radonroster.com</a> with your reference.</p>'
 +'<p class="muted">Reference: <span class="qt-ref">'+esc(j.lead_id||"")+'</span></p>'+(place?'<p><a href="/pa/county/'+cslug(place)+'/">See every certified firm in '+esc(place)+' County</a></p>':'')+'</div>'}
forms.forEach(function(f){var src=f.querySelector("[name=source]");if(src)src.value=location.pathname;
 var id=f.querySelector("[name=idem]");if(id&&!id.value)id.value=uid();
 f.addEventListener("focusin",loadTS,{once:true});f.addEventListener("pointerenter",loadTS,{once:true});
 var cs=f.querySelector("select[name=county]");if(cs&&pre&&!cs.value)cs.value=pre;
 var fi=f.querySelector("input[name=firm]"),fid=q.get("firm"),fn=fid&&(window.RR_FIRMS||{})[fid];
 if(fi&&fn&&/^F[0-9]{1,6}$/.test(fid)){fi.value=fid;var fl=f.querySelector(".lf-firm");if(fl){fl.innerHTML='Your request goes to <strong>'+esc(fn)+'</strong> and up to 2 other nearby certified pros.';fl.hidden=false}}
 f.addEventListener("submit",function(e){if(!window.fetch)return;e.preventDefault();var out=f.querySelector(".lf-out"),btn=f.querySelector("button[type=submit]"),d={},sent=false,st=0;
  new FormData(f).forEach(function(v,k){d[k]=v});d.consent=!!f.querySelector("[name=consent]").checked;var mk=f.querySelector("[name=marketing_opt_in]");d.marketing_opt_in=!!(mk&&mk.checked);
  if(!String(d.email||"").trim()&&!String(d.phone||"").trim()){emit(f,{ok:false,type:"missing_contact"});out.textContent="Please enter an email address or a phone number so firms can reach you.";(f.querySelector("[name=email]")||{focus:function(){}}).focus();return}
  btn.disabled=true;out.textContent="Sending...";
  fetch(f.action,{method:"POST",headers:{"content-type":"application/json",accept:"application/json"},body:JSON.stringify(d)}).then(function(r){sent=true;st=r.status;return r.json()}).then(function(j){
   if(j.ok){emit(f,{ok:true,duplicate:!!j.duplicate,firms:(j.firms||[]).length,county:j.county||d.county||"",need:d.need||""});var place=j.county||d.county||"";f.innerHTML=done(j,d);
    try{history.replaceState(null,"",location.pathname+"?sent=1"+location.hash)}catch(x){}var dn=f.querySelector(".lf-done");if(dn){dn.focus();try{dn.scrollIntoView({block:"start",behavior:"smooth"})}catch(x){}}return}
   btn.disabled=false;emit(f,{ok:false,status:st,duplicate:!!j.duplicate,fields:j.fields?Object.keys(j.fields):[]});
   if(j.error&&/couldn't find a certified firm/.test(j.error)){out.innerHTML=esc(j.error)+' <a href="/pa/counties/">Browse certified firms by county</a>, call the PA DEP Radon Hotline (800-237-2366), or order a mail-in test kit from a DEP-certified lab (labs are listed on every <a href="/pa/counties/">county page</a>).';}
   else out.textContent=j.fields?Object.keys(j.fields).map(function(k){return j.fields[k]}).join(" "):(j.error||"Something went wrong.");
   if(window.turnstile)try{turnstile.reset()}catch(x){}
  }).catch(function(){btn.disabled=false;emit(f,{ok:false,type:sent?"unconfirmed":"network"});
   /* Same idem key: the Worker won't route this request twice even if the first post got through. */
   if(!sent)f.submit();else out.innerHTML='We couldn\'t confirm your request. Please don\'t resend it. <a href="/pa/counties/">Browse certified firms by county</a> or call the PA DEP Radon Hotline: 800-237-2366.'})})})})();
