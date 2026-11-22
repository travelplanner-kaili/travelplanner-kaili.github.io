import re, json, sys
src = open(sys.argv[1], encoding='utf-8').read()
secs = []; cur = None; q = None
for line in src.splitlines():
    s = line.rstrip()
    if s.startswith('## '):
        t, era = s[3:].rsplit('@', 1)
        cur = dict(title=t.strip(), era=era.strip(), qs=[]); secs.append(cur); q = None
    elif s.startswith('### '):
        qid, title = s[4:].split(' | ', 1)
        q = dict(id=qid.strip(), q=title.strip(), s='', b=[]); cur['qs'].append(q)
    elif not s.strip():
        continue
    elif cur is None: continue
    elif q is None:
        cur.setdefault('intro', []).append(s.strip()); continue
    elif s.startswith('> '): q['s'] = (q['s'] + '\n' if q['s'] else '') + s[2:].strip()
    elif s.startswith('|'):
        cells = [c.strip() for c in s.strip().strip('|').split('|')]
        if all(set(c) <= set('-: ') for c in cells): continue
        if q['b'] and q['b'][-1][0] == 'tbl': q['b'][-1][1].append(cells)
        else: q['b'].append(['tbl', [cells]])
    elif s.strip() == '---': continue
    elif s.startswith('#### '): q['b'].append(['h', s[5:].strip()])
    elif s.startswith(':: '):
        if q['b'] and q['b'][-1][0] == 'box': q['b'][-1][1].append(s[3:].strip())
        else: q['b'].append(['box', [s[3:].strip()]])
    elif s.startswith('* '): q['b'].append(['sub', s[2:].strip()])
    elif s.startswith('- '): q['b'].append(['li', s[2:].strip()])
    elif re.match(r'\d+\. ', s): q['b'].append(['ol', re.sub(r'^\d+\.\s', '', s)])
    else: q['b'].append(['p', s.strip()])
json.dump(secs, open('qa2.json', 'w', encoding='utf-8'), ensure_ascii=False)
ids = [x['id'] for c in secs for x in c['qs']]
print(len(secs), len(ids), ids); assert len(ids) == len(set(ids))
for c in secs:
    for x in c['qs']: assert x['s'], x['id']
