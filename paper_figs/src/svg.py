"""Tiny SVG helper for the QuakeTwin figures (exported to vector PDF with rsvg-convert)."""
FONT = "Liberation Sans, Arial, Helvetica, sans-serif"

C = dict(
    teal="#0f766e", teal_bg="#e6f4f1",
    blue="#1d4ed8", blue_bg="#e8eefc",
    orange="#c2410c", orange_bg="#fdf0e6",
    red="#b91c1c", red_bg="#fdecec",
    amber="#a16207", amber_bg="#fdf6e3",
    gray="#334155", gray_bg="#f5f7fa", line="#94a3b8",
)


class SVG:
    def __init__(self, w, h):
        self.w, self.h, self.items = w, h, []
        self.items.append(
            '<defs>'
            + "".join(
                f'<marker id="a_{k}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
                f'<path d="M0,0 L10,5 L0,10 z" fill="{v}"/></marker>'
                for k, v in C.items() if not k.endswith("_bg")
            )
            + "</defs>"
        )

    def rect(self, x, y, w, h, stroke="gray", fill="#ffffff", sw=1.6, r=6, dash=None):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        s = C.get(stroke, stroke); f = C.get(fill, fill)
        self.items.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{f}" stroke="{s}" stroke-width="{sw}"{d}/>')

    def text(self, x, y, s, size=13, color="gray", weight="normal", anchor="middle", italic=False):
        c = C.get(color, color)
        st = ' font-style="italic"' if italic else ""
        s = s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        self.items.append(f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="{size}" fill="{c}" font-weight="{weight}" text-anchor="{anchor}"{st}>{s}</text>')

    def lines(self, x, y, rows, size=13, color="gray", weight="normal", anchor="middle", lh=None):
        lh = lh or size * 1.25
        for i, r in enumerate(rows):
            self.text(x, y + i * lh, r, size, color, weight, anchor)

    def box(self, x, y, w, h, title, rows=(), stroke="gray", fill="#ffffff", tsize=14, rsize=12, tcolor=None, dash=None, sw=1.6):
        self.rect(x, y, w, h, stroke, fill, sw=sw, dash=dash)
        n = len(rows)
        block = tsize + (n * rsize * 1.25 if n else 0) + (4 if n else 0)
        y0 = y + (h - block) / 2 + tsize * 0.85
        self.text(x + w / 2, y0, title, tsize, tcolor or stroke, "bold")
        self.lines(x + w / 2, y0 + 4 + rsize * 1.25, rows, rsize, "gray")

    def arrow(self, pts, color="gray", sw=1.8, dash=None, both=False):
        c = C.get(color, color)
        d = " ".join(f"{'M' if i == 0 else 'L'}{x},{y}" for i, (x, y) in enumerate(pts))
        da = f' stroke-dasharray="{dash}"' if dash else ""
        ms = f' marker-start="url(#a_{color})"' if both else ""
        self.items.append(f'<path d="{d}" fill="none" stroke="{c}" stroke-width="{sw}"{da}{ms} marker-end="url(#a_{color})"/>')

    def save(self, path):
        with open(path, "w") as f:
            f.write(f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.w}" height="{self.h}" viewBox="0 0 {self.w} {self.h}">')
            f.write(f'<rect width="{self.w}" height="{self.h}" fill="#ffffff"/>')
            f.write("".join(self.items) + "</svg>")
