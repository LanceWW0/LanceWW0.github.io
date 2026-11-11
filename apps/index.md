---
layout: default
title: Apps
description: A collection of iOS and Android apps by Laurence Wayne — AI identification tools, currency converters, earthquake tracking and more.
permalink: /apps/
---

<header class="page-head" data-reveal>
  <h1>My Apps</h1>
  <p>Nine apps for iOS and Android, built to educate, inspire and simplify everyday life.</p>
</header>

<section class="apps-grid">
  {%- for app in site.data.apps %}
  {% assign col = forloop.index0 | modulo: 3 %}{% include app-card.html app=app heading="h2" i=col %}
  {%- endfor %}
</section>

<p class="apps-note">Looking for privacy policies? You'll find each one on its app page.</p>
