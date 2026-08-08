---
layout: default
description: I build mobile apps, web tools and data projects — and write about the messy bits. Nine apps shipped across iOS and Android.
permalink: /
image: /assets/images/me_snow.jpeg
# Edit these paths:
hero_background: /assets/images/background.jpeg
headshot: /assets/images/me_snow.jpeg
---

<!-- HERO -->
<section class="hero" style="background-image: linear-gradient(to bottom, rgba(0,0,0,.4), rgba(0,0,0,.6)), url('{{ page.hero_background }}');">
  <div class="hero-inner">
    <img class="headshot" src="{{ page.headshot }}" alt="Laurence headshot" width="180" height="180" loading="eager" fetchpriority="high">
    <h1 class="hero-title">Hi, I'm Laurence.</h1>
    <p>
      I build things: mobile apps, web tools & data projects.<br/>
      Occasionally I write about it too.
    </p>
    <div class="hero-ctas">
      <a class="btn btn-hero-primary" href="/apps/">See my apps</a>
      <a class="btn btn-ghost" href="/blog/">Read the blog</a>
      <a class="btn btn-ghost" href="/about/">About me</a>
    </div>
  </div>
</section>

<!-- RIVERWATCH -->
<section class="section">
  <div class="highlight-card riverwatch-card">
    <div class="highlight-card-inner">
      <div class="icon-wrap">
        <img src="/assets/images/projects/river-watch/logo.png" alt="RiverWatch logo" width="120" height="120" loading="eager" fetchpriority="high">
      </div>
      <div class="content-wrap">
        <h2>Latest project: <span class="rw-name">River Watch</span></h2>
        <p>
          <strong class="rw-name">River Watch</strong> is an open-source project I'm building to visualise and track the health of England's rivers. It uses open government data—primarily from the Environment Agency—to surface trends, pollution events, and ecological indicators for every river.
        </p>
        <p>
          The goal is transparency: making it easy for anyone to see what's happening to their local waterways, identify what's causing degradation, and hold polluters to account.
        </p>
        <div class="rw-screenshot-wrap">
          <img class="rw-screenshot" src="/assets/images/projects/river-watch/screenshot.jpg" alt="RiverWatch screenshot showing river health data" loading="lazy" decoding="async" width="1400" height="786">
        </div>
        <div class="card-actions">
          <a class="btn btn-primary" href="https://www.riverwatch.earth" target="_blank" rel="noopener">Visit RiverWatch</a>
          <a class="btn btn-store" href="https://github.com/LanceWW0/River-Watch" target="_blank" rel="noopener">View on GitHub</a>
        </div>
      </div>
    </div>
  </div>
</section>

<!-- CLOUD POINT FIELD GUIDE -->
<section class="section">
  <div class="highlight-card cloudguide-card">
    <div class="highlight-card-inner">
      <div class="icon-wrap">
        <img src="/assets/images/apps/cloud-point/logo.png" alt="Cloud Point logo" width="120" height="120" loading="lazy" decoding="async">
      </div>
      <div class="content-wrap">
        <h2>New site: <span class="cg-name">Cloud Point Field Guide</span></h2>
        <p>
          To look a cloud up, you generally have to know its name already. <a href="https://en.wikipedia.org/wiki/List_of_cloud_types" target="_blank" rel="noopener">Wikipedia's list of cloud types</a> and the <a href="https://www.metoffice.gov.uk/weather/learn-about/weather/types-of-weather/clouds" target="_blank" rel="noopener">Met Office's cloud guide</a> are both solid catalogues of the genera — but they're indexed by Latin taxonomy, and nobody searches for <em>cavum</em> when what they saw was a neat round hole punched clean through a thin layer.
        </p>
        <p>
          <strong class="cg-name">Cloud Point</strong> is a field guide that starts from what you actually saw. Fifty-two entries, one a week, each pairing a photographed plate with a plain-English title and the proper name underneath. It runs in order of altitude — the first thing you can judge standing on the ground — and it covers the supplementary features, accessory clouds and optical phenomena that sit on top of the genera, which is where most misidentification happens. The taxonomy follows the WMO International Cloud Atlas.
        </p>
        <p>
          Plain descriptions, credited plates and a stable structure are also how AI models increasingly learn obscure subjects, so the guide is written to be read by both. And if you'd rather skip the reading entirely, the Cloud Point app will name it from a photo.
        </p>
        <div class="rw-screenshot-wrap">
          <img class="rw-screenshot" src="/assets/images/projects/cloud-point-guide/screenshot.jpg" alt="The Cloud Point library, showing a photographed plate for each cloud type in order of altitude" loading="lazy" decoding="async" width="1400" height="715">
        </div>
        <div class="card-actions">
          <a class="btn btn-primary" href="https://www.cloudpointapp.com" target="_blank" rel="noopener">Visit the field guide</a>
          <a class="btn btn-store" href="/apps/cloud-point/">Get the app</a>
        </div>
      </div>
    </div>
  </div>
