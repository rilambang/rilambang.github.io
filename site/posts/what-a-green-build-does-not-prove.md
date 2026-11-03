---
title: What a green build does not prove
tag: Build systems
summary: Five things I described as verified this week that were not: a pipeline that compiled a working copy, a lock file that pinned a branch, a push I said would deploy once, a release that changed nothing, and an analytics field I called unused. Same mistake each time, a colour taken as evidence about inputs.
---
A green pipeline says the build succeeded. It says nothing about what went into it. This week five things I had called verified turned out not to be, and every one failed the same way: I took a colour as evidence about inputs.

::fig green-claims

## The build that compiled a working copy

The pipeline went green, and I reported what I believed that proved: CI read the committed dependency list, fetched each dependency at the revision the list named, and compiled against it. What it proved was that the build succeeded. The input was wrong.

The runner was a shell executor whose build directory sits inside a developer's home directory, one level below the folder holding the dependency checkouts. So the code the build compiled was not fetched from the list at all. It was the local copies already on that disk, in whatever state the last person left them. An uncommitted edit could reach a build without a commit. The dirty-tree guard in the sync script existed and was correct. Nothing on the publishing path called it.

The lesson is not "configure your runner properly", though that too. A pipeline's inputs are a claim, and the only way to hold the claim is to print them. A build that does not name its inputs in its own log is a build nobody can reproduce, including the person who pressed the button.

## The lock file that pins a branch

The dependency list had one row per package, and every row named a branch. Zero rows named a revision. That file looks like a lock and behaves like a wish. On one afternoon the branch of a single dependency moved twice, so the same app commit resolved to two different sets of code on two runs, and neither log said which it got.

::fig green-pin

This is a cheap bug to have and a cheap one to fix, which is why it is worth writing down. The script already supported a revision in that column, falling back to a plain checkout when the name is not a remote branch. So the fix is one column, and the cost is honest: bumping a pinned dependency becomes an explicit commit, and you can no longer fast-forward a pinned checkout. That is the trade you are buying. It is the whole point of the file.

## The push that deploys twice

I said pushing the branch would deploy once. It deployed twice, once from the push and again from the merge into the default branch. What I had actually verified was that the merge-request pipeline does not deploy, since the rules exclude every source that is not a push, and I had quietly stopped counting there. The second deploy arrives after the review, when nobody is watching for it.

```
- if: '$CI_PIPELINE_SOURCE != "push"'
  when: never
```

The rule is good design: a branch that has not been merged should not ship. But "the merge request cannot deploy" and "this work deploys once" are different sentences, and only the second tells a tester how many builds are coming.

## The release that changed nothing

Two builds went out carrying the same version and build number, both identical in content to a build testers already had. The version strings had been lost in a merge, with three files quietly disagreeing about what the app was called, and restoring them was the right fix. It also meant a whole release whose only real change was a string.

Nothing in the store tells a tester that. The two releases differ only by an internal release id, the kind of identifier nobody outside the console sees. The only artifact that can say "you have already tested this, there is nothing here" is the release note. So the note is hand-written, per release, and it is the one piece of writing in the process I will not generate. A changelog derived from commits would have said "fix version strings", which is accurate and useless.

## The analytics change that was almost free

Identity handling moved from a per-event parameter to a first-class user property, and three custom parameters were dropped along the way. I called that free. A colleague checked the documentation instead of agreeing: one of the three is collected automatically with every event, and the other two are not.

So the precise statement is narrower than "nothing was lost". The information survives, because the platform's own Platform and Operating system dimensions collect it. What dies is the custom dimension names. Any report built on those literal parameter names goes blank on the next release. That is a five-minute console check, not a code change, and it is the sort of removal that stays unused right up until a chart proves otherwise.

## What I do differently now

- **Print the revisions.** Every job dumps the resolved revision of every dependency next to the app commit. If the inputs are not in the log, a claim about the binary is not evidence.
- **Pin revisions, not branches,** in anything whose output ships. A branch in a lock file records intent. A revision records a build.
- **Count deploys from the rules file,** not from memory and not from "the merge request cannot ship". Read what each pipeline shape does and add them up.
- **Put the purpose in the release note.** Two identical builds and a tester who cannot tell them apart is a documentation defect, not a testing plan.
- **Check "unused" against the documentation.** Before deleting a field, find out whether something was already collecting it. "We never used that" and "the SDK always did" look identical in a diff.

The habit underneath all five is the cheapest one available: verify with a command, not with a colour. A green check is a statement about the past tense of a machine I cannot see. One `rev-parse` is a statement about now.
