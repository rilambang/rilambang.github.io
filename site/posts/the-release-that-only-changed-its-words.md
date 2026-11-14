---
title: The release that only changed its words
tag: Build systems
summary: A release went out where no behaviour changed and every sentence on an error screen did. It still cost a version bump, three build numbers and five re-recorded reference frames. The interesting part was how I reverted it twice before finding a change that was small enough to be safe.
---
The release I cut last week changed no logic. Every diff that reached the app moved text: the sentence shown when the network drops, when a forced update blocks you, when the jailbreak check trips, when a task detail has no connection. The error codes stayed the same. The routing stayed the same. And it still took three builds, one package bump, and five screenshots re-recorded by hand.

That is not overhead. It is the price of the interface being made of words.

::motion release

## "Only the words" is a schedule claim

The work started as a normal cut. I pinned every package to its release tag and bumped the version, which is the point where you find out what you are actually shipping. The error-handling rework was in. It was also not what people were used to: every message carried a short code in brackets, and the sentences behind the codes had changed.

The product call came back quickly. Ship the previous wording. Keep the new handling. Those are not contradictory, but the first implementation treated them as one thing, and that is where the week's real lesson was.

## The first fix was six packages of risk

My first move was the obvious one: revert the error work for the release. Six packages went out as patch versions, each a release-only revert of its registry commits, and the app went back to the old constants for the unknown-link snackbar and lost two small surfaces whose only copy was a registry row.

It worked. It was also six packages of behavioural risk taken to change a sentence. Any one of those reverts could have dragged a fix out with it, and the release notes would have said "wording". I did not like it enough to leave it overnight.

## The second fix moved one string

I reverted the revert. The registry implementation stayed exactly as it was, the six packages went back to their previous versions, and only the package that owns the copy moved: every registry row now holds the sentence the older release showed for the same condition, with the code prefix gone. When the server sends its own sentence, that still wins.

One package, one version, no changed code paths. The app behaves like the new release and speaks like the old one.

I would rather arrive at that in an hour than in a day, but I would rather arrive at it in a day than ship six reverts I could not explain. The second version is the one I can defend in a conversation: here is the string table, here is the diff, nothing else moved.

## A copy change still spends a build number

The package bump broke two string-matching tests in another package, because they asserted the old text. That needed its own patch version, which means another build, because a build that carries a changed dependency set has to be a build you can test.

By then build one was already on TestFlight. App Store Connect will not accept the same build number twice for the same version, so the re-recorded frames could not ride along silently: they went out as build three, on a push that also carried a version bump. The rule I follow is that a push to the release branch is a build. If it carries a change, it carries a number.

::fig release-vocab

## Snapshots are evidence, not opinions

Five reference screenshots moved: the jailbreak screen, the certificate-pinning screen, the maintenance and forced-update screens, and one completed-task no-connection screen. Each one is a picture of what a student sees, so each one is a claim about the copy. The moment the sentences changed, the references were wrong. Arguing with them would have been arguing with the build.

Two others failed once and passed on the confirming run, while the CI deploy jobs were loading the same machine. I left their references alone. A screenshot that fails under load and passes alone is telling you about the machine, not the screen, and re-recording it would have erased the only evidence that something is flaky.

The distinction is worth writing down because it is the one that decays. A reference that moved because the product changed gets re-recorded. A reference that moved because the runner was busy gets investigated.

## The merge back is part of the release

The last step was merging the release into the long-lived branch, and the merge is not a formality. The release pins its packages to tags; the integration branch keeps its own lock rows, because a build there that quietly took the release's package set would stop testing what it thinks it tests. The five snapshot frames also stay as the integration branch recorded them: that branch still has the code prefix in its copy, so its frames describe a different screen on purpose.

What crosses over is the version. A branch that lags the release is a branch whose next build is not the next release.

## What I would keep

- Treat copy as a change with a schedule, not a comment.
- Revert the smallest thing that produces the shipped behaviour. One package beat six.
- Never reuse a build number to save a pipeline run.
- Re-record a screenshot when the product moved, investigate when the runner was busy.
- Merge the release back the same day, or you are maintaining two products.

The release shipped exactly what it promised: the same app, saying what it used to say. Getting there cost more thought than code, which is usually the sign that the thinking was the work.
