# ============================================================
#  NOVAPULSE — PHASE 2: CHANNEL DEEP DIVE
#  Your manager confirmed: landing page redesign happened
#  late March. Hypothesis is now a confirmed finding.
#  Now we go deeper into each channel.
# ============================================================

# ── WHY ARE WE DOING A SEPARATE SCRIPT? ─────────────────────
# In real life analysts keep their work modular.
# Phase 1 = data intake and audit (already done, don't touch)
# Phase 2 = channel analysis (this script)
# Phase 3 = recommendations and deck (next)
#
# This way if something breaks you know exactly which
# phase has the problem. And your manager can review
# each phase independently.
# ============================================================

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import warnings
warnings.filterwarnings('ignore')

plt.style.use('seaborn-v0_8-whitegrid')

print("=" * 65)
print("NOVAPULSE — PHASE 2: CHANNEL DEEP DIVE ANALYSIS")
print("Analyst: Jay")
print("=" * 65)


# ── STEP 1: RELOAD AND RECLEAN DATA ─────────────────────────
# WHAT: Load all 4 files again and apply the same cleaning
# WHY: This script runs independently from Phase 1.
#      We always start fresh — never assume the data from
#      a previous script is still in memory.
#      This is called "reproducibility" — anyone can run
#      this script from scratch and get the same result.

print("\n📂 Loading and cleaning data...")

google_df = pd.read_csv('novapulse_google_ads.csv')
meta_df   = pd.read_csv('novapulse_meta_ads.csv')
email_df  = pd.read_csv('novapulse_email.csv')

# --- Clean Google Ads ---
google_df['date'] = pd.to_datetime(google_df['date'])
google_df['conversions'] = google_df['conversions'].clip(lower=0)
google_df['revenue'] = google_df['revenue'].fillna(0)
google_df['month'] = google_df['date'].dt.month
google_df['period'] = google_df['month'].apply(
    lambda m: 'Pre-Redesign (Jan-Mar)' if m <= 3 else 'Post-Redesign (Apr-Jun)'
)

# --- Clean Meta Ads ---
meta_df['date'] = pd.to_datetime(meta_df['Date'], format='%m/%d/%Y')
meta_df = meta_df.rename(columns={
    'Campaign Name': 'campaign',
    'Link Clicks': 'clicks',
    'Amount Spent': 'spend',
    'Purchases': 'conversions',
    'Purchase Value': 'revenue'
})
meta_df['spend'] = meta_df['spend'].fillna(meta_df['spend'].median())
meta_df['month'] = meta_df['date'].dt.month
meta_df['period'] = meta_df['month'].apply(
    lambda m: 'Pre-Redesign (Jan-Mar)' if m <= 3 else 'Post-Redesign (Apr-Jun)'
)

# --- Clean Email ---
email_df['date'] = pd.to_datetime(email_df['send_date'])
email_df['month'] = email_df['date'].dt.month

print("  ✅ All data loaded and cleaned")


# ── STEP 2: GOOGLE ADS — CAMPAIGN LEVEL BREAKDOWN ───────────
# WHAT: Group by campaign and calculate KPIs for each
# WHY: The monthly trend showed Google Ads overall is declining.
#      But "overall" hides the story. Which specific campaigns
#      are the problem? Which are still working?
#
# This is called "drilling down" — going from summary level
# to detail level to find where the problem actually lives.
#
# .groupby('campaign').agg() groups all rows with the same
# campaign name together and calculates totals/averages.

print("\n\n" + "=" * 65)
print("GOOGLE ADS — CAMPAIGN LEVEL BREAKDOWN")
print("=" * 65)

g_campaign = google_df.groupby('campaign').agg(
    total_spend    = ('spend', 'sum'),
    total_revenue  = ('revenue', 'sum'),
    total_clicks   = ('clicks', 'sum'),
    total_conv     = ('conversions', 'sum'),
    total_impr     = ('impressions', 'sum'),
).reset_index()

# Calculate derived KPIs
# WHAT: These are the metrics we calculate FROM the raw numbers
# WHY: The raw data gives us spend, clicks, conversions.
#      But ROAS, CVR, CPC are what tell us if a campaign is
#      actually performing well or just spending money.
g_campaign['ROAS'] = (g_campaign['total_revenue'] / g_campaign['total_spend']).round(2)
g_campaign['CVR']  = (g_campaign['total_conv'] / g_campaign['total_clicks'] * 100).round(2)
g_campaign['CPC']  = (g_campaign['total_spend'] / g_campaign['total_clicks']).round(2)
g_campaign['CAC']  = (g_campaign['total_spend'] / g_campaign['total_conv'].replace(0,1)).round(2)
g_campaign['CTR']  = (g_campaign['total_clicks'] / g_campaign['total_impr'] * 100).round(2)

