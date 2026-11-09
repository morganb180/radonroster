/* Stepped quote form. Does not change field names, the endpoint, Turnstile, or consent.
   The lead router chooses recipients after submit, so this never names firms except the one
   the visitor already opened (?firm=), which lead.js writes into the firm field. */
(function(){
  var form=document.querySelector("form.qflow[data-lead]");
  if(!form)return;
  var steps=Array.prototype.slice.call(form.querySelectorAll(".qstep"));
  var n=steps.length,focusOk=false;
  function esc(s){return String(s==null?"":s).replace(/[&<>"]/g,function(c){return{"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]})}
  function on(){for(var i=0;i<n;i++)if(steps[i].classList.contains("is-on"))return i;return 0}
  function show(k,doFocus){
    if(k<0||k>=n)return;
    steps.forEach(function(s,i){s.classList.toggle("is-on",i===k)});
    var prog=document.getElementById("qprog"),meter=document.getElementById("qmeter"),bar=meter&&meter.querySelector("span");
    if(prog)prog.textContent="Question "+(k+1)+" of "+n;
    if(meter)meter.setAttribute("aria-valuenow",String(k+1));
    if(bar)bar.style.width=Math.round((k+1)/n*100)+"%";
    if(doFocus){
      var legend=steps[k].querySelector("legend");
      if(legend){legend.setAttribute("tabindex","-1");legend.focus()}
    }
  }
  function stepValid(step){
    var els=step.querySelectorAll("input,select,textarea"),j;
    for(j=0;j<els.length;j++){
      if(els[j].disabled||els[j].type==="hidden")continue;
      if(!els[j].checkValidity()){els[j].reportValidity();return false}
    }
    return true;
  }
  form.addEventListener("click",function(e){
    var t=e.target.closest&&e.target.closest("button");
    if(!t||!form.contains(t))return;
    var i=on();
    if(t.classList.contains("qnext")||t.classList.contains("qskip")){
      e.preventDefault();
      if(t.classList.contains("qskip")){var lv=form.querySelector("[name=level]");if(lv)lv.value=""}
      if(t.classList.contains("qnext")&&!stepValid(steps[i]))return;
      show(i+1,true);render();
    }else if(t.classList.contains("qback")){e.preventDefault();show(i-1,true)}
  });
  form.addEventListener("keydown",function(e){
    if(e.key!=="Enter"||e.target.tagName==="TEXTAREA"||!form.classList.contains("is-stepped"))return;
    var step=e.target.closest&&e.target.closest(".qstep");
    if(!step||!step.classList.contains("is-on"))return;
    if(on()<n-1){e.preventDefault();var btn=step.querySelector(".qnext");if(btn)btn.click()}
  });
  form.addEventListener("invalid",function(e){
    var s=e.target.closest&&e.target.closest(".qstep");
    if(!s)return;
    var idx=steps.indexOf(s);
    if(idx>=0)show(idx,false);
  },true);

  function checked(name){return form.querySelector('[name="'+name+'"]:checked')}
  function field(name){return form.querySelector('[name="'+name+'"]')}
  function needLabel(){
    var el=checked("need");
    if(!el)return "";
    var b=el.parentNode.querySelector("b");
    return b?b.textContent:el.value;
  }
  function firmName(){
    var id=(field("firm")||{}).value||"";
    if(!id||!window.RR_FIRMS)return "";
    return RR_FIRMS[id]||"";
  }
  function whoText(){
    var fn=firmName(),need=(checked("need")||{}).value||"";
    if(fn)return "We connect you with "+fn+" and up to 2 other nearby certified firms. They contact you directly. You will see who was included on the next screen. Firms can't pay to be picked.";
    if(need==="kit")return "We connect you with up to 3 DEP-certified radon labs. Labs on the PA DEP list can be anywhere, not only in your county. They contact you directly. You will see their names on the next screen. Firms can't pay to be picked.";
    return "We connect you with up to 3 PA DEP-certified firms that offer the service you chose, nearest available first, starting with your county and the counties next to it. They contact you directly. You will see their names on the next screen. If you came from a firm's listing, that firm is one of them. Firms can't pay to be picked.";
  }
  function buttonText(){
    var fn=firmName();
    if(fn)return "We connect you with "+fn+" and up to 2 other nearby PA DEP-certified firms. They contact you directly. Radon Roster is a directory, not a contractor. No obligation to hire.";
    return "We connect you with up to 3 nearby PA DEP-certified firms that offer this service. They contact you directly. Their names appear on the next screen. Radon Roster is a directory, not a contractor. No obligation to hire.";
  }
  function levelNote(){
    var el=document.getElementById("levelhint");
    if(!el)return;
    var need=(checked("need")||{}).value||"";
    var raw=(field("level")||{}).value||"";
    var num=parseFloat(raw);
    if(need!=="result"){
      el.textContent=raw?"Firms can see this number in the request. Choosing test, mitigation or a lab kit sends the request to firms that offer that service.":"Optional. You can skip this. Choosing test, mitigation or a lab kit sends the request to firms that offer that service.";
      return;
    }
    if(raw===""||isNaN(num)){el.textContent="If you skip the number, a help-with-a-result request goes to mitigators.";return}
    if(num>=4)el.textContent=num+" pCi/L is at or above EPA's 4 pCi/L action level, so this request goes to mitigators. PA DEP says most mitigation systems cost $800–$1,200.";
    else if(num>=2)el.textContent=num+" pCi/L is between 2 and 4, where EPA says to consider fixing. Under 4, this request goes to testers.";
    else el.textContent=num+" pCi/L is under 4, so this request goes to testers.";
  }
  function render(){
    var rows=[];
    var need=needLabel();if(need)rows.push(["Service",need]);
    var zip=(field("zip")||{}).value||"";if(zip)rows.push(["ZIP",zip]);
    var county=(field("county")||{}).value||"";if(county)rows.push(["County",county]);
    var level=(field("level")||{}).value||"";if(level)rows.push(["Result",level+" pCi/L"]);
    var name=(field("name")||{}).value||"";if(name)rows.push(["Name",name]);
    var sum=document.getElementById("qsum");
    if(sum){
      sum.innerHTML=rows.length?("<dl>"+rows.map(function(r){return "<div><dt>"+esc(r[0])+"</dt><dd>"+esc(r[1])+"</dd></div>"}).join("")+"</dl>"):'<p class="muted">Nothing entered yet.</p>';
    }
    var rec=document.getElementById("qrec");if(rec)rec.textContent=whoText();
    var who=document.getElementById("qwho");if(who)who.textContent=buttonText();
    levelNote();
  }
  var params=new URLSearchParams(location.search);
  var need=params.get("need");
  if(need){
    var radios=form.querySelectorAll("[name=need]"),r;
    for(r=0;r<radios.length;r++)if(radios[r].value===need){radios[r].checked=true;break}
  }
  var zip=params.get("zip");
  if(zip&&/^\d{5}$/.test(zip)&&field("zip"))field("zip").value=zip;
  var level=params.get("level");
  if(level&&/^\d+(\.\d+)?$/.test(level)&&field("level"))field("level").value=level;
  var slug=params.get("county")||"";
  if(slug&&window.RR_COUNTIES&&RR_COUNTIES[slug]&&field("county")){
    field("county").value=RR_COUNTIES[slug];
    var z=field("zip");
    if(z)z.required=false;
    var hint=document.getElementById("ziphint");
    if(hint)hint.textContent="Optional. We already have "+RR_COUNTIES[slug]+" County from the page you came from. A ZIP lets us start with firms closer to you.";
  }
  form.addEventListener("input",render);
  form.addEventListener("change",render);
  form.addEventListener("lead:result",function(e){
    var d=e.detail||{};
    if(!d.ok)return;
    var panel=document.getElementById("qpanel");
    if(!panel)return;
    panel.innerHTML='<h2>Connected</h2><p>The firms named in the confirmation are the ones you were connected with. They contact you directly. We don\'t call or text you.</p><ul class="qpriv"><li>We keep a copy of the request so we can run the service. We don\'t sell it.</li><li>Delete that copy anytime: <a href="mailto:hello@radonroster.com">hello@radonroster.com</a>.</li></ul>';
  });
  var more=document.querySelector(".qmore");
  if(more&&window.matchMedia("(max-width:900px)").matches)more.open=false;
  show(on(),false);
  render();
})();
