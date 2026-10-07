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
function acceptedFixture(value: unknown): value is CompiledPlan {
  if (!isCompiled(value) || value.mode !== 'FIXTURE' || value.status !== 'SUCCESS') return false;
  const { plan, proof } = value;
  const sources = new Set(proof.sources.map(e => e.evidence_id));
  const codes = new Set<string>(proof.validation.checks.map(c => c.code));
  return proof.validation.accepted && proof.validation.plan_id === plan.plan_id &&
    proof.sources.every(e => e.source === 'FIXTURE') && sources.size === proof.sources.length &&
    checkCodes.every(c => codes.has(c)) &&
    proof.validation.checks.every(c => c.hard && c.status === 'PASS' && c.evidence_ids.every(id => sources.has(id))) &&
    plan.routes.every(r => r.reachable && r.duration_seconds !== null && r.distance_meters !== null) &&
    plan.routes.reduce((n, r) => n + (r.duration_seconds ?? 0), 0) + plan.stops.reduce((n, s) => n + s.dwell_seconds, 0) === proof.total_duration_seconds &&
    plan.routes.reduce((n, r) => n + (r.distance_meters ?? 0), 0) === proof.walking_distance_meters;
}

function App() {
  const [state, setState] = useState<'home' | 'compiling' | 'result' | 'go'>('home');
  const [connection, setConnection] = useState<'checking' | 'ready' | 'unavailable'>('checking');
  const [attempt, setAttempt] = useState(0);
  const [duration, setDuration] = useState(90);
  const [budget, setBudget] = useState(500);
  const [scope, setScope] = useState<'PER_PERSON' | 'TOTAL'>('PER_PERSON');
  const [party, setParty] = useState<ConstraintSet['party_mode']>('FRIEND');
  const [size, setSize] = useState(4);
  const [vibe, setVibe] = useState<ConstraintSet['vibes'][number]>('Talk');
  const [veg, setVeg] = useState(true);
  const [mall, setMall] = useState(true);
  const [quiet, setQuiet] = useState(true);
  const [walking, setWalking] = useState(30);
  const [text, setText] = useState('');
  const [error, setError] = useState('');
  const [result, setResult] = useState<CompiledPlan | null>(null);
  const [sent, setSent] = useState<ConstraintSet | null>(null);
  const [step, setStep] = useState(0);
  const heading = useRef<HTMLHeadingElement>(null);
  const pending = useRef<AbortController | null>(null);
  useEffect(() => {
    const controller = new AbortController();
    const timeout = window.setTimeout(() => controller.abort(), 5000);
    setConnection('checking');
    fetch('/v1/health', { signal: controller.signal }).then(async response => {
      const value: unknown = await response.json();
      if (!response.ok || !value || typeof value !== 'object' || !('status' in value) || value.status !== 'ok') throw new Error('Health unavailable');
      setConnection('ready');
    }).catch(() => setConnection('unavailable')).finally(() => window.clearTimeout(timeout));
    return () => { window.clearTimeout(timeout); controller.abort(); };
  }, [attempt]);
  useEffect(() => { heading.current?.focus(); }, [state, step]);
  useEffect(() => () => pending.current?.abort(), []);
  async function compile(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const controls: ConstraintSet = {
      currency_code: 'INR', budget_minor_units: Math.round(budget * 100), budget_scope: scope,
      duration_max_minutes: duration, party_mode: party, party_size: party === 'SOLO' ? 1 : party === 'GROUP' ? size : 2, vibes: [vibe],
      hard_constraints: [...(veg ? [{ kind: 'DIETARY' as const, value: 'vegetarian' }] : []), ...(mall ? [{ kind: 'EXCLUDE_CATEGORY' as const, value: 'mall' }] : [])],
      soft_constraints: quiet ? [{ preference: 'quiet' }] : [], max_walking_minutes: walking,
      max_walking_meters: null, return_by_local: null, locale: 'en-IN',
      origin: { latitude: 13.0418, longitude: 80.2341 }, departure_at: new Date().toISOString(), strict_budget: true,
    };
    setSent(controls); setError(''); setResult(null); setStep(0); setState('compiling');
    const controller = new AbortController(); pending.current = controller;
    const timeout = window.setTimeout(() => controller.abort(), 185000);
    try {
      const response = await fetch('/v1/plans/compile', { method: 'POST', headers: { 'Content-Type': 'application/json' }, signal: controller.signal, body: JSON.stringify({ mode: 'FIXTURE', controls, free_text: text }) });
      const body: unknown = await response.json();
      if (!response.ok || !acceptedFixture(body)) throw new Error(isFailure(body) ? body.message : 'The response could not be verified. No plan displayed.');
      setResult(body); setState('result');
    } catch (cause) {
      setError(controller.signal.aborted ? 'Compilation stopped. Your controls are retained.' : cause instanceof Error ? cause.message : 'Compilation unavailable.');
      setState('home');
    } finally { window.clearTimeout(timeout); pending.current = null; }
  }
  const actions = result ? result.plan.routes.flatMap((route, index) => [
    { destination: index < result.plan.stops.length ? result.plan.stops[index].place.name ?? 'Fixture destination' : 'Fixture origin', action: `Walk ${Math.ceil((route.duration_seconds ?? 0) / 60)} minutes.` },
    ...(index < result.plan.stops.length ? [{ destination: result.plan.stops[index].place.name ?? 'Fixture destination', action: `Spend ${result.plan.stops[index].dwell_seconds / 60} minutes here.` }] : []),
  ]) : [];
  return <main>
    <p className="eyebrow">Ground Rule / {fixtureMode ? 'FIXTURE DEMO' : 'live compiler unavailable'}</p>
    {fixtureMode && <p className="notice">Fictional places, prices and routes. Practice only.</p>}
    {state === 'home' && <>
      <h1 ref={heading} tabIndex={-1}>Set your limits.<br />Leave the deciding here.</h1><p className="intro">One plan, checked against every hard rule.</p>
      {!fixtureMode ? <section><h2>Live evidence gate</h2><p>Real outing compilation is unavailable while required evidence is incomplete.</p></section> :
      <form onSubmit={compile} aria-label="Outing controls">
        <div className="controls">
          <label>Time incl. return (min)<input id="duration" type="number" min="15" max="480" step="1" required value={duration} onChange={e => setDuration(e.target.valueAsNumber)} /></label>
          <label>Budget in INR<input id="budget" type="number" min="0" max="100000" step="1" required value={budget} onChange={e => setBudget(e.target.valueAsNumber)} /></label>
          <label>Budget scope<select value={scope} onChange={e => setScope(e.target.value as typeof scope)}><option value="PER_PERSON">Per person</option><option value="TOTAL">Whole group</option></select></label>
          <label>Going with<select value={party} onChange={e => setParty(e.target.value as typeof party)}><option value="SOLO">Just me</option><option value="FRIEND">A friend</option><option value="DATE">A date</option><option value="GROUP">A group</option></select></label>
          {party === 'GROUP' && <label>People<input id="party-size" type="number" min="2" max="10" step="1" required value={size} onChange={e => setSize(e.target.valueAsNumber)} /></label>}
          <label>Vibe<select value={vibe} onChange={e => setVibe(e.target.value as typeof vibe)}>{['Food', 'Talk', 'Explore', 'Chill', 'Move', 'Surprise'].map(v => <option key={v}>{v}</option>)}</select></label>
          <label>Walking, all legs (min)<input id="walking" type="number" min="0" max="240" step="1" required value={walking} onChange={e => setWalking(e.target.valueAsNumber)} /></label>
        </div>
        <p className="area"><strong>Fixture area</strong> Chennai · T. Nagar<br /><span>Origin: 13.0418, 80.2341 · depart when you compile.</span></p>
        <fieldset><legend>Hard rules</legend><label className="check"><input id="vegetarian" type="checkbox" checked={veg} onChange={e => setVeg(e.target.checked)} />Vegetarian required</label><label className="check"><input id="no-mall" type="checkbox" checked={mall} onChange={e => setMall(e.target.checked)} />No mall</label></fieldset>
        <label className="check"><input id="quiet" type="checkbox" checked={quiet} onChange={e => setQuiet(e.target.checked)} />Prefer somewhere quiet</label>
        <details className="extras"><summary>Add a rule or preference</summary><label>Anything else? <span>Optional · parsed locally by Gemma</span><textarea maxLength={4000} rows={2} value={text} onChange={e => setText(e.target.value)} /></label></details>
        {error && <p role="alert" className="status">{error}</p>}
        <button type="submit" disabled={connection !== 'ready'}>Compile one fixture plan</button>
      </form>}
      <p role="status" className="connection">{connection === 'checking' ? 'Checking API…' : connection === 'ready' ? 'API connected · live compilation disabled' : 'API unavailable'}</p>
      {connection === 'unavailable' && <button type="button" onClick={() => setAttempt(attempt + 1)}>Check connection</button>}
    </>}
    {state === 'compiling' && <section aria-busy="true"><h1 ref={heading} tabIndex={-1}>Checking one outing.</h1><p role="status">Grounding fixture facts, checking hard rules, then selecting a valid plan with local Gemma.</p><button type="button" onClick={() => pending.current?.abort()}>Cancel</button></section>}
    {state === 'result' && result && sent && <section>
      <h1 ref={heading} tabIndex={-1}>One fixture plan.</h1>
      <dl className="totals"><div><dt>Total time</dt><dd>{result.proof.total_duration_seconds / 60} min</dd><small>including return</small></div><div><dt>Mandatory cost · {result.proof.cost.confidence}</dt><dd>{money(result.proof.cost.upper)}</dd><small>whole party · cap {money({ currency_code: 'INR', minor_units: (sent.budget_minor_units ?? 0) * (sent.budget_scope === 'PER_PERSON' ? sent.party_size ?? 1 : 1) })}</small></div></dl>
      <ol className="sequence">{actions.map((action, index) => <li key={index}><strong>{action.destination}</strong><span>{action.action}</span></li>)}</ol>
      <button type="button" onClick={() => setState('go')}>GO · practice</button>
      <details className="proof"><summary>Plan Proof · {result.proof.validation.checks.length} hard checks passed</summary>
        <p>Budget: {money(result.proof.cost.upper)} total. Time: {result.proof.total_duration_seconds / 60} min, including return. Walking: {result.proof.walking_distance_meters} m.</p>
        <ul>{result.proof.validation.checks.map(check => <li key={check.code}><strong>{check.status} {check.code}</strong><p>{check.message}</p><small>Evidence: {check.evidence_ids.join(', ') || 'No source needed for absent constraint'}</small></li>)}</ul>
        <h2>Source observations · FIXTURE</h2><ul>{result.proof.sources.map(source => <li key={source.evidence_id}><strong>{source.evidence_id}</strong><br /><small>{source.source_ref}<br />Observed {source.observed_at}<br />{sourceState(source)}{source.expires_at && ` · expires ${source.expires_at}`}</small></li>)}</ul>
      </details>
      <button className="secondary" type="button" onClick={() => setState('home')}>Edit constraints</button>
    </section>}
    {state === 'go' && result && <section className="go">
      <p className="eyebrow">NEXT · FIXTURE PRACTICE</p><h1 ref={heading} tabIndex={-1}>{actions[step]?.action ?? 'Practice complete.'}</h1>
      <p>{actions[step]?.destination ?? 'Return sequence completed.'}</p><p className="intro">Phone down.</p>
      <p className="notice">Destinations are fictional. This is a GO-mode practice.</p>
      {step < actions.length - 1 && <button type="button" onClick={() => setStep(step + 1)}>Next practice step</button>}
      <button className="secondary" type="button" onClick={() => setState('result')}>Back to plan</button>
    </section>}
    <footer>LLMs interpret. Data grounds. Code verifies.</footer>
  </main>;
}
createRoot(document.getElementById('root')!).render(<App />);
if (import.meta.env.PROD && 'serviceWorker' in navigator) navigator.serviceWorker.register('/sw.js').catch(() => console.warn('Shell service worker unavailable'));
