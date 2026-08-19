#!/usr/bin/env python3
"""CEOS Standalone HTML バンドル展開/再構築ツール

- unpack: バンドルHTMLから template / manifest / リソースを展開
- repack: 編集済みリソースからバンドルHTMLを再構築(スタイル=template は不変)
"""
import base64, gzip, json, re, sys, os

def unpack(src, outdir):
    html = open(src, encoding='utf-8').read()
    os.makedirs(outdir, exist_ok=True)
    m = re.search(r'<script type="__bundler/template">(.*?)</script>', html, re.S)
    tpl = json.loads(m.group(1).strip())
    open(f'{outdir}/template.html', 'w', encoding='utf-8').write(tpl)
    m2 = re.search(r'<script type="__bundler/manifest">(.*?)</script>', html, re.S)
    manifest = json.loads(m2.group(1).strip())
    json.dump(manifest, open(f'{outdir}/manifest.json', 'w'), ensure_ascii=False, indent=1)
    for k, v in manifest.items():
        raw = base64.b64decode(v['data'])
        if v.get('compressed'):
            raw = gzip.decompress(raw)
        ext = v['mime'].split('/')[-1]
        open(f'{outdir}/{k}.{ext}', 'wb').write(raw)
    print(f"unpacked {len(manifest)} resources to {outdir}")

def repack(out_html, src_html, workdir):
    """元HTML(src_html)の __bundler/manifest・__bundler/template ブロックを
    編集済みワークスペースの内容で置き換えて再構築する(他は不変)。"""
    html = open(src_html, encoding='utf-8').read()
    manifest = json.load(open(f'{workdir}/manifest.json', encoding='utf-8'))
    for k, v in manifest.items():
        ext = v['mime'].split('/')[-1]
        fn = f'{workdir}/{k}.{ext}'
        if os.path.exists(fn):
            raw = open(fn, 'rb').read()
            if v.get('compressed'):
                raw = gzip.compress(raw, mtime=0)
            v['data'] = base64.b64encode(raw).decode()
    tpl = open(f'{workdir}/template.html', encoding='utf-8').read()
    # script タグ内 JSON では `<` を \u003C にエスケープする必要がある
    # (生の </script> が script 閉じタグと誤認識されるのを防ぐ)
    manifest_json = json.dumps(manifest, ensure_ascii=False, separators=(',', ':')).replace('<', '\\u003C')
    tpl_json = json.dumps(tpl, ensure_ascii=False).replace('<', '\\u003C')

    def replace_block(html, name, payload):
        pat = re.compile(r'(<script type="__bundler/' + name + r'">)(.*?)(</script>)', re.S)
        return pat.sub(lambda m: m.group(1) + payload + m.group(3), html, count=1)

    html = replace_block(html, 'manifest', manifest_json)
    html = replace_block(html, 'template', tpl_json)
    open(out_html, 'w', encoding='utf-8').write(html)
    print(f"repacked -> {out_html} ({os.path.getsize(out_html)} bytes)")

if __name__ == '__main__':
    cmd = sys.argv[1]
    if cmd == 'unpack':
        unpack(sys.argv[2], sys.argv[3])
    elif cmd == 'repack':
        repack(sys.argv[2], sys.argv[3], sys.argv[4])
