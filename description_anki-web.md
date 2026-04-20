<h2>Friend Pack</h2>

<p>
Friend Pack is an Anki Browser add-on focused on faster tag-based review workflows.
It is built around three main tools:
</p>

<ul>
  <li><b>Missed Tags</b> for quickly tagging missed questions and repeat misses</li>
  <li><b>Find QIDs</b> for searching notes by question-bank ID</li>
  <li><b>Custom Tags</b> for adding your own preset tag actions from the right-click menu</li>
</ul>

<h3>What it does</h3>

<ul>
  <li>Adds a <b>Missed Tags</b> submenu in the Browser right-click menu</li>
  <li>Supports source-specific tagging for <b>UWorld</b>, <b>NBME</b>, and <b>Amboss</b></li>
  <li>Supports repeat-miss tagging such as <b>2x Missed</b></li>
  <li>Supports marking cards as <b>Guessed Correct</b></li>
  <li>Supports custom extra sources through an <b>Other</b> submenu</li>
  <li>Adds <b>QID search</b> tools for finding notes tagged with question-bank IDs</li>
  <li>Adds a <b>Custom Tags</b> submenu for your own saved tag presets</li>
  <li>Lets you rename menu labels and adjust tag roots to fit your own workflow</li>
</ul>

<h3>Designed for tag-based review</h3>

<p>
Friend Pack is most useful if you organize Anki notes around missed questions, question-bank sources, and review-state tags.
The default setup is built around a structured missed-question system using a primary tag such as:
</p>
<pre><code>##Missed-Qs</code></pre>

<p>
From that root, Friend Pack can build more specific child tags for sources like UWorld, NBME,
Amboss, and other custom review resources.
</p>

<h3>Example workflow</h3>

<p>With the default configuration, right-clicking selected notes in the Browser gives quick actions like:</p>

<ul>
  <li><b>♦️ Base</b></li>
  <li><b>🗺️ UW*rld</b></li>
  <li><b>🧠 NBME</b></li>
  <li><b>🦠 Amb*ss</b></li>
  <li><b>2x Missed 📌</b></li>
  <li><b>Guessed Correct 🎫</b></li>
  <li><b>Other</b> submenu for other Qbank resources</li>
</ul>

<p>Example tags created by default may look like:</p>

<pre><code>##Missed-Qs
##Missed-Qs::UW_Tests::...
##Missed-Qs::NBME::...
##Missed-Qs::Amboss::...
##Missed-Qs::2x::...
#Custom::correct_marked</code></pre>

<h3>Custom Tags bonus menu</h3>

<p>
Friend Pack also includes a lightweight <b>Custom Tags</b> menu for users who want
fast preset tagging actions without manually typing tags each time.
This is useful for personal workflow tags such as:
</p>

<pre><code>#Custom::Review
#Custom::Imaging</code></pre>

<h3>Configurable</h3>

<p>
Most users only need small config changes.
The add-on can be customized to:
</p>

<ul>
  <li>Rename the Browser menu title</li>
  <li>Rename the Missed Tags submenu</li>
  <li>Change the primary missed-question tag root</li>
  <li>Change source tag segments for UWorld, NBME, and Amboss</li>
  <li>Set a QID parent tag for search</li>
  <li>Choose whether QID search defaults to missed-only mode</li>
  <li>Add your own custom preset tag actions</li>
</ul>

<h3>Good fit for users who:</h3>

<ul>
  <li>Review missed questions in Anki after doing Q-banks</li>
  <li>Want quicker tagging from the Browser right-click menu</li>
  <li>Use UWorld, NBME, Amboss, or other tagged question sources</li>
  <li>Want a cleaner workflow for missed-question tracking and QID lookup</li>
</ul>

<h3>Notes</h3>

<ul>
  <li>This add-on is Browser-focused</li>
  <li>It works best when your notes already use a reasonably consistent tag structure</li>
  <li>The shipped defaults are a starting point and can be adjusted to match your own system</li>
</ul>