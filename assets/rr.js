/* Radon Roster v2 front end: search, result checker, listing filters, stepped quote form.
   lead.js still owns the actual submit (endpoint, Turnstile, consent, confirmation). */
(function () {
  "use strict";
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };
  var esc = function (s) { return String(s == null ? "" : s).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); };
  var qs = new URLSearchParams(location.search);

  /* menu: close on outside click / Escape */
  var menu = $(".menu");
  if (menu) {
    document.addEventListener("click", function (e) { if (menu.open && !menu.contains(e.target)) menu.open = false; });
    document.addEventListener("keydown", function (e) { if (e.key === "Escape") menu.open = false; });
  }

  /* ---------- home search: two popovers with one behaviour ---------- */
  var find = $("#find");
  if (find) {
    var places = [];
    try { places = JSON.parse($("#rr-places").textContent); } catch (x) {}
    var input = $("#s-where"), box = $("#s-ac"), need = $("#s-need");
    var nbtn = $("#s-need-btn"), nbox = $("#s-need-ac"), nopts = $$("a", nbox), nsel = 0;
    var sel = -1, shown = [];
    var norm = function (s) { return s.toLowerCase().replace(/\bcounty\b/, "").replace(/[^a-z]/g, ""); };
    var mark = function (list, i) { list.forEach(function (a, k) { a.setAttribute("aria-selected", k === i); }); };

    /* Looking for */
    var openNeed = function () { closeWhere(); nbox.hidden = false; nbtn.setAttribute("aria-expanded", "true"); mark(nopts, nsel); };
    var closeNeed = function () { nbox.hidden = true; nbtn.setAttribute("aria-expanded", "false"); };
    var choose = function (i) {
      nsel = i; need.value = nopts[i].dataset.v;
      nbtn.firstChild.textContent = nopts[i].querySelector("span").firstChild.textContent;
      closeNeed(); input.focus();
    };
    nbtn.closest(".seg").addEventListener("click", function (e) {
      if (e.target.closest(".ac")) return;
      nbox.hidden ? openNeed() : closeNeed();
    });
    nbox.addEventListener("click", function (e) {
      var a = e.target.closest("a"); if (!a) return;
      e.preventDefault(); choose(nopts.indexOf(a));
    });
    nbtn.addEventListener("keydown", function (e) {
      if (e.key === "ArrowDown" || e.key === "ArrowUp") {
        e.preventDefault();
        if (nbox.hidden) { openNeed(); return; }
        nsel = (nsel + (e.key === "ArrowDown" ? 1 : -1) + nopts.length) % nopts.length; mark(nopts, nsel);
      } else if ((e.key === "Enter" || e.key === " ") && !nbox.hidden) { e.preventDefault(); choose(nsel); }
      else if (e.key === "Escape") closeNeed();
    });

    /* Where */
    var go = function (p) {
      var n = need.value;
      if (!p) return;
      location.href = p.u + (n && p.k !== "z" ? "?need=" + encodeURIComponent(n) : (n && p.k === "z" ? "&need=" + encodeURIComponent(n) : ""));
    };
    var render = function () {
      closeNeed();
      var q = norm(input.value);
      if (/^\d{5}$/.test(input.value.trim())) {
        shown = [{ l: "Get matched with pros near " + input.value.trim(), s: "ZIP codes go straight to a quote request", u: "/quotes/?zip=" + input.value.trim(), k: "z" }];
      } else if (!q) {
        shown = places.filter(function (p) { return ["Pittsburgh", "Philadelphia", "Allentown", "Lancaster", "Harrisburg"].indexOf(p.l) > -1; });
      } else {
        shown = places.filter(function (p) { return norm(p.l).indexOf(q) === 0; })
          .concat(places.filter(function (p) { var n = norm(p.l); return n.indexOf(q) > 0; })).slice(0, 7);
      }
      sel = shown.length ? 0 : -1;
      box.innerHTML = shown.map(function (p, i) {
        return '<a href="' + p.u + '" role="option" id="ac' + i + '" aria-selected="' + (i === sel) + '"><i>' + (p.k === "c" ? "▦" : p.k === "z" ? "→" : "⌂") + "</i><span>" + esc(p.l) + "<small>" + esc(p.s) + "</small></span></a>";
      }).join("") || '<p class="mute" style="padding:12px">No match. Try a county name, or a 5-digit ZIP.</p>';
      box.hidden = false; input.setAttribute("aria-expanded", "true");
    };
    var closeWhere = function () { box.hidden = true; input.setAttribute("aria-expanded", "false"); };
    input.addEventListener("focus", render);
    input.addEventListener("input", render);
    input.addEventListener("keydown", function (e) {
      if (box.hidden) return;
      if (e.key === "ArrowDown" || e.key === "ArrowUp") {
        e.preventDefault();
        sel = (sel + (e.key === "ArrowDown" ? 1 : -1) + shown.length) % shown.length;
        mark($$("a", box), sel);
        input.setAttribute("aria-activedescendant", "ac" + sel);
      } else if (e.key === "Escape") closeWhere();
    });
    box.addEventListener("click", function (e) {
      var a = e.target.closest("a"); if (!a) return;
      e.preventDefault(); go(shown[$$("a", box).indexOf(a)]);
    });
    document.addEventListener("click", function (e) { if (!find.contains(e.target)) { closeWhere(); closeNeed(); } });
    find.addEventListener("submit", function (e) {
      e.preventDefault();
      if (box.hidden) render();
      if (sel > -1 && shown[sel]) go(shown[sel]);
      else location.href = "/pa/counties/";
    });
  }

  /* ---------- tabs (home browse) ---------- */
  $$(".tabs").forEach(function (t) {
    var bs = $$("button", t);
    bs.forEach(function (b) {
      b.addEventListener("click", function () {
        bs.forEach(function (x) { var on = x === b; x.setAttribute("aria-selected", on); document.getElementById(x.dataset.t).hidden = !on; });
      });
    });
  });

  /* ---------- result checker ---------- */
  var mv = $("#m-val");
  if (mv) {
    var ptr = $(".scale .ptr"), out = $("#m-out");
    var upd = function () {
      var v = parseFloat(mv.value);
      if (isNaN(v) || v < 0) {
        ptr.style.left = "0%"; out.className = "verdict";
        out.innerHTML = "<b>Type your result above</b><p>We'll tell you what EPA recommends at that level.</p>"; return;
      }
      ptr.style.left = Math.min(v, 10) * 10 + "%";
      if (v >= 4) {
        out.className = "verdict high";
        out.innerHTML = "<b>Fix it</b><p>EPA recommends fixing your home at 4 pCi/L or more. PA DEP says most systems cost $800–$1,200.</p>" +
          '<a class="btn block" data-ga-loc="checker" href="/quotes/?need=result&level=' + encodeURIComponent(v) + '">Get quotes from certified mitigators</a>';
      } else if (v >= 2) {
        out.className = "verdict mid";
        out.innerHTML = "<b>Consider a fix</b><p>EPA suggests considering a fix between 2 and 4 pCi/L. A second test can confirm a short-term result.</p>" +
          '<a class="btn block quiet" data-ga-loc="checker" href="/quotes/?need=result&level=' + encodeURIComponent(v) + '">Talk to a certified pro</a>';
      } else {
        out.className = "verdict low";
        out.innerHTML = "<b>Below 2 pCi/L</b><p>EPA doesn't call for a fix at this level. Levels change over time, so test again after big changes to the house.</p>";
      }
    };
    mv.addEventListener("input", upd);
  }

  /* ---------- listing: filter + sort ---------- */
  var list = $("#list");
  if (list) {
    var cards = $$(".pcard", list), chips = $$(".toolbar .chip[data-f]"), sortSel = $("#sort"), count = $("#count"), none = $("#none");
    var f = "all";
    var map = { test: "t", testing: "t", mitigation: "m", fix: "m", result: "m", lab: "l", kit: "l" };
    if (map[qs.get("need")]) f = map[qs.get("need")];
    var apply = function () {
      var n = 0;
      cards.forEach(function (c) {
        var ok = f === "all" || (f === "r" ? c.dataset.top === "1" : c.dataset.svc.indexOf(f) > -1);
        c.hidden = !ok; if (ok) n++;
      });
      chips.forEach(function (ch) { ch.setAttribute("aria-pressed", ch.dataset.f === f); });
      var lab = { score: "sorted by Google rating", n: "sorted by number of reviews", town: "sorted by town", name: "sorted by name" }[sortSel.value];
      count.innerHTML = n + " pro" + (n === 1 ? "" : "s") + " <span>· " + lab + "</span>";
      none.hidden = n > 0;
    };
    var sort = function () {
      var k = sortSel.value;
      cards.sort(function (a, b) {
        if (k === "score") return (+b.dataset.score - +a.dataset.score) || a.dataset.name.localeCompare(b.dataset.name);
        if (k === "n") return (+b.dataset.n - +a.dataset.n) || a.dataset.name.localeCompare(b.dataset.name);
        if (k === "town") return a.dataset.town.localeCompare(b.dataset.town) || a.dataset.name.localeCompare(b.dataset.name);
        return a.dataset.name.localeCompare(b.dataset.name);
      });
      cards.forEach(function (c) { list.appendChild(c); });
      apply();
    };
    document.addEventListener("click", function (e) {
      var ch = e.target.closest && e.target.closest(".chip[data-f]"); if (!ch) return;
      f = ch.dataset.f; apply();
    });
    sortSel.addEventListener("change", sort);
    var views = $$(".view button");
    var setView = function (v) {
      list.classList.toggle("table", v === "table");
      views.forEach(function (b) { b.setAttribute("aria-pressed", b.dataset.v === v); });
      try { localStorage.setItem("rr-view", v); } catch (x) {}
    };
    views.forEach(function (b) { b.addEventListener("click", function () { setView(b.dataset.v); }); });
    try { if (localStorage.getItem("rr-view") === "table") setView("table"); } catch (x) {}
    apply();
  }

  /* ---------- quote flow ---------- */
  var form = $("form.qflow[data-lead]");
  if (form) {
    form.classList.add("js");
    var steps = $$(".qstep", form), i = 0;
    var next = $(".qnext", form), back = $(".qback", form), send = $(".qsend", form), bar = $("#qbar");
    var field = function (n) { return form.querySelector('[name="' + n + '"]'); };
    var checked = function () { return form.querySelector('[name="need"]:checked'); };
    var show = function (k, focus) {
      i = Math.max(0, Math.min(steps.length - 1, k));
      steps.forEach(function (s, j) { s.classList.toggle("on", j === i); });
      bar.style.width = Math.round((i + 1) / steps.length * 100) + "%";
      back.hidden = i === 0;
      next.hidden = i === steps.length - 1; send.hidden = !next.hidden;
      if (focus) { var lg = $("legend", steps[i]); if (lg) lg.focus(); window.scrollTo({ top: 0, behavior: "smooth" }); }
      summary();
    };
    var valid = function () {
      var ok = true;
      $$("input,select,textarea", steps[i]).some(function (el) {
        if (el.type === "hidden" || el.disabled) return false;
        if (!el.checkValidity()) { el.reportValidity(); ok = false; return true; }
        return false;
      });
      return ok;
    };
    next.addEventListener("click", function () { if (valid()) show(i + 1, true); });
    back.addEventListener("click", function () { show(i - 1, true); });
    form.addEventListener("change", function (e) {
      if (e.target.name === "need") {
        $("#lf-lvl").hidden = e.target.value !== "result";
        if (e.target.value !== "result") setTimeout(function () { if (i === 0) show(1, true); }, 180);
      }
      summary();
    });
    form.addEventListener("input", summary);
    form.addEventListener("keydown", function (e) {
      if (e.key === "Enter" && e.target.tagName !== "TEXTAREA" && i < steps.length - 1) { e.preventDefault(); next.click(); }
    });
    form.addEventListener("invalid", function (e) {
      var s = e.target.closest(".qstep"); if (s && steps.indexOf(s) !== i) show(steps.indexOf(s), false);
    }, true);
    form.addEventListener("submit", function (e) {
      var em = field("email").value.trim(), ph = field("phone").value.trim();
      if (!em && !ph) { e.preventDefault(); e.stopImmediatePropagation(); var o = $(".lf-out", form); o.textContent = "Add an email or a phone number so pros can reach you."; try { form.dispatchEvent(new CustomEvent("lead:result", { bubbles: true, detail: { ok: false, type: "missing_contact" } })); } catch (x) {} field("email").focus(); return; }
      if (!form.checkValidity()) { e.preventDefault(); e.stopImmediatePropagation(); form.reportValidity(); }
    }, true);
    form.addEventListener("lead:result", function (e) {
      if (e.detail && e.detail.ok) { $(".qnav", form) && ($(".qnav", form).hidden = true); bar.style.width = "100%"; var p = $("#qpanel"); if (p) p.innerHTML = "<img src=\"/assets/img/inspector-thumbs.webp\" alt=\"\" style=\"width:120px;margin:-8px 0 8px\"><h2>What's next</h2><p style=\"margin-top:10px;color:var(--ink2)\">The pros named here will contact you directly. Compare their quotes and DEP numbers before you hire.</p><p class=\"mute\" style=\"margin-top:12px;font-size:.86rem\">To delete our copy of your request, email hello@radonroster.com.</p>"; }
    });

    var LBL = { test: "Test my home", mitigation: "Fix high radon", result: "Help with a result", kit: "Mail-in test kit" };
    function summary() {
      var rows = [], c = checked();
      if (c) rows.push(["Service", LBL[c.value] || c.value]);
      var lv = field("level").value; if (lv && c && c.value === "result") rows.push(["Result", lv + " pCi/L"]);
      var z = field("zip").value; if (z) rows.push(["ZIP", z]);
      var ct = field("county").value; if (ct) rows.push(["County", ct]);
      var fm = field("firm").value; if (fm && window.RR_FIRMS && RR_FIRMS[fm]) rows.unshift(["Starting with", RR_FIRMS[fm]]);
      $("#qsum").innerHTML = rows.length ? "<dl>" + rows.map(function (r) { return "<div><dt>" + esc(r[0]) + "</dt><dd>" + esc(r[1]) + "</dd></div>"; }).join("") + "</dl>" : '<p class="empty-s">Nothing yet.</p>';
      var h = $("#levelhint"), v = parseFloat(lv);
      if (h) h.textContent = isNaN(v) ? "At 4 pCi/L or more, we connect you with mitigators. Under 4, with testers." : v >= 4 ? v + " pCi/L is at or above EPA's action level, so this goes to certified mitigators." : v + " pCi/L is under 4, so this goes to certified testers.";
    }

    /* prefill from the link that brought them here */
    var n = qs.get("need");
    if (n) { var r = form.querySelector('[name="need"][value="' + n + '"]'); if (r) { r.checked = true; $("#lf-lvl").hidden = n !== "result"; } }
    var lv0 = qs.get("level"); if (lv0 && /^\d+(\.\d+)?$/.test(lv0)) { field("level").value = lv0; }
    var z0 = qs.get("zip"); if (z0 && /^\d{5}$/.test(z0)) field("zip").value = z0;
    var cs = qs.get("county");
    if (cs && window.RR_COUNTIES && RR_COUNTIES[cs]) {
      field("county").value = RR_COUNTIES[cs]; field("zip").required = false;
      $("#ziphint").textContent = "Optional. We'll look in " + RR_COUNTIES[cs] + " County; a ZIP helps us start with the closest pros.";
    }
    var start = 0;
    if (checked() && !(n === "result" && !lv0)) start = 1;
    if (start === 1 && field("zip").value) start = 2;
    show(start, false);
  }
})();
