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
        Sharing insights and stories from my indie development journey.
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
      <img class="card-icon" src="/assets/images/apps/earthquake-tracker/logo.png" alt="Geology AI logo" width="100" height="100" style="border-radius: 16px; box-shadow: 0 2px 12px rgba(0,0,0,0.07);" />
    </div>
    <div style="flex: 1 1 400px; min-width: 260px;">
      <h2 class="section-title" style="margin-top: 0; font-size: 2.2rem; letter-spacing: -1px; color: #2d3748;">Latest app: <span style="color: #6366f1;">Earthquake Tracker & Monitor</span></h2>
      <p class="card-body" style="font-size: 1.18em; line-height: 1.7; margin-bottom: 1.2em;">
        <strong>Earthquake Tracker & Monitor</strong> is built to visualise real-time earthquake data from the USGS (US Geological Survey) so you can stay safe wherever you are in the world.<br/>
        <span style="color: #6366f1;">Integrated with the latest Flutter features</span> for a seamless, modern experience understanding the data.
      </p>
      <div class="card-actions" style="display: flex; gap: 1rem;">
        <a class="btn btn-primary" href="/apps/earthquake-tracker/">Learn more</a>
        <a class="btn btn-primary" style="background-color: #4f46e5; color: #fff; border: none; box-shadow: 0 2px 8px rgba(79,70,229,0.15);" href="https://apps.apple.com/az/app/earthquake-tracker-monitor/id6748315703" target="_blank" rel="noopener">App Store</a>    </div>
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
        <h3 class="card-title">Geology AI</h3>
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
  <div class="list-posts">
    {%- assign posts = site.posts | slice: 0, 3 -%}
    {%- if posts.size > 0 -%}
      {%- for post in posts -%}
      <article class="post-item">
        <h3><a href="{{ post.url }}">{{ post.title }}</a></h3>
        <p class="post-meta">{{ post.date | date: "%B %d, %Y" }}</p>
        <p class="post-excerpt">{{ post.excerpt | strip_html | truncate: 140 }}</p>
      </article>
      {%- endfor -%}
      <p class="section-cta"><a href="/blog/">See all posts →</a></p>
    {%- else -%}
      <p>No posts yet — coming soon.</p>
    {%- endif -%}
  </div>
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
        <a href="mailto:cloud.point88@gmail.com" style="margin-left: 0.5em;">cloud.point88@gmail.com</a>
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
