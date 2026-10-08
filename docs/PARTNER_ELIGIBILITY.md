# Partner evidence ledger

Executed use and contest eligibility are different. Only the judge determines eligibility. No installation, key presence, HTTP 200 or unused credits is counted as working integration. All new cash spending is zero.

| Category | Executed capability / evidence | Claim status |
|---|---|---|
| Render | Two free public services; actual LIVE browser compile/proof/GO; CI-gated deployment and recovery receipts | VERIFIED deployment; availability limited by free/laptop runtime |
| Gemma | Actual Gemma 4 E2B local/remote parser and valid-plan ranker; digest and inference receipts | VERIFIED open-weight use |
| Sentry Agent Tracing | Actual production HTTP, grounding/validation and Gemma ranking spans queried; allowlisted technical tracing and privacy tests | VERIFIED technical agent spans; no raw prompt tracing |
| SerpApi | Real authorized official-link search and compiler provenance; snippets never determine facts | VERIFIED source discovery |
| ElevenLabs | Real free-quota cue generation and decoded public-browser playback; opt-in and noncommercial attribution | VERIFIED generic voice cue |
| GitHub Copilot | Actual read-only parser/ranker review; found dietary-negation issue and informed tested fix | VERIFIED development use; [sanitized session](agent-sessions/copilot-parser-review.md) |
| Entire | Actual Copilot session manually attached after noninteractive hooks failed; local review checkpoint `01M4EMKW8WXK8RP292FZAPWJ6Z` | VERIFIED manual session capture; automatic capture not claimed |
| DigitalOcean | No authorized account/runtime or spend cap | BLOCKED / not claimed |
| Backboard | Four chat attempts returned HTTP 200 with FAILED status; free credits restricted to Memory/RAG; no completed remote inference or charge | BLOCKED / not claimed |
| MongoDB Atlas | No demonstrated persistent-cache requirement or live Atlas operations | NOT QUALIFIED / not added |
| Temporal | No durable-job requirement or resume experiment | NOT QUALIFIED / not added |
| Mastra | No demonstrated benefit over existing bounded Python flow | NOT QUALIFIED / not added |
| Prior Labs / TabPFN | No historical availability dataset/entitlement or held-out study | BLOCKED / not claimed |
| Thinking Machines / Tinker | No approved training access/budget or real training experiment | BLOCKED / not claimed |
| Tiger Data | No corpus/retrieval scale justifying a second store or measured live retrieval | NOT QUALIFIED / not added |
| Qualcomm / Arduino UNO Q | User confirmed no physical board; no hardware execution | BLOCKED / not claimed |

Copilot CLI 1.0.94 used the existing authenticated entitlement with no paid overages. Entire CLI 0.11.4 was verified from the official Windows release/checksum and enabled only in a clean public-source clone. Its automatic hooks did not capture the noninteractive review; supported `session attach --agent copilot-cli --review --force` captured the genuine exported session instead. The root project commit history was not amended. Installation alone is not the evidence.

Backboard's comparison used four synthetic sentences and four real local Gemma calls; only two local semantic outputs matched the oracle, and malformed/conflicting outputs failed closed. Four Backboard attempts did not run inference. Its diagnostic message explicitly required paid credits/subscription, which were not authorized. See `release-backboard-comparison.json`; do not describe it as a successful model comparison.

Evidence receipts are in `evals/reports/release-*.json` and `artifacts/release/public-corrected`. Published model/source/audio licenses remain separate from the repository MIT license; see `NOTICE`. No partner is allowed to weaken the acceptance boundary.
