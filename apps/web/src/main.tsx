import { useEffect, useRef, useState, type FormEvent } from 'react';
import { createRoot } from 'react-dom/client';
import Ajv from 'ajv/dist/2020';
import addFormats from 'ajv-formats';
import compiledSchema from '../../../contracts/compiled-plan.schema.json';
import failureSchema from '../../../contracts/compilation-failure.schema.json';
import type { CompiledPlan, CompilationFailure, ConstraintSet, Evidence, Money } from '../../../contracts/domain';
import './style.css';

const ajv = new Ajv({ strict: false });
addFormats(ajv);
const isCompiled = ajv.compile<CompiledPlan>(compiledSchema);
const isFailure = ajv.compile<CompilationFailure>(failureSchema);
const fixtureMode = import.meta.env.DEV && import.meta.env.VITE_GROUND_RULE_FIXTURE_MODE === 'true';
const liveMode = import.meta.env.VITE_GROUND_RULE_LIVE_MODE === 'true';
const apiBase = (import.meta.env.VITE_API_BASE_URL ?? '').replace(/\/$/, '');
const isEnabled = fixtureMode || liveMode;
const voiceEnabled = import.meta.env.VITE_GROUND_RULE_VOICE_ENABLED === 'true';
const checkCodes = ['BUDGET', 'CURRENCY', 'DURATION', 'ROUTING', 'RETURN_TRIP', 'OPENING_HOURS', 'WALKING', 'EXCLUSIONS', 'DIETARY', 'GROUNDING', 'PRICE_CONFIDENCE'];
const ageHours: Record<string, number> = { identity: 720, coordinates: 720, categories: 168, excluded_categories: 168, dietary_options: 168, price: 24, opening_window: 24, walking_route: 0.25 };
function money(value: Money | null) {
  if (!value) return 'Unknown';
  return new Intl.NumberFormat('en-IN', { style: 'currency', currency: value.currency_code }).format(value.minor_units / (value.currency_code === 'JPY' ? 1 : 100));
}
function sourceState(source: Evidence) {
  const elapsed = (Date.now() - Date.parse(source.observed_at)) / 3600000;
  if (elapsed < 0) return 'Future observation';
  if ((source.expires_at && Date.now() >= Date.parse(source.expires_at)) || elapsed >= (ageHours[source.field] ?? Infinity)) return 'Stale — revalidation required';
  return 'Observation retained';
}
function acceptedPlan(value: unknown, controls: ConstraintSet): value is CompiledPlan {
  if (!isCompiled(value) || value.status !== 'SUCCESS') return false;
  const { plan, proof } = value;
  const sources = new Set(proof.sources.map(e => e.evidence_id));
  const codes = new Set<string>(proof.validation.checks.map(c => c.code));
  if (!proof.validation.accepted || proof.validation.plan_id !== plan.plan_id) return false;
  if (plan.origin.latitude !== controls.origin?.latitude || plan.origin.longitude !== controls.origin?.longitude || Date.parse(plan.departure_at) !== Date.parse(controls.departure_at ?? '')) return false;
  if (proof.total_duration_seconds > controls.duration_max_minutes * 60 || !proof.cost.upper || !['VERIFIED', 'BOUNDED'].includes(proof.cost.confidence)) return false;
  const limit = (controls.budget_minor_units ?? 0) * (controls.budget_scope === 'PER_PERSON' ? controls.party_size ?? 1 : 1);
  if (proof.cost.upper.currency_code !== controls.currency_code || proof.cost.upper.minor_units > limit) return false;
  const endpoints = ['origin', ...plan.stops.map(s => s.place.place_id), 'origin'];
  if (plan.routes.length !== endpoints.length - 1 || !plan.routes.every((r, i) => r.from_id === endpoints[i] && r.to_id === endpoints[i + 1])) return false;
  if (sources.size !== proof.sources.length || !checkCodes.every(c => codes.has(c))) return false;
  if (!proof.validation.checks.every(c => c.hard && c.status === 'PASS' && c.evidence_ids.every(id => sources.has(id)))) return false;
  if (!plan.routes.every(r => r.reachable && r.duration_seconds !== null && r.distance_meters !== null)) return false;
  if (plan.routes.reduce((n, r) => n + (r.duration_seconds ?? 0), 0) + plan.stops.reduce((n, s) => n + s.dwell_seconds, 0) !== proof.total_duration_seconds) return false;
  if (plan.routes.reduce((n, r) => n + (r.distance_meters ?? 0), 0) !== proof.walking_distance_meters) return false;
  if (controls.max_walking_minutes !== null && controls.max_walking_minutes !== undefined && plan.routes.reduce((n,r) => n+(r.duration_seconds ?? 0),0) > controls.max_walking_minutes*60) return false;
  if (value.mode === 'FIXTURE') {
    return proof.sources.every(e => e.source === 'FIXTURE');
  }
  if (value.mode === 'LIVE') {
    return proof.sources.every(e => ['OSM', 'DIRECT', 'VALHALLA', 'SERPAPI'].includes(e.source));
  }
  return false;
}

