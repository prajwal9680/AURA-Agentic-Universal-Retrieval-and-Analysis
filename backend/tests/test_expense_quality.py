import urllib.request, json, sys

base = 'http://127.0.0.1:8000'
r = urllib.request.urlopen(base + '/api/memories?category=receipt&limit=5', timeout=10)
mems = json.loads(r.read().decode())['memories']
print(f'Found {len(mems)} receipt memories')

for m in mems:
    data = json.dumps({'memory_id': m['id']}).encode()
    req = urllib.request.Request(base + '/api/actions/extract-expense', data=data, headers={'Content-Type': 'application/json'}, method='POST')
    with urllib.request.urlopen(req, timeout=20) as r2:
        res = json.loads(r2.read().decode())
    print('File:', m.get('original_filename'))
    print('  Merchant:', res.get('result', {}).get('merchant'))
    print('  Category:', res.get('result', {}).get('category'))
    total_str = str(res.get('result', {}).get('total_amount','')).encode('ascii', 'replace').decode()
    print('  Total:', total_str)
    print('  Payment:', res.get('result', {}).get('payment_method'))
    line_items_str = json.dumps(res.get('result', {}).get('line_items', [])).encode('ascii', 'replace').decode()
    print('  Line items:', line_items_str)
    print()
