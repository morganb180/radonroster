/* Radon Roster: quote form (progressive enhancement) + anonymous contact-link click counts. */
(function(){var API="https://leads.radonroster.com";
function beacon(f,t){try{var b=JSON.stringify({f:f,t:t});if(navigator.sendBeacon)navigator.sendBeacon(API+"/api/click",new Blob([b],{type:"text/plain"}));else fetch(API+"/api/click",{method:"POST",body:b,keepalive:true,mode:"no-cors"})}catch(e){}}
document.addEventListener("click",function(e){var a=e.target.closest&&e.target.closest("a[data-fid]");if(a)beacon(a.getAttribute("data-fid"),a.getAttribute("data-ct"))},true);
var forms=document.querySelectorAll("form[data-lead]");if(!forms.length)return;
var ts=false;function loadTS(){if(ts)return;ts=true;var s=document.createElement("script");s.src="https://challenges.cloudflare.com/turnstile/v0/api.js";s.async=true;s.defer=true;document.head.appendChild(s)}
var q=new URLSearchParams(location.search),pl=window.RR_PLACES||{},pre=pl[q.get("county")]||pl[q.get("city")];
function esc(x){return String(x==null?"":x).replace(/[&<>"]/g,function(c){return{"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]})}
function uid(){try{return crypto.randomUUID()}catch(e){return "k"+Date.now().toString(36)+Math.random().toString(36).slice(2,12)}}
function cslug(c){return String(c||"").toLowerCase().replace(/[^a-z]+/g,"-")}
var NEXT='<h3 class="lf-h">What happens next</h3><ol><li>Firms usually reply by phone or email within 1-2 business days.</li><li>Ask each for its PA DEP certification ID and a written quote. For mitigation, ask what post-mitigation test is included.</li><li>Questions? PA DEP Radon Hotline: 800-237-2366.</li></ol>';
forms.forEach(function(f){var src=f.querySelector("[name=source]");if(src)src.value=location.pathname;
 var id=f.querySelector("[name=idem]");if(id&&!id.value)id.value=uid();
 f.addEventListener("focusin",loadTS,{once:true});f.addEventListener("pointerenter",loadTS,{once:true});
 var cs=f.querySelector("select[name=county]");if(cs&&pre&&!cs.value)cs.value=pre;
 f.addEventListener("submit",function(e){if(!window.fetch)return;e.preventDefault();var out=f.querySelector(".lf-out"),btn=f.querySelector("button[type=submit]"),d={},sent=false;
  new FormData(f).forEach(function(v,k){d[k]=v});d.consent=!!f.querySelector("[name=consent]").checked;
  if(!String(d.email||"").trim()&&!String(d.phone||"").trim()){out.textContent="Please enter an email address or a phone number so firms can reach you.";(f.querySelector("[name=email]")||{focus:function(){}}).focus();return}
  btn.disabled=true;out.textContent="Sending...";
  fetch(f.action,{method:"POST",headers:{"content-type":"application/json",accept:"application/json"},body:JSON.stringify(d)}).then(function(r){sent=true;return r.json()}).then(function(j){
   if(j.ok){var place=j.county||d.county||"";f.innerHTML='<div class="lf-done" tabindex="-1"><h2 class="lf-h">'+(j.duplicate?'We already have your request':'Request sent')+'</h2><p>We sent your request to '+j.firms.length+' DEP-certified firm'+(j.firms.length==1?'':'s')+':</p><ul>'+j.firms.map(function(x){return'<li><strong>'+esc(x.name)+'</strong>'+(x.phone?' · <a href="tel:'+esc(String(x.phone).replace(/[^0-9+]/g,""))+'">'+esc(x.phone)+'</a>':'')+'</li>'}).join('')+'</ul><p class="muted">They will contact you directly.'+(d.email?' We emailed you this list.':' Keep this page or note the reference below.')+'</p>'+NEXT+'<p class="muted">Reference: '+esc(j.lead_id||"")+'</p>'+(place?'<p><a href="/pa/county/'+cslug(place)+'/">See every certified firm in '+esc(place)+' County</a></p>':'')+'</div>';
    try{history.replaceState(null,"",location.pathname+"?sent=1"+location.hash)}catch(x){}var dn=f.querySelector(".lf-done");if(dn)dn.focus();return}
   btn.disabled=false;
   if(j.error&&/couldn't find a certified firm/.test(j.error)){out.innerHTML=esc(j.error)+' <a href="/pa/counties/">Browse certified firms by county</a>, call the PA DEP Radon Hotline (800-237-2366), or order a mail-in test kit from a DEP-certified lab (labs are listed on every <a href="/pa/counties/">county page</a>).';}
   else out.textContent=j.fields?Object.keys(j.fields).map(function(k){return j.fields[k]}).join(" "):(j.error||"Something went wrong.");
   if(window.turnstile)try{turnstile.reset()}catch(x){}
  }).catch(function(){btn.disabled=false;
   /* Same idem key: the Worker won't route this request twice even if the first post got through. */
   if(!sent)f.submit();else out.innerHTML='We couldn\'t confirm your request. Please don\'t resend it. <a href="/pa/counties/">Browse certified firms by county</a> or call the PA DEP Radon Hotline: 800-237-2366.'})})})})();
