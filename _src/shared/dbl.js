/* ---- 電腦：在景點上點兩下 = 長按（畫出 / 擴大 100 公尺範圍）；點一下照常開介紹（等 0.25 秒確定不是點兩下） ---- */
(() => {
  const spotsEl = document.getElementById("spots");
  let lastType = "mouse", pend = null, bypass = false;
  spotsEl.addEventListener("pointerdown", e => { lastType = e.pointerType || "mouse"; }, true);
  spotsEl.addEventListener("click", e => {
    if (bypass || lastType !== "mouse" || (typeof distMode !== "undefined" && distMode)) return;
    const g = e.target.closest(".spot"); if (!g) return;
    e.stopPropagation(); e.preventDefault();
    if (pend && pend.g === g) {   // second click on the same spot
      clearTimeout(pend.t); pend = null;
      const id = g.dataset.id;
      if (RAD.id === id) RAD.r += 100; else { RAD.id = id; RAD.r = 100; }
      renderRad(); return;
    }
    if (pend) clearTimeout(pend.t);
    pend = { g, t: setTimeout(() => { pend = null; bypass = true; g.dispatchEvent(new MouseEvent("click", { bubbles: true })); bypass = false; }, 260) };
  }, true);
})();
