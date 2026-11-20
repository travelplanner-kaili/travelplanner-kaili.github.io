import asyncio, sys, json
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/usr/bin/google-chrome")
        pg = await b.new_page(viewport={"width":1440,"height":1000})
        html = open("/home/claude/rome/羅馬地圖.html").read()
        await pg.set_content("<!doctype html><meta charset=utf-8>"+html)
        await pg.wait_for_timeout(1500)
        errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        # overlap check using real rendered tab boxes
        res = await pg.evaluate("""() => {
          const tabs=[...document.querySelectorAll('.spot .tab')].map(t=>{const b=t.getBBox();return [t.parentNode.dataset.id,b.x,b.y,b.x+b.width,b.y+b.height]});
          const out=[];
          for(let i=0;i<tabs.length;i++)for(let j=i+1;j<tabs.length;j++){const a=tabs[i],b=tabs[j];
            if(!(a[3]<=b[1]||b[3]<=a[1]||a[4]<=b[2]||b[4]<=a[2]))out.push(a[0]+'/'+b[0]);}
          const pins=[...document.querySelectorAll('.spot .pin')].map(p=>{const b=p.getBBox();return [p.parentNode.dataset.id,b.x+b.width/2,b.y+b.height/2]});
          for(const t of tabs)for(const p of pins){ if(p[1]>t[1]-4&&p[1]<t[3]+4&&p[2]>t[2]-4&&p[2]<t[4]+4) out.push('pin '+p[0]+' under '+t[0]); }
          return out;}""")
        print("overlaps:", res)
        await pg.screenshot(path=sys.argv[1], full_page=True)
        await pg.click('#f-dist'); await pg.wait_for_timeout(400)
        res = await pg.evaluate('''() => {
          const bx=[...document.querySelectorAll('.spot .tab, .edge rect')].map(t=>{const b=t.getBBox();return [(t.closest('.spot')||{dataset:{id:'edge'}}).dataset.id,b.x,b.y,b.x+b.width,b.y+b.height]});
          const out=[];for(let i=0;i<bx.length;i++)for(let j=i+1;j<bx.length;j++){const a=bx[i],b=bx[j];if(!(a[3]<=b[1]||b[3]<=a[1]||a[4]<=b[2]||b[4]<=a[2]))out.push(a[0]+'/'+b[0]);}return out;}''')
        print("dist overlaps:", res)
        await pg.screenshot(path=sys.argv[2], full_page=True)
        print("errors:", errs)
        await b.close()
asyncio.run(main())
