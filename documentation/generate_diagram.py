import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

fig, ax = plt.subplots(figsize=(8, 16))
ax.set_xlim(0, 8)
ax.set_ylim(0, 16)
ax.axis('off')
fig.patch.set_facecolor('white')

CX = 1.5    # box left x
W  = 5.0    # box width
MX = CX + W / 2  # centre x = 4.0

def box(x, y, w, h, title, subtitle=None, fill='white', lw=1.5):
    rect = FancyBboxPatch((x, y), w, h,
                           boxstyle="round,pad=0.1",
                           linewidth=lw, edgecolor='black', facecolor=fill)
    ax.add_patch(rect)
    gap = h * 0.18 if subtitle else 0
    ax.text(x + w / 2, y + h / 2 + gap, title,
            ha='center', va='center', fontsize=10, fontweight='bold', color='black')
    if subtitle:
        ax.text(x + w / 2, y + h / 2 - gap, subtitle,
                ha='center', va='center', fontsize=8, color='#444444', style='italic')

def down_arrow(y1, y2, label=''):
    """Straight downward arrow from y1 to y2 at MX."""
    ax.annotate('', xy=(MX, y2), xytext=(MX, y1),
                arrowprops=dict(arrowstyle='->', color='black', lw=1.5))
    if label:
        ax.text(MX + 0.15, (y1 + y2) / 2, label,
                ha='left', va='center', fontsize=8, color='#333333', style='italic')

def side_loop(x_side, y_from, y_to, label, side='right'):
    """
    Draw an L-shaped loop arrow on the left or right side.
    Exits the box at x_side horizontally, travels vertically, re-enters the target box.
    """
    box_edge  = CX + W if side == 'right' else CX
    offset    = x_side          # the vertical rail x

    # Horizontal exit line: box_edge → rail
    ax.plot([box_edge, offset], [y_from, y_from], color='black', lw=1.2, zorder=5)
    # Vertical rail: y_from → y_to
    ax.plot([offset, offset], [y_from, y_to], color='black', lw=1.2, zorder=5)
    # Horizontal entry + arrowhead into target box
    ax.annotate('',
                xy=(box_edge, y_to),
                xytext=(offset, y_to),
                arrowprops=dict(arrowstyle='->', color='black', lw=1.2))
    # Label beside the vertical rail
    lx = offset + 0.1 if side == 'right' else offset - 0.1
    ha = 'left'       if side == 'right' else 'right'
    ax.text(lx, (y_from + y_to) / 2, label,
            ha=ha, va='center', fontsize=7.5, style='italic', color='#333333')

# ── Boxes (y_top, height) ─────────────────────────────────────────────────────
#                          y     h
USER     = (14.8, 0.9)
UPLOAD   = (13.0, 1.0)
EDA      = (11.4, 1.0)
QUERY    = ( 9.8, 1.0)
PHASE1   = ( 8.1, 1.1)
REVIEW   = ( 6.6, 0.9)
PHASE2   = ( 5.0, 1.1)
RESULT   = ( 3.4, 1.0)
MEMORY   = ( 1.8, 1.0)

def B(node, title, subtitle=None, fill='white', lw=1.5):
    box(CX, node[0], W, node[1], title, subtitle, fill=fill, lw=lw)

B(USER,   'User',                  'Business Analyst',                                fill='#d9d9d9', lw=2.0)
B(UPLOAD, 'Upload CSV / Parquet',  'Drag & drop in React UI')
B(EDA,    'EDA Analysis',          'CSVAnalysisAgent → analysis.md')
B(QUERY,  'User Types Query',      'Natural language request')
B(PHASE1, 'Phase 1 — Planning',    'Manager + Metadata Specialist\n→ implementation_plan.md', fill='#efefef')
B(REVIEW, 'Human Plan Review',     'Annotate & Approve / Reject',                     fill='#d9d9d9', lw=2.0)
B(PHASE2, 'Phase 2 — Execution',   'Coder → Executor → Validator\n(retry loop)',       fill='#efefef')
B(RESULT, 'Result',                'Final answer streamed to Chat UI')
B(MEMORY, 'Session Memory Update', 'Context_Manager → session_context.json')

# ── Main vertical arrows ──────────────────────────────────────────────────────
down_arrow(USER[0],   UPLOAD[0] + UPLOAD[1])
down_arrow(UPLOAD[0], EDA[0]    + EDA[1])
down_arrow(EDA[0],    QUERY[0]  + QUERY[1])
down_arrow(QUERY[0],  PHASE1[0] + PHASE1[1])
down_arrow(PHASE1[0], REVIEW[0] + REVIEW[1])
down_arrow(REVIEW[0], PHASE2[0] + PHASE2[1], label='Approved')
down_arrow(PHASE2[0], RESULT[0] + RESULT[1])
down_arrow(RESULT[0], MEMORY[0] + MEMORY[1])

# ── Side loops ────────────────────────────────────────────────────────────────
# RIGHT: Rejected — from mid-height of REVIEW box → mid-height of QUERY box
review_mid = REVIEW[0] + REVIEW[1] / 2
query_mid  = QUERY[0]  + QUERY[1]  / 2
side_loop(x_side=7.2, y_from=review_mid, y_to=query_mid,
          label='Rejected\n(re-plan)', side='right')

# LEFT: Follow-up query — from mid-height of MEMORY box → mid-height of QUERY box
memory_mid = MEMORY[0] + MEMORY[1] / 2
side_loop(x_side=0.8, y_from=memory_mid, y_to=query_mid,
          label='Follow-up\nquery', side='left')


# ── Save ──────────────────────────────────────────────────────────────────────
out = r'c:\Users\hariharan.balaji\Desktop\Personal\Codebase\Agents_openai revised\documentation\architecture_diagram.png'
fig.savefig(out, dpi=180, bbox_inches='tight', facecolor='white')
print(f'Saved: {out}')
