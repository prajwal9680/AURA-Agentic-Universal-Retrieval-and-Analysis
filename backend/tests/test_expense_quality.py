import urllib.request, json, sys
import pytest

def test_expense_quality():
    base = 'http://127.0.0.1:8000'
    try:
        r = urllib.request.urlopen(base + '/api/memories?category=receipt&limit=5', timeout=5)
        mems = json.loads(r.read().decode())['memories']
    except Exception as e:
        pytest.skip(f"Live server not running on port 8000: {e}")
        return

    print(f'Found {len(mems)} receipt memories')

    for m in mems:
        data = json.dumps({'memory_id': m['id']}).encode()
        req = urllib.request.Request(base + '/api/actions/extract-expense', data=data, headers={'Content-Type': 'application/json'}, method='POST')
        try:
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
        except Exception as e:
            print(f"Extraction error for {m.get('id')}: {e}")

if __name__ == "__main__":
    test_expense_quality()

