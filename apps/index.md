---
layout: default
title: Apps
description: A collection of iOS and Android apps by Laurence Wayne — AI identification tools, currency converters, earthquake tracking and more.
permalink: /apps/
---

<a href="/" class="back-link">← Back to Home</a>

<header class="apps-header">
  <h1 class="apps-header-title">My Apps</h1>
  <p class="apps-header-subtitle">A collection of iOS apps designed to educate, inspire, and simplify your life</p>
</header>

<section class="apps-grid">
  {%- for app in site.data.apps -%}
    <article
      class="app-card fancy"
      style="
        --accent:  {{ app.accent  | default: '#6C5CE7' }};
        --accent2: {{ app.accent2 | default: '#A29BFE' }};
      ">
      <a class="app-card-link" href="{{ app.url | relative_url }}">
        <img class="app-icon" src="{{ app.icon | relative_url }}" alt="{{ app.name }} app icon" width="88" height="88" />
        <div class="app-meta">
          <h2 class="app-title">{{ app.name }}</h2>
          <p class="app-desc">{{ app.description }}</p>
          <div class="app-actions">
            {%- for tag in app.tags -%}<span class="chip">{{ tag }}</span>{%- endfor -%}
          </div>
        </div>
      </a>
    </article>
  {%- endfor -%}
</section>

<p class="apps-note">Looking for privacy policies? You'll find each one on its app page.</p>
