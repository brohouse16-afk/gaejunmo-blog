#!/usr/bin/env python3
"""개준모 블로그 허브 생성기: 네이버 블로그 RSS -> index.html / sitemap.xml / feed 목록"""
import re, html, json, urllib.request, datetime, email.utils, os, sys
BLOG="brohouse13"; BASE=os.environ.get("HUB_BASE","https://brohouse16-afk.github.io/gaejunmo-blog/")
RSS=f"https://rss.blog.naver.com/{BLOG}.xml"
CATS=[("guide","약국 개국 가이드","개국 수익 구조, 약국 유형별 장단점, 컨설팅 활용법"),
      ("listing","약국 매물·임장","약국 매물 찾는 법, 임장 체크리스트, 브로커 주의점, 매물 모음"),
      ("contract","권리계약·특약","약국 권리계약 시 꼭 넣어야 할 특약과 주의사항"),
      ("ops","약국 경영·실무","의약품 몰 주소, 병의원·약국 개폐업 확인 등 실무 정보"),
      ("news","개준모 소식","개준모(개국을 준비하는 모임) 소개·가입 안내·소식"),
      ("policy","약생연·약사 정책","약사 생존전략 연구회 설문·성명서")]
MAP={"224318651218":"ops","224303809429":"listing","224294217778":"guide","224290215475":"listing","224285231508":"contract",
"224284500572":"listing","223349638669":"listing","223349635115":"listing","223348212455":"listing","223348210122":"guide",
"223346268991":"guide","223343293536":"ops","222958182205":"listing","222958177137":"contract","222953847198":"listing",
"222933076679":"news","222367292507":"policy","222346777654":"policy","222327327937":"policy","222322988152":"policy",
"221726120144":"listing","221725128332":"news","221723230198":"guide","221719839177":"news","221716471086":"news"}
NAME2KEY={n:k for k,n,_ in CATS}
def guess(cat,title):
    if cat in NAME2KEY: return NAME2KEY[cat]
    t=title
    for k,ws in [("contract",["권리","특약","계약"]),("listing",["매물","임장","자리","양도"]),("policy",["약생연","성명","설문"]),("ops",["몰","사이트","세무","재고"]),("news",["개준모 소개","공지","소식"])]:
        if any(w in t for w in ws): return k
    return "guide"
