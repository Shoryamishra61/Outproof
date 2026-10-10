# Product Specification

## Product

**Outproof**

Tagline: **One outing. Every limit checked.**

## Problem

People often want to leave home but fail to convert intention into an outing because of combined friction:

- cost uncertainty
- decision paralysis
- limited time
- travel effort
- incompatible preferences
- dietary/access constraints
- unreliable venue information
- endless browsing

Outproof reduces decisions rather than increasing recommendations.

## Job to be done

> When I want to do something outside but have constraints, compile one feasible local plan so I can stop researching and leave.

## Positioning

Global product.

India-first:
- field tests
- tuning
- demo
- article story

## Core session

### Required input

- origin/current area
- duration
- maximum spend
- party mode
- vibe

### Optional input

- natural-language hard rule
- walking tolerance
- dietary needs
- exclusions
- return deadline

### Output

Exactly one:
- route/sequence
- predicted duration
- supported cost range or free plan
- why it fits
- constraint proof
- source transparency

### After GO

Reduce UI to:
- next step
- optional navigation handoff
- backup only if primary invalidates

## UX principles

1. One-screen input.
2. No chat-first UI.
3. One default plan.
4. No discovery feed.
5. No review-reading workflow.
6. Unknown remains unknown.
7. Strict mode favors no answer over false confidence.
8. The product becomes less visible after success.

## Vibes

- Food
- Talk
- Explore
- Chill
- Move
- Surprise

Soft unless explicitly hard.

## Budget

Internally use:
- ISO `currency_code`
- integer minor units or Decimal
- `budget_scope`: total/per-person

### Proof levels

**VERIFIED**  
Direct price/menu evidence supports the bound.

**BOUNDED**  
Trusted range/price level supports a conservative bound.

**ESTIMATED**  
Weak/derived evidence only.

**UNKNOWN**  
No defensible price evidence.

Strict mode paid stops:
- allow VERIFIED
- allow BOUNDED
- reject ESTIMATED
- reject UNKNOWN

## Honest failure

### No verified paid plan

> I couldn't verify a paid stop under your limit. I can compile a free outing instead.

### No valid plan

> I couldn't verify an outing satisfying all hard constraints in this area right now.

Hard constraints are never silently relaxed.

## Metrics

### Product
- Time To Grass
- Screen Ratio
- plan acceptance
- completion
- reroll rate

### Engineering
- parser accuracy
- hard-constraint compliance
- grounding precision
- route feasibility
- price proof correctness
- source freshness
- latency

## Non-goals

Ground Rule does not:
- promise safety
- provide medical advice
- assess hygiene
- estimate calories
- optimize dating outcomes
- become a restaurant review app
- become a social network
