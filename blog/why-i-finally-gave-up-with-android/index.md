---
layout: post
title: "Why I Finally Gave Up With Android (and Why You Might Too)"
subtitle: "What drove me away from Android development — and why Apple just makes more sense for indie developers."
url: /blog/why-i-gave-up-on-android/
tags: [Android, App Development, Flutter, iOS, Indie Dev]
date: 2025-10-24
colour: "#4285F4"   # Google Blue
header_image: /blog/why-i-gave-up-on-android/header.png
image_desc: "Illustration of a broken Android logo fading into an Apple logo."
description: "After years of app development, I finally walked away from Android — here’s why. From impossible testing requirements to user spending gaps, this is the reality every indie dev should know."
---

<!-- SEO Meta Tags -->
<meta name="description" content="After years of app development, I finally walked away from Android — here’s why. From impossible testing requirements to user spending gaps, this is the reality every indie dev should know.">
<meta property="og:title" content="Why I Finally Gave Up on Android (and Why You Might Too)">
<meta property="og:description" content="After years of app development, I finally walked away from Android — here’s why. From impossible testing requirements to user spending gaps, this is the reality every indie dev should know.">
<meta property="og:type" content="article">
<meta property="og:url" content="https://yourusername.github.io/blog/why-i-gave-up-on-android/">
<meta property="og:image" content="https://yourusername.github.io/blog/why-i-gave-up-on-android/header.png">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="Why I Finally Gave Up on Android (and Why You Might Too)">
<meta name="twitter:description" content="After years of app development, I finally walked away from Android — here’s why. From impossible testing requirements to user spending gaps, this is the reality every indie dev should know.">
<meta name="twitter:image" content="https://yourusername.github.io/blog/why-i-gave-up-on-android/header.png">

<!-- Structured Data -->
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "BlogPosting",
  "headline": "Why I Finally Gave Up with Android (and Why You Might Too)",
  "image": "https://yourusername.github.io/blog/why-i-gave-up-on-android/header.png",
  "author": {
    "@type": "Person",
    "name": "Your Name"
  },
  "datePublished": "2025-10-24",
  "description": "After years of app development, I finally walked away from Android — here’s why. From impossible testing requirements to user spending gaps, this is the reality every indie dev should know.",
  "url": "https://yourusername.github.io/blog/why-i-gave-up-on-android/"
}
</script>

<p>
  <a href="/blog">← Back to Blog Posts</a>
</p>

