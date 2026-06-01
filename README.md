# pitwall ai

pitwall ai is a formula 1 race strategy assistant.

it shows live telemetry, strategy calls, race simulations, and fia rulebook answers in one web app.

## what it does

- shows live race and car data
- compares pit strategy options
- explains recommended strategy calls
- answers fia regulation questions
- provides a dashboard for demos

## what is included

- fastapi backend
- next.js frontend
- websocket telemetry
- strategy and simulation apis
- fia rag assistant
- langflow service

## run with docker compose

```bash
docker compose up --build
```

open the frontend:

```text
http://localhost:3000
```

open the backend docs:

```text
http://localhost:8000/docs
```

## run with langflow

```bash
docker compose --profile langflow up --build
```

open langflow:

```text
http://localhost:7860
```

## stop

```bash
docker compose down
```

## environment

the app can run without api keys using fallback providers.

to use IBM granite, set these in `.env`:

```text
WATSONX_API_KEY=
WATSONX_PROJECT_ID=
WATSONX_URL=
```
