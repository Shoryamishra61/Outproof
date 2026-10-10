import { useEffect, useRef, useState } from 'react';
import type { Map as LeafletMap, Marker } from 'leaflet';
import 'leaflet/dist/leaflet.css';

export type StartingPoint = { latitude: number; longitude: number; label: string };

function validPoint(value: unknown): value is { label: string; coordinates: { latitude: number; longitude: number } } {
  if (!value || typeof value !== 'object' || !('label' in value) || typeof value.label !== 'string' || !value.label.trim() || value.label.length > 280 || !('coordinates' in value)) return false;
  const p = value.coordinates;
  return !!p && typeof p === 'object' && 'latitude' in p && 'longitude' in p && typeof p.latitude === 'number' && typeof p.longitude === 'number' && Number.isFinite(p.latitude) && Number.isFinite(p.longitude) && Math.abs(p.latitude) <= 90 && Math.abs(p.longitude) <= 180;
}

export function LocationPicker({ apiBase, point, onChange }: { apiBase: string; point: StartingPoint | null; onChange: (point: StartingPoint | null) => void }) {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<StartingPoint[]>([]);
  const [searchState, setSearchState] = useState<'idle' | 'loading' | 'empty' | 'error' | 'results'>('idle');
  const [message, setMessage] = useState('');
  const [showMap, setShowMap] = useState(false);
  const [mapReady, setMapReady] = useState(false);
  const [mapError, setMapError] = useState('');
  const container = useRef<HTMLDivElement>(null);
  const mapToggle = useRef<HTMLButtonElement>(null);
  const map = useRef<LeafletMap | null>(null);
  const marker = useRef<Marker | null>(null);
  const search = useRef<AbortController | null>(null);
  const change = useRef(onChange);
  change.current = onChange;
  const currentPoint = useRef(point);
  currentPoint.current = point;

  useEffect(() => () => search.current?.abort(), []);
  useEffect(() => { if (point) setShowMap(true); }, [point]);
  useEffect(() => {
    if (!showMap || !container.current) return;
    setMapReady(false); setMapError('');
    let disposed = false;
    let resize: ResizeObserver | undefined;
    import('leaflet').then(L => {
      if (disposed || !container.current) return;
      const p = currentPoint.current;
      const instance = L.map(container.current, { keyboard: false, scrollWheelZoom: false, zoomAnimation: false, fadeAnimation: false, markerZoomAnimation: false });
      map.current = instance;
      instance.setView(p ? [p.latitude, p.longitude] : [20, 0], p ? 15 : 2);
      L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', { maxZoom: 19, referrerPolicy: 'strict-origin-when-cross-origin', attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors' })
        .on('tileerror', () => setMapError('Map imagery could not load. Place search and the selected starting point still work.'))
        .addTo(instance);
      const pin = L.marker(p ? [p.latitude, p.longitude] : instance.getCenter(), { draggable: true, keyboard: true, title: 'Starting point pin', icon: L.divIcon({ className: 'origin-pin', html: '<span aria-hidden="true"></span>', iconSize: [24, 32], iconAnchor: [12, 32] }) });
      marker.current = pin;
      if (p) pin.addTo(instance);
      const select = (latitude: number, longitude: number) => {
        const wrapped = L.latLng(latitude, longitude).wrap();
        if (Math.abs(wrapped.lat) <= 90) change.current({ latitude: wrapped.lat, longitude: wrapped.lng, label: 'Chosen starting point on the map' });
      };
      instance.on('click', e => select(e.latlng.lat, e.latlng.lng));
      pin.on('dragend', () => { const p = pin.getLatLng(); select(p.lat, p.lng); });
      resize = new ResizeObserver(() => instance.invalidateSize());
      resize.observe(container.current);
      setMapReady(true);
    }).catch(() => { if (!disposed) setMapError('The map could not start. Search for a place instead.'); });
    return () => { disposed = true; resize?.disconnect(); map.current?.remove(); map.current = null; marker.current = null; };
  }, [showMap]);
  useEffect(() => {
    if (!mapReady || !map.current || !marker.current) return;
    if (!point) { marker.current.remove(); return; }
    marker.current.setLatLng([point.latitude, point.longitude]).addTo(map.current);
    map.current.setView([point.latitude, point.longitude], 15, { animate: false });
  }, [point, mapReady]);

  async function findPlaces() {
    const text = query.trim();
    if (text.length < 2 || searchState === 'loading') return;
    search.current?.abort();
    const controller = new AbortController(); search.current = controller;
    const timeout = window.setTimeout(() => controller.abort(), 15000);
    setSearchState('loading'); setResults([]); setMessage('');
    try {
      const response = await fetch(`${apiBase}/v1/locations/search`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, signal: controller.signal, body: JSON.stringify({ query: text }) });
      const value: unknown = await response.json();
      if (search.current !== controller) return;
      if (!response.ok) throw new Error(response.status === 429 ? 'Search is busy. Wait a moment and try again.' : 'Place search is unavailable. Try again or choose on the map.');
      if (!value || typeof value !== 'object' || !('results' in value) || !Array.isArray(value.results) || value.results.length > 5 || !value.results.every(validPoint)) throw new Error('Search returned invalid location data. No starting point was selected.');
      const found = value.results.map(v => ({ label: v.label, ...v.coordinates }));
      setResults(found); setSearchState(found.length ? 'results' : 'empty');
    } catch (error) {
      if (search.current !== controller) return;
      setSearchState('error'); setMessage(controller.signal.aborted ? 'Search timed out. Try again or choose on the map.' : error instanceof Error ? error.message : 'Location search unavailable.');
    } finally { window.clearTimeout(timeout); if (search.current === controller) search.current = null; }
  }
  function editQuery(value: string) {
    search.current?.abort(); search.current = null;
    setQuery(value); setSearchState('idle'); setResults([]); setMessage(''); onChange(null);
  }

  return <div className="location-picker">
    <label htmlFor="place-search">Search for your starting area</label>
    <div className="location-search"><input id="place-search" type="search" autoComplete="off" maxLength={160} placeholder="City, neighbourhood, station or landmark" value={query} onChange={e => editQuery(e.target.value)} onKeyDown={e => { if (e.key === 'Enter') { e.preventDefault(); void findPlaces(); } }} /><button type="button" disabled={query.trim().length < 2 || searchState === 'loading'} onClick={() => void findPlaces()}>{searchState === 'loading' ? 'Searching…' : 'Search places'}</button></div>
    <p className="location-help">Search sends this text to Photon/OpenStreetMap. Use a public area or landmark, not a private address.</p>
    {searchState === 'loading' && <p role="status">Finding matching places…</p>}
    {searchState === 'empty' && <p role="status">No matching places. Add the city or country, or choose on the map.</p>}
    {searchState === 'error' && <p role="alert" className="status">{message}</p>}
    {searchState === 'results' && <ul className="location-results" aria-label="Matching starting locations">{results.map((p, index) => <li key={`${p.latitude}:${p.longitude}:${index}`}><button type="button" onClick={() => { onChange(p); setResults([]); setSearchState('idle'); mapToggle.current?.focus(); }}>{p.label}</button></li>)}</ul>}
    <button ref={mapToggle} className="secondary map-toggle" type="button" aria-expanded={showMap} onClick={() => setShowMap(!showMap)}>{showMap ? 'Hide map' : 'Choose on map'}</button>
    {showMap && <div className="origin-map-panel">{!mapReady && !mapError && <p role="status">Loading the starting-point map… Place search still works.</p>}<p id="map-help">Tap the map or drag the pin. With a keyboard, use arrow keys to move the map, then choose its centre.</p><div className="origin-map" ref={container} role="region" aria-busy={!mapReady} tabIndex={0} aria-label="Starting location map" aria-describedby="map-help" onKeyDown={e => { const steps: Record<string, [number, number]> = { ArrowLeft: [-80, 0], ArrowRight: [80, 0], ArrowUp: [0, -80], ArrowDown: [0, 80] }; if (steps[e.key]) { e.preventDefault(); map.current?.panBy(steps[e.key], { animate: false }); } }} /><button type="button" disabled={!mapReady} onClick={() => { const p = map.current?.getCenter().wrap(); if (p && Math.abs(p.lat) <= 90) onChange({ latitude: p.lat, longitude: p.lng, label: 'Chosen starting point on the map' }); }}>Use map centre as start</button>{mapError && <p role="status">{mapError}</p>}</div>}
    {point && <p role="status" className="selected-location"><strong>Starting point:</strong> {point.label}</p>}
    <small className="map-credit">Place search: <a href="https://photon.komoot.io" target="_blank" rel="noreferrer">Photon</a> · <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noreferrer">© OpenStreetMap contributors</a></small>
  </div>;
}
