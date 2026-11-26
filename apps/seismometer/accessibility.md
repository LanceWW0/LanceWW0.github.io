---
layout: default
title: Seismometer – Accessibility
description: How Seismometer works with Larger Text, Bold Text, Increase Contrast, Reduce Motion, VoiceOver and landscape on iPhone, and what hasn't been checked yet.
app_icon: /assets/images/apps/seismometer/logo.png
permalink: /apps/seismometer/accessibility/
last_updated: 2026-11-26
---

<a href="/apps/seismometer/" class="back-link">← Back to Seismometer</a>

<div class="accessibility-statement">

<header class="privacy-header">
  <img class="app-icon" src="{{ page.app_icon }}" alt="Seismometer app icon" loading="lazy" decoding="async">
  <h1>Accessibility</h1>
  <p class="last-updated">Last updated: <time datetime="{{ page.last_updated }}">{{ page.last_updated | date: "%-d %B %Y" }}</time></p>
</header>

<div class="privacy-content">

<section class="privacy-section" aria-labelledby="introduction">
  <h2 id="introduction"><span class="section-icon" aria-hidden="true">👋</span> Introduction</h2>
  <p>Seismometer works on iPhone and iPad. It follows the accessibility settings you choose in Settings &gt; Accessibility. For two of them, Increase Contrast and Reduce Motion, the app's own Settings &gt; Accessibility also has a switch, if you want them in this app only.</p>
  <p>On iPad, the app uses the iPhone layout at a larger size. It hasn't been laid out for iPad.</p>
  <p>Most of what's below has been checked in automated tests and in the iOS Simulator, but not yet on a real iPhone or iPad. The section <a href="#not-checked">Not done, or not checked yet</a> says exactly what's missing.</p>
</section>

<section class="privacy-section" aria-labelledby="larger-text">
  <h2 id="larger-text"><span class="section-icon" aria-hidden="true">🔠</span> Larger Text</h2>
  <ul>
    <li>All text follows your text size, up to the largest size iOS offers (310%).</li>
    <li>From 150%, things that sit side by side stack instead: the readings on Live and Meter, rows with a value, and the recordings and lessons lists.</li>
    <li>Sheets scroll as one page.</li>
    <li>Titles, tabs and segmented options stop growing early, because they can't grow sideways. Touch and hold a tab or an option to see its name at full size.</li>
    <li>Numbers on the graphs grow to 150% at most.</li>
  </ul>
</section>

<section class="privacy-section" aria-labelledby="bold-text">
  <h2 id="bold-text"><span class="section-icon" aria-hidden="true">🅱️</span> Bold Text</h2>
  <p>With Bold Text switched on, all text is bold, including the text drawn on the graphs and in the lesson pictures.</p>
</section>

<section class="privacy-section" aria-labelledby="contrast">
  <h2 id="contrast"><span class="section-icon" aria-hidden="true">🌓</span> Contrast</h2>
  <p>With Increase Contrast switched on, the app uses high-contrast versions of its dark and light themes:</p>
  <ul>
    <li>black or white backgrounds;</li>
    <li>text at a contrast ratio of 7:1 or better;</li>
    <li>borders and main grid lines at 3:1 or better;</li>
    <li>a heavier trace with no glow;</li>
    <li>the chosen option of a segmented control shown inverted.</li>
  </ul>
  <p>You can also switch this on in the app only, under Settings &gt; Accessibility &gt; Increase contrast.</p>
</section>

<section class="privacy-section" aria-labelledby="reduce-motion">
  <h2 id="reduce-motion"><span class="section-icon" aria-hidden="true">⏸️</span> Reduce Motion</h2>
  <ul>
    <li>Decorative movement stops: the lesson illustrations, and glides and transitions inside the app.</li>
    <li>The trace keeps scrolling, because the trace is the measurement.</li>
    <li>On the Pro screen, the looping examples become still pictures, and the highlighted feature has no spreading rings.</li>
    <li>The banner on the 6-second X, Y and Z preview has no draining bar.</li>
    <li>You can also switch this on in the app only, under Settings &gt; Accessibility &gt; Reduce motion.</li>
  </ul>
</section>

<section class="privacy-section" aria-labelledby="voiceover">
  <h2 id="voiceover"><span class="section-icon" aria-hidden="true">🗣️</span> VoiceOver, Switch Control and Keyboards</h2>
  <ul>
    <li>Every reading has a spoken label and value, with its units in words, and every control is a named button.</li>
    <li>Changes that don't move the focus are announced: a recording starting and stopping, the Meter's hold and reset, and the notes asking you to lay the phone flat.</li>
    <li>Settings &gt; Peak cues &gt; Speak peaks has the size of each knock spoken as it's detected.</li>
    <li>A saved recording is zoomed with VoiceOver's adjust gesture, and moved with the "Move earlier" and "Move later" actions.</li>
    <li>On the Pro screen, a screen reader gets one description in place of each moving example.</li>
    <li>Controls are standard buttons that can take focus. The app's own segmented control takes focus, shows a focus ring and is chosen with Space or Enter.</li>
  </ul>
