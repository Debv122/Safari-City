## Safari City — Early Player Segmentation (One‑Pager)

### Goal
Identify actionable early‑session segments to personalize difficulty, tips, and offers within Day 0–1.

### Minimal Features (from Task 1 events)

- Progress: `max_level_d0`, `episode1_complete`, `tasks_completed`, `time_to_first_key_s`
- Difficulty: `win_rate_L1_3`, `avg_attempts_L1_3`, `fail_streak_max`
- Economy: `keys_earned`, `key_spend_latency_s`, `booster_use_rate`
- Engagement: `session_length_s`, `continue_accept_rate` (ads/gems), `notification_opt_in`

### Simple Rule‑Based Segments (clear, early, actionable)

1) Beginners (learning the loop)
   - Rules: `tutorial_complete=1`, `avg_attempts_L1_3 ≤ 2.5`, `booster_use_rate=0`, `time_to_first_key_s ≤ 300`
   - Actions: short inline tips; pulsing key target; highlight “Quick Renovation” after L2.

2) Stuck/At‑Risk
   - Rules: `fail_streak_max ≥ 3` OR `key_spend_latency_s > 60` OR `continue_choice=end` on first modal
   - Actions: ad‑continue first; free booster after 2nd fail; guided camera to spend key; soften next board.

3) Fast/Momentum Players
   - Rules: `avg_level_duration_s` in bottom quartile AND `avg_attempts_L1_3 ≤ 2` AND `key_spend_latency_s ≤ 20`
   - Actions: streak bonuses, skip animations toggle, offer “Quick Build” bundle after milestone.

4) Booster‑Reliant Optimizers
   - Rules: `booster_use_rate ≥ 0.4` in L1–L5 OR `continue_accept_rate(ad|gems) ≥ 0.5`
   - Actions: show value packs; pre‑level hints; ensure levels remain fair without pay.

5) Decorators/Completion‑Focused
   - Proxy Rules: `tasks_completed` high vs `max_level_d0` (many spends), frequent `renovation_applied` events
   - Actions: theme sets, before/after comparisons, visible collection progress.

### Segmentation Map (visual)

```
                Motivation: Challenge ↑
                         ┌───────────────────────────────┐
                         │  Puzzle Masters / Fast        │
                         │  (low fails, quick loops)     │
                         └───────────────▲───────────────┘
                                         │
           Autonomy/Skill ↓              │              ↑ Autonomy/Skill ↑
                                         │
                         ┌───────────────▼───────────────┐
                         │   Beginners                    │
                         │   (learning the loop)          │
                         └───────────────▲───────────────┘
                                         │
                                         │
                         ┌───────────────▼───────────────┐
                         │  Stuck / At‑Risk               │
                         │  (fails, key‑spend friction)   │
                         └───────────────────────────────┘

            Parallel overlay across axes: Booster‑Reliant Optimizers; Decorators/Completion‑Focused
```

### Rationale (why these segments)

- They are detectable in session 1 from a handful of robust signals (wins/fails, key spend latency, booster use), enabling immediate personalization.
- They reflect distinct motivations: learning progress (Beginners), mastery/pace (Fast), relief/unblock (Stuck), optimization/power (Booster‑Reliant), and expression/collection (Decorators).
- They map directly to tunable levers the game already surfaces in your screenshots: boosters, continue modals, difficulty, renovation cadence, and offers.

### Product Use (examples per segment)

- Beginners: tooltips, clearer key spend CTA, gentler L2–L3, celebratory feedback after first renovation.
- Stuck/At‑Risk: ad‑continue default, free helper on 2nd fail, guaranteed favorable board next level, camera pan to task.
- Fast/Momentum: skip animations, streak rewards, optional challenge nodes, condensed task chains.
- Booster‑Reliant: tutorialize efficient booster use, balanced boards still winnable booster‑free, value packs post‑milestone.
- Decorators: unlock early theme sets, before/after comparisons, collection progress and share prompts.

### Marketing Use (UA/CRM)

- Messaging: “Finish your first room fast” (Beginners), “Beat tougher puzzles” (Fast), “Free boost to finish your build” (Stuck), “Optimize your build” (Booster‑Reliant), visual style showcases (Decorators).
- Channels/Creatives: Rewarded‑ad oriented retargeting for Stuck; ROAS/value creatives for Booster‑Reliant; visual UGC prompts for Decorators.
- Lifecycle: D1 notification copy varies by segment; offer timing aligned to milestone completions for Fast/Booster‑Reliant.

### KPIs by Segment (compare deltas)

- D1 retention, sessions_D0, ad engagement rate, ARPPU/ARPDAU, time_to_milestone_1

### Lightweight Scoring (optional)

If rules overlap, assign the highest‑priority label by this order:
Stuck/At‑Risk → Beginners → Fast/Momentum → Booster‑Reliant → Decorators.

### How to Use

- Target onboarding: show different helper copy per segment.
- Tune early difficulty: DDA for Stuck; optional challenges for Fast.
- Personalize monetization: rewarded ads first for Beginners/Stuck; bundles for Booster‑Reliant.


