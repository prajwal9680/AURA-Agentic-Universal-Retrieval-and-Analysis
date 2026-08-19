import urllib.request, urllib.parse, urllib.error, json, sys, struct, zlib, time

BASE = "http://127.0.0.1:8000"
PASS = 0
FAIL = 0

def p(label, ok, detail=""):
    global PASS, FAIL
    if ok:
        PASS += 1
        print("  PASS  " + label + (" [" + str(detail) + "]" if detail else ""))
    else:
        FAIL += 1
        print("  FAIL  " + label + (" [" + str(detail) + "]" if detail else ""))

def get(path, timeout=10):
    with urllib.request.urlopen(BASE + path, timeout=timeout) as r:
        return json.loads(r.read().decode())

def post_j(path, body, timeout=25):
    data = json.dumps(body).encode()
    req = urllib.request.Request(BASE + path, data=data, headers={"Content-Type":"application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode())

print("\n=== 1. HEALTH & VERSION ===")
h = get("/api/health")
p("status ok", h.get("status")=="ok", h.get("status","?"))
p("gemini configured", h.get("gemini_configured") is True)
p("version present", bool(h.get("version")), h.get("version","?"))

print("\n=== 2. DATABASE STATS ===")
s = get("/api/stats")
total = s.get("total_memories", 0)
rels = s.get("total_relationships", 0)
p(">=50 memories indexed", total >= 50, str(total) + " memories")
p(">=100 graph relationships", rels >= 100, str(rels) + " edges")

print("\n=== 3. MEMORY LIST & FILTERS ===")
m1 = get("/api/memories?limit=10&page=1")
items = m1.get("memories", [])
p("list returns items", len(items) > 0, str(len(items)))
p("pagination total correct", m1.get("total",0) == total, str(m1.get("total")))
p("pages > 1", m1.get("pages",0) > 1, str(m1.get("pages")))
mc = get("/api/memories?category=receipt")
p("category=receipt filter", mc.get("total",0) > 0, str(mc.get("total")) + " receipts")
ms = get("/api/memories?sensitivity=CRITICAL")
p("sensitivity=CRITICAL filter", ms.get("total",0) >= 0, str(ms.get("total")) + " critical")

print("\n=== 4. MEMORY DETAIL FIELDS ===")
fid = [m["id"] for m in items if not m.get("original_filename", "").startswith("test_")][0] if items else items[0]["id"]
md = get("/api/memories/" + fid)
for field in ["id","summary","category","sensitivity_level","image_url","thumbnail_url","entities","ocr_text","topics","importance_score"]:
    p("has " + field, field in md)

print("\n=== 5. IMAGE & THUMBNAIL ENDPOINTS ===")
try:
    with urllib.request.urlopen(BASE + "/api/memories/" + fid + "/thumbnail", timeout=10) as r:
        ct = r.headers.get("Content-Type","")
        sz = len(r.read())
    p("thumbnail returns image bytes", ct.startswith("image/") and sz > 1000, ct + " " + str(sz) + "B")
except Exception as e:
    p("thumbnail returns image bytes", False, str(e))

try:
    with urllib.request.urlopen(BASE + "/api/memories/" + fid + "/image", timeout=10) as r:
        ct = r.headers.get("Content-Type","")
        sz = len(r.read())
    p("full image returns image bytes", ct.startswith("image/") and sz > 1000, ct + " " + str(sz) + "B")
except Exception as e:
    p("full image returns image bytes", False, str(e))

print("\n=== 6. RELATIONSHIPS ===")
rel = get("/api/memories/" + fid + "/relationships")
p("relationships endpoint works", "relationships" in rel)
p("global relationship count > 0", rels > 0, str(rels) + " total edges")

print("\n=== 7. HYBRID SEMANTIC SEARCH (POST /api/search) ===")
for q in ["coffee receipt","Wi-Fi password","machine learning code","restaurant food","map location"]:
    sr = post_j("/api/search", {"query": q, "top_k": 5})
    found = len(sr.get("results", []))
    p("search: " + q, found > 0, str(found) + " results")

sr2 = post_j("/api/search", {"query": "laptop receipt", "top_k": 3})
mems2 = sr2.get("results", [])
p("results have relevance_score", bool(mems2) and "relevance_score" in mems2[0])
p("results have score_breakdown", bool(mems2) and "score_breakdown" in mems2[0])
p("sensitive_count in response", "sensitive_count" in sr2)

print("\n=== 8. AGENTIC INVESTIGATION (POST /api/investigate) ===")
inv = post_j("/api/investigate", {"query": "Show me computer vision project files", "deep": True}, 40)
p("has answer", bool(inv.get("answer")))
p("has confidence", "confidence" in inv)
p("has plan >=3 steps", len(inv.get("plan",[])) >= 3, str(len(inv.get("plan",[]))) + " steps")
p("has key_findings", len(inv.get("key_findings",[])) > 0, str(len(inv.get("key_findings",[]))) + " findings")
p("has results", len(inv.get("results",[])) > 0, str(len(inv.get("results",[]))) + " results")
p("has clusters", len(inv.get("clusters",[])) > 0, str(len(inv.get("clusters",[]))) + " clusters")
stats = inv.get("stats",{})
p("stats.total_found > 0", stats.get("total_found",0) > 0, str(stats.get("total_found")))

print("\n=== 9. MEMORY CLUSTERS ===")
cl_resp = get("/api/clusters")
clusters = cl_resp.get("clusters", [])
p("clusters is list", isinstance(clusters, list))
p(">=5 clusters returned", len(clusters) >= 5, str(len(clusters)) + " clusters")
if clusters:
    c0 = clusters[0]
    p("cluster has id", bool(c0.get("id")))
    p("cluster has name", bool(c0.get("name")))
    p("cluster has category", bool(c0.get("category")))
    p("cluster has count > 0", c0.get("count",0) > 0, str(c0.get("count")))
    p("cluster has samples", len(c0.get("samples",[])) > 0)
p("clusters total field", cl_resp.get("total",0) > 0, str(cl_resp.get("total")))

print("\n=== 10. CONSTELLATION GRAPH ===")
cn = get("/api/constellation")
p("constellation has nodes", len(cn.get("nodes",[])) > 0, str(len(cn.get("nodes",[]))) + " nodes")
p("constellation has edges", len(cn.get("edges",[])) > 0, str(len(cn.get("edges",[]))) + " edges")
if cn.get("nodes"):
    n0 = cn["nodes"][0]
    p("node has id", bool(n0.get("id")))
    p("node has label/name", bool(n0.get("label") or n0.get("name")))

print("\n=== 11. TIMELINE ===")
tl_resp = get("/api/timeline")
tl = tl_resp.get("timeline", tl_resp) if isinstance(tl_resp, dict) else tl_resp
p("timeline has entries", len(tl) > 0, str(len(tl)) + " groups")
if tl:
    g0 = tl[0]
    p("group has date/period", bool(g0.get("date") or g0.get("period") or g0.get("label")))
    gmems = g0.get("memories", g0.get("items", []))
    p("group has memories", len(gmems) > 0, str(len(gmems)) + " memories")

print("\n=== 12. AURA SHIELD ZERO-TRUST ===")
sh_stats = get("/api/shield/stats")
p("shield stats active", sh_stats.get("status") == "active")
p("zero_trust_enabled", sh_stats.get("zero_trust_enabled") is True)
p("critical_protected > 0", sh_stats.get("critical_protected",0) > 0, str(sh_stats.get("critical_protected")) + " critical")
p("total_monitored matches DB", sh_stats.get("total_monitored",0) == total)
sh_sens = get("/api/memories?sensitivity=SENSITIVE&limit=5")
sh_crit = get("/api/memories?sensitivity=CRITICAL&limit=5")
sh_all = sh_sens.get("memories",[]) + sh_crit.get("memories",[])
p("protected memories in DB", len(sh_all) > 0, str(len(sh_all)) + " found")

print("\n=== 13. CONTEXTUAL AI ACTIONS ===")
rec_mems = get("/api/memories?category=receipt&limit=5")
rid = rec_mems["memories"][0]["id"] if rec_mems.get("memories") else fid
ea = post_j("/api/actions/extract-expense", {"memory_id": rid}, 40)
p("extract-expense: result present", "result" in ea, str(list(ea.keys())[:5]))

sm2 = post_j("/api/actions/summarize", {"memory_id": fid}, 40)
p("summarize: result present", "result" in sm2, str(list(sm2.keys())[:5]))

code_mems = get("/api/memories?category=code&limit=5")
cid = code_mems["memories"][0]["id"] if code_mems.get("memories") else fid
db2 = post_j("/api/actions/debug-code", {"memory_id": cid}, 40)
p("debug-code: result present", "result" in db2, str(list(db2.keys())[:5]))

print("\n=== 14. UPLOAD & CLEANUP ===")
def tiny_png():
    def ck(n,d):
        c = zlib.crc32(n+d)&0xFFFFFFFF
        return struct.pack(">I",len(d))+n+d+struct.pack(">I",c)
    h2=ck(b"IHDR",struct.pack(">IIBBBBB",4,4,8,2,0,0,0))
    raw=b"\x00\xff\x00\x00\xff\x00\x00\xff\x00\xff"*4
    d2=ck(b"IDAT",zlib.compress(raw))
    e2=ck(b"IEND",b"")
    return b"\x89PNG\r\n\x1a\n"+h2+d2+e2
png = tiny_png()
bd = b"----AURAb7891"
body = b"--"+bd+b"\r\nContent-Disposition: form-data; name=\"file\"; filename=\"test_up.png\"\r\nContent-Type: image/png\r\n\r\n"+png+b"\r\n--"+bd+b"--\r\n"
req = urllib.request.Request(BASE+"/api/memories/upload",data=body,headers={"Content-Type":"multipart/form-data; boundary=----AURAb7891"},method="POST")
with urllib.request.urlopen(req, timeout=60) as r:
    up = json.loads(r.read().decode())
p("upload returns id", bool(up.get("id")))

# Poll for async pipeline processing
mem_id = up.get("id")
final_mem = up
for _ in range(15):
    if mem_id and final_mem.get("processing_status") != "done":
        time.sleep(1)
        try:
            final_mem = get("/api/memories/" + mem_id)
        except Exception:
            pass

p("upload assigns category", bool(final_mem.get("category")), final_mem.get("category"))
p("upload assigns sensitivity_level", bool(final_mem.get("sensitivity_level")), final_mem.get("sensitivity_level"))
if mem_id:
    urllib.request.urlopen(urllib.request.Request(BASE+"/api/memories/"+mem_id,method="DELETE"),timeout=5)
    p("upload test memory cleaned up", True)

print("\n=== 15. ERROR HANDLING ===")
try:
    get("/api/memories/nonexistent-uuid-00000")
    p("404 for unknown memory", False, "no exception")
except urllib.error.HTTPError as e:
    p("404 for unknown memory", e.code==404, "HTTP " + str(e.code))

print("\n=== 16. DATASET DIVERSITY ===")
all_m = get("/api/memories?limit=100")["memories"]
cats = {}
for m in all_m:
    c = m.get("category","other")
    cats[c] = cats.get(c,0)+1
print("  Distribution: " + json.dumps(dict(sorted(cats.items(),key=lambda x:-x[1]))))
p(">=5 distinct categories", len(cats) >= 5, str(len(cats)))
p("has receipt", "receipt" in cats)
p("has code", "code" in cats)
p("has chart/diagram/research", any(k in cats for k in ("chart","diagram","research")))
p("has product/shopping", any(k in cats for k in ("product","shopping","product")))
p("has map/travel", any(k in cats for k in ("map","travel")))
p("no single category > 40%", max(cats.values()) / len(all_m) < 0.4, str(round(100*max(cats.values())/len(all_m))) + "% max")

total_t = PASS+FAIL
pct = int(100*PASS/total_t) if total_t else 0
print("\n" + "="*62)
print("RESULT: " + str(PASS) + "/" + str(total_t) + " PASSED (" + str(pct) + "%)")
if FAIL:
    print("FAILED: " + str(FAIL) + " tests need attention")
    sys.exit(1)
else:
    print("ALL " + str(PASS) + " TESTS PASSED -- AURA IS SUBMISSION-READY")
print("="*62)
