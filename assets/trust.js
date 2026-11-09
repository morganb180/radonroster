/* Promotes the real PA DEP cert-id line onto each listing card. No new facts: the text is copied from the card's own source line. */
(function(){
  var cards=document.querySelectorAll(".firm");
  for(var i=0;i<cards.length;i++){
    var card=cards[i],ids=card.querySelector(".ids"),slot=card.querySelector("summary > div");
    if(!ids||!slot||slot.querySelector(".cred"))continue;
    var full=ids.textContent.replace(/\s+/g," ").trim();
    if(!full)continue;
    var parts=full.split(/\s*·\s*/).filter(Boolean);
    var el=document.createElement("span");
    el.className="cred";
    el.textContent="DEP "+parts[0]+(parts.length>1?" · +"+(parts.length-1)+" more":"");
    el.title="PA DEP cert IDs: "+full;
    slot.appendChild(el);
  }
})();
