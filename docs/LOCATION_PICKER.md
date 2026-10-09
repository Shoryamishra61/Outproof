# Starting location

Visual thesis: the existing field notebook, with one clear selected origin. Signature decisions: a plain place-search row rather than coordinate fields, a grass-coloured draggable pin, and an explicit selected-location line that keeps example, GPS and map choices distinct. This is an intake control, not a venue-browsing feed.

Live users choose their own starting point. Type a city, neighbourhood, station or landmark and press Enter or Search places, choose a matching result, then adjust the map if necessary. Tap the map or drag the pin; keyboard users can focus the map, use arrow keys and press Use map centre as start. The Singapore example is explicitly opt-in. No latitude/longitude entry is required.

GPS requests a fresh high-accuracy fix with a 15-second timeout and zero cache age. Refresh GPS requests again rather than reusing the first fix. Permission denial, timeout, invalid coordinates and low accuracy are handled separately. A coarse fix previews an area but cannot authorize compilation until the user selects a map point. Switching to a map/example invalidates late GPS callbacks. Browser/OS permissions and positioning accuracy remain outside the app's control.

`POST /v1/locations/search` accepts only a 2–160 character query and a maximum 2KB body. The configured HTTPS Photon provider supplies up to five validated points. Results are origin suggestions only; they establish no venue admission, price, hours, accessibility or outing validity. Hard outing checks remain unchanged.

The provider is configurable via server-side `GEOCODER_URL`. Requests are explicitly user-triggered, identified, serialized and limited to one new upstream request per second; excess requests return 429. Responses have a 12-second total wait and 1MB body bound, with no redirects. A maximum 128-entry, one-hour process-memory cache uses hashed query keys; raw query text is not logged or persisted. This quota assumes one production instance; use shared admission before scaling.

Search text goes to Photon; users are prompted to use public areas/landmarks rather than private addresses. The visible map sends tile coordinates and the site's origin referrer to OpenStreetMap. No raw GPS/query history is saved. Map data and third-party availability can be incomplete; location search does not extend verified outing coverage.

The [Photon public demo policy](https://github.com/komoot/photon#demo-server) permits moderate project use, with no availability guarantee. The [OSM tile policy](https://operations.osmfoundation.org/policies/tiles/) requires visible attribution, normal browser caching and an identifying referrer; no bulk/offline tile download is implemented. Automated map interaction tests intercept tiles with controlled imagery. Leaflet is pinned to 1.9.4 (BSD-2-Clause); map animations are disabled and its controls use existing tokens.
