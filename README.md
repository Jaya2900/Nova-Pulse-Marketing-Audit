# NovaPulse Marketing Analytics Audit

## Business Problem
NovaPulse, a DTC fitness supplements brand spending $120K/month 
on paid media, experienced a revenue plateau despite flat ad spend 
over 6 months. Goal was to identify root cause and recommend 
budget reallocation.

## Tools Used
Python (Pandas, Matplotlib) | Excel | PowerPoint

## Process
- Phase 1: Data audit across 4 sources — Google Ads, Meta Ads, 
  GA4 Website, Email Marketing
- Phase 2: Channel-level KPI deep dive and campaign breakdown
- Phase 3: Executive presentation with recommendations

## Key Findings
1. Landing page redesign in March caused Google Ads CVR to drop 
   from 5.0% to 2.7% — estimated $71,816 in lost revenue
2. Meta Ads budget misallocated — Retargeting_IG delivers 8.47x 
   ROAS at $7.75 CAC vs Prospecting_Broad at 1.26x ROAS
3. Email severely underinvested — 6.57x blended ROAS on $8K spend 
   vs Google Ads 1.26x on $230K

## Recommendations
1. A/B test original vs redesigned landing page immediately
2. Shift 35% of Prospecting_Broad budget to Retargeting_IG
3. Automate abandoned cart email sequence (25.78x ROAS)

## Files
- NovaPulse_Data_Audit.xlsx — Pre-analysis data audit framework
- novapulse_analysis.py — Phase 1 data cleaning and audit
- novapulse_phase2.py — Phase 2 channel deep dive
- NovaPulse_CMO_Deck.pptx — Executive presentation
