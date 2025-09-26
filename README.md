# Trip-Planner
LLM agent for trip plans including RoadTrip and City trip

Travel Planner MVP — README

Minimal, provider-agnostic backend to turn a short user request into a simple multi-day itinerary JSON.
Focus on structure and working defaults. No validator/repair yet. Frontend can wait.

1) Tech Stack (minimal)

Python

LangGraph (workflow graph / state machine)

LangChain (LLM calls; provider picked by env)

pydantic (schemas), httpx (HTTP), numpy, scikit-learn (KMeans)

Optional cache: redis (default is in-memory)

External APIs are not hardcoded. Everything goes through narrow service interfaces.

2) Project Layout
src/
  app.py                  # CLI entrypoint (single run)
  graph.py                # LangGraph wiring
  config.py               # env flags & defaults
  models.py               # Pydantic schemas
  llm/
    client.py             # LLM provider switch (env)
  services/
    pois.py               # POIService interface + demo provider
    routing.py            # RoutingService interface + demo provider
    weather.py            # WeatherService interface + demo provider
  logic/
    router_node.py        # 1) parse TripConstraints
    fetcher_node.py       # 2) fetch POIs/ETA/weather
    routing_node.py       # 3) derive RoutingParams
    scheduler_node.py     # 4) build DayPlans
    narrator_node.py      # 5) generate text
  storage/
    cache.py              # memory/redis cache
  utils/
    geo.py                # distance, clustering helpers
    timebox.py            # simple slot helpers
tests/
  sample_inputs/
    paris_short.json
README.md
.env.example

3) Minimal Schemas
TripConstraints (input)
{
  "city": "string",
  "dates": { "start": "YYYY-MM-DD", "end": "YYYY-MM-DD" },
  "party_size": 2,
  "mode": "walk | transit | drive",
  "pace": "relaxed | medium | tight",
  "themes": ["food","museum"]
}


Defaults if missing: party_size=2, mode="walk", pace="medium", themes=[].

CandidatePOI (fetched)
{
  "poi_id": "string",
  "name": "string",
  "lat": 0.0,
  "lon": 0.0,
  "category": "museum | food | park | viewpoint | other",
  "popularity": 0.0,
  "min_dwell": 60,
  "source": { "name": "string", "url": "string", "fetched_at": "ISO-8601" }
}

DistanceMatrix (sparse)
{
  "mode": "walk | transit | drive",
  "eta_min": [["poiA","poiB",18], ["poiB","poiC",12]]
}

WeatherSummary (daily)
{ "by_date": [ { "date": "YYYY-MM-DD", "precip_prob": 0.35, "note": "" } ] }

RoutingParams (derived)
{
  "primary_mode": "walk | transit | drive",
  "pace_coeff": 1.0,                // relaxed=0.8, medium=1.0, tight=1.2
  "theme_weights": { "food":1.0, "museum":1.0, "other":0.7 },
  "buffer_ratio": 0.15              // can bump to 0.25 on rainy days
}

TripPlan (output)
{
  "city": "string",
  "days": [
    {
      "date": "YYYY-MM-DD",
      "slots": [
        { "start":"09:00","end":"10:30","poi_id":"ID","transport":{"mode":"walk","eta_min":12} },
        { "start":"12:30","end":"13:30","type":"meal" }
      ],
      "day_total_time_min": 480,
      "transit_share": 0.25
    }
  ],
  "sources": ["POIService","RoutingService","WeatherService"],
  "itinerary_text": "string",
  "why_this_plan": "string"
}

4) Workflow (5 Nodes)

Router → parse free text into TripConstraints (fill defaults).

Fetcher → CandidatePOIs[] (top-N), DistanceMatrix (same mode, sparse), WeatherSummary.

RoutingParams → derive pace_coeff, buffer_ratio, theme_weights.

Scheduler → cluster (KMeans k=3–5), pick 3–4 POIs/day, insert travel buffers & lunch.

Narrator → add itinerary_text & why_this_plan; return TripPlan.

State carries: {constraints, pois, matrix, weather, routing_params, trip_plan}.

5) Service Interfaces (provider-agnostic)

POIService.search(city, themes, limit) -> CandidatePOIs[]

RoutingService.matrix(mode, pois) -> DistanceMatrix

WeatherService.summary(city, dates) -> WeatherSummary

Start with demo providers (mock/seeded data). Later plug any maintained APIs (Places/OSM/Wiki for POI; hosted or self-hosted routing; Open-Meteo/OpenWeather for weather).

6) Config & Env

.env.example

LLM_PROVIDER=openai|anthropic|google
LLM_MODEL=...
API_KEY_POI=...
API_KEY_ROUTING=...
API_KEY_WEATHER=...
CACHE_BACKEND=memory|redis
REDIS_URL=redis://localhost:6379/0
DEFAULT_TOP_N_POIS=40

7) Run (CLI)

Single shot, no server:

python -m src.app \
  --city "Kyoto" \
  --start 2025-04-02 \
  --end 2025-04-04 \
  --party 2 \
  --mode walk \
  --pace medium \
  --themes food museum


Prints a TripPlan JSON to stdout and saves output/trip_<timestamp>.json.

8) Heuristics (for MVP)

Day blocks: AM 09:00–12:00, PM 13:30–17:30, plus lunch 60 min around 12:30.

Select POIs from a single cluster per day; score = popularity * theme_weight.

Travel time used in slots = eta_min * (1 + buffer_ratio).

Dwell time scaled by pace_coeff.

No validation/repair yet (intentionally left out for a faster MVP).

9) Sprint (short)

Sprint 0: skeleton, schemas, LLM client, service interfaces + demo providers; Router & Fetcher runnable.

Sprint 1: wire LangGraph; implement clustering/timeboxing; produce TripPlan JSON end-to-end.

Sprint 2: narration & caching (memory default; optional Redis); provenance in sources.

Sprint 3 (optional): plug one real provider per service via env; keep demo providers as fallback.

10) Notes

Keep providers swappable; don’t store third-party raw content long-term unless terms allow.

Start with in-memory cache; flip to Redis later.

When ready, add Validator + Repair as new nodes, without changing existing contracts.