</section>

<!-- TWITTER BOT -->
<section class="section">
  <div class="highlight-card twitter-bot">
    <div class="highlight-card-inner">
      <div class="icon-wrap">
        <img src="/assets/images/apps/geology-toolkit/logo.png" alt="Geology Toolkit logo" width="120" height="120" loading="eager" fetchpriority="high">
      </div>
      <div class="content-wrap">
        <h2>Rock of the Day: <span>@GeologyToolkit</span></h2>
        <p>
          I built a Twitter bot that tweets a daily rock quiz! Each day it posts a mystery rock photo and challenges followers to identify it, then reveals the answer later. A fun way to learn geology and promote <strong>Geology Toolkit</strong>.
        </p>
        <p class="coming-soon">
          <em>Blog post coming soon on how it was made.</em>
        </p>
        <div class="rw-tweet-embed">
<blockquote class="twitter-tweet" data-dnt="true"><a href="https://x.com/GeologyToolkit/status/2038889201391800407">Loading tweet...</a></blockquote>
        </div>
        <div class="card-actions">
          <a class="btn btn-primary" href="https://x.com/GeologyToolkit" target="_blank" rel="noopener">Follow @GeologyToolkit</a>
          <a class="btn btn-store" href="/apps/geology-toolkit/">View the app</a>
        </div>
      </div>
    </div>
  </div>
</section>
<script async src="https://platform.twitter.com/widgets.js" charset="utf-8"></script>

<!-- FEATURED APPS -->
<section class="featured-section">
  <div class="section-header">
    <h2>Featured Apps</h2>
    <p>A selection of apps I've built and shipped to the App Store</p>
  </div>
  <div class="featured-grid">
    <!-- Cloud Point Card -->
    <div class="featured-card" style="--card-accent: #3b82f6; --card-accent-end: #06b6d4;">
      <img class="card-icon" src="/assets/images/apps/cloud-point/logo.png" alt="Cloud Point logo" width="80" height="80" loading="eager" fetchpriority="high">
      <h3 class="card-title">Cloud Point – Cloud Identifier</h3>
      <p class="card-body">
        A unique community created by and for cloud-spotters. No prior knowledge needed—just look up and explore!
      </p>
      <div class="card-actions">
        <a class="btn btn-sm btn-primary" href="/apps/cloud-point/">Learn more</a>
        <a class="btn btn-sm btn-accent" href="https://apps.apple.com/gb/app/cloud-point-cloud-identifier/id6480587789" target="_blank" rel="noopener">App Store</a>
      </div>
    </div>
    <!-- Geology AI Card -->
    <div class="featured-card" style="--card-accent: #f59e0b; --card-accent-end: #ef4444;">
      <img class="card-icon" src="/assets/images/apps/geology-toolkit/logo.png" alt="Geology AI logo" width="80" height="80" loading="eager" fetchpriority="high">
      <h3 class="card-title">Geology Toolkit: AI Rock ID</h3>
      <p class="card-body">
        A powerful toolkit for field Geologists, aiding understanding, interpretation and sketches in the field!
      </p>
      <div class="card-actions">
        <a class="btn btn-sm btn-primary" href="/apps/geology-toolkit/">Learn more</a>
        <a class="btn btn-sm btn-accent" href="https://apps.apple.com/my/app/geology-toolkit/id6745966254" target="_blank" rel="noopener">App Store</a>
      </div>
    </div>
  </div>
  <p class="section-cta"><a href="/apps/">Browse all apps →</a></p>
