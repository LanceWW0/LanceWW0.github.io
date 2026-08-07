---
layout: post
title: "The Quest for England's River Health Data: A Developer's Odyssey"
subtitle: "How I spent an Easter weekend downloading 25 years of water quality data one API call at a time — because the government deleted the download button."
tags: [Open Data, Environment, Python, RiverWatch]
date: 2026-04-15
colour: "#2E86AB"
header_image: /blog/the-quest-for-englands-river-health-data/header.png
image: /blog/the-quest-for-englands-river-health-data/header.png
image_desc: "Header image for the blog post about downloading England's river health data from the Environment Agency API."
description: "How I spent an Easter weekend downloading 25 years of water quality data one API call at a time — because the government deleted the download button."
seo:
  type: BlogPosting
---


  <p>
  If you've ever tried to answer a simple question with open government data, you'll know the journey is rarely simple. My question was straightforward: <strong>which rivers in England are in the worst health, and what's causing it?</strong>
  </p>
  <p>
  I'm building <a href="https://www.riverwatch.earth">RiverWatch</a>, an open source web app that visualises Environment Agency monitoring data — water quality surveys, fish populations, invertebrate counts — to help the public understand what's happening to England's rivers. The app already plots 65,000 sampling points on a map and lets you click through to time series graphs. But those are just individual dots. I wanted to connect them into a bigger picture: river-level health scores, colour-coded stretches, filterable by status, with the finger pointed squarely at what's causing the damage.
  </p>
  <p>
  To do that, I needed to get my hands on the data. All of it.
  </p>

  <h2>The Dataset That Disappeared</h2>
  <p>
  The Environment Agency's Water Quality Archive — known to its friends as WIMS — is one of the most valuable environmental datasets in England. It contains over 58 million measurements from 58,000 sampling points, dating back to the year 2000. Phosphate levels, ammonia concentrations, dissolved oxygen, pH, the works. It's the chemical biography of every monitored river, stream, and watercourse in the country.
  </p>
  <p>
  Until December 2025, you could download the whole thing as a bulk CSV. The kind of download that makes a data engineer's heart sing.
  </p>
  <p>
  Then, in December 2025, the EA retired the legacy Water Quality Archive and replaced it with a shiny new API built on "FAIR and Linked Data principles." The new system is genuinely impressive from a standards perspective — everything is semantically structured using the SOSA ontology, properly linked, machine-readable. There's just one small problem.
  </p>
  <p>
  They removed the bulk download.
  </p>
  <p>
  The new API is paginated, capped at 250 results per request, and limited to 100 sampling points per query. If you want the full dataset, the EA's official position is that users should select only the data they truly need, rather than sifting through entire datasets.
  </p>
  <p>
  I needed the entire dataset. I did not feel empowered.
  </p>

  <h2>The Email</h2>
  <p>
  The EA does offer a data request form for specific datasets, so I filled it in. Politely. Specifically. I listed the exact determinand codes I needed, the date range, the format I wanted, even offered to take it split by year. I mentioned the project was open source and non-commercial. I was the model data requester.
  </p>
  <p>
  The response came back promptly, to be fair. It said no. The bulk download no longer exists and the API is the only route. It was Easter weekend.
  </p>
  <div class="post-embed">
  <div class="tenor-gif-embed" data-postid="9396221664717142950" data-share-method="host" data-aspect-ratio="0.894309" data-width="100%"><a href="https://tenor.com/view/kedinehir-nehirkedi-mitcikedi-gif-9396221664717142950">Kedinehir Nehirkedi GIF</a>from <a href="https://tenor.com/search/kedinehir-gifs">Kedinehir GIFs</a></div>
  <script type="text/javascript" async src="https://tenor.com/embed.js"></script>
  </div>

  <h2>The Plan</h2>
  <p>
  Right. If the mountain won't come to Muhammad, Muhammad will write a Python script.
  </p>
  <p>
  The approach was simple in concept, if somewhat exhausting in execution. I already had the list of all 65,190 sampling point IDs — they're bundled into the RiverWatch app as GeoJSON tiles. For each point, I'd query the EA API for all historical observations, filter to the key determinands that drive river health classification, and save the results as a CSV. One file per sampling point.
  </p>
  <p>
  The key determinands — the ones that tell you whether a river is healthy or dying — are the same ones the EA uses for Water Framework Directive classification:
  </p>
  <ul>
  <li><strong>Orthophosphate</strong> (0180) — the biggest single driver of river failure in England. High levels cause algal blooms that choke everything else.</li>
  <li><strong>Ammoniacal Nitrogen</strong> (0111) — toxic to aquatic life at elevated levels. Spikes indicate slurry or manure entering the watercourse.</li>
  <li><strong>Dissolved Oxygen</strong> (9901) — the measure of whether a river can sustain life. Low oxygen = dead or dying ecosystem.</li>
  <li><strong>BOD</strong> (0085) — Biochemical Oxygen Demand. High BOD means organic matter is consuming oxygen. Classic indicator of sewage pollution.</li>
  <li><strong>Nitrate</strong> (0117) — fertiliser runoff signature. Also contributes to eutrophication.</li>
  <li><strong>pH</strong> (0061) — too acidic or too alkaline and the biology collapses.</li>
  </ul>
  <p>
  Plus a handful of supporting indicators: suspended solids, conductivity, total oxidised nitrogen, and temperature.
  </p>
  <p>
  The maths was daunting. 65,000 points &times; multiple pages per point &times; 250 results per page = a very large number of API calls. My initial estimate was 10&ndash;15 hours.
  </p>

  <h2>The Reality</h2>
  <p>
  The first version of the script was sequential. One point at a time. Polite. Respectful. Painfully slow.
  </p>
  <p>
  After 14 hours of running — including an unplanned pause overnight when my MacBook decided it had better things to do than stay awake — I had 2,011 points downloaded. Out of 65,000. At that rate, I was looking at roughly three weeks of continuous running.
  </p>
  <p>
  I briefly considered whether three weeks was acceptable. It was not.
  </p>

  <h3>The Concurrency Fix</h3>
  <p>
  The obvious solution was to download multiple points in parallel. Python's <code>ThreadPoolExecutor</code> made this straightforward — spin up multiple workers, each fetching a different sampling point simultaneously. The script was already designed to be resumable (if a CSV file exists, skip that point), so I could kill it, modify it, and restart without losing progress.
  </p>
  <p>
  I started with 5 workers. Then 10. Then 20. The EA API, to its credit, handled the load without complaint. No rate limiting. No angry 429 responses. Just steady, reliable data delivery.
  </p>
  <p>
  At 20 workers, the rate climbed to about 850 points per hour. Better, but still 70+ hours for the full dataset. The bottleneck wasn't my end — it was simply how long each API response took to come back.
  </p>
  <p>
  I pushed to 40 workers. The rate jumped. Then I went full send and the thing just... ran. Over Easter weekend, while normal people were eating chocolate eggs, my MacBook Pro sat in the corner with a YouTube video playing on screen (the sophisticated anti-sleep mechanism I deployed before discovering <code>caffeinate -s</code>), methodically downloading 25 years of English river chemistry.
  </p>

  <h3>The Slash Incident</h3>
  <p>
  Midway through, the script started throwing errors. Some sampling point IDs contain forward slashes — <code>SW-GWW16/05</code>, for example. When the script tried to save <code>SW-GWW16/05.csv</code>, the operating system interpreted <code>SW-GWW16</code> as a directory name and threw a fit. A quick sanitisation fix (replace <code>/</code> with <code>_</code> in filenames) sorted it out.
  </p>

  <h3>The SOSA Surprise</h3>
  <p>
  The first version of the parser extracted zero observations from every single point. Zero. Kept. The verbose logging showed hundreds of items coming back from the API, but nothing passing the filter.
  </p>
  <p>
  Turns out the EA's new API uses an entirely different data structure from the old one. What used to be <code>determinand.notation</code> is now <code>observedProperty.notation</code>. What used to be <code>result</code> is now <code>hasSimpleResult</code> or <code>hasResult.numericValue</code>. The old flat JSON had become a richly structured linked data graph using the SOSA (Sensor, Observation, Sample, and Actuator) ontology.
  </p>
  <p>
  Semantic web enthusiasts would call this progress. I called it an evening of debugging.
  </p>

  <h2>What Emerged from the Data</h2>
  <p>
  After the crawl finally completed, I ran the processing pipeline. Of the 65,190 sampling points:
  </p>
  <ul>
  <li><strong>5,462</strong> had usable river health data (the key determinands we were looking for)</li>
  <li><strong>59,728</strong> were empty — sewage treatment works, trade effluent monitoring, groundwater wells, and industrial compliance points</li>
  </ul>
  <p>
  The 5,462 points with data were scored using the Water Framework Directive's classification methodology. The WFD uses a "one-out-all-out" rule: a point's overall status is determined by its worst-performing determinand. If phosphate is Bad but everything else is High, the overall status is Bad. This is how the EA itself classifies waterbodies, mandated by EU legislation that the UK retained post-Brexit.
  </p>
  <p>
  The results were stark:
  </p>

  <div class="table-wrap" role="region" tabindex="0">
