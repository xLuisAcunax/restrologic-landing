import pathlib, re, sys
SRC = pathlib.Path("src"); fail = []
ui = (SRC/"i18n"/"ui.ts").read_text(encoding="utf-8")
KV = re.compile(r"'([a-zA-Z0-9._]+)':\s*(?:'(?:[^'\\]|\\.)*'|\"(?:[^\"\\]|\\.)*\")", re.S)
def block(a_,b_):
    a=ui.index(a_); b=ui.index(b_,a); return [m.group(1) for m in KV.finditer(ui[a:b])]
# Structural parse of each dictionary body.
#
# The key-regex scan below happily skips anything it does not recognise, which
# is how a stray duplicated value line once sailed through every check here and
# only failed at esbuild — in a deploy. This walks the body token by token and
# insists it is nothing but `'key': 'value',` pairs and comments, so a
# malformed literal fails locally instead.
def parse_dict(open_marker, close_marker, label):
    a = ui.index(open_marker) + len(open_marker)
    b = ui.index(close_marker, a)
    body, i, keys, n = ui[a:b], 0, [], len(ui[a:b])

    def skip_trivia(i):
        while i < n:
            if body[i] in " \t\r\n,":
                i += 1
            elif body.startswith("/*", i):
                i = body.index("*/", i) + 2
            elif body.startswith("//", i):
                i = body.find("\n", i)
                if i == -1:
                    return n
            else:
                return i
        return i

    def read_string(i):
        """Read one single- or double-quoted literal, honouring escapes."""
        quote = body[i]
        if quote not in "'\"":
            raise ValueError(
                f"{label}: expected a quoted string at "
                f"line {ui.count(chr(10), 0, a + i) + 1}, found {body[i:i+40]!r}"
            )
        j = i + 1
        while j < n:
            if body[j] == "\\":
                j += 2
                continue
            if body[j] == quote:
                return j + 1
            j += 1
        raise ValueError(f"{label}: unterminated string near line "
                         f"{ui.count(chr(10), 0, a + i) + 1}")

    while True:
        i = skip_trivia(i)
        if i >= n:
            break
        start = i
        i = read_string(i)
        key = body[start + 1:i - 1]
        i = skip_trivia(i)
        if i >= n or body[i] != ":":
            raise ValueError(
                f"{label}: key {key!r} is not followed by ':' "
                f"(line {ui.count(chr(10), 0, a + start) + 1}) — this is what a "
                f"stray value line looks like"
            )
        i = skip_trivia(i + 1)
        # Values may be a single literal or several concatenated with '+'.
        i = read_string(i)
        while True:
            j = skip_trivia(i)
            if j < n and body[j] == "+":
                i = read_string(skip_trivia(j + 1))
            else:
                break
        keys.append(key)
    return keys

try:
    es = parse_dict("const es = {", "} as const;", "es")
    en = parse_dict("const en: Dictionary = {", "\n};", "en")
    print(f"i18n structure   es and en parse cleanly")
except ValueError as exc:
    print(f"i18n structure   MALFORMED — {exc}")
    fail.append(str(exc))
    es = block("const es = {", "} as const;")
    en = block("const en: Dictionary = {", "\n};")
es_set,en_set=set(es),set(en)
print(f"i18n parity      es={len(es)}  en={len(en)}  identical={es_set==en_set}")
if es_set!=en_set: fail.append(f"key mismatch es-only={sorted(es_set-en_set)} en-only={sorted(en_set-es_set)}")
if len(es)!=len(es_set) or len(en)!=len(en_set): fail.append("duplicate keys")

files=[f for f in list(SRC.rglob("*.astro"))+list(SRC.rglob("*.ts")) if f.name!="ui.ts"]
used=set()
KEYFIELDS = "titleKey|textKey|altKey|labelKey|descKey|ctaKey|numKey|timeKey|qKey|aKey|nameKey|customPriceKey|footKey"
for f in files:
    txt=f.read_text(encoding="utf-8")
    used |= set(re.findall(r"(?<![A-Za-z0-9_.])t\(\s*'([a-zA-Z0-9._]+)'\s*\)", txt))
    used |= set(re.findall(rf"(?:{KEYFIELDS})\s*:\s*'([a-zA-Z0-9._]+)'", txt))
    for m in re.finditer(r"(?:bulletKeys|pointKeys|featureKeys)\s*:\s*\[(.*?)\]", txt, re.S):
        used |= set(re.findall(r"'([a-zA-Z0-9._]+)'", m.group(1)))
# Template-literal keys (hero.proof.N.*, stats.N.*, etc.) built at render time
dynamic = {k for k in es_set if re.match(r"(hero\.proof|stats)\.\d+\.", k)}
used |= dynamic
missing=sorted(used-es_set); unused=sorted(es_set-used)
print(f"i18n references  {len(used)} used  missing={missing or 'none'}  unused={unused or 'none'}")
if missing: fail.append(f"undefined keys: {missing}")
if unused: fail.append(f"dead keys: {unused}")

isrc=(SRC/"components"/"ui"/"icons.ts").read_text(encoding="utf-8")
a=isrc.index("export const iconPaths = {"); b=isrc.index("} as const;",a)
icons=set(re.findall(r"^\s{2}([a-zA-Z]+):",isrc[a:b],re.M))
ui_icons=set()
for f in files:
    t_=f.read_text(encoding="utf-8")
    ui_icons |= set(re.findall(r'<Icon\s+name="([a-zA-Z]+)"',t_)) | set(re.findall(r"icon:\s*'([a-zA-Z]+)'",t_))
bad=sorted(ui_icons-icons)
print(f"icons            {len(icons)} defined  {len(ui_icons)} used  undefined={bad or 'none'}  spare={sorted(icons-ui_icons)}")
if bad: fail.append(f"undefined icons: {bad}")