</section>

<!-- LATEST POSTS -->
<section class="blog-section">
  <div class="section-header">
    <h2>Latest Posts</h2>
  </div>
  <div class="blog-tiles-grid">
    <!-- Blog Tile 1 -->
    <a href="/blog/why-i-finally-gave-up-with-android/" style="text-decoration: none;">
      <div class="blog-tile" style="background-image: linear-gradient(135deg, rgba(66, 133, 244, 0.9), rgba(99, 102, 241, 0.85)), url('/blog/why-i-finally-gave-up-with-android/header.jpg'); background-size: cover; background-position: center;">
        <h3>Why I Finally Gave Up With Android</h3>
        <p>What drove me away from Android development — and why Apple just makes more sense for indie developers.</p>
      </div>
    </a>
    <!-- Blog Tile 2 -->
    <a href="/blog/escaping-the-app-trap/" style="text-decoration: none;">
      <div class="blog-tile" style="background-image: linear-gradient(135deg, rgba(139, 92, 246, 0.9), rgba(236, 72, 153, 0.85)), url('/blog/escaping-the-app-trap/header.jpg'); background-size: cover; background-position: center;">
        <h3>Escaping the App Trap</h3>
        <p>How I stopped chasing attention, rethought marketing, and found meaning in app development again.</p>
      </div>
    </a>
  </div>
  <p class="section-cta"><a href="/blog/">See all posts →</a></p>
</section>

{% comment %}
  HIRE ME — hidden while not taking on new work. Liquid comments are stripped
  at build time, so none of this reaches the served HTML.

  To restore: uncomment the block below, uncomment the footer link in
  _includes/footer.html, uncomment `hire/index.md` under header_pages in
  _config.yml, and set `published: true` in hire/index.md.

<section class="section">
<div class="hire-banner">
<p>Looking for a developer for your next mobile app, web tool or data project? I'm available for freelance work.</p>
<a class="btn btn-hire" href="/hire/">✦ Hire Me</a>
</div>
</section>
{% endcomment %}

<!-- MINI ABOUT -->
<section class="section">
  <div class="highlight-card about-card">
    <div class="highlight-card-inner">
      <div class="icon-wrap">
        <img class="about-headshot" src="assets/images/me_turkey.jpeg" alt="Laurence in Turkey" width="200" loading="eager" fetchpriority="high">
      </div>
      <div class="content-wrap">
        <h2>About Me</h2>
        <p>
          Hi, I'm Laurence - I'm a mobile developer, data scientist and indie app maker based in the UK. My background is unusual: I trained in geophysics, worked in data science at BT Group, then transitioned to building apps from hotel rooms in South-East Asia. It was a terrifying decision, but I've made some incredible things along the way.
        </p>
        <p>
        These days I build consumer apps in SwiftUI and Flutter, contribute to open source projects focused on the environment,  take on freelance projects and occasionally write about what I've learned. I care about clean code, real user value, and shipping things that actually work.
        </p>
        <div class="connect-links">
        <span class="connect-label">Let's connect:</span>
        <a href="mailto:hello@laurence-wayne.com">hello@laurence-wayne.com</a>
        <a href="https://github.com/LanceWW0">GitHub</a>
        <a href="https://twitter.com/solodevdude">Twitter</a>
        <a href="/about/">More about me →</a>
        </div>
        </div>
        </div>

  </div>
</section>