# Sort by ROAS descending — best performers at top
g_campaign = g_campaign.sort_values('ROAS', ascending=False)

print(f"\n{'Campaign':<26} {'Spend':>10} {'Revenue':>10} {'ROAS':>7} {'CVR%':>7} {'CAC':>8} {'CPC':>7}")
print("-" * 78)
for _, row in g_campaign.iterrows():
    flag = "  🔴 LOSING MONEY" if row['ROAS'] < 1.0 else ("  🟡 MARGINAL" if row['ROAS'] < 1.5 else "  🟢")
    print(f"{row['campaign']:<26} ${row['total_spend']:>9,.0f} ${row['total_revenue']:>9,.0f} "
          f"{row['ROAS']:>6.2f}x {row['CVR']:>6.2f}% ${row['CAC']:>7.2f} ${row['CPC']:>6.2f}{flag}")


# ── STEP 3: GOOGLE ADS — PRE vs POST REDESIGN ───────────────
# WHAT: Split performance into two periods and compare
# WHY: We know the redesign happened in late March.
#      We want to quantify exactly how much damage it caused
#      per campaign — not just overall.
#      This gives us a specific number to put in the deck:
#      "The redesign cost us X dollars in lost revenue."

print("\n\nGOOGLE ADS — PRE vs POST REDESIGN COMPARISON")
print("-" * 65)

g_period = google_df.groupby(['campaign', 'period']).agg(
    spend       = ('spend', 'sum'),
    revenue     = ('revenue', 'sum'),
    conversions = ('conversions', 'sum'),
    clicks      = ('clicks', 'sum'),
).reset_index()

g_period['ROAS'] = (g_period['revenue'] / g_period['spend']).round(2)
g_period['CVR']  = (g_period['conversions'] / g_period['clicks'] * 100).round(2)

# Pivot so Pre and Post are side by side
g_pivot = g_period.pivot_table(
    index='campaign',
    columns='period',
    values=['ROAS', 'CVR', 'revenue'],
    aggfunc='mean'
).round(2)

print("\nROAS by Campaign — Before vs After Redesign:")
print(f"\n{'Campaign':<26} {'Pre-Redesign ROAS':>20} {'Post-Redesign ROAS':>20} {'Change':>10}")
print("-" * 78)

pre_col  = 'Pre-Redesign (Jan-Mar)'
post_col = 'Post-Redesign (Apr-Jun)'

for camp in g_campaign['campaign']:
    try:
        pre  = g_pivot['ROAS'][pre_col][camp]
        post = g_pivot['ROAS'][post_col][camp]
        change = ((post - pre) / pre * 100)
        flag = "  ⬇ " + f"{abs(change):.0f}% decline"
        print(f"{camp:<26} {pre:>19.2f}x {post:>19.2f}x {flag}")
    except:
        pass

# Calculate total revenue lost due to redesign
pre_rev  = google_df[google_df['period'] == pre_col]['revenue'].sum()
post_rev = google_df[google_df['period'] == post_col]['revenue'].sum()
pre_spend  = google_df[google_df['period'] == pre_col]['spend'].sum()
post_spend = google_df[google_df['period'] == post_col]['spend'].sum()

# If post-period had maintained pre-period ROAS, what would revenue have been?
pre_roas = pre_rev / pre_spend
expected_post_rev = post_spend * pre_roas
actual_post_rev   = post_rev
revenue_lost      = expected_post_rev - actual_post_rev

print(f"\n{'─'*65}")
print(f"  Pre-redesign avg ROAS:    {pre_roas:.2f}x")
print(f"  Post-redesign avg ROAS:   {post_rev/post_spend:.2f}x")
print(f"  Expected revenue (at old ROAS): ${expected_post_rev:,.0f}")
print(f"  Actual revenue:                 ${actual_post_rev:,.0f}")
print(f"  ⚠️  Estimated revenue lost to redesign: ${revenue_lost:,.0f}")
print(f"{'─'*65}")
print(f"  This is the number that goes on the client deck.")


# ── STEP 4: META ADS — CAMPAIGN BREAKDOWN ───────────────────
# WHAT: Same drill-down as Google but for Meta campaigns
# WHY: We know Meta overall has 2.59x ROAS.
#      But is that driven by one great campaign or all of them?
#      If it is one campaign, the recommendation changes —
#      we want to scale THAT campaign, not Meta broadly.

