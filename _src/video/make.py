# frames (CDP screencast, real timing) -> constant 30 fps mp4, with caption cards burnt in
import json, sys, subprocess, os
from PIL import Image, ImageDraw, ImageFont
W, H = 1080, 1920
FONT = '/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc'   # index 3 = TC
def caption(lines, path, accent=(214, 96, 30)):
    big, small = 78, 60
    while True:   # shrink until the widest line fits inside the frame
        f = ImageFont.truetype(FONT, big, index=3); fs = ImageFont.truetype(FONT, small, index=3)
        ws = [ImageDraw.Draw(Image.new('RGB', (1, 1))).textbbox((0, 0), t, font=ft)[2] for t, ft in zip(lines, [f] + [fs] * (len(lines) - 1))]
        if max(ws) + 110 <= W - 40 or big < 50: break
        big -= 4; small -= 3
    fonts = [f] + [fs] * (len(lines) - 1)
    widths = [ImageDraw.Draw(Image.new('RGB', (1, 1))).textbbox((0, 0), t, font=ft)[2] for t, ft in zip(lines, fonts)]
    bw = max(widths) + 110; lh = [100] + [82] * (len(lines) - 1); bh = sum(lh) + 70
    im = Image.new('RGBA', (W, bh + 20), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    x0 = (W - bw) // 2
    d.rounded_rectangle([x0 + 6, 14, x0 + bw + 6, bh + 14], 34, fill=(0, 0, 0, 70))
    d.rounded_rectangle([x0, 6, x0 + bw, bh + 6], 34, fill=(255, 252, 246, 250), outline=accent, width=7)
    y = 6 + 35
    for t, ft, h, w in zip(lines, fonts, lh, widths):
        d.text(((W - w) // 2, y - 8), t, font=ft, fill=accent if ft is f else (40, 36, 33)); y += h
    im.save(path)
def build(frames_dir, caps, out, end_hold=0.0):
    fr = json.load(open(f'{frames_dir}/frames.json'))
    t0 = fr[0][1]; lst = []
    for i, (n, t) in enumerate(fr):
        dur = (fr[i + 1][1] - t) if i + 1 < len(fr) else 0.04 + end_hold
        lst.append(f"file '{os.path.abspath(frames_dir)}/{n}'\nduration {dur:.4f}")
    lst.append(f"file '{os.path.abspath(frames_dir)}/{fr[-1][0]}'")
    open(f'{frames_dir}/list.txt', 'w').write('\n'.join(lst) + '\n')
    total = fr[-1][1] - t0 + 0.04 + end_hold
    inputs = ['-f', 'concat', '-safe', '0', '-i', f'{frames_dir}/list.txt']; filt = ['[0:v]fps=30,scale=1080:1920,setsar=1[v0]']; last = 'v0'
    for k, (png, y, a, b) in enumerate(caps):
        inputs += ['-loop', '1', '-framerate', '30', '-i', png]
        fade = f'[{k+1}:v]format=rgba,fade=in:st={a}:d=0.25:alpha=1,fade=out:st={b-0.25}:d=0.25:alpha=1[c{k}]'
        filt.append(fade); filt.append(f"[{last}][c{k}]overlay=0:{y}:enable='between(t,{a},{b})':shortest=1[v{k+1}]"); last = f'v{k+1}'
    tmp = out[:-4] + '.part.mp4'
    cmd = ['ffmpeg', '-y', '-v', 'error', *inputs, '-filter_complex', ';'.join(filt), '-map', f'[{last}]', '-t', f'{total:.3f}',
           '-c:v', 'libx264', '-crf', '18', '-preset', 'veryfast', '-pix_fmt', 'yuv420p', '-r', '30', '-movflags', '+faststart', tmp]
    subprocess.run(cmd, check=True); os.replace(tmp, out); return total
if __name__ == '__main__':
    caption(['去羅馬自助旅行？', '景點、時間、票價，一張地圖看完'], 'test/cap1.png')
    caption(['點景點，介紹馬上滑出來', '營業時間、票價、搶票提醒都在'], 'test/cap2.png')
    t = build('test/f', [('test/cap1.png', 1380, 0.0, 2.6), ('test/cap2.png', 150, 3.05, 5.75)], 'test/test.mp4', end_hold=0.3)
    print('secs', t)
