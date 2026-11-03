"""
generate_a4_diagram.py
Generates an A4-optimized, hand-drawable Architecture Diagram with
Performance Analysis included across Level 5 and Level 6.
Perfect proportions (8.5 x 12.0 inches), clean rectangular boxes,
straight arrows, no overlapping labels, optimized for copying onto A4 paper.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch

fig, ax = plt.subplots(figsize=(8.5, 12.0), dpi=300)
ax.set_xlim(0, 100)
ax.set_ylim(0, 140)
ax.axis('off')

fig.patch.set_facecolor('#ffffff')
ax.set_facecolor('#ffffff')

# Helper: Draw box
def draw_card(x, y, w, h, title, subtitle="", is_new=False, is_data=False):
    if is_new:
        bg = '#f0fdf4'
        border = '#16a34a'
        tc = '#15803d'
    elif is_data:
        bg = '#fffbeb'
        border = '#d97706'
        tc = '#b45309'
    else:
        bg = '#f8fafc'
        border = '#334155'
        tc = '#0f172a'

    p = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.25,rounding_size=1.2",
                       facecolor=bg, edgecolor=border, linewidth=1.3, zorder=2)
    ax.add_patch(p)

    lines = title.split('\n')
    t_y = y + h - (2.5 if len(lines) == 1 else 3.6) if subtitle else y + h/2
    ax.text(x + w/2, t_y, title, ha='center', va='center',
            fontsize=7.3, fontweight='bold', color=tc, zorder=3)

    if is_new:
        ax.text(x + w - 0.7, y + h - 0.7, "[*NEW]", ha='right', va='top',
                fontsize=5.2, fontweight='bold', color='#dc2626', zorder=4)

    if subtitle:
        sub_y = y + (t_y - y)/2 - 0.2
        ax.text(x + w/2, sub_y, subtitle, ha='center', va='center',
                fontsize=5.8, color='#475569', linespacing=1.22, zorder=3)

# Helper: Straight arrow
def draw_arrow(x1, y1, x2, y2, label="", color="#334155", side_label=False):
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle="->", color=color, lw=1.2, shrinkA=0, shrinkB=0),
                zorder=4)
    if label:
        if side_label:
            mx, my = (x1 + x2)/2 + 4.5, (y1 + y2)/2
        else:
            mx, my = (x1 + x2)/2, (y1 + y2)/2
        ax.text(mx, my, label, ha='center', va='center',
                fontsize=5.6, fontweight='bold', color=color,
                bbox=dict(boxstyle="round,pad=0.15", facecolor='#ffffff', edgecolor='#cbd5e1', lw=0.5),
                zorder=5)

# Helper: Section Header Box
def draw_section_hdr(x, y, w, h, title):
    p = FancyBboxPatch((x, y), w, h, boxstyle="square,pad=0",
                       facecolor='#e2e8f0', edgecolor='#64748b', linewidth=1.0, zorder=1)
    ax.add_patch(p)
    ax.text(x + w/2, y + h/2, title, ha='center', va='center',
            fontsize=7.5, fontweight='bold', color='#1e293b', zorder=3)

# ── TOP TITLE ───────────────────────────────────────────────────────────────
ax.text(50, 137.2, "ARCHITECTURE DIAGRAM", ha='center', va='center',
        fontsize=13, fontweight='bold', color='#0f172a')
ax.text(50, 134.7, "AI-Based C++ Syntax Error Classification, Healing & Performance Platform", ha='center', va='center',
        fontsize=8.5, fontweight='semibold', color='#2563eb')
ax.text(50, 132.3, "(Complete System Architecture for A4 Paper Hand-Drawing)", ha='center', va='center',
        fontsize=7.0, color='#64748b', fontstyle='italic')

# Legend
ax.text(18, 129.5, "[  ] Original Component", ha='left', va='center', fontsize=6.8, color='#334155', fontweight='bold')
ax.text(60, 129.5, "[*NEW] Added / Extended Module", ha='left', va='center', fontsize=6.8, color='#dc2626', fontweight='bold')

# Outer A4 Drawing Border
border_rect = patches.Rectangle((4, 3), 92, 125, fill=False, edgecolor='#94a3b8', lw=1.2, linestyle=':')
ax.add_patch(border_rect)

# ── LEVEL 1: USER / DEVELOPER ──────────────────────────────────────────────
draw_section_hdr(6, 123.5, 88, 3.2, "LEVEL 1: USER INTERFACE & PRESENTATION LAYER")

draw_card(6, 114, 25, 8, "Developer / User", "Inputs C++ Code\nViews Healed Output", is_new=False)
draw_card(35, 114, 28, 8, "Web Code Editor", "Syntax Highlighting\nLine Error Markers", is_new=False)
draw_card(67, 114, 27, 8, "Visual AST Tree & Tabs", "SVG Graphical Tree\nRepair / Sec / Green / Perf", is_new=True)

draw_arrow(31, 118, 35, 118, "Code")
draw_arrow(67, 118, 63, 118)

# ── LEVEL 2: COMPILER FRONT-END ────────────────────────────────────────────
draw_section_hdr(6, 107.5, 88, 3.2, "LEVEL 2: COMPILER FRONT-END LAYER")

draw_card(6, 97.5, 26, 8.5, "Lexical Analyzer", "lexer.py\nRegex -> Tokens", is_new=False)
draw_card(36, 97.5, 28, 8.5, "Syntax Parser", "cpp_parser.py\nRecursive Descent -> AST", is_new=False)
draw_card(68, 97.5, 26, 8.5, "Semantic Analyzer", "semantic_analyzer.py\nSymbol Table & Typo Match", is_new=True)

draw_arrow(49, 114, 49, 110.8)
draw_arrow(32, 101.8, 36, 101.8, "Tokens")
draw_arrow(64, 101.8, 68, 101.8, "AST Tree")

# ── LEVEL 3: FEATURE ENGINEERING & MACHINE LEARNING ────────────────────────
draw_section_hdr(6, 91.5, 88, 3.2, "LEVEL 3: FEATURE EXTRACTION & MACHINE LEARNING LAYER")

draw_card(6, 81.5, 26, 8.5, "Feature Extractor", "ast_features.py\n30 Structural AST Features", is_new=False)
draw_card(36, 81.5, 28, 8.5, "Random Forest Classifier", "train.py / model.pkl\n200 Trees | 100% Accuracy", is_new=False)
draw_card(68, 81.5, 26, 8.5, "Error Dataset", "988 Training Samples\n13 Syntax Error Classes", is_new=False, is_data=True)

draw_arrow(19, 97.5, 19, 94.8)
draw_arrow(32, 85.8, 36, 85.8, "30 Features")
draw_arrow(68, 85.8, 64, 85.8, "Trained On")

# ── LEVEL 4: AGENTIC AI SELF-HEALING ENGINE (NEW CORE) ─────────────────────
draw_section_hdr(6, 75.5, 88, 3.2, "LEVEL 4: AGENTIC AI AUTONOMOUS SELF-HEALING ENGINE (agentic_engine.py) [*NEW]")

# 5 Phase Horizontal Turn Loop
p_w = 16.5
p_h = 8.5
draw_card(6,  64.5, p_w, p_h, "1. Perceive", "Inspect Source\n& ML Class", is_new=True)
draw_card(24, 64.5, p_w, p_h, "2. Tool Call", "cpp_parser AST\nSemantic Check", is_new=True)
draw_card(42, 64.5, p_w, p_h, "3. Reflect", "Detect ErrorNodes\nSelect Strategy", is_new=True)
draw_card(60, 64.5, p_w, p_h, "4. Action", "12 Surgical\nPatch Strategies", is_new=True)
draw_card(78, 64.5, 16,  p_h, "5. Verify", "0 Errors?\nExit / Loop", is_new=True)

# Loop arrows
draw_arrow(22.5, 68.7, 24, 68.7)
draw_arrow(40.5, 68.7, 42, 68.7)
draw_arrow(58.5, 68.7, 60, 68.7)
draw_arrow(76.5, 68.7, 78, 68.7)

# Loop back arrow
ax.annotate('', xy=(14, 64.5), xytext=(86, 64.5),
            arrowprops=dict(arrowstyle="->", color="#dc2626", lw=1.2,
                            connectionstyle="arc3,rad=-0.16"))
ax.text(50, 60.0, "Secondary Errors Remain: Autonomous Next Turn (MAX_TURNS = 8)",
        ha='center', va='center', fontsize=5.8, fontweight='bold', color='#dc2626')

# ML to Agent connection
draw_arrow(50, 81.5, 50, 78.8, "Prediction + Confidence")

# 12 Strategies Summary Strip
strat_rect = FancyBboxPatch((6, 48.5), 88, 9.5, boxstyle="round,pad=0.2,rounding_size=1.0",
                            facecolor='#f8fafc', edgecolor='#94a3b8', lw=1.0)
ax.add_patch(strat_rect)
ax.text(8, 56.0, "12 Knowledge-Based Surgical Strategies Applied During Action Phase:",
        fontsize=6.2, fontweight='bold', color='#1e293b')
ax.text(8, 53.4, "S1: Missing Main  |  S2: Semicolon Insert  |  S3: Missing Closing Brace  |  S4: Unclosed Brace  |  S5: Parentheses Fix",
        fontsize=5.4, color='#475569', fontfamily='monospace')
ax.text(8, 50.4, "S6: String Quotes  |  S7: Fuzzy Typo (coutt->cout)  |  S8: If-Condition (..)  |  S9: Array [N]  |  S10: Block Braces",
        fontsize=5.4, color='#475569', fontfamily='monospace')

# ── LEVEL 5: SPECIALIZED ANALYZERS & OPTIMIZERS (WITH PERFORMANCE ANALYSIS) 
draw_section_hdr(6, 42.5, 88, 3.2, "LEVEL 5: MULTI-DIMENSIONAL POST-ANALYSIS & BENCHMARK ENGINES [*NEW]")

b_w = 20.8
draw_card(6.0, 23.5, b_w, 17.5, "Green Computing\nProfiler",
          "• Time/Space O(n)\n• CPU Cycles\n• Energy (uJ)\n• Carbon gCO2e\n• Eco-Grade A+-F\n• Green Guidance", is_new=True)

draw_card(28.4, 23.5, b_w, 17.5, "CyberThreatShield\nSecurity Audit",
          "• CWE-120 Buffer\n• CWE-134 Format\n• CWE-401 Leaks\n• CWE-190 Wraps\n• Exploit Vector\n• Hardened Patch", is_new=True)

draw_card(50.8, 23.5, b_w, 17.5, "Code Optimizer\nEngine",
          "• endl -> '\\n' (10x)\n• i++ -> ++i (Pre)\n• O(n^2) -> O(n)\n• Vector .reserve()\n• map -> unord_map\n• Code Diff View", is_new=True)

draw_card(73.2, 23.5, b_w, 17.5, "Performance Analysis\nEngine",
          "• Detection Latency\n• Confidence Rate\n• Compile Success\n• Code Complexity\n  (Simple/Med/Cmplx)\n• Benchmarks Log", is_new=True)

# Feeds from verified code (Level 4 -> Level 5)
draw_arrow(86, 64.5, 50, 45.8, "Verified Clean Code (0 Errors)")
draw_arrow(50, 42.5, 16.4, 41.2)
draw_arrow(50, 42.5, 38.8, 41.2)
draw_arrow(50, 42.5, 61.2, 41.2)
draw_arrow(50, 42.5, 83.6, 41.2)

# ── LEVEL 6: FINAL RESULTS / DASHBOARD ─────────────────────────────────────
draw_section_hdr(6, 18.0, 88, 3.0, "LEVEL 6: FINAL OUTPUT DELIVERABLES")

draw_card(6.0,  7.5, b_w, 9.2, "1. Healed Code", "100% Compile-Ready\nZero Syntax Errors", is_new=False)
draw_card(28.4, 7.5, b_w, 9.2, "2. Security & Eco", "CVSS Threat Score\nEco-Grade (A+ to F)", is_new=True)
draw_card(50.8, 7.5, b_w, 9.2, "3. Optimal Code", "Time/Space Reduction\nInteractive Diff", is_new=True)
draw_card(73.2, 7.5, b_w, 9.2, "4. Perf Dashboard", "/performance View\nLatency & Accuracy", is_new=True)

draw_arrow(16.4, 23.5, 16.4, 21.1)
draw_arrow(38.8, 23.5, 38.8, 21.1)
draw_arrow(61.2, 23.5, 61.2, 21.1)
draw_arrow(83.6, 23.5, 83.6, 21.1)

# Upward return arrow to Developer / UI
draw_arrow(94, 12, 96, 114, "Feedback to IDE Dashboard", color="#2563eb", side_label=False)

# Footer note for paper submission
ax.text(50, 4.5, "System Pipeline: Input -> Lexer -> Parser -> ML -> Agentic Repair -> Green / Security / Optimizer / Performance -> Dashboard",
        ha='center', va='center', fontsize=5.8, color='#64748b', fontweight='semibold')

plt.tight_layout()

# Save A4 PNG
out_local = r"C:\Users\sanjay\Downloads\AI Based synatx error classification\a4_architecture_diagram.png"
out_onedrive = r"C:\Users\sanjay\OneDrive\AI BASED SYNTAX ERROR CLASSIFICAION\a4_architecture_diagram.png"

plt.savefig(out_local, dpi=300, bbox_inches='tight')
plt.savefig(out_onedrive, dpi=300, bbox_inches='tight')
print("Successfully generated A4 Architecture Diagram with Performance Analysis at:")
print(f"  - {out_local}")
print(f"  - {out_onedrive}")
