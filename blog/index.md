---
layout: post
title: Blog
description: Writing on indie app development, security incidents, open data and the business of shipping software solo.
permalink: /blog/
---

<a href="/" class="back-link">← Back to Home</a>

# Blog Posts

Welcome! Explore all blog posts below.

<style>
.blog-card {
    display: block;
    border: none;
    border-radius: 16px;
    padding: 0;
    background: #fff;
    transition: transform 0.25s ease, box-shadow 0.25s ease;
    text-decoration: none;
    overflow: hidden;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}
.blog-card:hover {
    transform: translateY(-6px);
    box-shadow: 0 12px 28px rgba(0, 0, 0, 0.15);
}

/* Image at top of each card - full width */
.blog-card img {
    width: 100%;
    height: auto;
    aspect-ratio: 16 / 10;
    object-fit: cover;
    display: block;
}

/* Card content area */
.blog-card-content {
    padding: 1.25rem 1.5rem 1.5rem;
}

.blog-card h2 {
    margin: 0 0 0.5rem 0;
    font-size: 1.3rem;
    line-height: 1.3;
}

.blog-card p {
    margin: 0.4rem 0;
    font-size: 0.95rem;
    opacity: 0.85;
}

.blog-card .tag {
    display: inline-block;
    font-size: 0.8rem;
    font-weight: 500;
}

/* Two columns on desktop, one column on smaller screens */
.posts-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 2rem;
    margin-top: 2rem;
}

/* Collapse to one column on narrow viewports */
@media (max-width: 700px) {
    .posts-grid {
        grid-template-columns: 1fr;
        gap: 1.5rem;
    }
}
</style>

<div class="posts-grid">

{% for post in site.data.blog_posts %}
<a class="blog-card"
   href="{{ post.url }}"
   style="border-left: 4px solid {{ post.colour }};"
   >
    <img src="{{ post.image }}" alt="{{ post.name }} header" />
    <div class="blog-card-content" style="color: #333;">
        <h2 style="color: {{ post.colour }};">
            {{ post.name }}
        </h2>
        <p><strong>{{ post.date }}</strong></p>
        <p>
            {% for tag in post.tags %}
                <span class="tag" style="background: {{ post.colour }}18; color: {{ post.colour }}; padding: 0.25em 0.7em; border-radius: 20px; margin-right: 0.3em;">{{ tag }}</span>
            {% endfor %}
        </p>
    </div>
</a>
{% endfor %}

</div>