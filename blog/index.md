---
layout: default
title: Blog
description: Writing on indie app development, security incidents, open data and the business of shipping software solo.
permalink: /blog/
---

<div class="blog-index">

<h1>Blog Posts</h1>

<p>Welcome! Explore all blog posts below.</p>

<div class="posts-grid">
{%- assign posts = site.pages | where_exp: "p", "p.date" | where_exp: "p", "p.layout == 'post'" | sort: "date" | reverse -%}
{%- for post in posts -%}
  <a class="blog-card" href="{{ post.url | relative_url }}"
     {% if post.colour %}style="--post-colour: {{ post.colour }};"{% endif %}>
    {% if post.header_image %}
    <img src="{{ post.header_image }}" alt="{{ post.image_desc | default: post.title | escape }}"
         loading="lazy" decoding="async" width="1200" height="750" />
    {% endif %}
    <div class="blog-card-content">
      <h2>{{ post.title }}</h2>
      <p><strong><time datetime="{{ post.date | date_to_xmlschema }}">{{ post.date | date: "%B %-d, %Y" }}</time></strong></p>
      {% if post.tags %}
      <p>
        {% for tag in post.tags %}<span class="tag">{{ tag }}</span>{% endfor %}
      </p>
      {% endif %}
    </div>
  </a>
{%- endfor -%}
</div>

</div>
