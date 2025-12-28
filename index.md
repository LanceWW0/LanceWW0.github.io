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
<section class="hero" style="background-image: linear-gradient(to bottom, rgba(0,0,0,.35), rgba(0,0,0,.55)), url('{{ page.hero_background }}');">
  <div class="hero-inner">
    <img class="headshot" src="{{ page.headshot }}" alt="Laurence headshot" width="200" height="200" />
    <h1 class="hero-title">Hi, I’m Laurence.</h1>
    <p>
        Crafting iOS apps with SwiftUI &amp; Flutter.<br/>
        Sharing insights and stories from my solo development journey.
    </p>
    <div class="hero-ctas">
      <a class="btn btn-primary" href="/apps/">See my apps</a>
      <a class="btn btn-ghost" href="/blog/">Read the blog</a>
      <a class="btn btn-ghost" href="/about/">About me</a>
    </div>
  </div>
</section>

<!-- LATEST APP -->
<section class="section latest-app-highlight" style="padding: 3.5rem 0; background: linear-gradient(90deg, #e0e7ff 0%, #f8fafc 100%); border-radius: 18px; box-shadow: 0 4px 24px rgba(60,60,120,0.08); margin-bottom: 2.5rem;">
  <div style="padding: 0 2.5rem; display: flex; align-items: center; justify-content: center; gap: 2.5rem; max-width: 1100px; margin: 0 auto; flex-wrap: wrap;">
    <div style="flex: 0 0 auto; display: flex; flex-direction: column; align-items: center;">
      <img class="card-icon" src="/assets/images/apps/currency-converter/logo.png" alt="Valuto logo" width="100" height="100" style="border-radius: 16px; box-shadow: 0 2px 12px rgba(0,0,0,0.07);" />
    </div>
    <div style="flex: 1 1 400px; min-width: 260px;">
      <h2 class="section-title" style="margin-top: 0; font-size: 2.2rem; letter-spacing: -1px; color: #2d3748;">Latest app: <span style="color: #6366f1;">Currency Converter – Valuto</span></h2>
      <p class="card-body" style="font-size: 1.18em; line-height: 1.7; margin-bottom: 1.2em;">
        <strong>Valuto</strong> is a fast, minimal currency converter designed for travel. Instantly convert major currencies—even offline—with a clean interface and no ads or tracking. Valuto makes it easy to check exchange rates on the go, save your favourite currencies, and quickly switch between them. Whether you’re exploring a new country or shopping online, Valuto helps you stay on top of your spending with reliable, up-to-date rates and a distraction-free experience.    </p>
      <div class="card-actions" style="display: flex; gap: 1rem;">
        <a class="btn btn-primary" href="/apps/currency-converter/">Learn more</a>
        <a class="btn btn-primary" style="background-color: #4f46e5; color: #fff; border: none; box-shadow: 0 2px 8px rgba(79,70,229,0.15);" href="https://apps.apple.com/app/valuto-currency-converter/id0000000000" target="_blank" rel="noopener">App Store</a>
      </div>
    </div>
  </div>
</section>

<!-- MAJOR UPDATE INCOMING -->
<section class="section major-update-highlight" style="padding: 3.5rem 0; background: linear-gradient(90deg, #fde68a 0%, #f8fafc 100%); border-radius: 18px; box-shadow: 0 4px 24px rgba(120,80,20,0.08); margin-bottom: 2.5rem;">
  <div style="padding: 0 2.5rem; display: flex; align-items: center; justify-content: center; gap: 2.5rem; max-width: 1100px; margin: 0 auto; flex-wrap: wrap;">
    <div style="flex: 0 0 auto; display: flex; flex-direction: column; align-items: center;">
      <img class="card-icon" src="/assets/images/apps/earthquake-tracker/logo.png" alt="Earthquake Tracker logo" width="100" height="100" style="border-radius: 16px; box-shadow: 0 2px 12px rgba(0,0,0,0.07);" />
    </div>
    <div style="flex: 1 1 400px; min-width: 260px;">
      <h2 class="section-title" style="margin-top: 0; font-size: 2.2rem; letter-spacing: -1px; color: #b45309;">Major update incoming: <span style="color: #f59e42;">Earthquake Tracker & Monitor</span></h2>
      <p class="card-body" style="font-size: 1.18em; line-height: 1.7; margin-bottom: 1.2em;">
        <strong>Earthquake Tracker & Monitor</strong> is about to get even better! A major update is on the way, bringing new features and improvements to help you visualise real-time earthquake data from the USGS (US Geological Survey) and stay safe wherever you are.<br/>
        <span style="color: #f59e42;">Built with the latest Flutter features</span> for a seamless, modern experience understanding the data.
      </p>
      <div class="card-actions" style="display: flex; gap: 1rem;">
        <a class="btn btn-primary" href="/apps/earthquake-tracker/">Learn more</a>
        <a class="btn btn-primary" style="background-color: #b45309; color: #fff; border: none; box-shadow: 0 2px 8px rgba(180,83,9,0.15);" href="https://apps.apple.com/az/app/earthquake-tracker-monitor/id6748315703" target="_blank" rel="noopener">App Store</a>
      </div>
    </div>
  </div>