print("\n\n" + "=" * 65)
print("META ADS — CAMPAIGN LEVEL BREAKDOWN")
print("=" * 65)

m_campaign = meta_df.groupby('campaign').agg(
    total_spend   = ('spend', 'sum'),
    total_revenue = ('revenue', 'sum'),
    total_clicks  = ('clicks', 'sum'),
    total_conv    = ('conversions', 'sum'),
    total_impr    = ('Impressions', 'sum'),
).reset_index()

m_campaign['ROAS'] = (m_campaign['total_revenue'] / m_campaign['total_spend']).round(2)
m_campaign['CVR']  = (m_campaign['total_conv'] / m_campaign['total_clicks'] * 100).round(2)
m_campaign['CPC']  = (m_campaign['total_spend'] / m_campaign['total_clicks']).round(2)
m_campaign['CAC']  = (m_campaign['total_spend'] / m_campaign['total_conv'].replace(0,1)).round(2)
m_campaign['CPM']  = (m_campaign['total_spend'] / m_campaign['total_impr'] * 1000).round(2)

m_campaign = m_campaign.sort_values('ROAS', ascending=False)

print(f"\n{'Campaign':<28} {'Spend':>10} {'Revenue':>10} {'ROAS':>7} {'CVR%':>7} {'CAC':>8} {'CPM':>7}")
print("-" * 80)
for _, row in m_campaign.iterrows():
    flag = "  🟢 SCALE THIS" if row['ROAS'] > 3.0 else ("  🟡 MONITOR" if row['ROAS'] > 1.5 else "  🔴 REVIEW")
    print(f"{row['campaign']:<28} ${row['total_spend']:>9,.0f} ${row['total_revenue']:>9,.0f} "
          f"{row['ROAS']:>6.2f}x {row['CVR']:>6.2f}% ${row['CAC']:>7.2f} ${row['CPM']:>6.2f}{flag}")


# ── STEP 5: EMAIL — CAMPAIGN TYPE BREAKDOWN ─────────────────
# WHAT: Group email by campaign type and compare performance
# WHY: Email overall is the best channel at 6.57x ROAS.
#      But not all email types are equal.
#      Abandoned cart emails behave completely differently
#      from newsletters. We need to show WHICH email types
#      are driving the performance and recommend scaling those.

print("\n\n" + "=" * 65)
print("EMAIL MARKETING — CAMPAIGN TYPE BREAKDOWN")
print("=" * 65)

e_type = email_df.groupby('campaign_type').agg(
    campaigns     = ('campaign_type', 'count'),
    total_spend   = ('spend', 'sum'),
    total_revenue = ('revenue', 'sum'),
    total_conv    = ('conversions', 'sum'),
    avg_open_rate = ('opens', 'sum'),
    total_sends   = ('list_size', 'sum'),
    total_clicks  = ('clicks', 'sum'),
).reset_index()

e_type['ROAS']      = (e_type['total_revenue'] / e_type['total_spend']).round(2)
e_type['CAC']       = (e_type['total_spend'] / e_type['total_conv'].replace(0,1)).round(2)
e_type['open_rate'] = (e_type['avg_open_rate'] / e_type['total_sends'] * 100).round(1)
e_type['CTR']       = (e_type['total_clicks'] / e_type['avg_open_rate'] * 100).round(1)
e_type['CVR']       = (e_type['total_conv'] / e_type['total_clicks'].replace(0,1) * 100).round(1)

e_type = e_type.sort_values('ROAS', ascending=False)

print(f"\n{'Type':<20} {'Campaigns':>10} {'Spend':>8} {'Revenue':>10} {'ROAS':>7} {'Open%':>7} {'CVR%':>7}")
print("-" * 72)
for _, row in e_type.iterrows():
    flag = "  ⭐ TOP" if row['ROAS'] > 15 else ""
    print(f"{row['campaign_type']:<20} {row['campaigns']:>10} ${row['total_spend']:>7,.0f} "
          f"${row['total_revenue']:>9,.0f} {row['ROAS']:>6.2f}x {row['open_rate']:>6.1f}% "
          f"{row['CVR']:>6.1f}%{flag}")


# ── STEP 6: FINAL CROSS-CHANNEL COMPARISON ──────────────────
# WHAT: One unified table comparing all channels side by side
# WHY: This is Slide 3 of the deck — the channel scorecard.
#      Stakeholders want to see all channels on one page
#      so they can make budget decisions instantly.
#      Your job is to make that comparison as clear as possible.

