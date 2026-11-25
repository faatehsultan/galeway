# Product walkthrough video script (target 8 minutes, max 10)

Record at 1440×900, light theme, browser zoom 100%. Close other tabs. Warm the API first (open the app a minute before). Use a trip with interesting weather on the day; have a fallback saved trip ready.

| Time | Section | Show | Say (key points) |
|---|---|---|---|
| 0:00 | Hook | Results screen already loaded | "Galeway picks the safest truck route through the weather and explains why. React and Django, deployed on free tiers." |
| 0:30 | Plan a trip | Type origin/destination, departure, 42,000 lb, 25 mi; submit | Validation, autocomplete; the loading steps are real backend stages |
| 1:30 | Results | Route cards, recommended badge, risk bars | 3 truck routes from TomTom with the real load weight; each card shows severe/high miles and the worst stretch |
| 2:15 | Map | Click checkpoints; hover; select route B | ETA at each checkpoint, forecast for that hour, and the condition that drove the level |
| 3:00 | Heatmap + slider | Drag, then play; switch Risk → Wind → Snow | Data loaded once; the slider only swaps a GPU paint expression, so it stays smooth. Truck marker shows where you'll be. |
| 3:45 | Why this route | Route detail: stats, explanation, table pagination/filter | The 4 ranking rules, applied in order; the explanation is generated from the ranking itself |
| 4:30 | Edge cases | Methodology panel | Boundaries go up; sustained vs gusts; rain without melted snow; missing data is never safe; all-no-travel shows no fake recommendation |
| 5:15 | Share + saved | Copy link → open in incognito; save trip, reload, open from the drawer | The URL is the state; saved trips stay on this device |
| 5:45 | States | Dev-only scenario switch: partial data, weather down, rate limit | Every failure has a calm, specific UI |
| 6:15 | Code tour | Repo tree; `planning/domain/risk.py`; a parametrized test; `service.py`; CI run with coverage | Functional core / imperative shell; tests for every rule; typed contract from OpenAPI |
| 7:15 | Quality | CI gates, coverage report, Lighthouse, security headers | What would block a merge |
| 7:45 | Wrap | Dark mode + mobile view | Trade-offs (free-tier cold start, sustained wind) and what I'd do next (Parking lot) |

Tips: speak to decisions, not keystrokes. If something goes wrong live, say what the app is showing; the error states are part of the product.
