---
layout: post
title: "Someone Tried to Bankrupt My Cloud App With Broken Images and Bad Intentions"
subtitle: "How a rogue user called TheBug0502 sent my Google Cloud bill into the stratosphere — and what I learned about protecting a Firebase backend the hard way."
url: /blog/someone-tried-to-bankrupt-my-app/
tags: [Firebase, Security, Indie Dev, Cloud Point]
date: 2026-04-02
colour: "#E63946"
header_image: /blog/someone-tried-to-bankrupt-my-app/header.png
image_desc: "Header image for the blog post about a rogue user trying to bankrupt a cloud app."
description: "How a rogue user called TheBug0502 sent my Google Cloud bill into the stratosphere — and what I learned about protecting a Firebase backend the hard way."
---

<!-- SEO Meta Tags -->
<meta name="description" content="How a rogue user called TheBug0502 sent my Google Cloud bill into the stratosphere — and what I learned about protecting a Firebase backend the hard way.">
<meta property="og:title" content="Someone Tried to Bankrupt My Cloud App With Broken Images and Bad Intentions">
<meta property="og:description" content="How a rogue user called TheBug0502 sent my Google Cloud bill into the stratosphere — and what I learned about protecting a Firebase backend the hard way.">
<meta property="og:type" content="article">
<meta property="og:url" content="https://LanceWW0.github.io/blog/someone-tried-to-bankrupt-my-app/">
<meta property="og:image" content="https://LanceWW0.github.io/blog/someone-tried-to-bankrupt-my-app/header.png">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="Someone Tried to Bankrupt My Cloud App With Broken Images and Bad Intentions">
<meta name="twitter:description" content="How a rogue user called TheBug0502 sent my Google Cloud bill into the stratosphere — and what I learned about protecting a Firebase backend the hard way.">
<meta name="twitter:image" content="https://LanceWW0.github.io/blog/someone-tried-to-bankrupt-my-app/header.png">

<!-- Structured Data -->
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "BlogPosting",
  "headline": "Someone Tried to Bankrupt My Cloud App With Broken Images and Bad Intentions",
  "image": "https://LanceWW0.github.io/blog/someone-tried-to-bankrupt-my-app/header.png",
  "author": {
    "@type": "Person",
    "name": "Laurence Wayne"
  },
  "datePublished": "2025-11-10",
  "description": "How a rogue user called TheBug0502 sent my Google Cloud bill into the stratosphere — and what I learned about protecting a Firebase backend the hard way.",
  "url": "https://LanceWW0.github.io/blog/someone-tried-to-bankrupt-my-app/"
}
</script>

<a href="/blog" class="back-link">&larr; Back to Blog Posts</a>