</section>

<section class="privacy-section" aria-labelledby="touch">
  <h2 id="touch"><span class="section-icon" aria-hidden="true">👆</span> Touch</h2>
  <ul>
    <li>Every control is at least 48 × 48 points.</li>
    <li>Zooming and moving along a saved recording have buttons, so nothing needs a pinch or a drag.</li>
  </ul>
</section>

<section class="privacy-section" aria-labelledby="landscape">
  <h2 id="landscape"><span class="section-icon" aria-hidden="true">📱</span> Landscape on iPhone</h2>
  <p>On iPhone, the app follows the phone into landscape, either way round (but not upside down), for a phone fixed on its side, such as on a wheelchair mount.</p>
  <ul>
    <li>The tabs run down the left edge instead of along the bottom.</li>
    <li>Live gives the graph the full height, with the title, controls and readings beside it. Meter shows the level beside its other readings and buttons.</li>
    <li>The introduction sets each picture beside its words, and its spirit level still moves towards the higher edge of the phone.</li>
    <li>Sheets stop 48 points short of the top, so a tap above one closes it, and their buttons scroll with their content.</li>
    <li>A name you're typing, for a new recording or a renamed one, stays in view above the keyboard.</li>
    <li>Pages keep clear of the camera cut-out at either end and of the home indicator.</li>
    <li>Turning the phone keeps the trace, a recording in progress and the page you have open.</li>
    <li>The system's rotation lock holds the picture still.</li>
  </ul>
</section>

<section class="privacy-section" aria-labelledby="haptics">
  <h2 id="haptics"><span class="section-icon" aria-hidden="true">🔔</span> Haptics and Sound</h2>
  <ul>
    <li>Haptics can be turned off in the app's Settings.</li>
    <li>Optional cues, a soft tap, a click or both, can mark detected peaks. They're off by default, because a cue is itself a vibration and shows on the trace.</li>
  </ul>
</section>

<section class="privacy-section" aria-labelledby="checked">
  <h2 id="checked"><span class="section-icon" aria-hidden="true">🧪</span> How This Has Been Checked</h2>
  <ul>
    <li>Automated tests go through every screen, sheet and page in the dark and light themes and their high-contrast versions, with the phone upright and on its side. They check text contrast measured from the pixels drawn, touch target sizes, and a spoken label on every control.</li>
    <li>Other tests go through them again at 310% and 200% text, on a standard and a small phone and with Bold Text, and fail if anything overflows or a control can't be reached. They do the same with the phone on its side, at iPhone 15 Pro and iPhone SE sizes.</li>
    <li>Tests look through what a screen reader is given for unnamed controls and for buttons that can't be activated, and cover the announcements and actions.</li>
    <li>In the iOS Simulator, Increase Contrast and the largest text size reached the app, and it changed as described.</li>
    <li>Landscape was tried in the iOS Simulator. The app turned both ways. The first step of the introduction, Live, the tabs and the sensitivity sheet were as described, a tap above the sheet closed it, and turning back upright kept the open tab. The spirit level moved the right way on simulated data.</li>
  </ul>
</section>

<section class="privacy-section" aria-labelledby="not-checked">
  <h2 id="not-checked"><span class="section-icon" aria-hidden="true">🚧</span> Not Done, or Not Checked Yet</h2>
  <ul>
    <li>Nothing on this page has been tried on a real iPhone or iPad yet. Bold Text and Reduce Motion have been checked only in tests.</li>
    <li>Nobody has yet used the app with VoiceOver switched on. The tests check what VoiceOver is given, not what it's like to use.</li>
    <li>Landscape hasn't been tried on a real phone, or on one fixed in a mount. Meter, a saved recording, the lessons, Settings and the other sheets have been seen on a phone on its side only as test pictures, and the keyboard there only in tests.</li>
    <li>The app has no rotation lock of its own, so the picture can turn as you lay the phone down flat. The system's rotation lock stops that. How often this happens on a real phone hasn't been tried.</li>
    <li>Only an iPhone on its side gets the side-by-side layout. An iPad gets the upright layout. Apart from a test that opens the first screen at tablet sizes, this hasn't been checked.</li>
    <li>The moving trace has no equivalent in sound. With a screen reader you get the readings and, with Speak peaks, each knock, but not the shape of the wave.</li>
  </ul>
</section>

<section class="privacy-section contact-card" aria-labelledby="feedback">
  <h2 id="feedback"><span class="section-icon" aria-hidden="true">📧</span> Feedback</h2>
  <p>If anything in Seismometer is hard to use with your accessibility settings, please get in touch. It helps to say which device you're using and which settings you have switched on.</p>
  <a href="mailto:hello@laurence-wayne.com" class="contact-email">
    <span aria-hidden="true">📧</span> hello@laurence-wayne.com
  </a>
</section>

</div>

</div>
