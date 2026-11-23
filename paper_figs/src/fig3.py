from svg import SVG, C
W,H=660,400
s=SVG(W,H)
def sat(cx,cy,col="#475569"):
    s.items.append(f'<g stroke="{col}" stroke-width="1.4" fill="#dbe4f0"><rect x="{cx-6}" y="{cy-7}" width="12" height="14" rx="2"/><rect x="{cx-26}" y="{cy-5}" width="17" height="10"/><rect x="{cx+9}" y="{cy-5}" width="17" height="10"/><line x1="{cx-9}" y1="{cy}" x2="{cx-6}" y2="{cy}"/><line x1="{cx+6}" y1="{cy}" x2="{cx+9}" y2="{cy}"/></g>')
def dish(cx,cy,col="#475569"):
    s.items.append(f'<g stroke="{col}" stroke-width="1.6" fill="#dbe4f0"><path d="M{cx-12},{cy-6} A14,14 0 0,0 {cx+10},{cy+10} Z"/><line x1="{cx-2}" y1="{cy+2}" x2="{cx-6}" y2="{cy+16}"/><line x1="{cx-12}" y1="{cy+16}" x2="{cx+2}" y2="{cy+16}"/></g>')
# satellites
sat(80,28); sat(470,28)
s.arrow([(112,28),(438,28)],"teal",dash="5,4",both=True)
s.text(275,20,"inter-satellite link: hybrid QKD + PQC",13,"teal","bold")
# access link
s.arrow([(80,42),(80,128)],"blue",both=True)
s.text(88,80,"access link:",13,"blue",anchor="start")
s.text(88,96,"ML-KEM (PQC)",13,"blue","bold",anchor="start")
# feeder
s.arrow([(470,42),(470,78)],"teal",both=True)
s.text(460,64,"feeder link: hybrid QKD + ML-KEM",13,"teal","bold",anchor="end")
dish(470,92)
s.text(492,97,"Ground station + gateway",13,"gray",anchor="start")
# disaster area
s.box(10,130,140,200,"Disaster area",[],stroke="gray",fill="#ffffff",tsize=15)
s.items.pop()  # remove centered title, redraw at top
s.text(80,154,"Disaster area",15,"gray","bold")
s.lines(80,182,["Autonomous systems","(drones · vehicles)","","IoT / edge devices","","Recovery crews"],13,"gray")
# QuakeTwin
s.rect(180,118,320,220,"#94a3b8","#ffffff",sw=1.4)
s.text(198,140,"QuakeTwin",15,"gray","bold",anchor="start")
s.rect(192,150,296,78,"teal","teal_bg")
s.text(204,169,"Communication DT",14,"teal","bold",anchor="start")
s.box(202,180,84,40,"Trust check",[],"teal","#ffffff",tsize=12)
s.box(300,180,90,40,"Hybrid keys",["QKD + ML-KEM"],"teal","#ffffff",tsize=12,rsize=11)
s.box(404,180,76,40,"Link",["monitor"],"teal","#ffffff",tsize=12,rsize=12)
s.arrow([(404,200),(392,200)],"teal",sw=1.4); s.arrow([(300,200),(288,200)],"teal",sw=1.4)
s.rect(192,256,296,74,"blue","blue_bg")
s.text(204,323,"Computational DT",14,"blue","bold",anchor="start")
s.box(202,264,84,38,"Road graph",[],"blue","#ffffff",tsize=12)
s.box(300,264,90,38,"QRL policy",[],"blue","#ffffff",tsize=12)
s.box(404,264,76,38,"Recovery",["strategy"],"blue","#ffffff",tsize=12,rsize=12)
s.arrow([(286,283),(298,283)],"blue",sw=1.4); s.arrow([(390,283),(402,283)],"blue",sw=1.4)
s.arrow([(244,220),(244,262)],"teal",sw=1.6)
s.text(252,244,"validated state + confidence",11,"teal",anchor="start")
# backhaul
s.arrow([(470,112),(470,148)],"blue")
s.text(478,132,"backhaul: ML-KEM",13,"blue","bold",anchor="start")
# WebGIS
s.box(540,160,110,52,"WebGIS",["operator view"],"gray","gray_bg",tsize=14,rsize=12)
s.arrow([(488,186),(538,186)],"line",dash="4,3")
# controller
s.box(540,252,110,62,"Transport",["controller"],"orange","orange_bg",tsize=14,rsize=14)
s.items[-1]=s.items[-1].replace('fill="#334155" font-weight="normal"','fill="#c2410c" font-weight="bold"')
s.arrow([(480,283),(538,283)],"orange")
s.text(509,276,"strategy",11,"orange")
# loop back
s.arrow([(595,314),(595,370),(80,370),(80,332)],"orange")
s.text(338,390,"route / repair orders → autonomous systems · crews → next observations + reward",12.5,"orange")
s.save("fig3_architecture.svg")
