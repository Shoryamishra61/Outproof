import type { CompiledPlan, Evidence } from '../../../contracts/domain';

const ageHours: Record<string, number> = { identity: 720, coordinates: 720, categories: 168, excluded_categories: 168, dietary_options: 168, price: 24, opening_window: 24, walking_route: 0.25 };
export function sourceState(source: Evidence, now = Date.now()) {
  const elapsed = (now - Date.parse(source.observed_at)) / 3600000;
  if (elapsed < 0) return 'Future observation';
  if ((source.expires_at && now >= Date.parse(source.expires_at)) || elapsed >= (ageHours[source.field] ?? Infinity)) return 'Stale — revalidation required';
  return 'Observation retained';
}

export function canStart(value: CompiledPlan, now = Date.now()): boolean {
  if (value.mode === 'FIXTURE') return true;
  if (now < Date.parse(value.compiled_at) || now - Date.parse(value.compiled_at) > 60000) return false;
  if (!value.proof.sources.every(s => sourceState(s, now) === 'Observation retained')) return false;
  if (value.return_by_local && now + value.proof.total_duration_seconds * 1000 > Date.parse(value.return_by_local)) return false;
  let arrival = now;
  for (const [i, stop] of value.plan.stops.entries()) {
    arrival += (value.plan.routes[i].duration_seconds ?? 0) * 1000;
    const departure = arrival + stop.dwell_seconds * 1000;
    if (!stop.place.opening_windows?.some(w => Date.parse(w.opens_at) <= arrival && Date.parse(w.closes_at) >= departure)) return false;
    arrival = departure;
  }
  return true;
}


export function responseTime(serverTime: string | null, compiledAt: string, requestElapsedMs: number): number | null {
  const server = Date.parse(serverTime ?? '');
  const compiled = Date.parse(compiledAt);
  if (!Number.isFinite(server) || !Number.isFinite(compiled) || server < compiled || !Number.isFinite(requestElapsedMs) || requestElapsedMs < 0 || requestElapsedMs > 185000) return null;
  // Include the whole request as a conservative network-delay bound; freshness limits stay unchanged.
  return server + requestElapsedMs;
}