<div style="text-align:center;">
  <h1 style="font-size:3em;">Someone Tried to Bankrupt My Cloud App</h1>
  <h2 style="font-weight:normal; color:grey;">How a rogue user sent my Google Cloud bill into the stratosphere.</h2>
  <p style="color:gray;">{{ page.date | date: "%B %-d, %Y" }}</p>
  <div style="max-width:800px; margin:0 auto;">
    <img src="/blog/someone-tried-to-bankrupt-my-app/header.png" alt="Header image for the blog post about a rogue user trying to bankrupt a cloud app." style="max-width:80%; height:auto; padding:16px; border-radius:24px;">
    <p style="font-size:1.35em; line-height:1.7; margin-top:24px;">
      There's a particular kind of Monday morning that every solo developer dreads. You open your email. There's a message from Google Cloud. The subject line contains a number that makes your coffee go cold.
    </p>
    <p style="font-size:1.35em; line-height:1.7;">
      That was my Monday.
    </p>

    <h3 style="margin-top:32px; font-weight:700; font-size:2em;">🔍 The Discovery</h3>
    <p style="font-size:1.35em; line-height:1.7; margin-top:12px;">
      I run a cloud-spotting app called <a href="https://apps.apple.com/sa/app/cloud-point-cloud-identifier/id6480587789">Cloud Point</a> — it lets people photograph the sky, identify cloud types using AI, and share their finds with a global community of people who enjoy looking up. It's a peaceful app. It's about clouds. Clouds are calm. Clouds don't cause drama.
    </p>
    <p style="font-size:1.35em; line-height:1.7;">
      Or so I thought.
    </p>
    <p style="font-size:1.35em; line-height:1.7;">
      I'd noticed my Firebase billing had climbed. Not a gentle drift upward like a cumulus on a summer afternoon — more like a cumulonimbus anvil shooting straight to the tropopause. Something was very wrong.
    </p>
    <p style="font-size:1.35em; line-height:1.7;">
      So I did what any developer does when the bill spikes: I panicked briefly, then opened the Firebase console. And there, nestled among my perfectly normal cloud-spotting users, was a name that will live in infamy.
    </p>
    <p style="font-size:1.35em; line-height:1.7;">
      <strong>TheBug0502.</strong>
    </p>
    <p style="font-size:1.35em; line-height:1.7;">
      A username that, in hindsight, was basically a signed confession.
    </p>

    <h3 style="margin-top:32px; font-weight:700; font-size:2em;">🐛 What TheBug0502 Was Up To</h3>
    <p style="font-size:1.35em; line-height:1.7; margin-top:12px;">
      TheBug0502 had been busy. Incredibly busy. They had uploaded an extraordinary number of images to my app. We're talking volumes of content that would put an entire meteorological society to shame.
    </p>
    <figure style="margin:16px auto; max-width:45%;">
      <video autoplay loop muted playsinline style="width:100%; height:auto; padding:16px; border-radius:24px; display:block;">
        <source src="/blog/someone-tried-to-bankrupt-my-app/many_images.MP4" type="video/mp4">
      </video>
      <figcaption style="font-size:0.95em; color:gray; margin-top:4px;">Scrolling through TheBug0502's uploads. It just keeps going.</figcaption>
    </figure>
    <p style="font-size:1.35em; line-height:1.7;">
      But here's the bizarre part — none of the images were actually displaying. If you navigated to the Firebase Storage URLs, you'd get a permissions error. The images were ghosts. Phantom uploads. Digital vapour clogging up my storage bucket and bleeding my wallet dry.
    </p>
    <figure style="margin:16px auto; max-width:45%;">
      <img src="/blog/someone-tried-to-bankrupt-my-app/example_bug_post.PNG" alt="A TheBug0502 post in Cloud Point showing no image — just the cloud type voting interface with zero hearts." style="width:100%; height:auto; padding:16px; border-radius:24px; display:block;">
      <figcaption style="font-size:0.95em; color:gray; margin-top:4px;">One of TheBug0502's phantom posts — no image, zero hearts, just wasted storage writes.</figcaption>
    </figure>
    <p style="font-size:1.35em; line-height:1.7;">
      The bill was climbing because Firebase charges for storage writes, bandwidth, and Firestore operations. TheBug0502 wasn't trying to use my app. They were trying to <em>exhaust</em> it. Every upload cost me money regardless of whether the image ever rendered for another human being.
    </p>
    <p style="font-size:1.35em; line-height:1.7;">
      They'd somehow got themselves a premium subscription too, which meant the upload limits I'd set for free users weren't doing their job as a natural throttle. Cloud Point gives free users 5 MB of storage — premium unlocks unlimited identification and advanced features. TheBug0502 had apparently decided "unlimited" was a challenge, not a feature.
    </p>
    <p style="font-size:1.35em; line-height:1.7;">
      Whether the subscription was legitimate or spoofed was another question entirely — one I'd need to investigate.
    </p>
    <figure style="margin:16px auto; max-width:45%;">
      <img src="/blog/someone-tried-to-bankrupt-my-app/bug_destroyed_leaderboard.PNG" alt="Cloud Point All Time leaderboard showing TheBug0502 in first place with 2920 points, well ahead of everyone else." style="width:100%; height:auto; padding:16px; border-radius:24px; display:block;">
      <figcaption style="font-size:0.95em; color:gray; margin-top:4px;">TheBug0502 casually sitting at #1 on the All Time leaderboard. Not suspicious at all.</figcaption>
    </figure>

    <h3 style="margin-top:32px; font-weight:700; font-size:2em;">😱 The "Oh No" Moment</h3>
    <p style="font-size:1.35em; line-height:1.7; margin-top:12px;">
      Here's the thing about Firebase: it's brilliant for getting an app off the ground quickly. It handles auth, storage, databases, and hosting with minimal backend code. But that convenience has a shadow side — if you haven't locked things down properly, a single motivated user can run up your bill like a teenager with a parent's credit card at an all-you-can-eat buffet.
    </p>
    <p style="font-size:1.35em; line-height:1.7;">
      My security rules were... fine. They were <em>fine</em>. They checked that users were authenticated before writing. They scoped uploads to user-specific paths. What they didn't do was rate-limit. They didn't cap how much a single user could upload per hour, per day, or per lifetime. They didn't have a concept of a banned user.
    </p>
    <p style="font-size:1.35em; line-height:1.7;">
      In other words, my front door had a lock, but once you were inside, you could rearrange all the furniture and I'd just have to watch.
    </p>

    <h3 style="margin-top:32px; font-weight:700; font-size:2em;">🛠️ The Fix: Triage Mode</h3>
    <p style="font-size:1.35em; line-height:1.7; margin-top:12px;">
      When your backend is actively haemorrhaging money, you don't have the luxury of an elegant solution. You need triage. Here's what I did, roughly in order:
    </p>

    <h4 style="margin-top:24px; font-weight:700; font-size:1.5em; text-align:left;">Step 1: Disable the Account</h4>
    <p style="font-size:1.35em; line-height:1.7; margin-top:8px;">
      Firebase Authentication lets you disable a user account without deleting it. This is important — you want the bleeding to stop, but you also want the evidence intact. Deleting the account would lose the UID, and I needed that to track down all their data.
    </p>
    <p style="font-size:1.35em; line-height:1.7;">
      I found TheBug0502's UID in the Firebase console and hit disable. Immediate effect: no more authenticated requests. The uploads stopped. The sky cleared, metaphorically speaking.
    </p>

    <h4 style="margin-top:24px; font-weight:700; font-size:1.5em; text-align:left;">Step 2: Clean Up the Mess</h4>
    <p style="font-size:1.35em; line-height:1.7; margin-top:8px;">
      TheBug0502 had left data scattered across Firestore collections and Storage buckets. Manually deleting each document and file would have taken hours, so I wrote a quick Node.js cleanup script using the Firebase Admin SDK.
    </p>
    <p style="font-size:1.35em; line-height:1.7;">
      The script queried every collection where a <code>userId</code> field matched their UID, batch-deleted the Firestore documents (in chunks of 500 — Firestore's batch limit), and then swept their Storage folder. One command, a few seconds of runtime, and the digital debris was gone.
    </p>

    <h4 style="margin-top:24px; font-weight:700; font-size:1.5em; text-align:left;">Step 3: Verify the Subscription</h4>
    <p style="font-size:1.35em; line-height:1.7; margin-top:8px;">
      Was the premium subscription real? This matters. If they paid through the App Store, it's a legitimate transaction even if the user is a menace. If they somehow bypassed receipt validation, that's a security hole. I checked my RevenueCat dashboard to confirm whether their subscription was genuine and whether it warranted any further action.
    </p>

    <h3 style="margin-top:32px; font-weight:700; font-size:2em;">📚 The Bigger Lesson: What I Should Have Had in Place</h3>
    <p style="font-size:1.35em; line-height:1.7; margin-top:12px;">
      TheBug0502 was a wake-up call. The kind of wake-up call that arrives in the form of an invoice. Here's what I've since implemented or plan to:
    </p>

    <h4 style="margin-top:24px; font-weight:700; font-size:1.5em; text-align:left;">Rate Limiting via Security Rules</h4>
    <p style="font-size:1.35em; line-height:1.7; margin-top:8px;">
      Firestore Security Rules can reference other documents. This means you can create a rate-limiting mechanism by maintaining a counter document for each user:
    </p>
    <pre style="text-align:left; background:#f4f4f4; padding:16px; border-radius:8px; overflow-x:auto; font-size:0.95em; line-height:1.5;"><code>match /uploads/{userId}/{file} {
  allow write: if request.auth.uid == userId
                &amp;&amp; getAfter(/databases/$(database)/documents/userCounts/$(userId)).data.dailyUploads &lt; 50;
}</code></pre>
    <p style="font-size:1.35em; line-height:1.7; margin-top:12px;">
      It's not perfect — there are race conditions at high concurrency — but for an indie app, it's a solid guardrail.
    </p>

    <h4 style="margin-top:24px; font-weight:700; font-size:1.5em; text-align:left;">A Ban List</h4>
    <p style="font-size:1.35em; line-height:1.7; margin-top:8px;">
      Rather than hardcoding blocked usernames into security rules (which is brittle and reactive), I now maintain a <code>bannedUsers</code> collection in Firestore. The security rules check for membership:
    </p>
    <pre style="text-align:left; background:#f4f4f4; padding:16px; border-radius:8px; overflow-x:auto; font-size:0.95em; line-height:1.5;"><code>allow write: if !exists(/databases/$(database)/documents/bannedUsers/$(request.auth.uid));</code></pre>
    <p style="font-size:1.35em; line-height:1.7; margin-top:12px;">
      Banning someone is now a single Firestore document write. No redeployment needed. Just swift, silent justice from above — like a cloud, but less fluffy.
    </p>

    <h4 style="margin-top:24px; font-weight:700; font-size:1.5em; text-align:left;">Cloud Function Triggers</h4>
    <p style="font-size:1.35em; line-height:1.7; margin-top:8px;">
      A <code>storage.object().onFinalize()</code> Cloud Function now runs on every upload. It checks file size, file type, upload frequency, and a few other heuristics. Anything suspicious gets flagged or auto-deleted before it accumulates cost.
    </p>

    <h4 style="margin-top:24px; font-weight:700; font-size:1.5em; text-align:left;">Budget Alerts</h4>
    <p style="font-size:1.35em; line-height:1.7; margin-top:8px;">
      Google Cloud lets you set budget alerts that notify you when spending hits certain thresholds. I had these set... but not aggressively enough. They're now configured to alert at much lower amounts so I catch anomalies within hours, not days.
    </p>

    <h3 style="margin-top:32px; font-weight:700; font-size:2em;">📜 The Terms of Use I Didn't Have</h3>
    <p style="font-size:1.35em; line-height:1.7; margin-top:12px;">
      Here's an embarrassing admission: before this incident, my app relied entirely on Apple's Standard EULA. That document protects Apple. It does not protect me.
    </p>
    <p style="font-size:1.35em; line-height:1.7;">
      It says nothing about what users can and can't do inside <em>my</em> app. It gives me no formal basis for banning someone, no clause about acceptable use, and no statement that abusive users aren't entitled to refunds.
    </p>
    <p style="font-size:1.35em; line-height:1.7;">
      I've since written proper Terms of Use that cover acceptable use, account termination at my discretion, and an explicit statement that subscriptions are non-refundable following a ban for abuse. If you're an indie developer reading this and you're still relying on Apple's standard EULA — go write your own terms. Today. Before your own TheBug0502 shows up.
    </p>
    <p style="font-size:1.35em; line-height:1.7;">
      You can literally see on the <a href="https://apps.apple.com/sa/app/cloud-point-cloud-identifier/id6480587789">App Store listing</a> that the Terms of Use link pointed straight to Apple's generic EULA. Rookie mistake. Don't be me.
    </p>

    <h3 style="margin-top:32px; font-weight:700; font-size:2em;">❓ What I Still Don't Know</h3>
    <p style="font-size:1.35em; line-height:1.7; margin-top:12px;">
      I don't know <em>why</em> TheBug0502 did this. Was it a bot? A bored teenager? A rival app developer who thought "cloud identifier" was a saturated market? Someone who was genuinely offended by my classification of their altocumulus as a stratocumulus?
    </p>
    <p style="font-size:1.35em; line-height:1.7;">
      The username suggests self-awareness — they knew they were being a pest. The images weren't displaying, which suggests either intentionally corrupted uploads or files that were being uploaded in a way that still triggered write costs without producing valid content. It's possible they were hitting the Firebase endpoints directly, bypassing the Flutter app entirely. If you know your way around the API, you don't need the UI.
    </p>
    <p style="font-size:1.35em; line-height:1.7;">
      Whatever the motivation, the result was the same: a spike in my cloud bill and a crash course in backend hardening that I should have taken before launch.
    </p>

    <h3 style="margin-top:32px; font-weight:700; font-size:2em;">💡 Advice for Other Indie Developers</h3>
    <p style="font-size:1.35em; line-height:1.7; margin-top:12px;">
      If you're building on Firebase (or any pay-per-use backend), here's my unsolicited advice, bought and paid for by TheBug0502's rampage:
    </p>
    <p style="font-size:1.35em; line-height:1.7;">
      <strong>Set budget alerts aggressively.</strong> Don't wait until the bill is alarming. Alert at the point where it's merely <em>surprising</em>.
    </p>
    <p style="font-size:1.35em; line-height:1.7;">
      <strong>Rate-limit everything.</strong> Every write, every upload, every API call. If a single user can generate unlimited operations, they will — whether by malice or by accident.
    </p>
    <p style="font-size:1.35em; line-height:1.7;">
      <strong>Have a ban mechanism ready.</strong> Not "I'll build one when I need it." Have it in your security rules from day one. A <code>bannedUsers</code> collection costs you nothing until you need it, and when you need it, you'll be glad it's there.
    </p>
    <p style="font-size:1.35em; line-height:1.7;">
      <strong>Write your own Terms of Use.</strong> Apple's standard EULA is not your friend. You need terms that give you the explicit right to moderate, suspend, and terminate.
    </p>
    <p style="font-size:1.35em; line-height:1.7;">
      <strong>Don't store what you can't afford.</strong> If your storage costs scale with user uploads, put hard limits on file sizes and counts. Make them generous enough for normal use and punishing enough that abuse is expensive for the abuser, not for you.
    </p>
    <p style="font-size:1.35em; line-height:1.7;">
      <strong>Disable first, delete later.</strong> When you find a problem account, disable it immediately to stop the damage. Keep the UID so you can audit and clean up properly.
    </p>

    <h3 style="margin-top:32px; font-weight:700; font-size:2em;">⛅ The Silver Lining</h3>
    <p style="font-size:1.35em; line-height:1.7; margin-top:12px;">
      Cloud Point is about looking up. It's about noticing the sky, identifying what you see, and sharing it with people who care about the same thing. It's a community app built on curiosity and calm.
    </p>
    <p style="font-size:1.35em; line-height:1.7;">
      TheBug0502 introduced turbulence. But if weather teaches you anything, it's that turbulence passes. The systems I've built since this incident are stronger than what came before. The app is more secure, the rules are tighter, and I now have a proper legal framework to fall back on.
    </p>
    <p style="font-size:1.35em; line-height:1.7;">
      So in a way, thanks, TheBug0502. You were an expensive lesson, but a valuable one.
    </p>
    <p style="font-size:1.35em; line-height:1.7;">
      Now please don't come back. The forecast is clear skies from here.
    </p>

    <hr style="margin-top:32px;">

    <p style="font-size:1.15em; line-height:1.7; font-style:italic; margin-top:16px;">
      If you're curious about the app that survived the assault, you can check out <a href="https://apps.apple.com/sa/app/cloud-point-cloud-identifier/id6480587789">Cloud Point on the App Store</a>. It identifies clouds using AI, lets you share photos with a global community, and it now has much better security rules. You're welcome.
    </p>
    <p style="font-size:1.15em; line-height:1.7; font-style:italic;">
      Got questions or war stories of your own? Drop me a line at <a href="mailto:hello@laurence-wayne.com">hello@laurence-wayne.com</a>.
    </p>
  </div>
  <footer class="post-footer">
    <hr>
    <p>Thanks for reading!</p>
  </footer>
</div>
