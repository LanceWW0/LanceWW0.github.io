# /health data job

Python job that pulls your Garmin data through the official **Garmin Connect
Personal API**, turns it into privacy-safe aggregates and (later) commits them
for the `/health` page. The full plan lives in the PR description. This file covers
setup and the rules the code enforces.

## Privacy rules (enforced in code, not by convention)

- **No GPS or locations.** Only allowlisted endpoints can be called
  (`garmin.ENDPOINTS`). FIT/ZIP downloads and activity details are not on
  the list. Activity names, `locationName` and coordinates are never read.
- **No precise times.** Timestamps are only used in memory to work out a
  date, then dropped.
- **Delay.** A date is published only once it has been over for 24 hours
  *everywhere* (`dates.publish_cutoff`), so travelling can't shorten it.
- **Secrets stay secret.** The API key comes from `GARMIN_PERSONAL_API_KEY`
  or `~/.config/garmin/connect-personal-api-key`. The 24-hour token lives in
  memory only, and is masked in GitHub Actions logs. Error messages carry an
  endpoint label and HTTP status, never response bodies.
- **Public logs.** Actions logs on this repo are public, so CI prints only
  status codes and counts.

## One-time setup

1. In Garmin Connect (web), go to **Personal API Key** → **Create Key**. Read
   the terms (look for anything about showing data publicly), and pick a
   **1-year** expiry. The key is shown once.
2. Save it outside the repo:

   ```bash
   mkdir -p ~/.config/garmin && pbpaste > ~/.config/garmin/connect-personal-api-key && chmod 600 ~/.config/garmin/connect-personal-api-key
   ```

3. Create the local environment (from the repo root):

   ```bash
   /opt/homebrew/bin/python3.12 -m venv .venv && .venv/bin/pip install --require-hashes -r scripts/health/requirements.txt
   ```

## Step 2: probe the data shape

```bash
.venv/bin/python -m scripts.health.probe --out .garmin-probe/report.txt
```

This takes about a minute (it throttles itself to about 1 request a second). It
prints a redacted report: field paths, types, how often each is present, and
flags for fields that look like GPS (`GEO`), times (`TIME`), free text (`TEXT`)
or IDs (`ID`). It never prints values, except activity type keys, HRV status
and token scopes. `.garmin-probe/` is gitignored.

Raw responses are only saved if you ask, and only outside the repo:
`--save-raw /tmp/garmin-raw` (delete it afterwards).

## Step 3: CI smoke test

```bash
gh secret set GARMIN_PERSONAL_API_KEY < ~/.config/garmin/connect-personal-api-key
```

Then run the **Health data** workflow (Actions tab → Run workflow, mode
`smoke`). It exchanges the key and makes one call, printing status only.

## Tests

```bash
.venv/bin/python -m pytest scripts/health
```

All tests run offline against fake HTTP sessions with synthetic data.

## Field mapping

From the probe run on 10 Nov 2026 (14-day sample, plus 13 months of activities).

| Metric | Endpoint | Field | Notes |
|---|---|---|---|
| Sleep duration | `sleep-summaries` | `sleepTimeSeconds` | Dated by `calendarDate`, the morning you wake: 14/14 nights matched the wake date. |
| Sleep score | `sleep-summaries` | `sleepScores.overall.value` | In the bulk endpoint, so no per-day calls. |
| Sleep stages | `sleep-summaries` | `deepSleepSeconds`, `lightSleepSeconds`, `remSleepSeconds`, `awakeSleepSeconds` | |
| HRV (nightly) | `hrv-range` | `hrvSummaries[].lastNightAvg` | `baseline.balancedLow` / `balancedUpper` give Garmin's "balanced" band. `status` is an enum. |
| Resting HR | `daily-summaries` | `data[].heartRate.restingValue` | |
| Body Battery | `daily-summaries` | `data[].bodyBattery.maxValue` | The day's peak. The separate `body-battery` endpoint isn't needed. |
| Activity type | `activities` | `activityType.typeKey` | Seen: running, walking, hiking, cycling, multi_sport, road_biking. |
| Distance / time | `activities` | `distance` (m), `movingDuration` (s; fall back to `duration`) | |
| Intensity | `activities` | `activityTrainingLoad` | For the training-calendar levels. |
| Activity date | `activities` | date part of `startTimeLocal` | The time is thrown away immediately. |

**Never read.** The probe found all of these, and they stay out of the build:
- start/end latitude and longitude, `locationName`, `activityName`
- `owner*` (full name, display name, profile image URLs)
- elevation fields, `pulseOx.avgAltitudeInMeters`
- every `*Timestamp*` / `*Time*` field
- the sleep-need and sleep-alignment `*Mins` fields (recommended bedtime, sleep midpoint), which are times of day stored as minutes
- `hrvReadings[]` and `bodyBatteryValuesArray` (intraday, timestamped)
- split summaries, IDs, UUIDs
- `sleepScorePersonalizedInsight` (free text)

**Measured limits:**

| Endpoint | Range per call | Notes |
|---|---|---|
| `sleep-summaries` | ≥ 32 days | We use 31, the documented cap. |
| `hrv-range` | ≥ 90 days | |
| `daily-summaries` | ≥ 366 days | |
| `body-battery` | 31 days | Not used. |
| `activities` | pages of up to 100 | |

**History:** data starts in 2023; there's none in 2022. A full rebuild of all
history is about 75 calls, roughly a minute and a quarter at one request per
second.

## Updating dependencies

Edit `requirements.in`, then:

```bash
.venv/bin/uv pip compile scripts/health/requirements.in --universal --python-version 3.12 --generate-hashes -o scripts/health/requirements.txt
```