print("\n\n" + "=" * 65)
print("CROSS-CHANNEL SCORECARD — 6 Month Summary")
print("=" * 65)

g_tot = {'spend': google_df['spend'].sum(), 'revenue': google_df['revenue'].sum(),
         'conv': google_df['conversions'].sum(), 'clicks': google_df['clicks'].sum()}
m_tot = {'spend': meta_df['spend'].sum(), 'revenue': meta_df['revenue'].sum(),
         'conv': meta_df['conversions'].sum(), 'clicks': meta_df['clicks'].sum()}
e_tot = {'spend': email_df['spend'].sum(), 'revenue': email_df['revenue'].sum(),
         'conv': email_df['conversions'].sum(), 'clicks': email_df['clicks'].sum()}

summary = {
    'Google Ads': g_tot,
    'Meta Ads':   m_tot,
    'Email':      e_tot,
}

print(f"\n{'Channel':<14} {'Spend':>10} {'Revenue':>10} {'ROAS':>7} {'CAC':>8} {'Conv':>8}  Verdict")
print("-" * 75)
verdicts = {
    'Google Ads': '🔴 Underperforming — fix landing page',
    'Meta Ads':   '🟡 Solid — scale selectively',
    'Email':      '🟢 Best ROI — invest more',
}
for ch, d in summary.items():
    roas = d['revenue'] / d['spend']
    cac  = d['spend'] / max(d['conv'], 1)
    print(f"{ch:<14} ${d['spend']:>9,.0f} ${d['revenue']:>9,.0f} {roas:>6.2f}x "
          f"${cac:>7.2f} {d['conv']:>8,}  {verdicts[ch]}")

total_spend = sum(d['spend'] for d in summary.values())
total_rev   = sum(d['revenue'] for d in summary.values())
print("-" * 75)
print(f"{'TOTAL':<14} ${total_spend:>9,.0f} ${total_rev:>9,.0f} {total_rev/total_spend:>6.2f}x")


# ── STEP 7: GENERATE PHASE 2 CHARTS ─────────────────────────
# WHAT: 4 charts for the client deck
# WHY: Every finding needs a visual. Charts go into PowerPoint.
#      Raw numbers in a table are hard to digest for a CMO.
#      A bar chart makes the story obvious in 3 seconds.

print("\n\n📊 Generating Phase 2 charts...")

fig, axes = plt.subplots(2, 2, figsize=(15, 11))
fig.suptitle('NovaPulse — Channel Deep Dive Analysis', fontsize=16, fontweight='bold')

colors_map = {
    'Brand_Search': '#3b82f6',
    'Competitor_Targeting': '#f59e0b',
    'Generic_Supplements': '#ef4444',
    'Retargeting_30d': '#10b981',
    'Prospecting_Broad': '#6366f1',
    'Lookalike_Purchasers': '#f59e0b',
    'Retargeting_IG': '#10b981',
    'UGC_Creative_Test': '#ec4899',
}

# Chart 1: Google Ads ROAS by Campaign
ax1 = axes[0, 0]
camp_colors = [('#10b981' if r >= 1.5 else '#ef4444') for r in g_campaign['ROAS']]
bars = ax1.barh(g_campaign['campaign'], g_campaign['ROAS'], color=camp_colors)
ax1.axvline(x=1.0, color='red', linestyle='--', alpha=0.7, label='Break-even (1.0x)')
ax1.axvline(x=2.5, color='green', linestyle='--', alpha=0.5, label='Target (2.5x)')
ax1.set_title('Google Ads ROAS by Campaign', fontweight='bold')
ax1.set_xlabel('ROAS (x)')
ax1.legend(fontsize=8)
for bar, val in zip(bars, g_campaign['ROAS']):
    ax1.text(val + 0.02, bar.get_y() + bar.get_height()/2,
             f'{val:.2f}x', va='center', fontsize=9)

# Chart 2: Meta Ads ROAS by Campaign
ax2 = axes[0, 1]
meta_colors = [('#10b981' if r >= 3.0 else '#f59e0b' if r >= 1.5 else '#ef4444')
               for r in m_campaign['ROAS']]
bars2 = ax2.barh(m_campaign['campaign'], m_campaign['ROAS'], color=meta_colors)
ax2.axvline(x=2.5, color='green', linestyle='--', alpha=0.5, label='Target (2.5x)')
ax2.set_title('Meta Ads ROAS by Campaign', fontweight='bold')
ax2.set_xlabel('ROAS (x)')
ax2.legend(fontsize=8)
for bar, val in zip(bars2, m_campaign['ROAS']):
    ax2.text(val + 0.02, bar.get_y() + bar.get_height()/2,
             f'{val:.2f}x', va='center', fontsize=9)