<table class="data-table">
  <thead>
  <tr>
  <th>Status</th>
  <th>Points</th>
  <th>Percentage</th>
  </tr>
  </thead>
  <tbody>
  <tr><td><strong>High</strong></td><td>1,311</td><td>24%</td></tr>
  <tr><td><strong>Good</strong></td><td>766</td><td>14%</td></tr>
  <tr><td><strong>Moderate</strong></td><td>452</td><td>8%</td></tr>
  <tr><td><strong>Poor</strong></td><td>613</td><td>11%</td></tr>
  <tr><td><strong>Bad</strong></td><td>2,115</td><td>39%</td></tr>
  <tr><td>Unknown</td><td>205</td><td>4%</td></tr>
  </tbody>
  </table>
</div>

  <p>
  <strong>Nearly 40% of monitored river points in England scored Bad.</strong> Only 38% achieved Good or High status.
  </p>
  <p>
  This broadly aligns with the EA's own reporting — just 14% of English rivers meet good ecological status — though our numbers aren't directly comparable because the official WFD classification incorporates biological quality elements alongside the chemistry, and uses river-type-specific thresholds that vary by alkalinity and altitude. Our scoring uses simplified flat thresholds, which we're transparent about.
  </p>
  <p>
  But the story the data tells is unmistakable. England's rivers are in trouble.
  </p>

  <h2>What's Next</h2>
  <p>
  The scored data is now live on <a href="https://www.riverwatch.earth">RiverWatch</a>. You can see colour-coded sampling points across the map, filter to show only Poor and Bad sites, click through to determinand breakdowns showing exactly what's failing, and view time series graphs that load instantly from pre-processed static files rather than waiting for the EA API.
  </p>
  <p>
  The next step is linking these point-level scores to actual river stretches. The EA divides each river into Water Framework Directive waterbody segments, each a few kilometres long, with their own classification and — crucially — their own "Reasons for Not Achieving Good Status" (RNAG) data. The RNAG dataset is the finger-pointing layer: it literally records whether a stretch is failing because of agriculture, the water industry, urban runoff, or something else.
  </p>
  <p>
  When that's wired in, you'll be able to look at a stretch of river, see it's in Bad status for phosphate, and see that the EA attributes it to agricultural diffuse pollution. Or see a stretch failing for ammonia near a sewage treatment works, attributed to the water industry. The data exists. It just needs connecting.
  </p>

  <h2>The Bigger Picture</h2>
  <p>
  The whole experience crystallised something I'd been thinking about for a while. Open data is only open if people can actually get to it. The EA's water quality data is technically available — it's published under the Open Government Licence, the API is documented, anyone can query it. But the practical barrier to accessing it at scale is now enormous. A paginated API with a 250-result limit and no bulk export is, for all practical purposes, a locked door with the key hidden under a very heavy rock.
  </p>
  <p>
  The irony is that the EA's own analysis depends on bulk access to this data. Their scientists, their Catchment Data Explorer, their WFD classifications — all of it requires the kind of comprehensive dataset view that the new API makes impractical for external users. The asymmetry matters, because public accountability depends on the public being able to see what the regulators see.
  </p>
  <p>
  I don't think this is malicious. The new API is genuinely well-designed from a technical standards perspective. But somewhere in the modernisation process, the use case of "researcher or civic tech developer who needs the whole dataset" got deprioritised in favour of "casual user who wants to look up their local river." Both are valid. Only one was served.
  </p>
  <p>
  So here's my request to Defra and the EA: <strong>please bring back the bulk download</strong>. Or at minimum, offer an annual data dump alongside the API. The data is public. The licence allows reuse. The infrastructure to generate CSVs clearly exists. All that's needed is the will to make it available.
  </p>
  <p>
  Until then, I'll be here with my 40 concurrent API threads and a <code>caffeinate -s</code> command, doing it the hard way. The rivers are worth it.
  </p>

  <hr>

  <p class="post-aside">
  <a href="https://www.riverwatch.earth">RiverWatch</a> is an open source project visualising Environment Agency data to help the public understand river health in England. The code is available on <a href="https://github.com/LanceWW0/River-Watch">GitHub</a>. All data is sourced from the Environment Agency under the Open Government Licence v3.0.
  </p>
  <p class="post-aside">
  Health scores shown on RiverWatch are based on simplified WFD physicochemical thresholds and use the same "one-out-all-out" methodology as official WFD classification. They do not account for river-type-specific thresholds or biological quality elements. For official classifications, see the <a href="https://environment.data.gov.uk/catchment-planning">EA Catchment Data Explorer</a>.
  </p>
  <footer class="post-footer">
  <hr>
  <p>Thanks for reading!</p>
  </footer>
