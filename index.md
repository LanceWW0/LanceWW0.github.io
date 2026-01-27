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
      Crafting iOS apps with SwiftUI &amp; Flutter.<br/>
      Sharing insights from my solo development journey.
    </p>
    <div class="hero-ctas">
      <a class="btn btn-primary" href="/apps/">See my apps</a>
      <a class="btn btn-ghost" href="/blog/">Read the blog</a>
      <a class="btn btn-ghost" href="/about/">About me</a>
    </div>
  </div>
</section>

<!-- LATEST APP -->
<section class="section">
  <div class="highlight-card latest-app">
    <div class="highlight-card-inner">
      <div class="icon-wrap">
        <img src="/assets/images/apps/currency-converter/logo.png" alt="Valuto logo" width="120" height="120" />
      </div>
      <div class="content-wrap">
        <h2>Latest app: <span>Currency Converter – Valuto</span></h2>
        <p>
          <strong>Valuto</strong> is a fast, minimal currency converter designed for travel. Instantly convert major currencies—even offline—with a clean interface and no ads or tracking. Save your favourite currencies and stay on top of your spending with reliable, up-to-date rates.
        </p>
        <div class="card-actions">
          <a class="btn btn-primary" href="/apps/currency-converter/">Learn more</a>
          <a class="btn btn-store" href="https://apps.apple.com/app/valuto-currency-converter/id0000000000" target="_blank" rel="noopener">App Store</a>
        </div>
      </div>
    </div>
  </div>
</section>

<!-- MAJOR UPDATE -->
<section class="section">
  <div class="highlight-card major-update">
    <div class="highlight-card-inner">
      <div class="icon-wrap">
        <img src="/assets/images/apps/earthquake-tracker/logo.png" alt="Earthquake Tracker logo" width="120" height="120" />
      </div>
      <div class="content-wrap">
        <h2>Major update incoming: <span>Earthquake Tracker &amp; Monitor</span></h2>
        <p>
          <strong>Earthquake Tracker &amp; Monitor</strong> is getting even better! A major update brings new features to help you visualise real-time earthquake data from the USGS and stay safe wherever you are. Built with the latest Flutter features for a seamless, modern experience.
        </p>
        <div class="card-actions">
          <a class="btn btn-primary" href="/apps/earthquake-tracker/">Learn more</a>
          <a class="btn btn-store" href="https://apps.apple.com/az/app/earthquake-tracker-monitor/id6748315703" target="_blank" rel="noopener">App Store</a>
        </div>
      </div>
    </div>
  </div>
</section>

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
      <img class="card-icon" src="/assets/images/apps/geology-ai/logo.png" alt="Geology AI logo" width="80" height="80" />
      <h3 class="card-title">Geology Toolkit: AI Rock ID</h3>
      <p class="card-body">
        A powerful toolkit for field Geologists, aiding understanding, interpretation and sketches in the field!
      </p>
      <div class="card-actions">
        <a class="btn btn-sm btn-primary" href="/apps/geology-ai/">Learn more</a>
        <a class="btn btn-sm btn-accent" href="https://apps.apple.com/my/app/geology-ai/id6745966254" target="_blank" rel="noopener">App Store</a>
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
          Hi, I'm Laurence — a passionate mobile developer based in the UK, currently travelling the world. Although I started out in cyber security, I now design, build, and ship helpful consumer apps with a focus on positive user experiences and clean, efficient code.
        </p>
        <p>
          My current work explores the power of <strong>SwiftUI</strong> for iOS, while I continue to improve my <strong>Flutter</strong> projects. I love experimenting with new frameworks, prototyping ideas, and sharing the lessons I've learned along the way.
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