<div style="text-align:center;">
    <h1 style="font-size:3em;">Why I Finally Gave Up With Android</h1>
    <h2 style="font-weight:normal; color:grey;">What drove me away from Android development — and why Apple just makes more sense for indie developers.</h2>
    <p style="color:gray;">{{ page.date | date: "%B %-d, %Y" }}</p>
    <div style="max-width:800px; margin:0 auto;">
        <img src="/blog/why-i-finally-gave-up-with-android/header.png" alt="Illustration of a broken Android logo fading into an Apple logo." style="max-width:80%; height:auto; padding:16px; border-radius:24px;">
        <p style="font-size:1.35em; line-height:1.7; margin-top:24px;">
            Back in mid-2023, I had the brilliant (maybe slightly delusional) idea of building my own apps. I’d done bits and pieces of web development before at work — mostly small, scrappy prototypes - but never anything full-scale. Never something real that people could actually download, use, and maybe even enjoy.
        </p>
        <p style="font-size:1.35em; line-height:1.7;">
            I had no clue how to start — but that turned out to be my secret weapon. Being a total noob meant I wasn’t afraid to fail spectacularly. I just kept building — before work, after work, probably even in work if we’re being honest — and somehow, it started to click.
        </p>
        <p style="font-size:1.35em; line-height:1.7;">
            After binging countless YouTube tutorials (because this was pre-AI-helper times), I landed on <strong>Flutter</strong>: Google’s sleek framework built on Dart that lets you code once and deploy across iOS, Android, and even desktop. It felt perfect. I spent way too long perfecting my first app, <em>Cloud Point</em>, and after a few polite duels with Apple’s review team, it was finally live on the App Store.
        </p>
        <p style="font-size:1.35em; line-height:1.7;">
            Next came Android. I thought it would be the easy part. <strong>Spoiler: it wasn’t.</strong>
        </p>
        <hr style="margin:40px 0;">
        <h3 style="font-size:2em; color:#4285F4;">Reason One: Android’s Ridiculous Entry Requirements for Solo Developers</h3>
        <p style="font-size:1.35em; line-height:1.7;">
            I happened to create my developer account right after Google changed their rules. To publish an app, you now needed 20 real users testing it for 14 consecutive days. Sounds manageable — until you remember how few of your friends actually have Androids. (And how few of them will actually test your app properly instead of just saying “yeah, sure.”)
        </p>
        <p style="font-size:1.35em; line-height:1.7;">
            For me, that number was two — my parents.
        </p>
        <p style="font-size:1.35em; line-height:1.7;">
            Cue me trawling Reddit, pleading with strangers in <code>r/androiddev</code> and <code>r/ClosedTesting</code> to install my app and “use it daily” for two straight weeks. The reality? Most people just install your app, open it once, and vanish. And because Google tracks tester activity, they’ll reject your submission if it doesn’t look “properly tested.”
        </p>
        <p style="font-size:1.35em; line-height:1.7;">
            You then have to start again. From scratch. I went through that nightmare three times.
        </p>
        <p style="font-size:1.35em; line-height:1.7;">
            Eventually, I gave up and hired a freelancer on Fiverr to handle testing. (Pro tip: just do that. Save your sanity.) Even after that, your app still faces manual review — where a human reviewer can reject it without telling you why. So you upload, get rejected, tweak, upload again… until you receive the email every Android dev dreads:
        </p>
        <blockquote style="font-size:1.5em; font-weight:bold; color:#4285F4; margin:24px 0;">
            “Your app has been suspended from the Google Play Store.”
        </blockquote>
        <p style="font-size:1.35em; line-height:1.7;">
            <strong>Translation:</strong> start from zero. Again. Honestly? Soul-destroying.
        </p>
        <hr style="margin:40px 0;">
        <h3 style="font-size:2em; color:#4285F4;">Reason Two: The Never-Ending Device Maze</h3>
        <p style="font-size:1.35em; line-height:1.7;">
            Android is the most widely used mobile OS in the world — and that’s exactly the problem. There are thousands of devices, each with different screen sizes, chipsets, and quirks. As a solo dev, testing on all of them is impossible.
        </p>
        <p style="font-size:1.35em; line-height:1.7;">
            Even just handling screen sizing logic is like solving a Rubik’s Cube while blindfolded. I quit Android before foldable phones became mainstream — I shudder to think what the layout logic for those looks like.
        </p>
        <hr style="margin:40px 0;">
        <h3 style="font-size:2em; color:#4285F4;">Reason Three: Apple’s One-Code-to-Rule-Them-All Philosophy</h3>
        <p style="font-size:1.35em; line-height:1.7;">
            Apple keeps things simple: one codebase for iOS, macOS, watchOS, visionOS, and tvOS. It just works. Flutter tries to offer that same magic, but there are more hoops to jump through on Android. You can write for the full Android ecosystem — phones, tablets, TVs, watches — but after my Play Store trauma? Hard pass.
        </p>
        <hr style="margin:40px 0;">
        <h3 style="font-size:2em; color:#4285F4;">Reason Four: Apple Users Actually Pay</h3>
        <p style="font-size:1.35em; line-height:1.7;">
            It’s not a myth — Apple users statistically spend more. Whether it’s paying for premium features, subscriptions, or removing ads, iOS users convert better.
        </p>
        <p style="font-size:1.35em; line-height:1.7;">
            Even seasoned developers like <a href="https://www.youtube.com/results?search_query=Adam+Lyttle" target="_blank" rel="noopener noreferrer">Adam Lyttle</a> have found that Android users are far more likely to sit through an ad than to pay to remove it. So, if you’re a solo indie dev looking to actually earn something, Apple’s ecosystem is the smarter bet.    </p>
        <figure style="max-width:800px;margin:0 auto;text-align:center;">
          <a href="https://explodingtopics.com/blog/iphone-android-users" target="_blank" rel="noopener noreferrer">
            <img src="https://cdn.buttercms.com/output=f:webp/3Do7T6oYQmOJEL0i2Del" alt="iPhone vs Android users — Exploding Topics" style="max-width:80%;height:auto;padding:16px;border-radius:12px;">
          </a>
          <figcaption style="font-size:0.9em;color:gray;margin-top:8px;">
            Image credit: <a href="https://explodingtopics.com/blog/iphone-android-users" target="_blank" rel="noopener noreferrer">Exploding Topics — "iPhone vs Android Users"</a>
          </figcaption>
        </figure>
        <hr style="margin:40px 0;">
        <h3 style="font-size:2em; color:#4285F4;">Reason Five: The Apple Experience Just Feels Premium</h3>
        <p style="font-size:1.35em; line-height:1.7;">
            Maybe it’s marketing witchcraft, maybe it’s genuine quality — but Apple’s ecosystem just feels... elegant. Android, on the other hand, still conjures images of buggy apps, inconsistent UI, and the occasional virus. iOS feels like craftsmanship. Yes, it’s expensive, but you get what you pay for.
        </p>
        <hr style="margin:40px 0;">
        <h3 style="font-size:2em; color:#4285F4;">Conclusion: Sometimes You Just Have to Walk Away</h3>
        <p style="font-size:1.35em; line-height:1.7;">
            Quitting Android wasn’t an easy decision. I’d invested time learning cross-platform development, and Android’s global market share is impossible to ignore. But I’ve learned that to make real progress, sometimes you have to say no to what doesn’t serve your goals.
        </p>
        <p style="font-size:1.35em; line-height:1.7;">
            So, for now — farewell, Android. No hard feelings. (But I definitely won’t miss you.)
        </p>
    </div>
    <footer class="post-footer">
      <hr>
      <p>Thanks for reading!</p>
      <!-- <p>Enjoyed this? You might also like <a href="/blog/flutter-vs-swiftui/">Flutter vs SwiftUI: Which Is Better for Indie Devs?</a>.</p> -->
    </footer>
</div>