# Chart 3: Email ROAS by Campaign Type
ax3 = axes[1, 0]
email_colors = ['#10b981' if r > 10 else '#3b82f6' if r > 5 else '#f59e0b'
                for r in e_type['ROAS']]
bars3 = ax3.bar(e_type['campaign_type'], e_type['ROAS'], color=email_colors)
ax3.set_title('Email ROAS by Campaign Type', fontweight='bold')
ax3.set_ylabel('ROAS (x)')
plt.setp(ax3.xaxis.get_majorticklabels(), rotation=20, ha='right', fontsize=8)
for bar, val in zip(bars3, e_type['ROAS']):
    ax3.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 0.2,
             f'{val:.1f}x', ha='center', fontsize=9, fontweight='bold')

# Chart 4: Channel Comparison — Spend vs Revenue bubble-style
ax4 = axes[1, 1]
channels    = ['Google Ads', 'Meta Ads', 'Email']
spends      = [g_tot['spend']/1000, m_tot['spend']/1000, e_tot['spend']/1000]
revenues    = [g_tot['revenue']/1000, m_tot['revenue']/1000, e_tot['revenue']/1000]
ch_colors   = ['#ef4444', '#f59e0b', '#10b981']
x = np.arange(len(channels))
w = 0.35
b1 = ax4.bar(x - w/2, spends, w, label='Spend ($K)', color='#6366f1', alpha=0.85)
b2 = ax4.bar(x + w/2, revenues, w, label='Revenue ($K)', color='#10b981', alpha=0.85)
ax4.set_title('Spend vs Revenue by Channel ($K)', fontweight='bold')
ax4.set_ylabel('Amount ($000s)')
ax4.set_xticks(x)
ax4.set_xticklabels(channels)
ax4.legend()
roas_vals = [g_tot['revenue']/g_tot['spend'], m_tot['revenue']/m_tot['spend'],
             e_tot['revenue']/e_tot['spend']]
for i, (bar, roas) in enumerate(zip(b2, roas_vals)):
    ax4.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 2,
             f'{roas:.1f}x', ha='center', fontsize=10, fontweight='bold',
             color='#065f46')

plt.tight_layout()
plt.savefig('/home/claude/novapulse_phase2_charts.png', dpi=150, bbox_inches='tight')
plt.close()
print("  ✅ Charts saved: novapulse_phase2_charts.png")


# ── STEP 8: THE MANAGER UPDATE ───────────────────────────────
# This is what you send your manager in Slack after Phase 2.
# Same format as Phase 1 — clear, structured, no fluff.

print("\n\n" + "=" * 65)
print("📧 PHASE 2 UPDATE — Ready to send to manager")
print("=" * 65)

rev_lost = revenue_lost

print(f"""
TO: [Manager]
FROM: Jay
RE: NovaPulse Phase 2 — Channel Deep Dive Complete

Hi [Manager],

Phase 2 done. Three main findings:

FINDING 1 — GOOGLE ADS: TWO CAMPAIGNS ARE LOSING MONEY
────────────────────────────────────────────────────────
Competitor_Targeting and Generic_Supplements are both below
1.0x ROAS — meaning we are spending more than we are making back.
Brand_Search and Retargeting_30d are still healthy.
The redesign hit all campaigns but hit Generic_Supplements hardest.
Estimated revenue lost since redesign: ${rev_lost:,.0f}

FINDING 2 — META ADS: ONE CAMPAIGN IS CARRYING THE CHANNEL
────────────────────────────────────────────────────────────
Retargeting_IG is the standout performer with the highest ROAS
and lowest CAC. Lookalike_Purchasers is also solid.
Prospecting_Broad has the highest spend but weakest returns.
Recommendation: shift budget from Prospecting toward Retargeting_IG.

FINDING 3 — EMAIL: ABANDONED CART IS THE HIDDEN GOLDMINE
──────────────────────────────────────────────────────────
Abandoned cart campaigns have by far the highest ROAS and CVR
of any email type. They are also the highest open rate.
NovaPulse is sending abandoned cart campaigns but not enough of them.
This is the single highest-ROI action they can take immediately.

NEXT STEP
──────────
Ready to build the recommendations and CMO deck.
I'll structure it as: Root Cause → Channel Scorecard →
3 Recommendations → 90-Day Roadmap.

— Jay
""")

print("✅ Phase 2 complete.")
print("   Files ready:")
print("   • novapulse_phase2_charts.png")
print("   • This script (documents all analysis steps)")
