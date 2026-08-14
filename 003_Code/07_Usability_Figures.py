he printed transcript during analysis.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUT = PROJECT_ROOT / "002_Dataset" / "outputs"

THEME_PRIMARY = '#1E7A8C'
THEME_MED = '#7FB3C2'
THEME_LIGHT = '#EAF3F5'
THEME_TEXT = '#1B2A33'
WARN = '#B5651D'
RISK_COLORS = {'Low': '#639922', 'Medium': '#EF9F27', 'High': '#E24B4A'}

plt.rcParams.update({"font.family": "sans-serif", "text.color": THEME_TEXT})

# ── Figure 5.1 — Participant distribution by version ──────────────────────
fig, ax = plt.subplots(figsize=(5.5, 5))
ax.bar(['Version A', 'Version B'], [3, 3], color=[THEME_PRIMARY, THEME_MED], width=0.5)
for i, v in enumerate([3, 3]):
    ax.text(i, v + 0.05, str(v), ha='center', fontsize=13, fontweight='bold')
ax.set_ylabel("Participants (n)")
ax.set_ylim(0, 4)
ax.set_title("Participant distribution by dashboard version (n=6)", fontsize=12, fontweight='bold')
ax.grid(axis='y', alpha=0.3)
plt.tight_layout()
plt.savefig(f"{OUT}/usability_participant_distribution.png", dpi=220, facecolor='white')
plt.close()
print("Saved usability_participant_distribution.png")

# ── Figure 5.2 — Risk levels evaluated (as recorded in Q3) ─────────────────
fig, ax = plt.subplots(figsize=(6, 5))
levels = ['Low', 'Medium', 'High']
counts = [1, 1, 4]
colors = [RISK_COLORS[l] for l in levels]
ax.bar(levels, counts, color=colors)
for i, v in enumerate(counts):
    ax.text(i, v + 0.05, str(v), ha='center', fontsize=13, fontweight='bold')
ax.set_ylabel("Responses (n)")
ax.set_ylim(0, 5)
ax.set_title("Risk levels evaluated, as recorded in Q3 (n=6)\nP06 recorded 'High' in Q3 but described 'Low' in Q4/Q5 — see §5.12",
             fontsize=11, fontweight='bold')
ax.grid(axis='y', alpha=0.3)
plt.tight_layout()
plt.savefig(f"{OUT}/usability_risk_levels_evaluated.png", dpi=220, facecolor='white')
plt.close()
print("Saved usability_risk_levels_evaluated.png")

# ── Figure 5.3 — Trust/explanation theme presence, A vs B ─────────────────
fig, ax = plt.subplots(figsize=(8, 5.5))
themes = ['Cites explanation/\nreasoning as trust driver', 'Uses "black box" /\ntransparency language',
          'Notes SHAP/technical\nterminology difficulty']
a_counts = [3, 0, 0]
b_counts = [3, 2, 2]
x = np.arange(len(themes))
w = 0.32
ax.bar(x - w / 2, a_counts, width=w, label='Version A (n=3)', color=THEME_PRIMARY)
ax.bar(x + w / 2, b_counts, width=w, label='Version B (n=3)', color=THEME_MED)
for i, v in enumerate(a_counts):
    ax.text(i - w / 2, v + 0.05, str(v), ha='center', fontsize=10)
for i, v in enumerate(b_counts):
    ax.text(i + w / 2, v + 0.05, str(v), ha='center', fontsize=10)
ax.set_xticks(x)
ax.set_xticklabels(themes, fontsize=9.5)
ax.set_ylabel("Participants mentioning theme (n)")
ax.set_ylim(0, 3.5)
ax.set_title("Trust and explanation themes by version (thematic tally, not a validated scale)",
             fontsize=11, fontweight='bold')
ax.legend()
ax.grid(axis='y', alpha=0.3)
plt.tight_layout()
plt.savefig(f"{OUT}/usability_trust_explanation_themes.png", dpi=220, facecolor='white')
plt.close()
print("Saved usability_trust_explanation_themes.png")

# ── Figure 5.4 — Recommendation usefulness and action intent ──────────────
fig, axes = plt.subplots(1, 2, figsize=(10, 5))
axes[0].bar(['Yes'], [6], color=THEME_PRIMARY, width=0.4)
axes[0].text(0, 6.05, '6', ha='center', fontsize=13, fontweight='bold')
axes[0].set_ylim(0, 7)
axes[0].set_title("Q8: Recommendations felt\nrelevant and useful (n=6)", fontsize=10.5, fontweight='bold')
axes[0].set_ylabel("Responses (n)")
axes[0].grid(axis='y', alpha=0.3)

cats = ['Yes', 'Qualified /\npartial', 'Maybe', 'No']
vals = [3, 1, 1, 1]
axes[1].bar(cats, vals, color=[THEME_PRIMARY, WARN, THEME_MED, '#B0B0B0'])
for i, v in enumerate(vals):
    axes[1].text(i, v + 0.05, str(v), ha='center', fontsize=11, fontweight='bold')
axes[1].set_ylim(0, 4)
axes[1].set_title("Q7: Would you change your\nbehaviour or take action? (n=6)", fontsize=10.5, fontweight='bold')
axes[1].grid(axis='y', alpha=0.3)
plt.tight_layout()
plt.savefig(f"{OUT}/usability_recommendation_action.png", dpi=220, facecolor='white')
plt.close()
print("Saved usability_recommendation_action.png")

# ── Figure 5.5 — SHAP explanation feedback (Version B only, n=3) ──────────
fig, ax = plt.subplots(figsize=(8, 5))
shap_themes = ['Explanation reduced\n"black box" perception', 'Noted difficulty with\nSHAP/technical terminology',
               'Suggested SHAP-specific\nimprovement (legend/tooltip)']
shap_counts = [3, 2, 1]
ax.barh(shap_themes, shap_counts, color=THEME_MED)
for i, v in enumerate(shap_counts):
    ax.text(v + 0.05, i, str(v), va='center', fontsize=11, fontweight='bold')
ax.set_xlabel("Version B participants (n=3)")
ax.set_xlim(0, 3.5)
ax.set_title("SHAP explanation feedback, Version B only (n=3)", fontsize=12, fontweight='bold')
ax.grid(axis='x', alpha=0.3)
plt.tight_layout()
plt.savefig(f"{OUT}/usability_shap_feedback.png", dpi=220, facecolor='white')
plt.close()
print("Saved usability_shap_feedback.png")

# ── Figure 5.6 — User-suggested improvement themes (all n=6) ──────────────
fig, ax = plt.subplots(figsize=(8.5, 5.5))
imp_themes = ['Live/real-time weather\ndata', 'Wider geographic\ncoverage', 'Historical flood\ninformation',
              'More detailed summary', 'SHAP legend/tooltip\nor simple-vs-detailed toggle', 'No specific\nimprovement suggested']
imp_counts = [2, 2, 1, 1, 1, 2]
ax.barh(imp_themes, imp_counts, color=THEME_PRIMARY)
for i, v in enumerate(imp_counts):
    ax.text(v + 0.05, i, str(v), va='center', fontsize=10.5, fontweight='bold')
ax.set_xlabel("Participants (n=6)")
ax.set_xlim(0, 3)
ax.set_title("User-suggested improvement themes, Q10 (n=6)", fontsize=12, fontweight='bold')
ax.grid(axis='x', alpha=0.3)
plt.tight_layout()
plt.savefig(f"{OUT}/usability_improvement_themes.png", dpi=220, facecolor='white')
plt.close()
print("Saved usability_improvement_themes.png")

print("\nAll Chapter 5 usability figures complete.")
