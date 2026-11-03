---
title: Four gates that passed without testing anything
tag: Build systems
summary: A lint gate that linted a directory, a pre-push script that ran two thirds of the tests and printed success, a build number shared by three uploads, and snapshots that recorded a session instead of a screen. Every one was green, and every green was true about the wrong thing.
---
Every gate I added this month passed. That was the problem. Four of them were answering a different question from the one I thought I had asked, and in each case the green text was accurate, about something other than what I believed it certified.

None of the four was a subtle bug. Each was a single line that described the machine the job happened to run on instead of the thing that was supposed to ship. That is why they all looked fine: they were correct on my laptop.

::fig gates-claims

## The gate that described a disk

A lint job went red with a wall of violations, almost none of them new. The dependency manifest names the packages the app actually links, and the gate never read it. It globbed a parent directory and linted every checkout sitting there, including two old working copies nobody had linked in months. Those two produced most of the failure, while the packages that really shipped were clean.

The same config carried a second defect in the same direction. The baseline that absorbs legacy violations was keyed by absolute path, one entry per file, prefixed with the path of the machine that generated it. On that machine it matched and the gate was green. On any other checkout, in CI or on a fresh clone, the keys match nothing, and every legacy violation becomes an error in a job that never reaches the compiler.

The fix was to drive the include from the first column of the manifest instead of a glob, and to delete the baseline instead of repairing it. A file that is a hundred kilobytes of one machine's state is not configuration. The rules it suppressed belong in a `disabled_rules` list, which is stable, reviewable and identical everywhere.

## The gate that ran two thirds of the tests

The complaint was that snapshot failures were found in CI after a push, not before it. So I built a pre-push script that ran only the snapshot suites, selected by filename: twelve files with Snapshot in the name, twelve `-only-testing` arguments.

`xcodebuild` accepted all twelve, ran a third fewer tests than the suite contains, and printed `TEST SUCCEEDED`. Three of the twelve selectors matched nothing, because the suites do not live in files named after them. They live in files named after features. A selector that matches nothing is not an error to the tool. It is silently omitted from a run that still exits zero.

The lesson is narrower than "test everything" and more useful: derive the selector from the source, then assert that what you derived equals what you passed. The count is the cheap check, and it is the one that would have caught this. A gate that quietly tests less than it claims is worse than no gate, because it consumes the attention you would have spent checking.

## The build number that told nothing apart

Three consecutive uploads carried the same marketing version and the same build number. The deploy job had no `changes:` rule, so every branch push produced a build, including pushes whose diff could not compile into the app. And nobody bumped the build number, because nobody was looking at the artifact. The pipeline was green, and green was what was being watched.

::fig gates-build-number

Firebase accepts three uploads with one identity and gives each a release id. App Store Connect does not: it rejects a duplicate build number at upload. That rejection arrives weeks later, on a release branch, when the person holding it has no memory of why the number stopped moving. The bandage is one line in each configuration. The cause is a deploy job that treats every push as shippable.

## The snapshot that recorded the session

Three captures differed from their references. Both images were the same size, on the same device, at the same scale, so this was not a device or runtime mismatch. The difference was a student's name.

The references had been recorded signed out. The new captures had a signed-in user, leaked from an earlier test in the same process. The harness reset its cache between captures and not its session, so the reference described the history of the test run and not the screen. Re-recording would have made it pass, and would have baked a leaked session into the reference permanently, where nobody would look again.

That is the most dangerous shape of a stale reference: not old pixels, but a test measuring the wrong thing and going on measuring it, consistently, forever.

## The shape they share

All four gates reported on their input accurately and on their claim inaccurately. The lint job told me about a directory. The pre-push script told me twelve selectors had been accepted. The deploy job told me a command had exited zero. The snapshot run told me the screen matched a previous process.

Three questions, asked before trusting any gate:

- **What does it read?** A manifest, a source tree, or whatever happens to be on this disk? If the last, the result is a property of one machine, and portability is not a nicety to fix later.
- **What does green mean?** That a command exited zero, or that a property holds? Most of the work is turning the first into the second.
- **Does it fail on a machine that isn't mine?** Not "would it run", since `xcodebuild` would. Whether the answer it gives there is still true.

In every case the repair was smaller than the analysis: one column, one count, one bump, one reset. The expensive part was noticing that a green check says nothing until you can name what it checked.