def strip(s): return re.sub(r"\s+"," ",re.sub(r"<[^>]+>","",s)).strip()
def main():
    src=sys.argv[1] if len(sys.argv)>1 else None
    x=open(src,encoding="utf-8").read() if src else urllib.request.urlopen(urllib.request.Request(RSS,headers={"User-Agent":"Mozilla/5.0"}),timeout=30).read().decode("utf-8")
    posts=[]
    for it in re.findall(r"<item>(.*?)</item>",x,re.S):
        g=lambda tag: (re.search(rf"<{tag}>(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?</{tag}>",it,re.S) or [None,""])[1]
        url=g("guid").strip(); no=url.rsplit("/",1)[-1]
        d=email.utils.parsedate_to_datetime(g("pubDate"))
        desc=strip(html.unescape(g("description")))
        desc=re.sub(r"https?://\S+","",desc).strip()
        img=(re.search(r'src="([^"]+)"',g("description")) or [None,""])[1]
        posts.append(dict(no=no,url=url,title=strip(g("title")),date=d.strftime("%Y-%m-%d"),iso=d.isoformat(),cat=MAP.get(no) or guess(strip(g("category")),strip(g("title"))),
                          desc=(desc[:150]+"…") if len(desc)>150 else desc,tags=[t for t in strip(g("tag")).split(",") if t],img=img))
    posts.sort(key=lambda p:p["iso"],reverse=True)
    now=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9)))
    e=html.escape
    def card(p):
        cn=[n for k,n,_ in CATS if k==p["cat"]][0]
        return f'<article class="post"><a href="{e(p["url"])}" rel="noopener"><span class="cat">{e(cn)}</span><h3>{e(p["title"])}</h3><p>{e(p["desc"])}</p><time datetime="{p["date"]}">{p["date"]}</time></a></article>'
    secs=""
    for k,n,d in CATS:
        ps=[p for p in posts if p["cat"]==k]
        if not ps: continue
        secs+=f'<section id="{k}" class="cat-sec"><h2>{e(n)} <small>{len(ps)}</small></h2><p class="cd">{e(d)}</p><div class="grid">{"".join(card(p) for p in ps)}</div></section>'
    latest="".join(card(p) for p in posts[:6])
    ld={"@context":"https://schema.org","@graph":[
        {"@type":"Organization","@id":"https://gaejunmopharm.com/#org","name":"개준모(약국 개국을 준비하는 모임)","alternateName":["개준모","개국을 준비하는 모임"],"url":"https://gaejunmopharm.com/","logo":BASE+"assets/profile.png",
         "sameAs":[f"https://blog.naver.com/{BLOG}","https://cafe.naver.com/openpharmacy","https://gaejunmopharm.com/"]},
        {"@type":"Blog","name":"개준모 블로그","url":f"https://blog.naver.com/{BLOG}","publisher":{"@id":"https://gaejunmopharm.com/#org"},"inLanguage":"ko-KR",
         "blogPost":[{"@type":"BlogPosting","headline":p["title"],"url":p["url"],"datePublished":p["iso"],"description":p["desc"]} for p in posts[:50]]}]}
    nav="".join(f'<a href="#{k}">{e(n)}</a>' for k,n,_ in CATS)
    page=f'''<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>개준모 블로그 | 약국 개국·약국 매물·임장·권리계약 정보 모음</title>
<meta name="description" content="약사 1만3천여 명의 약국 개국 커뮤니티 개준모(개국을 준비하는 모임) 블로그 글 모음. 약국 개국 준비, 약국 매물·임장 체크리스트, 권리계약 특약, 약국 경영 실무 정보를 주제별로 정리했습니다.">
<link rel="canonical" href="{BASE}"><meta name="robots" content="index,follow,max-image-preview:large">
<!--VERIFY-->
<meta property="og:type" content="website"><meta property="og:title" content="개준모 블로그 | 약국 개국 정보 모음"><meta property="og:description" content="약국 개국 준비·매물·임장·권리계약 정보를 약사의 시선으로 정리합니다."><meta property="og:image" content="{BASE}assets/pc_title.png"><meta property="og:url" content="{BASE}"><meta property="og:locale" content="ko_KR">
<link rel="alternate" type="application/rss+xml" title="개준모 블로그 RSS" href="{RSS}"><link rel="icon" href="assets/icon.png">
<script type="application/ld+json">{json.dumps(ld,ensure_ascii=False)}</script>
<style>
@font-face{{font-family:P;src:url(assets/PretendardVariable.woff2) format("woff2");font-weight:100 900;font-display:swap}}
*{{box-sizing:border-box}}body{{margin:0;font-family:P,-apple-system,"Apple SD Gothic Neo","Malgun Gothic",sans-serif;background:#EEF1F7;color:#1B1F3B;line-height:1.6}}
a{{color:inherit;text-decoration:none}}
header{{background:linear-gradient(180deg,#121747,#232A6E 60%,#343C8E);color:#fff;padding:28px 20px 34px}}
.in{{max-width:1080px;margin:0 auto}}
.brand{{display:flex;align-items:center;gap:14px}}.brand img{{width:56px;height:56px}}
h1{{margin:0;font-size:30px;letter-spacing:-.8px}}h1 small{{display:block;font-size:15px;font-weight:500;color:#C9CDF6;letter-spacing:-.2px}}
.lead{{margin:16px 0 18px;color:#E3E6FF;font-size:16px;max-width:760px}}
.cta{{display:flex;flex-wrap:wrap;gap:10px}}.cta a{{padding:9px 16px;border-radius:999px;font-weight:700;font-size:14px;background:rgba(255,255,255,.14);border:1px solid rgba(255,255,255,.3)}}
.cta a.p{{background:#1F5FBF;border-color:#1F5FBF}}.cta a.y{{background:#FFD43B;color:#121747;border-color:#FFD43B}}
nav.cats{{position:sticky;top:0;background:#fff;border-bottom:1px solid #DDE2EE;z-index:5;overflow-x:auto;white-space:nowrap}}nav.cats .in{{display:flex;gap:4px;padding:10px 20px}}
nav.cats a{{padding:7px 12px;border-radius:999px;font-size:14px;font-weight:600;color:#232A6E}}nav.cats a:hover{{background:#E8ECFA}}
main{{padding:24px 20px 60px}}h2{{font-size:22px;margin:34px 0 4px;letter-spacing:-.5px}}h2 small{{color:#1F5FBF;font-size:15px;margin-left:4px}}.cd{{margin:0 0 14px;color:#5B6080;font-size:14px}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:14px}}
.post a{{display:block;height:100%;background:#fff;border:1px solid #E1E5F0;border-radius:16px;padding:18px;transition:.15s}}.post a:hover{{border-color:#1F5FBF;box-shadow:0 6px 18px rgba(31,95,191,.12)}}
.post h3{{font-size:17px;margin:6px 0 6px;letter-spacing:-.4px;line-height:1.45}}.post p{{font-size:14px;color:#4A4F6E;margin:0 0 10px}}.post time{{font-size:12px;color:#8A8FA8}}
.cat{{display:inline-block;font-size:12px;font-weight:700;color:#1F5FBF;background:#E8EFFC;padding:2px 9px;border-radius:999px}}
footer{{background:#121747;color:#C9CDF6;font-size:13px;padding:26px 20px}}footer a{{text-decoration:underline}}
</style></head><body>
<header><div class="in"><div class="brand"><img src="assets/icon.png" alt="개준모 로고" width="56" height="56"><h1>개준모 블로그<small>약국 개국을 준비하는 모임 · 공식 네이버 블로그 글 모음</small></h1></div>
<p class="lead">약사 1만3천여 명이 함께하는 약국 개국 커뮤니티 <b>개준모</b>가 네이버 블로그에 정리한 약국 개국 준비, 약국 매물·임장, 권리계약 특약, 약국 경영 실무 글을 주제별로 모았습니다. 각 글을 누르면 네이버 블로그 원문으로 이동합니다.</p>
<div class="cta"><a class="p" href="https://blog.naver.com/{BLOG}">네이버 블로그 바로가기</a><a class="y" href="https://gaejunmopharm.com/">약사 전용 플랫폼 gaejunmopharm.com</a><a href="https://cafe.naver.com/openpharmacy">네이버 카페 개준모</a></div></div></header>
<nav class="cats" aria-label="주제"><div class="in"><a href="#latest">최신 글</a>{nav}</div></nav>
<main class="in"><section id="latest"><h2>최신 글</h2><p class="cd">최근 네이버 블로그에 올라온 글</p><div class="grid">{latest}</div></section>{secs}</main>
<footer><div class="in">© 주식회사 개준모 · 개준모(약국 개국을 준비하는 모임) · 원문 출처: <a href="https://blog.naver.com/{BLOG}">네이버 블로그 brohouse13</a> · 마지막 갱신 {now.strftime("%Y-%m-%d %H:%M")} KST · 글 {len(posts)}개</div></footer>
</body></html>'''
    ver=open("verify.html",encoding="utf-8").read().strip() if os.path.exists("verify.html") else ""
    page=page.replace("<!--VERIFY-->",ver)
    open("index.html","w",encoding="utf-8").write(page)
    sm='<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    sm+=f'  <url><loc>{BASE}</loc><lastmod>{posts[0]["date"] if posts else now.date()}</lastmod><changefreq>daily</changefreq><priority>1.0</priority></url>\n</urlset>\n'
    open("sitemap.xml","w").write(sm)
    open("robots.txt","w").write(f"User-agent: *\nAllow: /\n\nSitemap: {BASE}sitemap.xml\n")
    json.dump(posts,open("posts.json","w",encoding="utf-8"),ensure_ascii=False,indent=1)
    print(len(posts),"posts")
if __name__=="__main__": main()
