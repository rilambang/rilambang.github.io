---
title: An audit week on a shipping exam app: fix by consequence, then fix your fixes
tag: Hardening
summary: I ranked an audit backlog by what a failure costs a student, not by how long it takes. Then some fixes broke things of their own: a debugging library still in the binary, a coverage gate that could not fail, tests that slept. What I changed, in the order I would do it again.
---
The app is a proctored exam client used by schools. After a long run of feature work I spent a few days on nothing but an audit backlog: a long list of small items and no new screens. This is what I fixed first, what I fixed second, and the three fixes that needed fixing.

Nothing here is specific to one product. It is the shape of a hardening week on any app where a failure lands on a person who cannot retry.

## Rank by consequence, not by effort

The backlog arrived in the order people had noticed things. Effort is the wrong sort key, because the cheap items are usually the untidy ones. I sorted by one question instead: what does this cost the person holding the phone?

::fig audit-ladder

**First, anything that can lose a student's work or lock them out.** An answer waiting to upload has to outlive a session change, so a student who is signed out mid-exam does not lose what they already answered. A keychain read that fails because the phone is still locked after a restart is not "signed out". It is "not yet", so the app retries once the phone unlocks instead of treating the failure as a verdict. And crash and performance reporting has to be on in every build, with symbol files uploaded in every lane, because a failure you cannot see at scale is one you find out about from a teacher.

**Second, anything that can fail quietly later.** The base view model became main-actor isolated, so isolation is the default and leaving it is the explicit choice. The architecture rules that had lived in a document moved into the lint job, where a violation fails the pipeline.

**Third, anything slow, flaky or untidy.** It matters, and it can wait for a quiet afternoon.

## Subtract before you add

Some of the best fixes were deletions. Three dependencies nobody imported were removed. Two background modes the app declared and never used came out of the plist. A pair of plain-HTTP exceptions for a video host went away once the app upgraded those links to HTTPS before loading exam content. Every permission and exception you carry is a question someone can ask about your app, and the cheapest answer is not having it.

## The fix that was not a fix: a debugging library in the binary

We use an open-source network inspector in development builds. The first change compiled its calls out of Production. That looked done and was not: the package was still linked into every configuration, and its classes were kept alive, so hundreds of its symbols were sitting in a Production build.

::fig audit-binary

Package products cannot be linked per configuration, so the real fix was structural. The library moved into its own framework target. The app depends on it for build order but does not link it, and a build phase embeds and signs it only for Development and Staging. I checked the result by counting: zero symbols and zero strings in a Production build, and no framework in the archive.

Then the archive broke. In an archive the framework is a relative symlink into a products folder, and a plain recursive copy copied the link instead of the framework. The link dangled inside the app, signing failed, and every development archive failed until someone looked. The one-flag fix was to copy what the link points at. The lesson is the one in this whole article: a fix is a change, and it needs its own verification, including the build you do not usually run.

## A gate that cannot fail is decoration

The coverage check ran in an `after_script` with `|| true` on the end. The runner ignores the exit code of that stage anyway, so it could never stop a pipeline, and it measured against one flat floor that several targets did not meet. I moved the call into the job's `script` and replaced the single number with a floor per target: the measured value, rounded down, minus one point for the difference between measuring on a device and on a simulator.

That last clause earned its place the same day. One module read lower on the CI simulator than on a device, with no change to the module, so the gate failed on a measurement difference and not a loss of coverage. I recalibrated the floor, then reverted it, then fixed the lens instead of the number. A floor is only meaningful if you write down what measured it.

## Tests that sleep prove nothing

Dozens of tests waited a fixed few hundred milliseconds for a scripted network reply to land, then asserted. That is a guess about a clock. Where a request exists, the test now waits for the request to be made and then for the number of in-flight requests to reach zero, including any follow-up request the reply triggers.

::fig audit-settle

The exceptions matter as much as the rule. A test that asserts nothing happens, and a delay that runs before any request exists, cannot settle on in-flight work, because there is none. Settling on nothing would make "no call went out" vacuously true. Those keep their short, deliberate waits, with a comment saying why.

## The slow job was a cold compile

The package test job spent most of its time compiling, not testing. Its build cache lived in a folder inside the checkout, and the job's own `git clean` wiped it before every run. Moving the cache outside the checkout, per runner slot, removed most of the wait with the same tests and the same gate. I also timestamped the log, because a slow run you cannot break down is a slow run you cannot fix.

## Navigation was re-rendering the world

The app coordinator was an `ObservableObject` with many `@Published` properties, so any change, a tab index or a sheet, re-evaluated the root navigation stack. Moving it to `@Observable` means each view re-renders for the properties it actually reads. I also made the coordinator release the cached view of every screen that left the stack, which before happened only when the stack emptied.

## Plans can be wrong too

The written plan for one change had a rule that was too broad, and the audit review caught it: the plan, not the code, was the defect. I narrowed the rule in the plan before touching the code. If you review code but not the plan that produced it, you are auditing the cheaper half.

## What I would do the same way

- **Rank by consequence.** Put the person who cannot retry at the top of the list.
- **Delete first.** Dependencies, permissions and exceptions you do not use.
- **Verify each fix with its own check.** A symbol count, an archive build, a measured floor.
- **Write down the lens.** A number without what measured it is a guess.
- **Wait for events, not clocks,** and keep the clock only where there is no event.

A hardening week does not make an app bulletproof. It makes the failures cheaper to see and harder to hide, which is the only version of safe I trust.