</section>

<!-- FEATURED APPS -->
<section class="section featured-apps-highlight">
  <div class="featured-wrap">
    <h2 class="section-title" style="margin-top: 0; font-size: 2.2rem; letter-spacing: -1px; color: #2d3748;">Featured Apps</h2>
    <div class="featured-grid" style="padding-top: 2.5rem; padding-bottom: 2.5rem;">
      <!-- Cloud Point Card -->
      <div class="featured-card">
        <img class="card-icon" src="/assets/images/apps/cloud-point/logo.png" alt="Cloud Point logo" width="80" height="80" />
        <h3 class="card-title">Cloud Point – Cloud Identifier</h3>
        <p class="card-body">
          A unique community created by and for cloud-spotters. No prior knowledge needed!
        </p>
        <div class="card-actions">
          <a class="btn btn-sm btn-primary" href="/apps/cloud-point/">Learn more</a>
          <a class="btn btn-sm btn-accent" href="https://apps.apple.com/gb/app/cloud-point-cloud-identifier/id6480587789" target="_blank" rel="noopener">App Store</a>
        </div>
      </div>
      <!-- Geology AI Card -->
      <div class="featured-card">
        <img class="card-icon" src="/assets/images/apps/geology-ai/logo.png" alt="Geology AI logo" width="80" height="80" />
        <h3 class="card-title">Geology Toolkit: AI Rock ID</h3>
        <p class="card-body">
          A powerful toolkit for field Geologists, aiding understanding, interpretation and sketches!
        </p>
        <div class="card-actions">
          <a class="btn btn-sm btn-primary" href="/apps/geology-ai/">Learn more</a>
          <a class="btn btn-sm btn-accent" href="https://apps.apple.com/my/app/geology-ai/id6745966254" target="_blank" rel="noopener">App Store</a>
        </div>
      </div>
    </div>
    <p class="section-cta" style="text-align: center;"><a href="/apps/">Browse all apps →</a></p>
  </div>
</section>



