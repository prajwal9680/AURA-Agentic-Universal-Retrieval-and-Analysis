import urllib.request, json

base = 'http://127.0.0.1:8000'

# Check category distribution reality
r = urllib.request.urlopen(base+'/api/memories?limit=100', timeout=5)
mems = json.loads(r.read().decode())['memories']
cats = {}
for m in mems:
    cats[m.get('category','other')] = cats.get(m.get('category','other'),0)+1
print('CATEGORY BREAKDOWN:')
for k,v in sorted(cats.items(), key=lambda x:-x[1]):
    pct = round(100*v/len(mems))
    bar = '#'*pct
    print('  ' + k.ljust(20) + ': ' + str(v).rjust(3) + ' (' + str(pct).rjust(2) + '%) ' + bar)
print()

searches = [
    ('show me food or cooking', ['recipe']),
    ('laptop purchase bill', ['receipt','invoice']),
    ('python code or programming', ['code']),
    ('location or address map', ['map','travel','diagram']),
]
print('SEARCH RELEVANCE QUALITY:')
for q, expected_cats in searches:
    data = json.dumps({'query': q, 'top_k': 5}).encode()
    req = urllib.request.Request(base+'/api/search', data=data, headers={'Content-Type':'application/json'}, method='POST')
    with urllib.request.urlopen(req, timeout=15) as r2:
        sr = json.loads(r2.read().decode())
    results = sr.get('results', [])
    hits = sum(1 for m in results if m.get('category') in expected_cats)
    scores = [round(m.get('relevance_score',0),2) for m in results[:3]]
    top_cats = [m.get('category') for m in results[:5]]
    print('  Query: ' + repr(q))
    print('    Top cats: ' + str(top_cats))
    print('    Expected: ' + str(expected_cats) + ' | Hits: ' + str(hits) + '/5 | Scores: ' + str(scores))
