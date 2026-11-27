import math
Y='#F6C21B';C='#F4ECD4';K='#0C0B09'
cx=cy=256
def laurel(side):
    out=[];R=116;lcx,lcy=cx,cy+26
    a0,a1=(98,158) if side<0 else (82,22)
    pts=[]
    for i in range(41):
        a=math.radians(a0+(a1-a0)*i/40);pts.append((lcx+R*math.cos(a),lcy+R*math.sin(a)))
    out.append('<path d="M'+' L'.join(f'{x:.1f},{y:.1f}' for x,y in pts)+f'" fill="none" stroke="{Y}" stroke-width="3.5" stroke-linecap="round"/>')
    n=5
    for i in range(n):
        t=(i+0.5)/n;a=a0+(a1-a0)*t;ar=math.radians(a)
        x=lcx+R*math.cos(ar);y=lcy+R*math.sin(ar)
        tang=a+(90 if side>0 else -90)
        for off in (-1,1):
            ang=tang+off*45
            lx=x+11*math.cos(math.radians(ang));ly=y+11*math.sin(math.radians(ang))
            out.append(f'<ellipse cx="{lx:.1f}" cy="{ly:.1f}" rx="12.5" ry="5.2" fill="{Y}" transform="rotate({ang:.1f} {lx:.1f} {ly:.1f})"/>')
    ar=math.radians(a1);x=lcx+R*math.cos(ar);y=lcy+R*math.sin(ar);ang=a1+(90 if side>0 else -90)
    lx=x+9*math.cos(math.radians(ang));ly=y+9*math.sin(math.radians(ang))
    out.append(f'<ellipse cx="{lx:.1f}" cy="{ly:.1f}" rx="12" ry="5" fill="{Y}" transform="rotate({ang:.1f} {lx:.1f} {ly:.1f})"/>')
    return out
def star(x,y,r):
    p=[]
    for i in range(10):
        rr=r if i%2==0 else r*0.45;a=math.radians(-90+36*i);p.append(f'{x+rr*math.cos(a):.1f},{y+rr*math.sin(a):.1f}')
    return f'<polygon points="{" ".join(p)}" fill="{Y}"/>'
def plate(x,y0,w,h):
    return f'<rect x="{x}" y="{y0-h/2}" width="{w}" height="{h}" rx="7" fill="{C}" stroke="{K}" stroke-width="4"/>'
dy=cy-10
db=[f'<rect x="160" y="{dy-8}" width="192" height="16" rx="4" fill="{C}" stroke="{K}" stroke-width="4"/>']
for s in (-1,1):
    X=lambda x0,w: x0 if s<0 else 512-x0-w
    db.append(plate(X(122,15),dy,15,40))
    db.append(plate(X(135,24),dy,24,84))
    db.append(plate(X(157,32),dy,32,116))
    db.append(f'<rect x="{X(157,32)+7 if s<0 else X(157,32)+20}" y="{dy-46}" width="5" height="92" rx="2.5" fill="{Y}"/>')
    db.append(f'<rect x="{X(187,9)}" y="{dy-13}" width="9" height="26" rx="2" fill="{C}" stroke="{K}" stroke-width="3"/>')
for i in range(9):
    x=214+i*10.5;db.append(f'<line x1="{x:.1f}" y1="{dy-4}" x2="{x:.1f}" y2="{dy+4}" stroke="{K}" stroke-width="2"/>')
band=[];stars=[]
for s in (-1,1):
    x1,x2=(16,82) if s<0 else (430,496)
    for yy in (cy-17,cy+17):
        band.append(f'<line x1="{x1}" y1="{yy}" x2="{x2}" y2="{yy}" stroke="{Y}" stroke-width="3"/>')
    for x in ((34,50,66) if s<0 else (446,462,478)): stars.append(star(x,cy,7))
r_text=189
svg=f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" width="512" height="512">
<defs><path id="arc" d="M {cx-r_text},{cy} A {r_text} {r_text} 0 0 1 {cx+r_text},{cy}"/>
<path id="arc2" d="M {cx-218},{cy} A 218 218 0 0 0 {cx+218},{cy}"/>
<radialGradient id="g" cx="50%" cy="42%" r="60%"><stop offset="0" stop-color="#211d13"/><stop offset="1" stop-color="{K}"/></radialGradient></defs>
<circle cx="{cx}" cy="{cy}" r="254" fill="{C}"/>
<circle cx="{cx}" cy="{cy}" r="246" fill="{K}"/>
<circle cx="{cx}" cy="{cy}" r="236" fill="none" stroke="{Y}" stroke-width="5"/>
<rect x="8" y="{cy-17}" width="78" height="34" fill="{K}"/><rect x="426" y="{cy-17}" width="78" height="34" fill="{K}"/>
<circle cx="{cx}" cy="{cy}" r="172" fill="url(#g)" stroke="{Y}" stroke-width="6"/>
<circle cx="{cx}" cy="{cy}" r="163" fill="none" stroke="{C}" stroke-width="2" opacity=".5"/>
<text font-family="Archivo Black" font-size="52" letter-spacing="6" fill="{C}" text-anchor="middle"><textPath href="#arc" startOffset="50%">PINO GYM</textPath></text>
<text font-family="Archivo Black" font-size="17" letter-spacing="7" fill="{Y}" text-anchor="middle"><textPath href="#arc2" startOffset="50%">PREPARACIÓN FÍSICA</textPath></text>
{''.join(band)}{''.join(stars)}
{''.join(laurel(-1))}{''.join(laurel(1))}
{''.join(db)}
</svg>'''
open('pino-gym.svg','w').write(svg)
