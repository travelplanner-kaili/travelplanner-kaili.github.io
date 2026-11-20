import re, json, numpy as np
h = open('/home/claude/lucca/live/lucca.html').read()
xy = {m[0]: (float(m[1]), float(m[2])) for m in re.findall(r'id:"(\w+)", cat:"\w+", x:(\d+), y:(\d+)', h)}
G = {"duomo": (43.8407828, 10.505633), "campanile": (43.8405536, 10.5054285), "museo": (43.8409578, 10.5061943),
 "giovanni": (43.8411779, 10.5043386), "guinigi": (43.8437635, 10.5069855), "ore": (43.8434109, 10.5041578),
 "frediano": (43.8461445, 10.5048744), "michele": (43.8432639, 10.5026008), "giusto": (43.842066, 10.5036328),
 "alessandro": (43.842323, 10.5011028), "hotel": (43.843074, 10.509845), "station": (43.8374125, 10.5061477),
 "anfiteatro": (43.8453319, 10.5061788), "piazzamichele": (43.8430907, 10.5031507)}
ids = [k for k in G if k in xy]
A = np.array([[xy[k][0], xy[k][1], 1] for k in ids]); 
lat = np.array([G[k][0] for k in ids]); lng = np.array([G[k][1] for k in ids])
ca, *_ = np.linalg.lstsq(A, lat, rcond=None); cb, *_ = np.linalg.lstsq(A, lng, rcond=None)
f = lambda x, y: (float(ca @ [x, y, 1]), float(cb @ [x, y, 1]))
for k in ids:
    p = f(*xy[k]); d = ((p[0]-G[k][0])*111000, (p[1]-G[k][1])*80000); print(k, round(d[0]), round(d[1]))
LL = {k: list(G.get(k) or f(*xy[k])) for k in xy}
area = [[float(a) for a in p.split(',')] for p in re.search(r'area:"([^"]+)"', h).group(1).split()]
json.dump({"ll": LL, "area": [list(f(*p)) for p in area]}, open('coords.json', 'w'))
print(LL['mura'], LL['shopping'])
