<p>
  <a href="/">← Back to Home</a>
</p>

<section class="apps-grid">
  {%- for app in site.data.apps -%}
    <article class="app-card">
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
-->

<p class="apps-note">Looking for privacy policies? You’ll find each one on its app page.</p>