function canStart(value: CompiledPlan): boolean {
  if (value.mode === 'FIXTURE') return true;
  const now = Date.now();
  if (now < Date.parse(value.compiled_at) || now - Date.parse(value.compiled_at) > 60000) return false;
  if (!value.proof.sources.every(s => sourceState(s) === 'Observation retained')) return false;
  let arrival = now;
  for (const [i, stop] of value.plan.stops.entries()) {
    arrival += (value.plan.routes[i].duration_seconds ?? 0) * 1000;
    const departure = arrival + stop.dwell_seconds * 1000;
    if (!stop.place.opening_windows?.some(w => Date.parse(w.opens_at) <= arrival && Date.parse(w.closes_at) >= departure)) return false;
    arrival = departure;
  }
  return true;
}

function App() {
  const [state, setState] = useState<'home' | 'compiling' | 'result' | 'go'>('home');
  const [connection, setConnection] = useState<'checking' | 'ready' | 'unavailable'>('checking');
  const [attempt, setAttempt] = useState(0);
  const [duration, setDuration] = useState(90);
  const [budget, setBudget] = useState(liveMode ? 0 : 500);
  const [currency, setCurrency] = useState<NonNullable<ConstraintSet['currency_code']>>(liveMode ? 'SGD' : 'INR');
  const [scope, setScope] = useState<'PER_PERSON' | 'TOTAL'>(liveMode ? 'TOTAL' : 'PER_PERSON');
  const [party, setParty] = useState<ConstraintSet['party_mode']>(liveMode ? 'SOLO' : 'FRIEND');
  const [size, setSize] = useState(4);
  const [vibe, setVibe] = useState<ConstraintSet['vibes'][number]>(liveMode ? 'Explore' : 'Talk');
  const [veg, setVeg] = useState(!liveMode);
  const [mall, setMall] = useState(!liveMode);
  const [quiet, setQuiet] = useState(true);
  const [walking, setWalking] = useState(liveMode ? 60 : 30);
  const [originMode, setOriginMode] = useState<'demo' | 'device' | 'manual'>('demo');
  const [latitude, setLatitude] = useState(1.3068);
  const [longitude, setLongitude] = useState(103.819);
  const [deviceCoords, setDeviceCoords] = useState<{ latitude: number; longitude: number } | null>(null);
  const [isLocating, setIsLocating] = useState(false);
  const [text, setText] = useState('');
  const [error, setError] = useState('');
  const [result, setResult] = useState<CompiledPlan | null>(null);
  const [sent, setSent] = useState<ConstraintSet | null>(null);
  const [step, setStep] = useState(0);
  const [audioError, setAudioError] = useState(false);
  const heading = useRef<HTMLHeadingElement>(null);
  const pending = useRef<AbortController | null>(null);
  const locationRequest = useRef(0);
  useEffect(() => {
    const controller = new AbortController();
    const timeout = window.setTimeout(() => controller.abort(), 60000);
    setConnection('checking');
    fetch(`${apiBase}/v1/health/ready`, { signal: controller.signal }).then(async response => {
      const value: unknown = await response.json();
      if (!response.ok || !value || typeof value !== 'object' || !('compilation_available' in value) || value.compilation_available !== true) throw new Error('Compilation unavailable');
      setConnection('ready');
    }).catch(() => setConnection('unavailable')).finally(() => window.clearTimeout(timeout));
    return () => { window.clearTimeout(timeout); controller.abort(); };
  }, [attempt]);
  useEffect(() => { heading.current?.focus(); }, [state, step]);
  useEffect(() => () => pending.current?.abort(), []);
  async function compile(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (pending.current || isLocating || (originMode === 'device' && !deviceCoords)) return;
    const isLive = liveMode;
    const origin = originMode === 'manual' ? { latitude, longitude } : originMode === 'device' && deviceCoords
      ? deviceCoords
      : isLive
      ? { latitude: 1.3068, longitude: 103.819 }
      : { latitude: 13.0418, longitude: 80.2341 };
    const controls: ConstraintSet = {
      currency_code: currency, budget_minor_units: Math.round(budget * (currency === 'JPY' ? 1 : 100)), budget_scope: scope,
      duration_max_minutes: duration, party_mode: party, party_size: party === 'SOLO' ? 1 : party === 'GROUP' ? size : 2, vibes: [vibe],
      hard_constraints: [...(veg ? [{ kind: 'DIETARY' as const, value: 'vegetarian' }] : []), ...(mall ? [{ kind: 'EXCLUDE_CATEGORY' as const, value: 'mall' }] : [])],
      soft_constraints: quiet ? [{ preference: 'quiet' }] : [], max_walking_minutes: walking,
      max_walking_meters: null, return_by_local: null, locale: 'en-IN',
      origin, departure_at: new Date().toISOString(), strict_budget: true,
    };
    setSent(controls); setError(''); setResult(null); setStep(0); setState('compiling');
    const controller = new AbortController(); pending.current = controller;
    const timeout = window.setTimeout(() => controller.abort(), 185000);
    try {
      const mode = isLive ? 'LIVE' : 'FIXTURE';
      const response = await fetch(`${apiBase}/v1/plans/compile`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, signal: controller.signal, body: JSON.stringify({ mode, controls, free_text: text }) });
      const body: unknown = await response.json();
      if (pending.current !== controller) return;
      if (!response.ok || !acceptedPlan(body, controls)) {
        const failureMessage = isFailure(body)
          ? body.message
          : 'The response could not be verified. No plan displayed.';
        const contextHelp = originMode === 'device'
          ? `${failureMessage} Reviewed live evidence currently covers only the Singapore Botanic Gardens Tanglin entrance corridor.`
          : failureMessage;
        throw new Error(contextHelp);
      }
      setResult(body); setState('result');
    } catch (cause) {
      if (pending.current !== controller) return;
      setError(controller.signal.aborted ? 'Compilation stopped. Your controls are retained.' : cause instanceof Error ? cause.message : 'Compilation unavailable.');
      setState('home');
    } finally { window.clearTimeout(timeout); if (pending.current === controller) pending.current = null; }
  }
  const isResultLive = result?.mode === 'LIVE';
  const navPoints = result ? [result.plan.origin, ...result.plan.stops.map(s => s.place.coordinates), result.plan.origin] : [];
  const navFrom = navPoints[Math.floor(step/2)];
  const navTo = navPoints[Math.floor(step/2)+1];
  const actions = result ? result.plan.routes.flatMap((route, index) => [
    { destination: index < result.plan.stops.length ? result.plan.stops[index].place.name ?? 'Destination' : 'Origin', action: `Walk ${Math.ceil((route.duration_seconds ?? 0) / 60)} minutes.` },
    ...(index < result.plan.stops.length ? [{ destination: result.plan.stops[index].place.name ?? 'Destination', action: `Spend ${result.plan.stops[index].dwell_seconds / 60} minutes here.` }] : []),
  ]) : [];
  return <main>
    <p className="eyebrow">Ground Rule / {isResultLive ? 'LIVE' : liveMode ? 'LIVE' : fixtureMode ? 'FIXTURE DEMO' : 'live compiler unavailable'}</p>
    {!isResultLive && fixtureMode && <p className="notice">Fictional places, prices and routes. Practice only.</p>}
    {isResultLive && <p className="notice">Verified live places, operating hours and pedestrian routes.</p>}
    {state === 'home' && <>
      <h1 ref={heading} tabIndex={-1}>Set your limits.<br />Leave the deciding here.</h1><p className="intro">One plan, checked against every hard rule.</p>
      {liveMode && <p className="notice">Reviewed live coverage: Singapore Botanic Gardens, Tanglin entrance. Main grounds only, 05:00–00:00 Singapore time. Other places may return no verified plan. Your location goes to map and routing providers; it is not saved as outing history.</p>}
      {!isEnabled ? <section><h2>Live evidence gate</h2><p>Real outing compilation is unavailable while required evidence is incomplete.</p></section> :
      <form onSubmit={compile} aria-label="Outing controls">
        <fieldset className="origin-choice">
          <legend>Starting location</legend>
          <label className="check">
            <input
              type="radio"
              name="origin-mode"
              id="origin-demo"
              checked={originMode === 'demo'}
              onChange={() => { locationRequest.current++; setIsLocating(false); setOriginMode('demo'); setError(''); }}
            />
            {liveMode ? 'Use the Singapore example start (1.3068, 103.819)' : 'Fixture Chennai example (T. Nagar: 13.0418, 80.2341)'}
          </label>
          <label className="check">
            <input
              type="radio"
              name="origin-mode"
              id="origin-device"
              checked={originMode === 'device'}
              onChange={() => {
                setOriginMode('device');
                setError('');
                const requestId = ++locationRequest.current;
                if (!('geolocation' in navigator)) { setError('Geolocation unavailable. Choose an example or enter coordinates.'); return; }
                if (!deviceCoords && 'geolocation' in navigator) {
                  setIsLocating(true);
                  navigator.geolocation.getCurrentPosition(
                    pos => {
                      if (locationRequest.current !== requestId) return;
                      setDeviceCoords({ latitude: Number(pos.coords.latitude.toFixed(6)), longitude: Number(pos.coords.longitude.toFixed(6)) });
                      setIsLocating(false);
                    },
                    err => {
                      if (locationRequest.current !== requestId) return;
                      setIsLocating(false);
                      setError(`Location access unavailable (${err.message}). Choose an example or enter coordinates.`);
                    },
                    { timeout: 8000 }
                  );
                }
              }}
            />
            {isLocating ? 'Detecting your device location…' : deviceCoords ? `Device location (${deviceCoords.latitude}, ${deviceCoords.longitude})` : 'Use my current location (GPS)'}
          </label>
          <label className="check"><input type="radio" name="origin-mode" checked={originMode === 'manual'} onChange={() => { locationRequest.current++; setIsLocating(false); setOriginMode('manual'); setError(''); }} />Enter coordinates</label>
          {originMode === 'manual' && <div className="controls"><label>Latitude<input type="number" required min="-90" max="90" step="any" value={latitude} onChange={e => setLatitude(e.target.valueAsNumber)} /></label><label>Longitude<input type="number" required min="-180" max="180" step="any" value={longitude} onChange={e => setLongitude(e.target.valueAsNumber)} /></label></div>}
        </fieldset>
        <div className="controls">
          <label>Time incl. return (min)<input id="duration" type="number" min="15" max="480" step="1" required value={duration} onChange={e => setDuration(e.target.valueAsNumber)} /></label>
          <label>Budget in {currency}<input id="budget" type="number" min="0" max="100000" step="1" required value={budget} onChange={e => setBudget(e.target.valueAsNumber)} /></label>
          <label>Currency<select value={currency} onChange={e => setCurrency(e.target.value as typeof currency)}>{['INR', 'USD', 'GBP', 'SGD', 'JPY', 'EUR', 'AUD', 'CAD', 'AED'].map(c => <option key={c}>{c}</option>)}</select></label>
          <label>Budget scope<select value={scope} onChange={e => setScope(e.target.value as typeof scope)}><option value="PER_PERSON">Per person</option><option value="TOTAL">Whole group</option></select></label>
          <label>Going with<select value={party} onChange={e => setParty(e.target.value as typeof party)}><option value="SOLO">Just me</option><option value="FRIEND">A friend</option><option value="DATE">A date</option><option value="GROUP">A group</option></select></label>
          {party === 'GROUP' && <label>People<input id="party-size" type="number" min="2" max="10" step="1" required value={size} onChange={e => setSize(e.target.valueAsNumber)} /></label>}
          <label>Vibe<select value={vibe} onChange={e => setVibe(e.target.value as typeof vibe)}>{['Food', 'Talk', 'Explore', 'Chill', 'Move', 'Surprise'].map(v => <option key={v}>{v}</option>)}</select></label>
          <label>Walking, all legs (min)<input id="walking" type="number" min="0" max="240" step="1" required value={walking} onChange={e => setWalking(e.target.valueAsNumber)} /></label>
        </div>
        <fieldset><legend>Hard rules</legend><label className="check"><input id="vegetarian" type="checkbox" checked={veg} onChange={e => setVeg(e.target.checked)} />Vegetarian required</label><label className="check"><input id="no-mall" type="checkbox" checked={mall} onChange={e => setMall(e.target.checked)} />No mall</label></fieldset>
        <label className="check"><input id="quiet" type="checkbox" checked={quiet} onChange={e => setQuiet(e.target.checked)} />Prefer somewhere quiet</label>
        <details className="extras"><summary>Add a rule or preference</summary><label>Anything else? <span>Optional · parsed by Gemma</span><textarea maxLength={4000} rows={2} value={text} onChange={e => setText(e.target.value)} /></label></details>
        {error && <p role="alert" className="status">{error}</p>}
        <button type="submit" disabled={connection !== 'ready' || isLocating || (originMode === 'device' && !deviceCoords)}>{liveMode ? 'Compile one live plan' : 'Compile one fixture plan'}</button>
      </form>}
      <p role="status" className="connection">{connection === 'checking' ? 'Checking API…' : connection === 'ready' ? (liveMode ? 'API connected · live mode ready' : 'API connected · live compilation disabled') : 'API unavailable'}</p>
      {connection === 'unavailable' && <button type="button" onClick={() => setAttempt(attempt + 1)}>Check connection</button>}
    </>}
    {state === 'compiling' && <section aria-busy="true"><h1 ref={heading} tabIndex={-1}>Checking one outing.</h1><p role="status">Grounding sources, checking hard rules, then selecting a valid plan with Gemma.</p><button type="button" onClick={() => { pending.current?.abort(); pending.current = null; setError('Compilation stopped. Your controls are retained.'); setState('home'); }}>Cancel</button></section>}
    {state === 'result' && result && sent && <section>
      <h1 ref={heading} tabIndex={-1}>{isResultLive ? 'One verified plan.' : 'One fixture plan.'}</h1>
      <dl className="totals"><div><dt>Total time</dt><dd>{Math.ceil(result.proof.total_duration_seconds / 60)} min</dd><small>including return</small></div><div><dt>Mandatory cost · {result.proof.cost.confidence}</dt><dd>{money(result.proof.cost.upper)}</dd><small>whole party · cap {money({ currency_code: sent.currency_code ?? currency, minor_units: (sent.budget_minor_units ?? 0) * (sent.budget_scope === 'PER_PERSON' ? sent.party_size ?? 1 : 1) })}</small></div></dl>
      {result.plan.stops.flatMap(s => s.place.evidence.filter(e => e.field === 'visit_scope')).map(e => <p className="notice" key={e.evidence_id}>{String(e.value)}</p>)}
      <ol className="sequence">{actions.map((action, index) => <li key={index}><strong>{action.destination}</strong><span>{action.action}</span></li>)}</ol>
      <button type="button" onClick={() => { if (!canStart(result)) { setError('Plan evidence or departure window needs a fresh check. Compile again before leaving.'); setState('home'); } else setState('go'); }}>{isResultLive ? 'GO' : 'GO · practice'}</button>
      <details className="proof"><summary>Plan Proof · {result.proof.validation.checks.length} hard checks passed</summary>
        <p>Budget: {money(result.proof.cost.upper)} total. Time: {result.proof.total_duration_seconds / 60} min, including return. Walking: {result.proof.walking_distance_meters} m.</p>
        <ul>{result.proof.validation.checks.map(check => <li key={check.code}><strong>{check.status} {check.code}</strong><p>{check.message}</p><small>Evidence: {check.evidence_ids.join(', ') || 'No source needed for absent constraint'}</small></li>)}</ul>
        <h2>Source observations · {result.mode}</h2><ul>{result.proof.sources.map(source => <li key={source.evidence_id}><strong>{source.evidence_id}</strong><br /><small>{source.source_ref.startsWith('https://') ? <a href={source.source_ref} target="_blank" rel="noreferrer">Source</a> : source.source_ref}<br />Observed {source.observed_at}<br />{sourceState(source)}{source.expires_at && ` · expires ${source.expires_at}`}</small></li>)}</ul>
      </details>
      <button className="secondary" type="button" onClick={() => setState('home')}>Edit constraints</button>
    </section>}
    {state === 'go' && result && <section className="go">
      <p className="eyebrow">{isResultLive ? 'NEXT' : 'NEXT · FIXTURE PRACTICE'}</p><h1 ref={heading} tabIndex={-1}>{actions[step]?.action ?? (isResultLive ? 'Outing complete.' : 'Practice complete.')}</h1>
      <p>{actions[step]?.destination ?? 'Return sequence completed.'}</p><p className="intro">Phone down.</p>
      {voiceEnabled && step === 0 && <div><p>Optional spoken GO cue · <a href="https://elevenlabs.io" target="_blank" rel="noreferrer">elevenlabs.io</a> · noncommercial demo</p><audio controls preload="none" src="/go-cue.mp3" aria-label="Optional spoken GO cue" onError={() => setAudioError(true)} />{audioError && <p role="status">Voice unavailable. The instruction above remains usable.</p>}</div>}
      {isResultLive && step % 2 === 0 && navFrom && navTo && <a target="_blank" rel="noreferrer" href={`https://www.openstreetmap.org/directions?engine=fossgis_valhalla_foot&route=${navFrom.latitude}%2C${navFrom.longitude}%3B${navTo.latitude}%2C${navTo.longitude}`}>Open walking map</a>}
      {!isResultLive && <p className="notice">Destinations are fictional. This is a GO-mode practice.</p>}
      {step < actions.length - 1 && <button type="button" onClick={() => setStep(step + 1)}>{isResultLive ? 'Next step' : 'Next practice step'}</button>}
      <button className="secondary" type="button" onClick={() => setState('result')}>Back to plan</button>
    </section>}
    <footer>LLMs interpret. Data grounds. Code verifies.</footer>
  </main>;
}
createRoot(document.getElementById('root')!).render(<App />);

if (import.meta.env.PROD && 'serviceWorker' in navigator) navigator.serviceWorker.register('/sw.js').catch(() => console.warn('Shell service worker unavailable'));
