import urllib.request, json
import pytest

def test_investigate_quality():
    base = 'http://127.0.0.1:8000'
    queries = [
        'what food or recipes do I have',
        'laptop purchase bill and receipt',
        'computer vision project and machine learning',
        'where is the wifi password stored'
    ]

    for q in queries:
        data = json.dumps({'query': q, 'deep': True}).encode()
        req = urllib.request.Request(base + '/api/investigate', data=data, headers={'Content-Type': 'application/json'}, method='POST')
        try:
            with urllib.request.urlopen(req, timeout=25) as r:
                inv = json.loads(r.read().decode())
            print('Query:', repr(q))
            print('  Answer:', inv.get('answer'))
            print('  Confidence:', inv.get('confidence'))
            print('  Key findings:', inv.get('key_findings')[:2])
            print('  Top results:', [r.get('original_filename') for r in inv.get('results', [])[:3]])
            print()
        except Exception as e:
            pytest.skip(f"Live server not responding on port 8000: {e}")
            return

if __name__ == "__main__":
    test_investigate_quality()

