---
layout: post
title: "93 Million Tokens, One Very Bad Afternoon"
subtitle: "How a leaked API key burned through $91.60 of OpenAI credits in about 10 minutes."
tags: [OpenAI, Security, Indie Dev, API]
date: 2026-05-10
colour: "#10A37F"
header_image: /blog/93-million-tokens-one-very-bad-afternoon/header.jpg
image: /blog/93-million-tokens-one-very-bad-afternoon/header.jpg
image_desc: "Header image for the blog post about a leaked OpenAI API key burning through credits."
description: "How a leaked API key burned through $91.60 of OpenAI credits in a single afternoon — and what I changed about my secrets hygiene afterwards."
seo:
  type: BlogPosting
---


  <p>
  Here's a sequel I never wanted to write.
  </p>
  <p>
  A few weeks ago I <a href="https://laurence-wayne.com/blog/someone-tried-to-bankrupt-my-app/">published a post</a> about a delightful character called TheBug0502 who tried to bankrupt my cloud-spotting app by uploading thousands of phantom images to Firebase. I closed that post with the optimistic line "the forecast is clear skies from here."
  </p>
  <p>
  As usual, the forecast lied.
  </p>

  <h2>🔍 The Discovery</h2>
  <p>
  This one started not with an email but with a screen I check more often than I'd like to admit: the OpenAI usage dashboard. It exists because some of my apps use OpenAI's API for AI features, and I like to keep an eye on what they're costing me. Normally it's a flat line punctuated by tiny purple bumps — a few cents here, a few cents there. Nothing to lose sleep over.
  </p>
  <p>
  This time the line was not flat.
  </p>
  <!-- TODO: add screenshot of OpenAI Home dashboard showing 93,212,827 tokens, $91.60 spend
  <figure>
  <img src="/blog/93-million-tokens-one-very-bad-afternoon/dashboard.png" alt="OpenAI usage dashboard showing 93,212,827 tokens used and $91.60 in spend." loading="lazy" decoding="async">
  <figcaption>93,212,827 tokens. In one afternoon. From an account that normally moves a few cents a day.</figcaption>
  </figure>
  -->
  <p>
  <strong>93,212,827 tokens.</strong> In one afternoon. From an account that, on a normal day, processes roughly the same number of tokens as a polite email exchange.
  </p>
  <p>
  The "May spend" bar was the colour of a road cone. My £60 monthly budget had been gleefully ignored. The credit balance was draining in real time.
  </p>
  <p>
  I did the only sensible thing. I panicked. (Again...)
  </p>

  <div class="post-embed">
  <div class="tenor-gif-embed" data-postid="9396221664717142950" data-share-method="host" data-aspect-ratio="0.894309" data-width="100%"><a href="https://tenor.com/view/kedinehir-nehirkedi-mitcikedi-gif-9396221664717142950">Kedinehir Nehirkedi GIF</a>from <a href="https://tenor.com/search/kedinehir-gifs">Kedinehir GIFs</a></div>
  <script type="text/javascript" async src="https://tenor.com/embed.js"></script>
  </div>

  <h2>🐛 What Was Happening</h2>
  <p>
  I didn't know. That was the worst part. Unlike TheBug0502, who had a username and a leaderboard ranking, this had no face. Just a column on a chart that suggested <em>something, somewhere</em> was hammering my API key like it owed money.
  </p>
  <p>
  The shape of the spike told a story though. 267 requests producing 93 million tokens averages out at roughly 350,000 tokens per request — which is enormous. That's not a chatbot replying to a user. That's something stuffing entire codebases, long documents, or ludicrous context windows into every call. Whatever it was, it wasn't using the API the way I'd designed any of my apps to use it.
  </p>
  <!-- TODO: add screenshot of usage page showing the spike on May 7 vs the flat line of normal days
  <figure>
  <img src="/blog/93-million-tokens-one-very-bad-afternoon/usage_spike.png" alt="OpenAI usage chart showing one enormous spike on May 7 against a flat baseline." loading="lazy" decoding="async">
  <figcaption>The May 7 spike, against weeks of nothing.</figcaption>
  </figure>
  -->
  <p>
  My best guess at the time: somewhere, somehow, the API key had escaped.
  </p>

  <h2>😱 The "Oh No" Moment</h2>
  <p>
  There's a particular flavour of dread reserved for the moment you realise you might have leaked an API key. It's the dread of not knowing where, when, or how — and knowing that until you find out, you can't be sure it won't happen again.
  </p>
  <p>
  OpenAI charges for input <em>and</em> output tokens, with the heavier models (GPT-4-class and above) priced steeply. At those rates, an automated script doing nothing but firing off bloated requests can chew through your budget faster than you can refresh the page. And refresh I did. Repeatedly. Watching the number tick upward like a meter in a London taxi stuck in traffic.
  </p>

  <h2>🛠️ The Fix: Triage Mode</h2>
  <p>
  Same playbook as last time, different platform. When something is actively setting fire to your account, you don't optimise — you extinguish.
  </p>

  <h3>Step 1: Revoke Everything</h3>
  <p>
  OpenAI lets you delete API keys instantly. So I deleted them. All of them. Every key on my account, regardless of which app it belonged to. Yes, this immediately broke every one of my apps that uses OpenAI. Yes, that's fine. Broken apps make zero API calls. Broken apps cost zero pounds.
  </p>
  <p>
  A brief note for anyone thinking "but I'll just downgrade the key permissions to read-only first, that should stop charges, right?" — no. OpenAI's permission scopes don't restrict the inference endpoints that actually cost money. A read-only or restricted key can still happily generate completions until your credit card weeps. <strong>Delete, don't downgrade.</strong>
  </p>
  <!-- TODO: add screenshot of empty API keys page
  <figure>
  <img src="/blog/93-million-tokens-one-very-bad-afternoon/empty_keys.png" alt="OpenAI API keys page showing no active keys." loading="lazy" decoding="async">
  <figcaption>A reassuringly empty keys list.</figcaption>
  </figure>
  -->

  <h3>Step 2: Lower the Hard Limit</h3>
  <p>
  Even with no keys present, I dropped my organisation's monthly usage limit to a token amount. This is the equivalent of turning the water off at the mains while you fix a leak — even if a new key gets created and somehow leaked again, the damage is capped.
  </p>

  <h3>Step 3: Watch the Lag</h3>
  <p>
  After deleting the keys, the dashboard kept climbing for a while. This was alarming until I realised it was just billing lag — usage data trickles in over 5 to 30 minutes, so the numbers I was watching were already-completed requests being totalled up after the fact, not new requests happening in real time. It eventually settled at $91.60.
  </p>
  <!-- TODO: add screenshot of final usage page showing the settled total spend and the dramatic May 7 bar -->

  <h3>Step 4: Open a Support Ticket</h3>
  <p>
  OpenAI's support is gated behind an AI bot first, which would be funny in any other context. I gave it the relevant facts — unauthorised usage, key deleted, requesting a review — and after some polite confusion it escalated me to a human. A few hours later, charges refunded.
  </p>
  <p>
  This is worth dwelling on for a moment: <strong>OpenAI did the right thing.</strong> They didn't have to. The leak was almost certainly my fault somewhere along the line. But they reviewed the case, saw it was a one-off anomaly on an account with otherwise modest usage, and refunded the unauthorised spend. Credit where it's due.
  </p>

  <h2>🕵️ Where Did the Key Leak From?</h2>
  <p>
  I don't know for certain — and I may never know for certain — but the suspect list is short.
  </p>
  <p>
  I had API keys stored in <code>.env</code> files across several apps. I'd also (here's the embarrassing part) kept a couple in Apple Notes for convenience. And I have apps that use the OpenAI API in production, which means the key was sitting in environment variables on hosting platforms, in build artifacts, and possibly in places I'd long forgotten about.
  </p>
  <p>
  The most likely culprits, in rough order of probability:
  </p>
  <p>
  <strong>Git history.</strong> The classic. If a <code>.env</code> file was ever committed to a repo even briefly — even to a private repo, even to a repo I deleted — the key is in the git history forever. Bots scrape GitHub's public event firehose constantly looking for credentials. Private repos aren't safe either if any collaborator's account gets compromised.
  </p>
  <p>
  <strong>Apple Notes.</strong> Notes themselves are reasonably secure (especially with Advanced Data Protection enabled), but if my Apple ID was ever in a breach, or if I ever screen-shared, screenshotted, or left a device logged in somewhere I shouldn't have, the keys could have walked out that way.
  </p>
  <p>
  <strong>A clipboard manager.</strong> I use one. If I ever copied a key from Notes to paste into a <code>.env</code> file, it's been sitting in clipboard history ever since. Clipboard managers are usually less secure than Notes, and they sync across devices.
  </p>
  <p>
  <strong>Some forgotten place.</strong> A Slack DM. A screen recording. A tutorial I once made. The list of "places a string of characters might end up" gets long when you've been a developer for a while.
  </p>

  <h2>📚 The Bigger Lesson: What I Should Have Had in Place</h2>
  <p>
  Same shape of lesson as the Cloud Point post, different villain. Here's what I've changed:
  </p>

  <h3>One Key Per App</h3>
  <p>
  Previously I'd reused the same API key across multiple apps because it was convenient. It is not convenient when one of them leaks and you have to break all of them at once. From now on, every app gets its own key, in its own OpenAI project, with its own per-project spend limit. If one leaks, only one breaks, and only one can drain budget.
  </p>

  <h3>Per-Project Spend Caps</h3>
  <p>
  OpenAI lets you set hard spending limits at the project level, not just at the org level. This is the real safety net. A leaked key in a project capped at $10/month can't ruin my week even if a botnet finds it. It's a five-minute setup that would have saved me ninety dollars.
  </p>

  <h3>No More Keys in Notes</h3>
  <p>
  Apple Notes is for shopping lists and half-formed blog ideas. Secrets go in a password manager — Apple's built-in Passwords app is free and decent, 1Password and Bitwarden are excellent. These tools are designed for secrets, with audit logs, breach monitoring, and fewer ways to accidentally leak something.
  </p>

  <h3>Audit the Git History</h3>
  <p>
  I went through every repo and ran <code>git log --all --full-history -p | grep -i "sk-"</code> to check whether any keys had ever made it into a commit. Anything that turns up is, by definition, already burned — but knowing where the leaks happened is half the battle for not repeating them.
  </p>

  <h3>Secrets Live in the Hosting Platform</h3>
  <p>
  For deployed apps, the key never touches a file. It's set as an environment variable in the hosting platform's UI (Vercel, Netlify, Railway, whatever). The local <code>.env</code> is gitignored, gets rebuilt from the password manager when needed, and never gets committed.
  </p>

  <h2>💡 Advice for Other Indie Developers</h2>
  <p>
  Bought and paid for, again, by my own carelessness:
  </p>
  <p>
  <strong>One key per app, every time.</strong> No exceptions. No "I'll consolidate them later." Later is when they get leaked.
  </p>
  <p>
  <strong>Set hard spend caps at the project level.</strong> Not just budget alerts — actual hard caps. The difference between "I get an email" and "the API stops working" is the difference between a refund request and bankruptcy.
  </p>
  <p>
  <strong>Don't store secrets in Notes, screenshots, or DMs.</strong> Use a password manager. Yes, even for the keys you're "only using for testing." Especially those.
  </p>
  <p>
  <strong>Audit your git history before you assume you're clean.</strong> Deleting a <code>.env</code> doesn't remove it from git history. The key is still there, on every clone, every fork, every backup, forever.
  </p>
  <p>
  <strong>Delete first, investigate second.</strong> If you suspect a key is compromised, delete it. Don't downgrade permissions. Don't try to rotate gracefully. Delete. The bleeding stops the moment the key dies.
  </p>
  <p>
  <strong>Open a support ticket even if it was your fault.</strong> OpenAI (and most providers) will often refund unauthorised charges, especially if you acted quickly to stop them. The worst they can say is no.
  </p>

  <h2>⛅ The Silver Lining</h2>
  <p>
  In the Cloud Point post I said the systems I'd built were stronger than what came before. Same is true here. My OpenAI setup was casual — one key, reused everywhere, generous limits, secrets stored in places where secrets should not live. Now it's a project per app, hard caps everywhere, no plain-text storage anywhere outside a password manager.
  </p>
  <p>
  There's a recurring theme in indie development that I'm going to have to make peace with: every breach, every spike, every TheBug0502 is the universe charging tuition for a class I should have already taken. The bill is annoying. The lesson tends to stick.
  </p>
  <p>
  So thank you, mysterious key-leaker, whoever and wherever you are. You cost me an afternoon of stress and a refunded $91.60. In exchange you gave me the discipline I should have had all along.
  </p>
  <p>
  Now please, both of you, find a different developer to torment.
  </p>
  <p>
  The forecast — and yes, I know I said this last time — is clear skies from here.
  </p>

  <hr>

  <p class="post-aside">
  If you're using OpenAI (or any pay-per-use API) in your apps and you've just realised your setup looks suspiciously like mine did before this happened, please go and split your keys and set your spend caps right now. Future you will be very grateful.
  </p>
  <p class="post-aside">
  Got your own war stories? Drop me a line at <a href="mailto:hello@laurence-wayne.com">hello@laurence-wayne.com</a>.
  </p>
  <footer class="post-footer">
  <hr>
  <p>Thanks for reading!</p>
  </footer>
