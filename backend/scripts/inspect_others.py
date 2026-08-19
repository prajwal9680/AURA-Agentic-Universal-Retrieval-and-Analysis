import urllib.request, json
r = urllib.request.urlopen('http://127.0.0.1:8000/api/memories?limit=100', timeout=5)
mems = json.loads(r.read().decode())['memories']
others = [m for m in mems if m.get('category') == 'other']
print('Total other count:', len(others))
for o in others:
    fn = o.get('original_filename', '')
    summary = (o.get('summary') or '')[:70]
    ocr = (o.get('ocr_text') or '')[:50]
    print(f"{fn.ljust(35)} | {summary.ljust(70)} | {ocr}")
