## Safari City — Early Player Journey Funnel (One‑Pager)

### Visual Funnel

```
Install
  ↓
First Open
  ↓
Title Screen → Play Tap
  ↓
Tutorial Start ──▶ Tutorial Complete
  ↓
Level 1 Start ──▶ Level 1 Win (First Key Earned)
  ↓
Spend First Key ──▶ First Renovation Applied
  ↓
Levels 2–3 Loop ──▶ First Room Milestone
  ↓
Episode 1 Complete ──▶ Next Goal Set / Notif Opt‑in

Friction Modals (can appear in loop):
• Out of Moves (Continue via Ad/Gems or End)
• Out of Keys (Prompt to Play Levels)
• "Don’t Give Up" Encouragement (Continue or End)
```

### Minimal Events

`app_open(first_open)` · `title_play_tap` · `tutorial_start` · `tutorial_step_complete(step_id)` · `tutorial_complete` · `level_start(level_id)` · `level_end(level_id,outcome,duration_s,attempt_num)` · `booster_panel_view(level_id)` · `booster_use(level_id,type)` · `key_earned(level_id)` · `key_spend(task_id)` · `renovation_applied(task_id)` · `continue_offer_shown(level_id,reason)` · `continue_choice(option)` · `out_of_keys_shown` · `out_of_keys_play_tap` · `encouragement_shown(type=dont_give_up)` · `encouragement_choice(continue/end)` · `milestone_reached(milestone_id)` · `episode_complete(episode_id)` · `next_task_set(task_id)` · `notification_opt_in(status)`

### KPI Snapshot (targets in parentheses)

| Stage/Metric | Definition | Target |
|---|---|---|
| Tutorial completion % | `tutorial_complete / tutorial_start` | ≥ 85% |
| Time to first key | First open → `key_earned(level=1)` | ≤ 5 min |
| Key spend conversion | `key_spend` within 1 min of `key_earned` | ≥ 95% |
| Early win rates | L1/L2/L3 `win%` | ≥90/≥85/≥80% |
| D0 Episode‑1 completion | `episode_complete(1)` on Day 0 | 35–55% |

### Noted Risks from Playthrough → Quick Fixes

- Perceived delay awarding keys → ensure `level_end→key_earned` feedback < 2s and animate key counter immediately.
- Out of Moves/“Don’t Give Up” → favor ad‑continue in early levels; cap pay prompts pre‑Episode‑1.
- Out of Keys modal → one‑tap route back to next beatable level; track bounce.
- Fast early pace → add periodic “big reveal” renovations to sustain excitement.

### Observations During Early Gameplay → Retention Impact

- Title screen with a big Play CTA is clear
  - Impact: Smooth first click helps Open→Play conversion. Keep load time short so players don’t stall here.

- Boosters are surfaced pre‑level (blender, gems, bomb, generator)
  - Impact: Good for teaching power early; however, if boosters feel required before L3, non‑spenders may churn. Track win rate without boosters and tune early boards to be beatable booster‑free.

- “Out of Keys” modal appears between build steps
  - Impact: Reinforces core loop (beat levels → earn keys). Ensure the Play CTA returns to the next beatable level in one tap; extra friction risks session drop.

- Loading tip shows how to create bombs
  - Impact: Smart passive onboarding; keep these contextually relevant to the next mechanic to lift L2–L3 win rates.

- “Out of Moves” + “Don’t Give Up” prompt with options (Ad +5, Gems +5, or End)
  - Impact: Powerful save‑from‑frustration. Early on, bias toward ad‑continue visibility over paid gems to avoid rage‑quit; gradually increase monetization after Episode 1.

- Perceived delay before key is granted after a win
  - Impact: Breaks the earn→reward association and can reduce satisfaction. Add instant key pop + counter increment; defer any server sync to background.

- Fast early progression (you finished many levels and two episodes quickly)
  - Impact: Momentum builds habit and D0 completion, but if every payoff is small, novelty decays. Insert periodic “big reveal” renovations and short narrative beats to anchor memory and D1 return.

- Visual clarity of where to spend a key after earning it
  - Impact: If players can’t find the task within ~60s, they feel blocked. Use guided camera pan and a pulsing key slot to drive spend‑conversion.

- Monetization touchpoints exist but aren’t overwhelming early
  - Impact: Positive for trust. Keep pre‑Episode‑1 IAP prompts light; rely on rewarded ads at “Out of Moves” to preserve goodwill and session length.



