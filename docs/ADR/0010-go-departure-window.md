# Preserve source-backed hours and return deadline for GO

The compiler previously derived an opening window equal to the requested visit interval. Any model latency then shifted a real GO visit beyond that artificial end. The hours adapter now finds the next continuous closure on UTC minute boundaries, bounded to 24 additional hours and source expiry. It retains original provenance and does not bridge lunch closures, holidays or DST gaps.

GO also needs the effective dated return deadline after parser additions. `CompiledPlan.return_by_local` is an optional, timezone-aware field, defaulting to null for old snapshots. Compilation copies the actual control; the domain rejects a deadline preceding the complete round trip. The frontend checks the deadline against the proposed current departure before entering GO. Schema and TypeScript are exported from the domain source.

This does not update or refresh source evidence. Stale observations and expired departure windows still require a new compilation.
