import json, subprocess, os, make
from PIL import Image, ImageDraw, ImageFont, ImageFilter
F='full/f'; m=json.load(open(f'{F}/marks.json')); fr=json.load(open(f'{F}/frames.json'))
C=[(['去羅馬自助旅行？','景點、時間、票價，一張地圖看完'],1380,0.0,m['tap1']-0.05),
   (['點景點，介紹馬上滑出來','特色、看點，一次看懂'],150,m['tap1']+0.45,m['tips']-0.05),
   (['實用資訊都整理好了','營業時間、從住宿走多遠、小提醒'],1440,m['tips']+0.35,m['close1']+0.3),
   (['6 條 City Walk 散步路線','沿路景點都幫你串好'],1440,m['walk']+0.3,m['close2']+0.3),
   (['點兩個景點，秒算距離','照真實街道算，不是直線'],150,m['dist']+0.3,m['distoff']+0.3),
   (['排出你自己的每日行程','一鍵加入，一鍵 Google 導航'],150,m['plan']+0.3,m['end']+0.2)]
caps=[]
for i,(t,y,a,b) in enumerate(C):
    p=f'full/cap{i}.png'; make.caption(t,p); caps.append((p,y,round(a,2),round(b,2)))
body=make.build(F,caps,'full/body.mp4',end_hold=0.2)
# end card: last frame, blurred + dimmed, with the call to action
W,H=1080,1920
bg=Image.open(f'{F}/{fr[-1][0]}').convert('RGB').filter(ImageFilter.GaussianBlur(18))
bg=Image.blend(bg,Image.new('RGB',(W,H),(30,26,22)),0.45)
d=ImageDraw.Draw(bg); FT='/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc'
f=lambda s:ImageFont.truetype(FT,s,index=3)
def ctext(y,t,ft,fill):
    w=d.textbbox((0,0),t,font=ft)[2]; d.text(((W-w)//2,y),t,font=ft,fill=fill)
d.rounded_rectangle([110,700,970,1180],48,fill=(255,252,246))
ctext(780,'我的羅馬地圖小勞作',f(80),(214,96,30))
ctext(915,'到 2027 年 2 月為止',f(56),(40,36,33))
ctext(1000,'會持續自動更新',f(56),(40,36,33))
ctext(1830,'地圖資料 © OpenStreetMap 貢獻者',f(30),(235,230,224))
bg.save('full/end.jpg',quality=92)
Image.open(f'{F}/{fr[-1][0]}').save('full/last.jpg',quality=92)
tmp='full/end.part.mp4'
subprocess.run(['ffmpeg','-y','-v','error','-framerate','30','-i','full/last.jpg','-framerate','30','-i','full/end.jpg','-filter_complex',
 '[0:v]format=yuv420p,loop=-1:1,trim=duration=3.6,setpts=PTS-STARTPTS[a];[1:v]format=yuv420p,loop=-1:1,trim=duration=3.6,setpts=PTS-STARTPTS[b];[a][b]xfade=transition=fade:duration=0.5:offset=0.05,trim=duration=3.5[v]',
 '-map','[v]','-c:v','libx264','-crf','18','-preset','veryfast','-pix_fmt','yuv420p','-r','30',tmp],check=True); os.replace(tmp,'full/end.mp4')
open('full/concat.txt','w').write("file 'body.mp4'\nfile 'end.mp4'\n")
out='full/羅馬地圖介紹片.mp4'
subprocess.run(['ffmpeg','-y','-v','error','-f','concat','-safe','0','-i','full/concat.txt','-c','copy','-movflags','+faststart','full/x.part.mp4'],check=True); os.replace('full/x.part.mp4',out)
print(body)
