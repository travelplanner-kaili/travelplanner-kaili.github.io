const { chromium } = require('playwright');
(async () => { const b = await chromium.launch(); const p = await b.newPage();
 p.on('pageerror', e=>console.log('ERR', e.message, (e.stack||'').split('\n')[1]));
 await p.goto('file:///home/claude/lucca/real/lucca-real.html'); await p.waitForTimeout(800); await b.close(); })();