css="".join((SRC/"styles"/n).read_text(encoding="utf-8") for n in
    ["tokens.css","base.css","primitives.css","components.css","sections.css","animations.css"])
# Declarations, plus @property registrations, plus the local vars that only
# ever get a value from JS or from a parent component.
defined = set(re.findall(r"^\s*(--[a-z0-9-]+):", css, re.M))
defined |= set(re.findall(r"@property\s+(--[a-z0-9-]+)", css))
# Set from markup or JS, never declared in a stylesheet:
#   --mx/--my   cursor position, written by the spotlight scene
#   --x/--y     callout coordinates, written inline from the content model
defined |= {"--mx", "--my", "--x", "--y",
            "--flow", "--cluster-gap", "--grid-gap", "--grid-min",
            "--btn-bg", "--btn-fg", "--btn-border", "--btn-shadow",
            "--tone", "--tone-ink", "--tone-soft", "--tone-border", "--tone-on",
            "--tone-strong"}
undef=sorted(set(re.findall(r"var\((--[a-z0-9-]+)",css))-defined)
print(f"css variables    {len(defined)} defined  undefined={undef or 'none'}")
if undef: fail.append(f"undefined CSS vars: {undef}")

markup=set()
for f in SRC.rglob("*.astro"):
    for m in re.finditer(r'class(?:Name)?=(?:"([^"]*)"|\{`([^`]*)`\})',f.read_text(encoding="utf-8")):
        markup |= {c for c in re.sub(r"\$\{[^}]*\}"," ",m.group(1) or m.group(2) or "").split() if c}
orphans=sorted(c for c in markup-set(re.findall(r"\.([a-zA-Z][a-zA-Z0-9_-]*)",css)) if not c.startswith("i-"))
print(f"css classes      {len(markup)} in markup  unstyled={orphans or 'none'}")
if orphans: fail.append(f"unstyled classes: {orphans}")

for f in files:
    for m in re.finditer(r"from '(\.[^']+)'",f.read_text(encoding="utf-8")):
        base=(f.parent/m.group(1)).resolve()
        if not (base.exists() or any(base.with_suffix(s).exists() for s in [".ts",".astro",".js"])):
            fail.append(f"{f.name}: unresolved import '{m.group(1)}'")
print(f"imports          all resolved={'yes' if not any('unresolved' in x for x in fail) else 'NO'}")
# Shipped screenshots must not carry identifying data. This is the check that
# matters most on this repo: the captures come from a live tenant, and a
# regression here publishes a real person's address.
try:
    import pytesseract
    from PIL import Image
    BAD = re.compile(r"\bmajo\b|\bfonseca\b|pomodoro\.co", re.I)
    leaks = []
    shots = sorted(pathlib.Path("src/assets/screens").glob("*.webp"))
    for shot in shots:
        text = pytesseract.image_to_string(Image.open(shot).convert("RGB"), lang="spa+eng")
        hits = sorted({m.group(0) for m in BAD.finditer(text)})
        if hits:
            leaks.append(f"{shot.name}: {hits}")
    print(f"screenshot PII   {len(shots)} asset(s) scanned  leaks={leaks or 'none'}")
    if leaks:
        fail.append(f"personal data in screenshots: {leaks}")
except ImportError:
    print("screenshot PII   skipped (pytesseract/PIL not installed)")

# The generated ramp block in tokens.css must still match what tools/ramp.py
# emits. Hand-editing a step there would silently break the contrast
# guarantees the whole palette rests on.
try:
    import subprocess
    tokens = (SRC/"styles"/"tokens.css").read_text(encoding="utf-8")
    a = tokens.index("/* BEGIN generated ramps"); a = tokens.index("\n", a) + 1
    b = tokens.index("/* END generated ramps")
    pasted = tokens[a:b].strip()
    emitted = subprocess.run(
        [sys.executable, "tools/ramp.py", "--css"],
        capture_output=True, text=True, check=True,
    ).stdout.strip()
    norm = lambda t: [l.strip() for l in t.splitlines() if l.strip()]
    match = norm(pasted) == norm(emitted)
    print(f"ramp drift       generated block matches tools/ramp.py: {match}")
    if not match:
        fail.append("tokens.css ramp block is out of sync with tools/ramp.py --css")
except Exception as exc:
    print(f"ramp drift       skipped ({exc})")

# The dark palette is declared twice — once under [data-theme="dark"] and once
# under the prefers-color-scheme media query — because the cascade gives no way
# to share them. Nothing stops the two drifting except this check.
tokens = (SRC/"styles"/"tokens.css").read_text(encoding="utf-8")
def decls(start_marker):
    i = tokens.index(start_marker)
    depth, j, out = 0, i, []
    while j < len(tokens):
        if tokens[j] == "{":
            depth += 1
        elif tokens[j] == "}":
            depth -= 1
            if depth == 0:
                break
        j += 1
    return [ln.strip().rstrip(";") for ln in tokens[i:j].splitlines()
            if ln.strip().startswith("--")]
attr = decls('[data-theme="dark"] {')
media = decls(':root:not([data-theme="light"]) {')
same = attr == media
print(f"dark parity      {len(attr)} vs {len(media)} declarations, identical={same}")
if not same:
    only_a = [d for d in attr if d not in media]
    only_m = [d for d in media if d not in attr]
    fail.append(f"dark theme blocks differ: attr-only={only_a[:4]} media-only={only_m[:4]}")

print()
if fail:
    print("FAILURES:"); [print("  x",x) for x in fail]; sys.exit(1)
print("ALL STATIC CHECKS PASSED")
