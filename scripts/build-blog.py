#!/usr/bin/env python3
"""Emit the blog as plain static HTML into public/blog/.

Deliberately not a markdown pipeline and not a Vite multi-page entry: Vite copies
publicDir verbatim, so these land in docs/blog/ as real HTML with the prose in the
served file. A pasted link resolves cold, works with JS off, and is greppable in the
deployed bundle. No dependency, no router, no history-mode trap.
"""
import html
import os
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "public" / "blog"
SITE = "https://rilambang.github.io"
CARD = f"{SITE}/og.png"

CSS = """
:root{--bg:#fbfaf7;--ink:#14140f;--muted:#6d6b62;--line:#e6e3da;--accent:#1f4fd8}
*{box-sizing:border-box}
html{scroll-behavior:smooth}
body{margin:0;background:var(--bg);color:var(--ink);
  font:16px/1.65 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
  -webkit-font-smoothing:antialiased}
.wrap{max-width:720px;margin:0 auto;padding:40px 24px 80px}
.top{display:flex;justify-content:space-between;align-items:baseline;
  border-bottom:1px solid var(--line);padding-bottom:14px;margin-bottom:40px;font-size:14px}
.top a{color:var(--muted);text-decoration:none}
.top a:hover{color:var(--accent)}
.top .who{font-weight:600;color:var(--ink);text-decoration:none}
h1{font-size:32px;line-height:1.2;letter-spacing:-0.02em;margin:0 0 10px}
h2{font-size:19px;letter-spacing:-0.01em;margin:34px 0 10px}
h3{font-size:16px;margin:24px 0 6px}
p,li{color:#22221b}
.lede{font-size:18px;color:var(--muted);margin:0 0 34px}
ul,ol{padding-left:20px}
li{margin:6px 0}
a{color:var(--accent)}
code{font:14px/1.5 ui-monospace,SFMono-Regular,Menlo,monospace;
  background:#f1efe8;padding:1px 5px;border-radius:4px}
pre{background:#f1efe8;border:1px solid var(--line);border-radius:10px;
  padding:14px 16px;overflow-x:auto}
pre code{background:none;padding:0}
blockquote{margin:22px 0;padding:2px 0 2px 18px;border-left:3px solid var(--line);color:var(--muted)}
.sources{margin-top:48px;border-top:1px solid var(--line);padding-top:18px;font-size:14px}
.sources h2{font-size:12px;letter-spacing:.1em;text-transform:uppercase;color:var(--muted);margin:0 0 10px}
.sources li{margin:6px 0}
.foot{margin-top:56px;border-top:1px solid var(--line);padding-top:18px;font-size:14px;color:var(--muted)}
/* index */
.list{list-style:none;padding:0;margin:0}
.list li{border-top:1px solid var(--line);padding:20px 0}
.list h2{margin:0 0 6px;font-size:20px}
.list a{text-decoration:none}
.list a:hover h2{color:var(--accent)}
.list p{margin:0;color:var(--muted);font-size:15px}
.tag{font-size:12px;letter-spacing:.08em;text-transform:uppercase;color:var(--accent)}
@media (max-width:600px){.wrap{padding:28px 18px 60px}h1{font-size:26px}}
@media (prefers-reduced-motion:reduce){html{scroll-behavior:auto}}
"""

