from svg import SVG
W,H=700,428
s=SVG(W,H)
def zone(x,y,w,h,title):
    s.rect(x,y,w,h,"line","#f8fafc",sw=1.3,dash="4,3")
    s.text(x+8,y+19,title,13,"gray","bold",anchor="start")
cw=161; gap=12; top=6; zh=236
xs=[6+i*(cw+gap) for i in range(4)]
zone(xs[0],top,cw,zh,"Zone 1 · Untrusted edge")
for i,t in enumerate(["Drones · vehicles","IoT traffic sensors","Traffic / incident feeds","Street View imagery","PCI / CV pipeline"]):
    s.box(xs[0]+10,top+32+i*38,cw-20,30,t,[],"gray","#ffffff",tsize=12.5,tcolor="gray")
    s.items[-1]=s.items[-1].replace('font-weight="bold"','font-weight="normal"')
zone(xs[1],top,cw,zh,"Zone 2 · Channel")
s.box(xs[1]+10,top+40,cw-20,56,"Satellite links",["ML-KEM · QKD + ML-KEM"],"teal","teal_bg",tsize=13,rsize=11.5)
s.box(xs[1]+10,top+128,cw-20,74,"MITM attacker",["intercept · modify","delay · replay · drop"],"red","red_bg",tsize=13,rsize=11.5)
s.arrow([(xs[1]+cw/2,top+96),(xs[1]+cw/2,top+126)],"red",dash="4,3")
zone(xs[2],top,cw,zh,"Zone 3 · DT ingestion")
thr=[("Spoofing","fake or Sybil reports","red","red_bg"),("Tampering","modified or replayed data","red","red_bg"),("Info. disclosure","eavesdropped state","amber","amber_bg"),("Denial of service","flooding · dropped links","orange","orange_bg"),("State manipulation","injected DT state","red","red_bg")]
for i,(t,r,c,f) in enumerate(thr):
    s.box(xs[2]+8,top+30+i*41,cw-16,37,t,[r],c,f,tsize=12,rsize=10.5,tcolor="gray")
zone(xs[3],top,cw,zh,"Zone 4 · QRL inputs")
s.box(xs[3]+10,top+32,cw-20,46,"Per-segment state",["condition · hazard · age"],"blue","#ffffff",tsize=12.5,rsize=11.5)
s.box(xs[3]+10,top+86,cw-20,30,"Reward (Eq. 2)",[],"blue","#ffffff",tsize=12.5)
s.box(xs[3]+10,top+124,cw-20,46,"Policy output",["wait · repair · rebuild"],"blue","#ffffff",tsize=12.5,rsize=11.5)
s.arrow([(xs[3]+cw/2,top+78),(xs[3]+cw/2,top+84)],"blue",sw=1.3)
s.arrow([(xs[3]+cw/2,top+116),(xs[3]+cw/2,top+122)],"blue",sw=1.3)
s.box(xs[3]+10,top+178,cw-20,40,"Accepted tampering",["→ wrong recovery actions"],"red","red_bg",tsize=12,rsize=11.5)
# flows between zones
for a,b,c in [(0,1,"teal"),(1,2,"red"),(2,3,"red")]:
    s.arrow([(xs[a]+cw,top+zh/2-30),(xs[b]-1,top+zh/2-30)],c)
# zone 5
z5y=top+zh+30; z5h=H-z5y-24
s.rect(6,z5y,W-12,z5h,"line","#f8fafc",sw=1.3,dash="4,3")
s.text(14,z5y+19,"Zone 5 · Mitigation controls in the Communication DT",14,"gray","bold",anchor="start")
ctr=[("S · Source authentication","ML-DSA · cross-source check"),("T · Integrity and freshness","AES-GCM / MAC tags"),("I · Hybrid keys","QKD + ML-KEM"),
     ("D · Availability monitoring","degraded-mode operation"),("Anomaly detection","cross-source consistency"),("Confidence gate","hold uncertain states")]
bw=(W-12-20-16)/3
for i,(t,r) in enumerate(ctr):
    s.box(16+(i%3)*(bw+8),z5y+28+(i//3)*44,bw,38,t,[r],"teal","teal_bg",tsize=12,rsize=11)
for x in xs:
    s.arrow([(x+cw/2,z5y-2),(x+cw/2,top+zh+2)],"teal",dash="4,3")
s.text(W/2,z5y+z5h-6,"Response: detect → validate → isolate → recover → re-synchronize",12.5,"teal","bold")
# legend
lx=W/2-170; ly=H-8
for i,(lab,c,f) in enumerate([("critical risk","red","red_bg"),("high risk","orange","orange_bg"),("medium risk","amber","amber_bg")]):
    s.rect(lx+i*120,ly-10,12,12,c,f,sw=1.2,r=2); s.text(lx+i*120+18,ly,lab,11.5,"gray",anchor="start")
s.save("fig7_threat_model.svg")
