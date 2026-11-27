// Full-res recorder: page animations are slowed by SLOW, frames grabbed as fast as possible (~11/s), times divided by SLOW later.
const {chromium}=require('playwright');const fs=require('fs');
const OUT=process.argv[2];const seq=require(process.argv[3]);const SLOW=+(process.env.SLOW||4);
fs.rmSync(OUT,{recursive:true,force:true});fs.mkdirSync(OUT,{recursive:true});
(async()=>{const b=await chromium.launch();
const c=await b.newContext({viewport:{width:432,height:768},deviceScaleFactor:2.5,isMobile:true,hasTouch:true});const p=await c.newPage();
await p.addInitScript((B)=>{localStorage.setItem('trip-tour-rome','1');localStorage.setItem('trip-tour-plan-rome','1');localStorage.setItem('trip-nobase-rome',B);},process.env.BASE||'lv1');
const need=new Set();
await c.route('http://rome.test/**',r=>r.fulfill({path:'/home/claude/rome/real/rome-real.html',contentType:'text/html; charset=utf-8'}));
await c.route(/tile\.openstreetmap\.org/,async r=>{const m=r.request().url().match(/org\/(\d+)\/(\d+)\/(\d+)\.png/);const f=m&&`/home/claude/video/tiles/${m[1]}/${m[2]}/${m[3]}.png`;if(f&&fs.existsSync(f))return r.fulfill({path:f,contentType:'image/jpeg'});if(m)need.add(m.slice(1,4).join('/'));return r.abort();});
const RT=fs.existsSync('/home/claude/video/routes.json')?JSON.parse(fs.readFileSync('/home/claude/video/routes.json','utf8')):{};const needR=new Set();
await c.route(/routing\.openstreetmap/,r=>{const u=r.request().url();if(RT[u])return r.fulfill({body:JSON.stringify(RT[u]),contentType:'application/json'});needR.add(u);return r.abort();});
await c.route(/overpass|version\.json/,r=>r.abort());
await p.goto('http://rome.test/rome-real.html');await p.waitForTimeout(1500);
await p.addStyleTag({content:`.leaflet-control-attribution{display:none!important}
.tapfx{position:fixed;width:46px;height:46px;margin:-23px 0 0 -23px;border-radius:50%;background:rgba(255,255,255,.6);border:3px solid rgba(30,30,30,.6);box-shadow:0 0 0 6px rgba(255,255,255,.35);z-index:99999;pointer-events:none;animation:tapfx .6s ease-out forwards}
@keyframes tapfx{0%{transform:scale(.4);opacity:1}70%{opacity:.9}100%{transform:scale(1.7);opacity:0}}`});
if(seq.pre)await seq.pre(p);
const cdp=await c.newCDPSession(p);
await cdp.send('Animation.enable');await cdp.send('Animation.setPlaybackRate',{playbackRate:1/SLOW});
const frames=[];let rec=true,n=0;
const loop=(async()=>{while(rec){const t=Date.now();const r=await cdp.send('Page.captureScreenshot',{format:'jpeg',quality:92,optimizeForSpeed:true,clip:{x:0,y:0,width:432,height:768,scale:2.5}});const name=`${String(n++).padStart(5,'0')}.jpg`;fs.writeFileSync(`${OUT}/${name}`,Buffer.from(r.data,'base64'));frames.push([name,t/1000/SLOW]);}})();
const H={SLOW,wait:ms=>p.waitForTimeout(ms*SLOW),
  xy:id=>p.evaluate(id=>{const r=mapEl.getBoundingClientRect();const q=map.latLngToContainerPoint(LL[id]);return [r.x+q.x,r.y+q.y]},id),
  el:sel=>p.evaluate(s=>{const e=document.querySelector(s);if(!e)return null;const r=e.getBoundingClientRect();return [r.x+r.width/2,r.y+r.height/2]},sel),
  ripple:xy=>p.evaluate(([x,y])=>{const d=document.createElement('div');d.className='tapfx';d.style.left=x+'px';d.style.top=y+'px';document.body.appendChild(d);setTimeout(()=>d.remove(),5000)},xy),
  marks:{}};
H.tap=async xy=>{await H.ripple(xy);await H.wait(150);await p.touchscreen.tap(xy[0],xy[1]);};
H.tapSel=async sel=>{await H.ripple(await H.el(sel));await H.wait(150);await p.locator(sel).first().tap({force:true});};
H.tapSpot=async id=>{const xy=await H.xy(id);await H.tap(xy);await H.wait(350);const ok=await p.evaluate(id=>{const d=document.getElementById('drawer');const h=d.querySelector('h3');return !d.hidden&&h&&h.textContent.includes(byId(id).name)},id);if(!ok){console.log('spot miss',id,xy);await p.evaluate(id=>openSpot(id),id);}};
H.mark=k=>{H.marks[k]=Date.now()/1000/SLOW;};
H.fly=(ll,z,d)=>p.evaluate(([ll,z,d])=>{const c0=map.getCenter(),z0=map.getZoom(),t0=performance.now();const e=t=>t<.5?2*t*t:1-Math.pow(-2*t+2,2)/2;
  const st=()=>{const k=Math.min(1,(performance.now()-t0)/(d*1000)),q=e(k);map.setView([c0.lat+(ll[0]-c0.lat)*q,c0.lng+(ll[1]-c0.lng)*q],z0+(z-z0)*q,{animate:false});if(k<1)requestAnimationFrame(st);};st();},[Array.isArray(ll)?ll:[ll.lat,ll.lng],z,d*SLOW]);
const t0=Date.now()/1000/SLOW;H.mark('start');await seq(p,H);H.mark('end');
rec=false;await loop;
const m={};for(const k in H.marks)m[k]=H.marks[k]-frames[0][1];
fs.writeFileSync(`${OUT}/frames.json`,JSON.stringify(frames));fs.writeFileSync(`${OUT}/marks.json`,JSON.stringify(m));
fs.writeFileSync(`${OUT}/need.json`,JSON.stringify([...need]));console.log('missing tiles',need.size);fs.writeFileSync(`${OUT}/needR.json`,JSON.stringify([...needR]));console.log('missing routes',[...needR].map(u=>u.split('/driving/')[1].split('?')[0].split(';').length));console.log('frames',frames.length,'out secs',(frames.at(-1)[1]-frames[0][1]).toFixed(2),'marks',JSON.stringify(m));
await b.close();})();
