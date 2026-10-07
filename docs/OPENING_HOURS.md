# Opening hours

`ground_rule.hours.is_open_for_interval(expression, arrival, departure, timezone)`
uses opening-hours-py 2.1.4, the MIT/Apache-2.0 Rust-backed OSM parser:
https://github.com/remi-dupre/opening-hours-rs.

The interval is half-open: closing exactly at departure is allowed. Inputs must
be aware instants with an explicit IANA venue timezone. Weekdays, multiple daily
intervals, overnight ranges and closed-day overrides are parsed by the library.
Evaluation visits every UTC minute boundary and the arrival instant; the grammar
has minute precision. Both repeated local hours are visited and spring gaps are
skipped by actual elapsed time, avoiding ambiguous local iterator endpoints.

Unknown syntax, parser warnings, unknown states and missing context return
UNKNOWN. Solar events, PH/SH/easter rules require coordinates/calendar context
and are unsupported here. Appointments and arbitrary provider prose are not OSM
syntax. Dates before 1970, second-resolution timezone offsets and visits longer
than 48 hours are unsupported. No timezone is guessed from a locale or address.

`windows_from_hours` produces only an interval proven open for the requested
dwell, retains the raw evidence alongside it, and preserves source references
and observation/expiry timestamps. Policy still enforces its unchanged 24-hour
opening-evidence age and positive confidence rules. Parsing does not refresh a
stale observation or establish live hours.
