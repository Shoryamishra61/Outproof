# Preserved Phase 3 parser failures and pilots

These are exploratory local `gemma3:1b` CPU calls, separate from each 100-case
benchmark. Observations below record visible results, not reconstructed full
responses. They are not pooled into a benchmark score.

- Initial schema-array smoke: `veg, no mall, somewhere quiet` gained an unrequested
  allergy-safety hard constraint. JSON validation alone did not detect the error.
- Compact array prompt, three calls: quiet, no malls, and vegan food still gained
  unrelated mall/diet/preferences. The prompt change did not qualify the parser.
- Small three-boolean schema, four calls: quiet and vegetarian presence were
  identified, but `No malls please` emitted exclude_mall=false. `Malls are fine`
  also emitted false, appropriately. This was not a complete parser benchmark.
- Full boolean schema pilot: `Somewhere quiet` omitted quiet; the second call,
  `No malls please`, asserted conflicting vegetarian and vegan. Decoding stopped
  that three-sentence pilot after two calls.
- Boolean schema with an explicit empty template, three calls: quiet, no malls,
  and vegan food all returned false for every semantic slot. Template copying
  replaced interpretation. The boolean implementation was removed after failure.
- Loose JSON mode, three calls: responses had extra fields, duplicate preferences
  keys, diet of the wrong type, and incomplete structure. This path was rejected.

The first complete benchmark is preserved in `parser-gemma3-1b-run-1.json`:
97/100 schema-valid, 0/100 exact hard/soft matches, 5/8 merged unsupported
retentions. No authoritative control corruption, no place fields or extra fields.
This is a failed semantic experiment, not a Phase 3 PASS.

Five offline regressions first failed before correction: two dropped clock-only
deadlines and three numbers bound to the wrong control. They passed after adding
deadline retention and explicit field/unit binding. Later tests also reject
missing explicit hard constraints, vegan weakening, and invented allergy safety.

An initial Gemma 3 4B pull was stopped when download reported ~716 KB/s and an
hour-plus estimate while free physical RAM was ~0.6 GiB. The user's subsequent
request to retry after freeing RAM showed ~5.2 GiB free. The pull was resumed.
Partial downloads remain intact; a downloaded model is not a benchmark result.


Further Gemma 4 E2B QAT diagnostic runs (not pooled into the 100-case scores):

- System-role-only revision, five real calls: only optional coffee was an exact
  semantic match. Chain exclusion and the combined exclusions failed; no malls
  gained unrequested quiet/low-walking preferences. Preserved full requests and
  responses: `parser-gemma4-system-role-pilot.json`.
- Thinking=true with 1024 prediction tokens, three real calls: chain exclusion
  still failed, vegetarian/no alcohol gained an unwanted uncrowded preference,
  and optional coffee truncated its JSON. Latencies were 38,642, 39,769 and
  52,231 ms. Preserved `parser-gemma4-thinking-pilot.json`; not promoted.
- Schema supplied in prompt as well as format, five real calls: four exact
  semantic matches (chains, vegetarian/no alcohol, optional coffee, no malls).
  The budget-range sentence still gained an unwanted short-outing preference.
  Preserved `parser-gemma4-schema-prompt-pilot.json`. This diagnosis justified
  one small request change and separate complete reruns for both larger models;
  the five-case pilot is not a release score.

The eight final merge regressions first failed (8 failed / 48 passed), then
passed after shared guards retained combined exclusions, explicit dated
requirements and the complete unsupported source sentence, including timeout
failures. The final schema-in-prompt regression passed with the 57 parser tests.