<!-- LATEST POSTS -->
<section class="section">
  <h2 class="section-title">Latest posts</h2>
  <div class="blog-tiles-grid" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 2rem; margin-bottom: 2rem;">
    <!-- Blog Tile 1 -->
    <a href="/blog/why-i-gave-up-on-android/" style="text-decoration: none;">
      <div class="blog-tile" style="position: relative; height: 320px; border-radius: 16px; overflow: hidden; box-shadow: 0 4px 20px rgba(0,0,0,0.1); cursor: pointer; transition: all 0.4s cubic-bezier(0.25, 0.46, 0.45, 0.94); background-image: linear-gradient(135deg, rgba(66, 133, 244, 0.85), rgba(66, 133, 244, 0.7)), url('/blog/why-i-gave-up-on-android/header.png'); background-size: cover; background-position: center; display: flex; flex-direction: column; justify-content: flex-end; padding: 2rem; color: white; text-decoration: none;">
        <h3 style="margin: 0 0 0.75rem 0; font-size: 1.5rem; font-weight: 600; line-height: 1.3; letter-spacing: -0.5px; color: white;">Why I Finally Gave Up With Android</h3>
        <p style="margin: 0; font-size: 1rem; line-height: 1.5; opacity: 0.95; color: rgba(255,255,255,0.95);">What drove me away from Android development — and why Apple just makes more sense for indie developers.</p>
        <style>
          .blog-tile:hover {
            transform: translateY(-8px);
            box-shadow: 0 12px 32px rgba(66, 133, 244, 0.25);
          }
        </style>
      </div>
    </a>
    <!-- Blog Tile 2 -->
    <a href="/blog/escaping-the-app-trap/" style="text-decoration: none;">
      <div class="blog-tile" style="position: relative; height: 320px; border-radius: 16px; overflow: hidden; box-shadow: 0 4px 20px rgba(0,0,0,0.1); cursor: pointer; transition: all 0.4s cubic-bezier(0.25, 0.46, 0.45, 0.94); background-image: linear-gradient(135deg, rgba(60, 145, 230, 0.85), rgba(60, 145, 230, 0.7)), url('/blog/escaping-the-app-trap/header.png'); background-size: cover; background-position: center; display: flex; flex-direction: column; justify-content: flex-end; padding: 2rem; color: white; text-decoration: none;">
        <h3 style="margin: 0 0 0.75rem 0; font-size: 1.5rem; font-weight: 600; line-height: 1.3; letter-spacing: -0.5px; color: white;">Escaping the App Trap</h3>
        <p style="margin: 0; font-size: 1rem; line-height: 1.5; opacity: 0.95; color: rgba(255,255,255,0.95);">How I stopped chasing attention, rethought marketing, and found meaning in app development again.</p>
      </div>
    </a>
  </div>
  <p class="section-cta" style="text-align: center;"><a href="/blog/">See all posts →</a></p>
</section>

<!-- MINI ABOUT -->
<section class="section about-highlight" style="padding: 3.5rem 0; background: linear-gradient(90deg, #e0e7ff 0%, #f8fafc 100%); border-radius: 18px; box-shadow: 0 4px 24px rgba(60,60,120,0.08); margin-bottom: 2.5rem;">
  <div style="padding: 0 2.5rem; display: flex; align-items: center; justify-content: center; gap: 2.5rem; max-width: 1100px; margin: 0 auto; flex-wrap: wrap;">
    <!-- Photo -->
    <div style="flex: 0 0 auto; display: flex; flex-direction: column; align-items: center;">
      <img class="about-headshot" src="assets/images/me_turkey.jpeg" alt="Laurence turkey picture" width="200" style="border-radius: 16px; box-shadow: 0 2px 12px rgba(0,0,0,0.07); margin-bottom: 1rem;" />
    </div>
    <!-- About Content -->
    <div style="flex: 1 1 400px; min-width: 260px;">
      <h2 class="section-title" style="margin-top: 0; font-size: 2.2rem; letter-spacing: -1px; color: #2d3748;">About me</h2>
      <p style="font-size: 1.18em; line-height: 1.7; margin-bottom: 1.1em;">
        Hi, I’m Laurence — a passionate mobile developer based in the UK, while currently travelling the world. Although I started out in cyber security, I now design, build, and ship helpful consumer apps with a focus on positive user experiences and clean, efficient code.
      </p>
      <p style="font-size: 1.18em; line-height: 1.7; margin-bottom: 1.1em;">
        My current work explores the power of <strong>SwiftUI</strong> for iOS, while I continue to improve my <strong>Flutter</strong> projects. I love experimenting with new frameworks, prototyping ideas, and sharing the lessons I've learned along the way with others.
      </p>
      <p>
        Find out more about me and my indie development journey here.
      </p>
      <p style="margin-bottom: 0;">
        <span style="font-weight: 500;">Let’s connect:</span>
        <a href="mailto:hello@laurence-wayne.com" style="margin-left: 0.5em;">hello@laurence-wayne.com</a>
        &nbsp;·&nbsp;
        <a href="https://github.com/LanceWW0">GitHub</a>
        &nbsp;·&nbsp;
        <a href="https://twitter.com/solodevdude">Twitter</a>
        &nbsp;·&nbsp;
        <a href="/about/">More about me →</a>
      </p>
    </div>
  </div>
</section>