POSTS = [
    {
        "slug": "kiosk-and-assessment-apps",
        "tag": "Platform rules",
        "title": "Kiosk and assessment apps: what Apple will and won't let you lock",
        "summary": "The hardest problem in a proctored exam app is not the exam. It is that the OS owns the device, and your anti-cheat has to be something Apple agreed to.",
        "body": """
<p class="lede">The hardest problem in a proctored exam app is not the exam. It is that the
operating system owns the device, and every restriction you want has to be one Apple already
agreed to enforce.</p>

<p>Every team building assessment software has the same first instinct: build the lock.
Disable the home button, block the app switcher, kill notifications, watch for screenshots,
detect a second screen. It is a long list of interesting engineering, and almost all of it
is either impossible or unnecessary.</p>

<h2>Two questions decide everything</h2>

<p>Before writing a line of anti-cheat, answer these:</p>

<ol>
  <li><strong>Is the device supervised?</strong> A supervised device is enrolled and managed
  by an organisation — the school or the testing centre owns it and can configure it
  centrally. A student's own iPad is not supervised and never will be.</li>
  <li><strong>Does the OS already have a mode for this?</strong> If it does, your job is to
  turn it on correctly, not to reimplement it worse.</li>
</ol>

<p>Those two questions divide the problem cleanly, and they are the reason a kiosk app is a
smaller engineering project than it looks.</p>

<h2>What Apple actually provides</h2>

<p>For assessment software specifically, Apple ships the <strong>Automatic Assessment
Configuration</strong> framework. Its own summary is the clearest possible statement of
scope: <em>"Enter single-app mode and prevent students from accessing specific system
features while taking an exam."</em></p>

<p>Three properties of it are worth knowing before you plan anything:</p>

<ul>
  <li><strong>It needs no device management.</strong> Apple's own support documentation says
  securing an iPad or Mac for testing with a supported app "requires no additional setup or
  management, such as a device management service." An app that adopts this framework locks
  the device into itself automatically. That is the difference between shipping an exam mode
  to every student and shipping it only to schools with an MDM.</li>
  <li><strong>It is the app's decision, not the tester's.</strong> The app enables it, and
  while it is active the user cannot switch to another app. There is no setup flow the exam
  taker can skip, because there is nothing for them to do.</li>
  <li><strong>Manual modes win, and that is a trap.</strong> If Single App Mode or Guided
  Access is already enabled on the device, "that feature supersedes assessment mode
  restrictions." A school that pre-locked the iPads by hand is not getting your app's
  configuration — they are getting their own, and it may be stricter or looser than you
  assume.</li>
</ul>

<p>Assessment mode on iPadOS is supported from iPadOS 9.3.2 onward, and the same framework
covers macOS — which matters more than it first appears, because it is the same product
decision for two platforms rather than two separate anti-cheat implementations.</p>

<h2>The part that is a product decision, not a technical one</h2>

<p>Once you know what the OS will do, the remaining work is a policy conversation dressed as
engineering:</p>

<p><strong>What do you do with a violation?</strong> A framework that prevents an action gives
you a clean story. A framework that merely observes one does not. If you cannot prevent it,
your options are to warn, to log, or to ignore — and each of those is a different product.
Discovery after the exam is not prevention, and telling a candidate they failed because of
telemetry they cannot see is not a defensible process.</p>

<p><strong>What do you do when the lock fails?</strong> Exam mode is a state the app enters,
which means it can also fail to enter — low battery, a crash, a force-quit, a device the OS
decided to restart. The honest design assumes the lock will break at least once, and decides
in advance what the exam does when it notices. An exam that silently continues in an unlocked
state is worse than one that visibly halts.</p>

<p><strong>Who is the fallback for?</strong> Assessment mode covers the app. It does not cover
a second phone on the desk, a written answer sheet, or a person helping. Every proctoring
system has a human layer eventually; deciding where your layer ends is cheaper than
discovering it during an incident.</p>

<h2>What I'd tell anyone starting this</h2>

<p>Read Apple's platform capabilities before designing the countermeasure, because the
countermeasures you invent yourself are the ones that get rejected, break on OS updates, or
quietly stop working when a device is configured differently than you assumed. The interesting
engineering in a proctored exam app is not the lock — it is the exam runtime: offline
resilience, autosave that survives a crash, a submission that is idempotent, and a state
machine that never loses a candidate's work. The lock is a configuration. Treat it like one,
and spend the effort where the candidate actually feels it.</p>
""",
        "sources": [
            ("Set up iPad and Mac to give tests and assessments — Apple Support", "https://support.apple.com/101976"),
            ("Automatic Assessment Configuration — Apple Developer Documentation", "https://developer.apple.com/documentation/automaticassessmentconfiguration"),
            ("iOS Configuration and APIs for Kiosk and Assessment Apps — WWDC17 session 716", "https://developer.apple.com/videos/play/wwdc2017/716/"),
        ],
    },
    {
        "slug": "splitting-an-app-into-local-packages",
        "tag": "Modularisation",
        "title": "Splitting an app into local Swift packages: what breaks first",
        "summary": "The files move in a day. The boundaries take a quarter. Here is the order things actually break in, and the one rule that keeps the first week from turning into a public-API explosion.",
        "body": """
<p class="lede">Moving files into packages takes a day. Getting the boundaries right takes a
quarter. The gap between those two numbers is where most modularisation projects quietly
stall.</p>

<p>I have done this on more than one app now, and the failures are consistent enough to
predict. This is the order things actually break in.</p>

<h2>1. Resources, and the fact that they fail at runtime</h2>

<p>The first casualty is anything that reads from the bundle. A JSON fixture, a font, a
string file, an asset catalog image. Inside a package, the code needs
<code>Bundle.module</code>. Code that still reaches for <code>Bundle.main</code> compiles
perfectly and returns nil at runtime.</p>

<p>This is the worst class of breakage in the whole migration: it is invisible to the compiler,
invisible in code review, and usually caught by a user rather than a test. Sweep for
<code>Bundle.main</code> and <code>UIImage(named:)</code> <em>before</em> moving anything, and
decide per call site whether it belongs to the package or to the app.</p>

<h2>2. <code>internal</code> becomes <code>public</code>, and everything gets worse</h2>

<p>The moment code lives in another module, <code>internal</code> stops being enough. The
tempting response is to add <code>public</code> until it compiles. That is how a codebase ends
up with a package that exposes forty types and enforces nothing — the boundary exists
physically and not at all conceptually.</p>

<blockquote>The test I use: if a package needs more than a handful of public symbols, it is
not a module. It is a folder that happens to have a manifest.</blockquote>

<p>So the real work is not moving code, it is <em>designing the API you wish existed</em> and
then making the code fit behind it. Write the interface first. If it is awkward to write, the
boundary is in the wrong place, and you have found that out before the expensive part.</p>

<h2>3. Build settings stop being inherited</h2>

<p>A package does not inherit your app target's build settings. The Swift language version, the
warnings you had silenced, optimisation flags, the deployment target — all of it is declared in
the manifest and is now a decision someone has to make deliberately. Do it in one pass, or you
will spend a fortnight on warnings that appear in one module and not the adjacent one.</p>

<h2>4. Names collide immediately</h2>

<p>Every modular codebase has a <code>User</code>, a <code>Config</code>, an
<code>Extensions</code>, a <code>Logger</code>. Once they are in separate modules they are all
legal and all ambiguous at every call site. Type names have to say what they are now — which
sounds like a nit and is actually a boundary leaking into every file that touches two modules.</p>

<h2>5. Tests cannot see across the wall either</h2>

<p><code>@testable import</code> works for a package's own tests. It does not let a test in one
module reach into another's internals. That is the point, but it means tests that were quietly
testing implementation details have to be rewritten against the public surface — or the surface
has to grow to make the behaviour testable. The second option is usually correct, and it is a
useful signal that something is missing from the API.</p>

<h2>6. The awkward middle, and why people quit here</h2>

<p>For a while, everything is public, nothing is faster, and there are more files than before.
That is not the design failing; it is the design being incomplete. The end state — narrow
public surfaces, small rebuilds, obvious ownership — is what pays. Judge it at the end, not in
week two.</p>

<h2>7. Cycles surface, which is the whole point</h2>

<p>The first genuinely valuable thing modularisation does is make circular dependencies
<em>compile errors</em>. In a single target, A using B and B using A is invisible. Across
module boundaries it cannot exist.</p>

<p>That error is not an obstacle in your way. It is the design bug you had been hiding,
finally unable to hide. The wrong fix is to merge the two modules so it compiles again.</p>

<h2>The sequencing I'd use again</h2>

<ol>
  <li><strong>Leaves first.</strong> The things that depend on nothing: design tokens, models,
  a networking core, a logger. Low risk, immediate proof that the tooling works.</li>
  <li><strong>Then the middle.</strong> Shared UI, shared services. This is where the API
  design conversation actually happens.</li>
  <li><strong>Feature modules last.</strong> They are the ones that need the seams below them
  to be settled, and the ones most likely to move again if they are not.</li>
  <li><strong>The app target ends up a shell.</strong> Composition, navigation, configuration.
  If the app target still contains business logic, the split is not finished.</li>
</ol>

<p>The thing I would do differently: agree the vocabulary <em>and</em> the public surface
before anyone starts moving code, in writing, and treat a change to either as a design
decision rather than a refactor. Moving files is mechanical. Everything that made the project
worth doing is not.</p>
""",
        "sources": [
            ("Creating Swift Packages — WWDC19 session 410", "https://developer.apple.com/videos/play/wwdc2019/410/"),
            ("Binary Frameworks in Swift — WWDC19 session 416", "https://developer.apple.com/videos/play/wwdc2019/416/"),
            ("Swift API Design Guidelines", "https://www.swift.org/documentation/api-design-guidelines/"),
        ],
    },
    {
        "slug": "build-time-is-a-dependency-graph-problem",
        "tag": "Build systems",
        "title": "Build time is a dependency-graph problem, not a machine problem",
        "summary": "Faster hardware buys you a constant factor. The graph is the exponent. Why the first fix is almost always deleting a script phase, and what to measure before you touch anything.",
        "body": """
<p class="lede">When builds get slow, the first proposal is always a better machine. A faster
Mac buys a constant factor. The dependency graph is the exponent.</p>

<p>Apple's own guidance on incremental build performance is worth reading before optimising
anything, and it is refreshingly blunt: the things that break incrementality are the things
that make the build redo work it did not need to redo. That is a graph problem.</p>

<h2>Measure the build, not the vibe</h2>

<p>Before changing a setting, get the timing summary from a build and look at where the time
actually goes. Two facts usually fall out immediately:</p>

<ul>
  <li>One or two tasks dominate, and they are not the compiler.</li>
  <li>The build is compiling far more than the change touched.</li>
</ul>

<p>Both point at structure rather than at hardware.</p>

<h2>The most common culprit is a Run Script phase</h2>

<p>A script phase with no declared inputs and outputs runs on <em>every</em> build. It does not
matter that the script is quick. The cost is not the script's runtime, it is that it invalidates
downstream work and forces the build to redo it. A five-line script can be responsible for
minutes.</p>

<p>Three responses, in order of preference:</p>

<ol>
  <li><strong>Delete it.</strong> A surprising share of script phases exist to do something the
  build system already does, or to copy a file that should be a build setting.</li>
  <li><strong>Declare inputs and outputs.</strong> If the script genuinely generates something,
  tell the build system what it reads and what it writes, so it can be skipped when neither
  changed.</li>
  <li><strong>Move it somewhere it is not on the critical path</strong> — earlier in the
  pipeline, or out of the build entirely.</li>
</ol>

<h2>Then look at what a change actually invalidates</h2>

<p>In a single-target app, the answer is usually "everything downstream", which is to say
"most of the app". A change to a shared file in a large target can recompile a majority of the
codebase — not because the compiler is slow, but because the unit of work is the target.</p>

<p>Splitting the target is the fix, and the reason it works is not micro-optimisation. It is
that an unchanged module is genuinely unchanged, and the build system can skip it. The
incremental case — which is the case you live in, hundreds of times a day — gets faster by an
order of magnitude rather than by a percentage.</p>

<h2>Whole-module optimisation, and the debug/release asymmetry</h2>

<p>Whole-module compilation is faster for a clean build and much worse for an incremental one,
because the module is the unit that must be redone. The interesting consequence is that your
debug builds and your release builds want opposite things, and a configuration that is right
for one is wrong for the other. Decide per configuration rather than applying one global
preference.</p>

<h2>Type-checking hot spots are real and they are local</h2>

<p>A single expression that the type checker cannot resolve quickly — a large literal, a deep
nesting of operators, a long chain of overloaded calls — can take longer to compile than the
file around it. The compiler will tell you if you ask it, and the fix is to make the expression
simpler or to name the type explicitly. It is a small, contained edit with an outsize effect.</p>

<h2>Asset catalogs</h2>

<p>Assets are compiled, and a large catalog that changes often is a step you pay for repeatedly.
Keeping generated or throwaway assets out of the catalog is not a style preference; it is
build time.</p>

<h2>What I'd tell a team staring at a slow build</h2>

<ol>
  <li>Get the timing summary. Guess nothing.</li>
  <li>Delete or declare script phases. Cheapest win available, almost always.</li>
  <li>Split the target so unchanged code can be skipped.</li>
  <li>Fix the one or two type-checking hot spots the compiler names.</li>
  <li>Only then consider hardware or caching, and expect a constant factor rather than a step
  change.</li>
</ol>

<p>The uncomfortable part is that the first four are all structural. The build is slow because
the code is shaped in a way that makes it slow, and no amount of machine fixes a shape.</p>
""",
        "sources": [
            ("Improving the speed of incremental builds — Apple Developer Documentation", "https://developer.apple.com/documentation/xcode/improving-the-speed-of-incremental-builds"),
            ("Creating Swift Packages — WWDC19 session 410", "https://developer.apple.com/videos/play/wwdc2019/410/"),
        ],
    },
    {
        "slug": "uikit-to-swiftui-without-a-rewrite",
        "tag": "Migration",
        "title": "UIKit to SwiftUI without a rewrite",
        "summary": "The migration succeeds or fails on one decision: who owns navigation. Everything else is a sequence of small, reversible steps.",
        "body": """
<p class="lede">The migration succeeds or fails on one decision: who owns navigation. Get that
right and the rest is a sequence of small, reversible steps. Get it wrong and you end up with
two systems that each half-know where you are.</p>

<p>I have taken more than one shipped app across this boundary. Nobody regrets the destination.
People regret the order.</p>

<h2>Do not start with the app shell</h2>

<p>The instinct is to rewrite the root and let the screens follow. That inverts the risk: the
shell is the part every screen depends on, and it is the part you cannot ship incrementally.</p>

<p>Start with leaf screens — a detail view, a settings page, a form. Screens that do not own
navigation are the safe unit of migration, because failure costs you one screen rather than
the app.</p>

<h2>Pick one direction of interop at a time</h2>

<p>The two directions are not symmetric and should not be started together:</p>

<ul>
  <li><strong>UIKit shell, SwiftUI leaves</strong> — a UIKit view controller hosts a SwiftUI
  view. This is the low-risk direction, and it is where a migration should begin.</li>
  <li><strong>SwiftUI shell, UIKit leaves</strong> — a SwiftUI view wraps a UIKit component.
  Necessary for the handful of things SwiftUI still does not do well, and the direction that
  tends to accumulate if you are careless.</li>
</ul>

<p>Whichever you are in, know which one it is. A codebase that is doing both, everywhere, with
no rule, has no migration at all.</p>

<h2>Navigation is the seam, so give it exactly one owner</h2>

<p>This is the decision that determines whether the migration is a project or a permanent tax.
Two systems that both believe they own the stack produce bugs that are extremely hard to
diagnose: a screen that appears twice, a back button that does nothing, state that resets on
pop.</p>

<p>Keep navigation in one place for the whole migration — whether that is the UIKit navigation
controller or a SwiftUI stack driven by a coordinator. The other side renders content and
reports events. It does not push.</p>

<h2>State ownership: pass data in, events out</h2>

<p>Do not let the two worlds observe each other's state. A view controller watching a SwiftUI
observable object, or a SwiftUI view holding a reference to a view controller and polling it,
is a future bug in both directions.</p>

<p>The contract that survives: the parent passes a value in and receives callbacks out. That is
enough for almost every screen, and it keeps either side replaceable.</p>

<h2>What actually bites</h2>

<ul>
  <li><strong>Keyboard avoidance.</strong> Two systems, two opinions, one screen. This is the
  most common source of visual regressions during the swap and it is worth a dedicated pass.</li>
  <li><strong>List identity.</strong> A list that reuses cells and a list that keys on identity
  behave differently on update. Missing or unstable identity produces animations and state loss
  that look like a rendering bug and are not.</li>
  <li><strong>Lifecycle timing.</strong> "Appeared" does not mean the same instant in both
  systems. Code that kicks off work on appear and cancels on disappear will behave differently,
  and the difference shows up under a slow network, not on your desk.</li>
  <li><strong>Measurement.</strong> Geometry readers used for layout maths are a smell in a
  declarative system. Most of the time the layout you were computing by hand is a two-line
  native layout, and the manual version is the expensive one.</li>
</ul>

<h2>Availability is part of the plan, not an afterthought</h2>

<p>Everything you adopt has to exist on your deployment target, and anything newer needs a
working fallback — not an <code>#available</code> that silently renders nothing. Write down the
minimum supported version and treat every adoption above it as a decision with a cost.</p>

<h2>How you know it is finished</h2>

<p>The app target compiles without importing the old UI framework outside the places the
platform genuinely requires it. Until then, you have a mixed app, which is a perfectly good
state to ship from — but it is a state, not an outcome. Name the finish line, or the migration
becomes the architecture.</p>
""",
        "sources": [
            ("Introducing SwiftUI: Building Your First App — WWDC19 session 204", "https://developer.apple.com/videos/play/wwdc2019/204/"),
            ("SwiftUI Essentials — WWDC19 session 216", "https://developer.apple.com/videos/play/wwdc2019/216/"),
            ("Human Interface Guidelines — Apple Developer", "https://developer.apple.com/design/human-interface-guidelines"),
        ],
    },
    {
        "slug": "a-design-system-is-a-review-policy",
        "tag": "Craft",
        "title": "A design system is a review policy, not a library",
        "summary": "Importing a token package changes nothing. The system holds when the correct choice is easier than the wrong one — and when review refuses the local override.",
        "body": """
<p class="lede">A design system is not a package you import. It is a set of decisions that
review enforces, and the package is only the place those decisions live.</p>

<p>I have watched more than one design system die at screen three. The failure is always the
same and never looks like a design problem at the time: someone had a deadline, the component
almost fit, and they wrote the value inline. That file is now the precedent.</p>

<h2>Three copies of every value</h2>

<p>In a healthy system there are exactly two places a colour can come from: the design source,
and the token that mirrors it. In a real codebase there is a third — the literal somebody
pasted into a view — and that is the one that ages badly. It does not break. It just drifts,
one hex at a time, until nobody can change the brand colour without a treasure hunt.</p>

<h2>What makes it stick</h2>

<ol>
  <li><strong>Token names describe intent, not value.</strong> <code>surface</code>,
  <code>danger</code>, <code>border-subtle</code> survive a redesign. <code>grey300</code>
  does not, and it invites the next person to pick a neighbouring number by eye.</li>
  <li><strong>The default has to be the correct one.</strong> If using the system is harder
  than not using it, the system loses, every time, to someone under pressure. Convenience beats
  policy.</li>
  <li><strong>The component owns its own spacing.</strong> A system where every screen
  re-specifies the padding of the same button is a component in name only.</li>
  <li><strong>Review rejects the override.</strong> This is the actual enforcement. Not a lint
  rule, not a guideline — a person saying no, in a review, with a reason. The first few of
  those set the norm for the next hundred.</li>
</ol>

<h2>What I check in review</h2>

<ul>
  <li>No raw colour values outside the tokens file. None, including "just for the shadow".</li>
  <li>No font sizes written as numbers in a view.</li>
  <li>Spacing from the scale — not <code>13</code> because it looked right that afternoon.</li>
  <li>A component not re-specifying spacing the component already defines.</li>
  <li>New tokens: does an existing one already mean this? Duplicated intent is how a token file
  becomes a colour palette.</li>
</ul>

<h2>The honest cost, said out loud</h2>

<p>A design system slows down the first screen and speeds up the tenth. That is the entire trade,
and it is a bad deal if you only ever build one screen. Teams abandon systems because nobody
said the first half of that sentence, so the first screen feels like overhead and the tenth
never arrives.</p>

<p>Say it in the same breath as the plan. "This will be slower for a fortnight and faster after
that" is a sentence a team can agree to. "We are adopting a design system" is not.</p>

<h2>The design side is a person, not a handoff</h2>

<p>The systems I have seen work have a designer who reads the diff, or a developer who has the
design file open. The ones that fail have a Figma link and a prayer. The gap between the mock
and the implementation is where defaults get invented — and invented defaults are the beginning
of the third copy.</p>

<p>None of this is about tooling. It is about which choice is the path of least resistance on a
Thursday afternoon, and who is standing between the deadline and the hardcoded hex.</p>
""",
        "sources": [
            ("Human Interface Guidelines — Apple Developer", "https://developer.apple.com/design/human-interface-guidelines"),
            ("Swift API Design Guidelines", "https://www.swift.org/documentation/api-design-guidelines/"),
        ],
    },
    {
        "slug": "how-i-review-ios-pull-requests",
        "tag": "Behaviour",
        "title": "How I review iOS pull requests",
        "summary": "Risk before style, deletion before addition, and three questions I ask on every diff. What I refuse to merge, and why the comment that explains the failure mode is worth ten that state the rule.",
        "body": """
<p class="lede">A review that starts with naming has already wasted its most useful attention.
Here is the order I read a diff in, and the things I refuse to merge.</p>

<h2>The order</h2>

<ol>
  <li><strong>Does it do what the description says?</strong> Not what the code says — what the
  description claims. If they diverge, that is the first comment, before anything else.</li>
  <li><strong>Can it crash?</strong> Force unwraps, array indexing, casts, anything that
  assumes a shape it has not checked.</li>
  <li><strong>What is the failure path?</strong> Every network call fails. Every write can be
  interrupted. A diff that only handles success is half a diff.</li>
  <li><strong>What was deleted?</strong> Removed guards and removed tests first.</li>
  <li><strong>Style.</strong> Last, and usually not at all.</li>
</ol>

<h2>Three questions, every time</h2>

<ul>
  <li><strong>What happens on a slow network?</strong> Not down — slow. That is the state
  where double submissions, spinners that never resolve, and buttons that fire twice live.</li>
  <li><strong>What happens if the user backgrounds the app mid-operation?</strong> Very few
  diffs survive this question unconcerned, and the ones that do are the ones I trust.</li>
  <li><strong>What happens the second time?</strong> Is this operation idempotent? Retrying a
  payment, a submission, a sync — the second call is where data loss is born.</li>
</ul>

<h2>What I refuse to merge</h2>

<ul>
  <li>A skipped or disabled test. If it cannot pass, delete it and say so; a disabled test is a
  lie that gets inherited.</li>
  <li>A test that asserts nothing, or that asserts the mock.</li>
  <li><code>try?</code> on a write. Swallowing a failed save is how a user loses an hour of work
  and nobody finds out.</li>
  <li>A new dependency for something the platform already does.</li>
  <li>A control with no accessibility label. This is not a later ticket; it is an unfinished
  control.</li>
</ul>

<h2>Concurrency, because that is where the crashes actually are</h2>

<p>Most of the real defects I find in review are structural rather than logical:</p>

<ul>
  <li>A task started from a view that outlives the view, and writes to state after it is gone.</li>
  <li>State mutated off the main actor that a view reads on it.</li>
  <li>Two writes racing to the same store with no single owner.</li>
</ul>

<p>These do not need a deep read of the logic. They need one question: <em>who owns this state,
and on which actor is it touched?</em> If the diff cannot answer in one sentence, that is the
comment.</p>

<h2>Two habits that pay</h2>

<p><strong>I review the smallest possible unit, early.</strong> A large diff gets a shallow read
and a rubber stamp, and both parties know it. Several small diffs get real attention. If a
change is too big to review carefully, the review is not the problem to fix — the change is.</p>

<p><strong>I explain the failure, not the rule.</strong> "This will double-submit if the user
taps twice before the response" teaches something. "Don't allow double taps" produces a fix for
this instance and the same bug next month. The comment that names the failure mode is worth ten
that quote the standard — and it is the difference between a review and a gate.</p>

<h2>What review is for</h2>

<p>Not catching typos, and not demonstrating that the reviewer read the code. It is the last
point at which the person who wrote something still remembers why, and someone else can ask
"what happens when this goes wrong?" while the answer is cheap. Everything else about it is
negotiable. That is not.</p>
""",
        "sources": [
            ("Swift API Design Guidelines", "https://www.swift.org/documentation/api-design-guidelines/"),
            ("Human Interface Guidelines — Apple Developer", "https://developer.apple.com/design/human-interface-guidelines"),
        ],
    },
    {
        "slug": "the-ios-stack-i-actually-reach-for",
        "tag": "Tooling",
        "title": "The iOS stack I actually reach for",
        "summary": "Not the stack I would pick on a greenfield project — the one I reach for on someone else's codebase at 3am. Every choice is priced by the next engineer's ability to debug it.",
        "body": """
<p class="lede">This is not the stack I would choose on a blank project. It is the one I reach
for on a codebase I did not write, where the deciding question is who has to debug this at
3am.</p>

<h2>Language and concurrency</h2>

<p>Swift, on the newest language mode the team can hold, with strict concurrency on rather than
aspirational. Adopting it late costs more than adopting it early, because the cost is
proportional to how much code you already have. Everything is main-actor by default and
explicitly off it only where work is genuinely expensive — the opposite default produces code
that is concurrent by accident.</p>

<h2>UI</h2>

<p>SwiftUI for new screens, UIKit where the platform still requires it or where a table or
collection needs control the declarative layer does not yet give. That is an honest position
rather than a religious one: a rewrite that ships is better than a purity that does not.</p>

<p>Navigation has one owner. Always. Two systems that both think they own the stack produce the
worst bugs to diagnose.</p>

<h2>Structure</h2>

<p>Local Swift packages per seam, the app target as a thin shell. The reason is not elegance —
it is that an unchanged module does not get rebuilt, and a circular dependency becomes a
compile error rather than a convention nobody follows.</p>

<h2>Networking</h2>

<p>Whatever the codebase already has, unless it is actively harmful. A second networking layer
is a worse outcome than an imperfect first one. On a greenfield app I would reach for the
platform's own concurrency tools over a reactive framework; on an existing app I leave the
existing one alone until there is a reason to move it.</p>

<h2>Persistence</h2>

<p>The platform's own persistence before a hand-rolled SQL layer, and a real constraint in the
schema before validation in the app. Constraints are enforced under concurrency and app bugs
are not. Where the data matters, the second copy of the truth is the one that goes stale.</p>

<h2>Strings</h2>

<p>A single string catalogue, referenced by key. Never a literal in a view — not because of
localisation, though that too, but because a literal in a view is unsearchable and permanent.
This is the cheapest discipline on the list and the one most often skipped.</p>

<h2>Testing</h2>

<p>Tests for logic, first and always: parsers, state machines, anything with a branch. They run
in seconds and they catch the regressions that matter. UI tests sparingly, on the flows that
carry money or data, because they are slow and inherently flaky and a flaky suite gets ignored
— which is worse than not having one.</p>

<p>A test that cannot fail is not a test. If I cannot describe the change that would turn it
red, it is decoration.</p>

<h2>Third-party dependencies</h2>

<p>Only for a problem the platform does not solve. The bar is not popularity, it is: can I read
this library when it misbehaves, and is anyone still maintaining it in two years? A small
dependency I understand beats a large one I do not, and "we might need it later" has never once
been true.</p>

<h2>Build health</h2>

<p>Build warnings treated as a budget rather than as weather. A codebase with three hundred
warnings cannot notice the fourth hundred, and one of those was going to tell you that a main
thread write had just become an act of faith.</p>

<h2>The meta-decision</h2>

<p>I have changed stacks more than once, and each time the framework-specific knowledge expired
faster than I expected. What survived is the habit underneath it: prefer the boring choice,
prefer the platform's own tool, prefer the option a new hire can debug on their first weekend
on call, and leave the codebase so that the next person's hard problem is the interesting one
— not the one you set up for them by being clever.</p>
""",
        "sources": [
            ("Swift API Design Guidelines", "https://www.swift.org/documentation/api-design-guidelines/"),
            ("Improving the speed of incremental builds — Apple Developer Documentation", "https://developer.apple.com/documentation/xcode/improving-the-speed-of-incremental-builds"),
            ("Human Interface Guidelines — Apple Developer", "https://developer.apple.com/design/human-interface-guidelines"),
        ],
    },
]


