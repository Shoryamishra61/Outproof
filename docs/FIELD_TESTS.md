# Three real outings — preparation only

Results: NOT TESTED. Do not fill this form from synthetic fixtures or provider
ETAs. Do not perform an outing until the factual compiler gate is met.

Copy `field-test-form.json` separately for A, B and C:

| Test | Scenario to record later | Result |
|---|---|---|
| A | Solo, confirmed free, INR0, 45–75 minutes | blank |
| B | Friend, INR250–500/person, 60–120 minutes, food + talk | blank |
| C | Date/group, dietary + exclusion hard requirements | blank |

Before starting, record structured constraints and the actual compiled proof.
Start a physical stopwatch and record planning start, GO, actual outdoors start,
and return/finish as ISO timestamps with offsets. Record predicted supported
cost range/confidence, actual receipts/tickets/minimum spends (integer minor
units), scope and party size. Compare money only in matching currency/scope;
do not substitute a price level for a numeric prediction. Record real dwell,
travel and walking distance; leave unavailable measurements null.

Measure active Ground Rule screen time during planning and separately while
outside using device screen-time records plus a stopwatch/video log if needed.
Do not count the entire time the application is running in the background.
Record external navigation use separately in notes. Log closed venues, price
surprises, missed deadlines, inaccessible entrances and crowds honestly.
Do not claim route, accessibility, allergy or hygiene guarantees.

```powershell
uv run python scripts/field_metrics.py path/to/actual-outing.json
```

The script refuses blank, naive, out-of-order or impossible measurements.
`planning_to_go_seconds` measures planning latency. `time_to_grass_seconds`
measures planning start to the recorded physical outdoor start, separately.
`screen_ratio_percent` is active Ground Rule screen seconds while outside /
actual outside elapsed seconds × 100. Report both timestamps/definitions with
results; never call API latency a field Time To Grass measurement.

Keep records locally. No precise location timeline or raw private prompts are
required, and this script makes no network calls. Redact receipts/private notes
before choosing to publish evidence. Report all three outcomes, including
failures; publish no table of actual results before measurements exist.
