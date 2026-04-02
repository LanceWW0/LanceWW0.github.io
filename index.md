---
layout: default
title: Home
description: Apps, experiments, and notes by Waz.
permalink: /
# Edit these paths:
hero_background: /assets/images/background.jpeg
headshot: /assets/images/me_snow.jpeg
---

<!-- HERO -->
<section class="hero" style="background-image: linear-gradient(to bottom, rgba(0,0,0,.4), rgba(0,0,0,.6)), url('{{ page.hero_background }}');">
  <div class="hero-inner">
    <img class="headshot" src="{{ page.headshot }}" alt="Laurence headshot" width="180" height="180" />
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
  <div class="highlight-card riverwatch-card" style="border-top: 4px solid #2a8a8a;">
    <div class="highlight-card-inner">
      <div class="icon-wrap">
        <img src="/assets/images/projects/river-watch/logo.png" alt="RiverWatch logo" width="120" height="120" />
      </div>
      <div class="content-wrap">
        <h2>Latest project: <span style="color: #2a8a8a;">River Watch</span></h2>
        <p>
          <strong style="color: #2a8a8a;">River Watch</strong> is an open-source project I'm building to visualise and track the health of England's rivers. It uses open government data—primarily from the Environment Agency—to surface trends, pollution events, and ecological indicators for every river.
        </p>
        <p>
          The goal is transparency: making it easy for anyone to see what's happening to their local waterways, identify what's causing degradation, and hold polluters to account.
        </p>
        <div class="rw-screenshot-wrap">
          <img class="rw-screenshot" src="/assets/images/projects/river-watch/screenshot.png" alt="RiverWatch screenshot showing river health data" />
        </div>
        <div class="card-actions">
          <a class="btn btn-primary" style="background-color: #2a8a8a;" href="https://www.riverwatch.earth" target="_blank" rel="noopener">Visit RiverWatch</a>
          <a class="btn btn-store" href="https://github.com/LanceWW0/River-Watch" target="_blank" rel="noopener">View on GitHub</a>
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
        <img src="/assets/images/apps/geology-toolkit/logo.png" alt="Geology Toolkit logo" width="120" height="120" />
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
      <img class="card-icon" src="/assets/images/apps/cloud-point/logo.png" alt="Cloud Point logo" width="80" height="80" />
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
      <img class="card-icon" src="/assets/images/apps/geology-toolkit/logo.png" alt="Geology AI logo" width="80" height="80" />
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
      <div class="blog-tile" style="background-image: linear-gradient(135deg, rgba(66, 133, 244, 0.9), rgba(99, 102, 241, 0.85)), url('/blog/why-i-finally-gave-up-with-android/header.png'); background-size: cover; background-position: center;">
        <h3>Why I Finally Gave Up With Android</h3>
        <p>What drove me away from Android development — and why Apple just makes more sense for indie developers.</p>
      </div>
    </a>
    <!-- Blog Tile 2 -->
    <a href="/blog/escaping-the-app-trap/" style="text-decoration: none;">
      <div class="blog-tile" style="background-image: linear-gradient(135deg, rgba(139, 92, 246, 0.9), rgba(236, 72, 153, 0.85)), url('/blog/escaping-the-app-trap/header.png'); background-size: cover; background-position: center;">
        <h3>Escaping the App Trap</h3>
        <p>How I stopped chasing attention, rethought marketing, and found meaning in app development again.</p>
      </div>
    </a>
  </div>
  <p class="section-cta"><a href="/blog/">See all posts →</a></p>
</section>

<!-- HIRE ME -->
<section class="section">
<div class="hire-banner">
<p>Looking for a developer for your next mobile app, web tool or data project? I'm available for freelance work.</p>
<a class="btn btn-hire" href="/hire/">✦ Hire Me</a>
</div>
</section>

<!-- MINI ABOUT -->
<section class="section">
  <div class="highlight-card about-card">
    <div class="highlight-card-inner">
      <div class="icon-wrap">
        <img class="about-headshot" src="assets/images/me_turkey.jpeg" alt="Laurence in Turkey" width="200" />
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
        <span style="font-weight: 600; color: #374151;">Let's connect:</span>
        <a href="mailto:hello@laurence-wayne.com">hello@laurence-wayne.com</a>
        <a href="https://github.com/LanceWW0">GitHub</a>
        <a href="https://twitter.com/solodevdude">Twitter</a>
        <a href="/about/">More about me →</a>
        </div>
        </div>
        </div>

  </div>
</section>