def page(title, description, url, body, extra_head=""):
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(description)}">
<link rel="canonical" href="{url}">
<meta property="og:type" content="article">
<meta property="og:title" content="{html.escape(title)}">
<meta property="og:description" content="{html.escape(description)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{CARD}">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'><rect width='32' height='32' rx='7' fill='%231f4fd8'/><text x='16' y='23' font-family='Georgia,serif' font-size='20' fill='%23fbfaf7' text-anchor='middle'>R</text></svg>">
<link rel="stylesheet" href="./blog.css">
{extra_head}</head>
<body>
<div class="wrap">
  <div class="top">
    <a class="who" href="/">Muhammad Ilham Rilambang</a>
    <a href="./index.html">Writing</a>
  </div>
{body}
</div>
</body>
</html>
"""


def render_post(p):
    src = "".join(
        f'      <li><a href="{u}" target="_blank" rel="noreferrer">{html.escape(t)}</a></li>\n'
        for t, u in p["sources"]
    )
    body = (
        f'  <p class="tag">{html.escape(p["tag"])}</p>\n'
        f'  <h1>{html.escape(p["title"])}</h1>\n'
        f'{p["body"].strip()}\n'
        f'  <div class="sources">\n    <h2>Sources</h2>\n    <ul>\n{src}    </ul>\n  </div>\n'
        f'  <p class="foot">Written from experience shipping iOS apps. No client names, no '
        f'internal details, no unpublished numbers — everything citable here is public.</p>\n'
    )
    url = f"{SITE}/blog/{p['slug']}.html"
    return page(p["title"], p["summary"], url, body)


def render_index():
    items = "".join(
        f'      <li>\n'
        f'        <a href="./{p["slug"]}.html"><h2>{html.escape(p["title"])}</h2></a>\n'
        f'        <p>{html.escape(p["summary"])}</p>\n'
        f'      </li>\n'
        for p in POSTS
    )
    body = (
        '  <h1>Writing</h1>\n'
        '  <p class="lede">Notes on the craft of iOS — platform rules, modularisation, build\n'
        '  health, migration and review practice. Seven pieces, written October 2026.</p>\n'
        f'  <ul class="list">\n{items}  </ul>\n'
        '  <p class="foot">Everything here is public and citable — no employer internals, no\n'
        '  colleague names, no unpublished metrics. If a claim needs a source it has one.</p>\n'
    )
    return page(
        "Writing — Muhammad Ilham Rilambang",
        "Notes on the craft of iOS: platform rules, modularisation, build health, migration and review practice.",
        f"{SITE}/blog/",
        body,
    )


OUT.mkdir(parents=True, exist_ok=True)
(OUT / "blog.css").write_text(CSS.lstrip())
(OUT / "index.html").write_text(render_index())
for p in POSTS:
    (OUT / f"{p['slug']}.html").write_text(render_post(p))
print(f"{len(POSTS)} posts + index + css -> {OUT}")
