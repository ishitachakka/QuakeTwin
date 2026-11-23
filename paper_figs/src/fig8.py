import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
plt.rcParams.update({"font.family":"Liberation Sans","font.size":10,"pdf.fonttype":42})
st=["baseline","low","medium","high","disaster"]
D={ # setting -> agent -> list of (mean,ci) from ablation_summary.md
"No Comm DT":{"QRL":[(65.9,10.0),(70.1,9.6),(67.9,9.8),(59.7,8.8),(48.8,9.3)],"PPO-small":[(54.2,3.7),(60.0,3.7),(54.1,2.4),(43.2,1.2),(25.9,0.9)],"PPO":[(67.1,4.8),(71.3,2.8),(58.3,0.4),(43.3,0.2),(23.2,0.2)]},
"Comm-aware":{"QRL":[(80.6,4.1),(81.7,2.6),(72.2,2.5),(62.0,2.1),(48.1,4.7)],"PPO-small":[(65.5,3.5),(68.2,2.9),(55.4,2.4),(44.1,0.7),(29.6,2.5)],"PPO":[(88.5,2.6),(82.5,1.2),(59.1,0.2),(44.1,0.1),(26.3,0.4)]},
"Comm-aware + security":{"QRL":[(91.6,1.6),(90.6,1.4),(74.8,1.2),(63.2,1.1),(50.6,1.3)],"PPO-small":[(88.2,2.3),(87.5,2.4),(72.8,1.1),(62.5,1.1),(50.4,0.9)],"PPO":[(91.5,1.7),(90.6,1.5),(76.1,1.2),(64.1,1.2),(52.5,1.9)]}}
sty={"QRL":dict(color="#1d4ed8",marker="o"),"PPO-small":dict(color="#c2410c",marker="s"),"PPO":dict(color="#0f766e",marker="^")}
fig,axs=plt.subplots(1,3,figsize=(7.0,2.3),sharey=True)
for ax,(name,ag) in zip(axs,D.items()):
    for k,v in ag.items():
        off={"QRL":-0.08,"PPO-small":0,"PPO":0.08}[k]
        ax.errorbar([i+off for i in range(5)],[m for m,_ in v],yerr=[c for _,c in v],label=k,capsize=2.5,lw=1.5,ms=4.5,**sty[k])
    ax.set_title(name,fontsize=10.5); ax.set_xticks(range(5)); ax.set_xticklabels(st,fontsize=9)
    ax.grid(alpha=.3); ax.set_ylim(15,100)
axs[0].set_ylabel("Decision accuracy (%)")
axs[0].legend(fontsize=8.5,loc="lower left",frameon=False)
fig.tight_layout(pad=0.4,w_pad=0.6)
fig.savefig("ablation_stress.pdf"); fig.savefig("fig8.png",dpi=150)
