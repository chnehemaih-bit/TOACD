"""
generate_arch_diagram.py
Generates an executive, publication-grade Architecture Diagram comparing the
Original AI-Based Syntax Error Classification Architecture with the NEW
Extended Multi-Agent Autonomous Healing & Optimization System.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

fig, ax = plt.subplots(figsize=(20, 26), dpi=300)
ax.set_xlim(0, 200)
ax.set_ylim(0, 250)
ax.axis('off')

# Background
fig.patch.set_facecolor('#ffffff')
ax.set_facecolor('#ffffff')

# Helper: Draw rounded box
def draw_box(x, y, w, h, title, subtitle="", box_type="old", badge=""):
    if box_type == "old":
        bg, border, title_c = '#f8fafc', '#475569', '#0f172a'
    elif box_type == "new":
        bg, border, title_c = '#eff6ff', '#2563eb', '#1d4ed8'
    elif box_type == "agent":
        bg, border, title_c = '#f0fdf4', '#15803d', '#166534'
    elif box_type == "ext":
        bg, border, title_c = '#faf5ff', '#9333ea', '#6b21a8'
    elif box_type == "data":
        bg, border, title_c = '#fffbeb', '#b45309', '#92400e'

    p = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.5,rounding_size=2.0",
                       facecolor=bg, edgecolor=border, linewidth=1.5, zorder=2)
    ax.add_patch(p)

    lines = title.split('\n')
    num_title_lines = len(lines)

    if subtitle:
        # Title near top
        t_y = y + h - (3.2 if num_title_lines == 1 else 4.6)
        ax.text(x + w/2, t_y, title, ha='center', va='center',
                fontsize=9.5, fontweight='bold', color=title_c, zorder=3)
        # Subtitle in remaining middle
        sub_y = y + (t_y - y - (1.5 * num_title_lines))/2 + 1.0
        ax.text(x + w/2, sub_y, subtitle, ha='center', va='center',
                fontsize=7.8, color='#334155', linespacing=1.3, zorder=3)
    else:
        ax.text(x + w/2, y + h/2, title, ha='center', va='center',
                fontsize=9.5, fontweight='bold', color=title_c, zorder=3)

    if badge:
        b_color = '#dc2626' if 'NEW' in badge else '#2563eb'
        ax.text(x + w - 1.2, y + h - 1.2, badge, ha='right', va='top',
                fontsize=7.0, fontweight='bold', color=b_color,
                bbox=dict(boxstyle="round,pad=0.18", facecolor='#fee2e2' if 'NEW' in badge else '#dbeafe', edgecolor=b_color, lw=0.6),
                zorder=4)
    return (x, y, w, h)

# Helper: Layer boundary box
def draw_layer(x, y, w, h, label, is_new=False):
    border = '#2563eb' if is_new else '#64748b'
    bg = '#fcfdfe' if is_new else '#f8fafc'
    p = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.8,rounding_size=2.5",
                       facecolor=bg, edgecolor=border, linewidth=1.5,
                       linestyle='--' if is_new else '-', zorder=1)
    ax.add_patch(p)
    tag = "  [EXTENDED / NEW]" if is_new else "  [CORE SYSTEM]"
    ax.text(x + 3.0, y + h - 2.8, f"▼ {label}{tag}", ha='left', va='center',
            fontsize=10.0, fontweight='bold', color='#1d4ed8' if is_new else '#0f172a', zorder=3)

# Helper: Arrow
def draw_arrow(x1, y1, x2, y2, label="", color="#475569", lw=1.3, style="->", rad=0.0):
    arrow = FancyArrowPatch((x1, y1), (x2, y2),
                            arrowstyle=style, mutation_scale=11,
                            color=color, linewidth=lw,
                            connectionstyle=f"arc3,rad={rad}", zorder=4)
    ax.add_patch(arrow)
    if label:
        mx, my = (x1 + x2)/2, (y1 + y2)/2
        ax.text(mx, my + 1.0, label, ha='center', va='bottom',
                fontsize=7.4, fontweight='bold', color=color,
                bbox=dict(boxstyle="round,pad=0.2", facecolor='#ffffff', edgecolor='#cbd5e1', lw=0.6, alpha=0.95),
                zorder=5)

# ── HEADER & TITLE ──────────────────────────────────────────────────────────
ax.text(100, 243, "Architecture Diagram: AI-Based C++ Syntax Error Classification & Healing Platform",
        ha='center', va='center', fontsize=15.5, fontweight='bold', color='#0f172a')
ax.text(100, 238.5, "Integrated System Architecture Linking Original ML Pipeline with Next-Gen Agentic Self-Healing & Optimization Extensions",
        ha='center', va='center', fontsize=9.5, color='#475569')

# Legend
leg_y = 234.5
ax.text(35, leg_y, "[■] Original Component", ha='left', va='center', fontsize=8.5, color='#475569', fontweight='bold')
ax.text(85, leg_y, "[■] NEW: Agentic AI Autonomous Engine", ha='left', va='center', fontsize=8.5, color='#15803d', fontweight='bold')
ax.text(150, leg_y, "[■] NEW: Optimizers & Analyzers", ha='left', va='center', fontsize=8.5, color='#2563eb', fontweight='bold')

# ── TOP: DEVELOPER ACTOR ───────────────────────────────────────────────────
dev_x, dev_y = 100, 222
ax.plot([dev_x, dev_x], [dev_y - 3, dev_y + 1], color='#0f172a', lw=2, zorder=3)
ax.plot(dev_x, dev_y + 2.5, marker='o', markersize=7, color='#0f172a', zorder=3)
ax.text(dev_x, dev_y + 4.5, "Developer / User", ha='center', va='bottom', fontsize=10, fontweight='bold', color='#0f172a')

# ── 1. USER INTERFACE LAYER ────────────────────────────────────────────────
draw_layer(8, 187, 184, 28, "1. User Interface Layer (Interactive Dark IDE v2.0)")

draw_box(13, 191, 48, 18, "Code Submission Editor", "C++ Input / File Upload", "old")
draw_box(67, 191, 62, 18, "Diagnostic & Visual AST Viewer", "SVG Parse Tree (Reingold-Tilford Layout)", "new", "[NEW]")
draw_box(135, 191, 53, 18, "Multi-Tab Control Center", "Repair - Sec - Green - Optim - Agent", "new", "[NEW]")

# Arrows from Developer
draw_arrow(dev_x - 10, dev_y - 2, 37, 209, "Submit C++ Source Code", color="#2563eb", rad=0.08)
draw_arrow(161, 209, dev_x + 10, dev_y - 2, "Optimal Code, AST & Diagnostics", color="#15803d", rad=0.08)

# ── 2. COMPILER FRONT-END LAYER ────────────────────────────────────────────
draw_layer(8, 131, 58, 51, "2. Compiler Front-End Layer")

draw_box(12, 163, 50, 12, "Lexical Analyzer (lexer.py)", "Regex Engine -> Token Stream", "old")
draw_box(12, 148, 50, 12, "AST Parser (cpp_parser.py)", "Recursive Descent -> Parse Tree", "old")
draw_box(12, 134, 50, 11, "Semantic Analyzer (semantic_analyzer.py)", "Symbol Table - Scopes - Typo Distance", "new", "[NEW]")

draw_arrow(37, 163, 37, 160, "tokens.csv", color="#475569")
draw_arrow(37, 148, 37, 145, "AST Nodes", color="#475569")

# ── 3. DATA & FEATURE ENGINEERING LAYER ────────────────────────────────────
draw_layer(70, 131, 54, 51, "3. Data & Feature Engineering Layer")

draw_box(74, 162, 46, 13, "Syntax Error Dataset", "988 Training Samples (13 Classes)", "data")
draw_box(74, 147, 46, 12, "Model Repository", "model.pkl - scaler.pkl - encoder", "data")
draw_box(74, 134, 46, 10, "AST Feature Extractor", "ast_features.py (30 Numeric Features)", "old")

# ── 4. MACHINE LEARNING LAYER ──────────────────────────────────────────────
draw_layer(128, 131, 64, 51, "4. Machine Learning Classification Layer")

draw_box(132, 160, 56, 15, "ML Classifier (train.py)", "Random Forest (200 Trees, 100% Accuracy)", "old")
draw_box(132, 137, 56, 18, "Trained Model Predictor", "classify_syntax_error(code)\n13 Error Classes + Confidence Score", "new", "[ENHANCED]")

# Cross-layer connections
draw_arrow(37, 191, 37, 175, "Raw Source Code", color="#2563eb")
draw_arrow(37, 134, 74, 139, "AST Tree & Parse Errors", color="#475569")
draw_arrow(120, 139, 132, 143, "30 AST Features", color="#475569")
draw_arrow(97, 162, 97, 159, "Training Data", color="#b45309")
draw_arrow(120, 167, 132, 167, "Features.csv", color="#b45309")
draw_arrow(160, 160, 160, 155, "model.pkl", color="#b45309")

# ── 5. AGENTIC AI SELF-HEALING ENGINE (CORE NEW) ───────────────────────────
draw_layer(8, 57, 184, 69, "5. Core Agentic AI Autonomous Self-Healing Engine (agentic_engine.py)", is_new=True)

# Turn loop container box
draw_box(13, 93, 174, 27, "Multi-Turn Autonomous Self-Healing Loop (MAX_TURNS = 8)", "", "agent")

# Turn loop 5 phases
draw_box(16, 96, 30, 19, "1. Perceive", "Inspect code,\nAST & tokens", "agent", "[NEW]")
draw_box(52, 96, 33, 19, "2. Tool Call", "cpp_parser.build_ast()\nSemanticAnalyzer", "agent", "[NEW]")
draw_box(91, 96, 31, 19, "3. Reflect", "ErrorNodes & Typos\nSelect Strategy", "agent", "[NEW]")
draw_box(128, 96, 33, 19, "4. Action: Patch", "Apply 12 Surgical\nHealing Strategies", "agent", "[NEW]")
draw_box(167, 96, 17, 19, "5. Verify", "0 Errors?\nLoop/Exit", "agent", "[NEW]")

draw_arrow(46, 105.5, 52, 105.5, color="#15803d")
draw_arrow(85, 105.5, 91, 105.5, color="#15803d")
draw_arrow(122, 105.5, 128, 105.5, color="#15803d")
draw_arrow(161, 105.5, 167, 105.5, color="#15803d")
# Iterative loop back
draw_arrow(175.5, 96, 31, 96, "If ErrorNodes > 0 (Secondary Error Repair Loop)", color="#dc2626", lw=1.3, rad=-0.16)

# 12 Strategies box
draw_box(13, 61, 174, 28, "12 Surgical Healing Strategies (Context-Aware Transformation Engine)", "", "new")
strat_col1 = " S1: Missing Main Function\n S2: Semicolon Insertion (Comment-Aware)\n S3: Unmatched Closing Braces\n S4: Unclosed Opening Braces"
strat_col2 = " S5: Unmatched Parentheses\n S6: String Quotes Termination\n S7: Fuzzy Typo Repair (coutt->cout)\n S8: Missing If-Condition Parentheses"
strat_col3 = " S9: Array Bracket Repair [10;\n S10: Missing Function/Class Braces\n S11: Duplicate & Misplaced Tokens\n S12: Invalid Type Aliasing (interger->int)"

ax.text(17, 79, strat_col1, ha='left', va='top', fontsize=7.6, color='#1e293b', fontfamily='monospace')
ax.text(72, 79, strat_col2, ha='left', va='top', fontsize=7.6, color='#1e293b', fontfamily='monospace')
ax.text(130, 79, strat_col3, ha='left', va='top', fontsize=7.6, color='#1e293b', fontfamily='monospace')

# Connect ML prediction to Agent
draw_arrow(160, 137, 160, 126, "Predicted Error Class", color="#2563eb")
draw_arrow(160, 126, 31, 120, color="#2563eb", rad=0.05)

# Connect Front-End parser tools to Agent Tool Call
draw_arrow(37, 131, 68, 120, "Compiler Tool Invocation", color="#15803d", rad=-0.05)

# ── 6. SPECIALIZED AGENTIC ANALYZERS & OPTIMIZERS ──────────────────────────
draw_layer(8, 8, 184, 44, "6. Multi-Dimensional Agentic Analyzers & Optimizers", is_new=True)

draw_box(13, 12, 54, 34, "Green Computing Profiler\n(GreenComputingProfiler)", 
         "Time & Space Complexity O(n)\nCPU Instruction Cycles Estimation\nActive Energy Consumption (uJ)\nCarbon Footprint (gCO2e / 10M runs)\nEco-Score Grade (A+ to F Rating)\nGreen Software Optimization Tips", "ext", "[NEW]")

draw_box(73, 12, 56, 34, "Cybersecurity Threat Shield\n(CyberThreatShield)", 
         "Buffer Overflow Audit (CWE-120/121)\nFormat String Attack Audit (CWE-134)\nMemory Leak Detection (CWE-401)\nInteger Overflow Check (CWE-190)\nUnbounded DoS Loop Scan (CWE-835)\nAttack Vector & Hardened C++ Patch", "ext", "[NEW]")

draw_box(135, 12, 53, 34, "Code Optimizer Engine\n(CodeOptimizer)", 
         "endl -> '\\n' (10x Loop I/O Speedup)\ni++ -> ++i (Micro-Optimization)\nNested Loop Algorithmic Shift O(n)\nVector .reserve() Pre-Allocation\nstd::map -> std::unordered_map\nSide-by-Side Interactive Diff", "new", "[NEW]")

# Verified Healed Code routing to 3 extensions
draw_arrow(40, 61, 40, 46, "Verified Healed Code", color="#15803d")
draw_arrow(101, 61, 101, 46, "Verified Healed Code", color="#9333ea")
draw_arrow(161, 61, 161, 46, "Verified Healed Code", color="#2563eb")

# Feedback to UI
draw_arrow(40, 46, 11, 191, "Eco Grade & Carbon", color="#15803d", rad=-0.22)
draw_arrow(101, 46, 98, 191, "Security Audit & Hardening", color="#9333ea", rad=0.15)
draw_arrow(161, 46, 178, 191, "Optimized Code & Diff", color="#2563eb", rad=0.22)

plt.tight_layout()

# Save image
out_local = r"C:\Users\sanjay\Downloads\AI Based synatx error classification\architecture_diagram_v2.png"
out_onedrive = r"C:\Users\sanjay\OneDrive\AI BASED SYNTAX ERROR CLASSIFICAION\architecture_diagram_v2.png"

plt.savefig(out_local, dpi=300, bbox_inches='tight')
plt.savefig(out_onedrive, dpi=300, bbox_inches='tight')
print("Successfully generated high-res architecture diagram v2 at:")
print(f"  - {out_local}")
print(f"  - {out_onedrive}")
