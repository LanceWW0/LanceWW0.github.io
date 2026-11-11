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
<section class="hero hero--home" style="background-image: linear-gradient(to bottom, rgba(0,0,0,.4), rgba(0,0,0,.6)), url('{{ page.hero_background }}');">
  <div class="hero-inner">
    <img class="headshot" src="{{ page.headshot }}" alt="Laurence Wayne" width="180" height="180" loading="eager" fetchpriority="high">
    <h1 class="hero-title">Hi, I'm Laurence.</h1>
    <p>
      I build mobile apps, web tools and data projects.<br/>
      Nine apps shipped on iOS and Android so far.
    </p>
    <div class="hero-ctas">
      <a class="btn btn-hero-primary" href="/apps/">See my apps</a>
      <a class="btn btn-ghost" href="/about/">About me</a>
    </div>
  </div>
</section>

<!-- APPS -->
<section class="home-section" aria-labelledby="home-apps">
  <div class="home-section-head" data-reveal>
    <h2 id="home-apps">Apps</h2>
    <a href="/apps/">All {{ site.data.apps | size }} apps <span class="arrow" aria-hidden="true">→</span></a>
  </div>
  <div class="home-grid home-grid--apps">
    {%- assign featured = site.data.apps | where: "featured", true %}
    {%- for app in featured %}
    {% include app-card.html app=app heading="h3" i=forloop.index0 %}
    {%- endfor %}
  </div>
</section>

<!-- PROJECTS -->
<section class="home-section" aria-labelledby="home-projects">
  <div class="home-section-head" data-reveal>
    <h2 id="home-projects">Projects</h2>
  </div>
  <div class="home-grid home-grid--three">
    {%- for project in site.data.projects %}
    {%- assign main = project.links | first %}
    <article class="proj-card" data-reveal style="--accent: {{ project.accent | default: '#6366f1' }}; --i: {{ forloop.index0 }};">
      <div class="card-media{% if project.media == 'logo' %} card-media--logo{% endif %}">
        <img src="{{ project.image | relative_url }}" alt="{{ project.image_alt | escape }}" loading="lazy" decoding="async">
      </div>
      <div class="card-body">
        <p class="card-eyebrow">{{ project.label }}</p>
        <h3><a href="{{ main.url }}"{% if main.url contains '://' %} target="_blank" rel="noopener"{% endif %}>{{ project.name }}</a></h3>
        <p class="card-text">{{ project.description }}</p>
        <p class="card-links">
          {%- for link in project.links %}
          <a class="text-link" href="{{ link.url }}"{% if link.url contains '://' %} target="_blank" rel="noopener"{% endif %}>{{ link.label }}{% if forloop.first %} <span class="arrow" aria-hidden="true">→</span>{% endif %}</a>
          {%- endfor %}
        </p>
      </div>
    </article>
    {%- endfor %}
  </div>
</section>

<!-- WRITING: the three newest posts, same query as /blog/ -->
<section class="home-section" aria-labelledby="home-writing">
  <div class="home-section-head" data-reveal>
    <h2 id="home-writing">Writing</h2>
    <a href="/blog/">All posts <span class="arrow" aria-hidden="true">→</span></a>
  </div>
  <div class="home-grid home-grid--three">
    {%- assign posts = site.pages | where_exp: "p", "p.date" | where_exp: "p", "p.layout == 'post'" | sort: "date" | reverse %}
    {%- for post in posts limit: 3 %}
    <article class="post-card" data-reveal style="--accent: {{ post.colour | default: '#6366f1' }}; --i: {{ forloop.index0 }};">
      {%- if post.header_image %}
      <div class="card-media">
        <img src="{{ post.header_image }}" alt="" loading="lazy" decoding="async" width="1200" height="750">
      </div>
      {%- endif %}
      <div class="card-body">
        <p class="card-eyebrow"><time datetime="{{ post.date | date_to_xmlschema }}">{{ post.date | date: "%-d %B %Y" }}</time></p>
        <h3><a href="{{ post.url | relative_url }}">{{ post.title }}</a></h3>
        {%- if post.subtitle %}
        <p class="card-text">{{ post.subtitle }}</p>
        {%- endif %}
      </div>
    </article>
    {%- endfor %}
  </div>
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

<!-- ABOUT -->
<section class="home-section" aria-labelledby="home-about">
  <div class="home-section-head" data-reveal>
    <h2 id="home-about">About</h2>
  </div>
  <div class="home-about" data-reveal>
    <img class="home-about-photo" src="/assets/images/me_turkey_small.jpeg" alt="Laurence in Turkey" width="420" height="560" loading="lazy" decoding="async">
    <div class="home-about-text">
      <p>
        I'm a mobile developer and data scientist based in the UK. I trained in geophysics, worked in data science at BT Group, then left to build apps from hotel rooms in South-East Asia. It was a terrifying decision, but I've made some incredible things along the way.
      </p>
      <p>
        These days I build consumer apps in SwiftUI and Flutter, contribute to open-source projects focused on the environment, and occasionally write about what I've learned. I care about clean code, real user value and shipping things that actually work.
      </p>
      <p class="home-about-links">
        <a class="text-link" href="mailto:hello@laurence-wayne.com">hello@laurence-wayne.com</a>
        <a class="text-link" href="https://github.com/LanceWW0">GitHub</a>
        <a class="text-link" href="https://twitter.com/solodevdude">Twitter</a>
        <a class="text-link" href="/about/">More about me <span class="arrow" aria-hidden="true">→</span></a>
      </p>
    </div>
  </div>
</section>
