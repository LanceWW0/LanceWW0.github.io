---
layout: post
---

# Blog Posts

Welcome! Explore all blog posts below.

<style>
.blog-card {
    display: block;
    border: 2px solid;
    border-radius: 8px;
    padding: 1rem;
    background: #fff;
    transition: background 0.2s, color 0.2s;
    text-decoration: none;
}
.blog-card:hover {
    /* Hover visuals are handled inline per card so colors come from post.colour */
}
</style>

<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 1.5rem;">

{% for post in site.data.blog_posts %}
<a class="blog-card"
   href="{{ post.url }}"
   style="border-color: {{ post.colour }}; color: {{ post.colour }};"
   onmouseover="this.style.background='{{ post.colour }}'; this.style.color='#fff'; this.querySelectorAll('.tag').forEach(t=>{t.style.background='#fff'; t.style.color='{{ post.colour }}';});"
   onmouseout="this.style.background='#fff'; this.style.color='{{ post.colour }}'; this.querySelectorAll('.tag').forEach(t=>{t.style.background='{{ post.colour }}22'; t.style.color='{{ post.colour }}';});"
   >
    <h2 style="margin-top: 0;">
        {{ post.name }}
    </h2>
    <p><strong>Date:</strong> {{ post.date }}</p>
    <p>
        <strong>Tags:</strong>
        {% for tag in post.tags %}
            <span class="tag" style="background: {{ post.colour }}22; color: {{ post.colour }}; padding: 0.2em 0.6em; border-radius: 4px; margin-right: 0.3em;">{{ tag }}</span>
        {% endfor %}
    </p>
</a>
{% endfor %}

</div>