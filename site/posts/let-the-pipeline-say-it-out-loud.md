---
title: Let the pipeline say it out loud
tag: Tooling
summary: Every build reached the testers and nobody heard about it. This week the deploy lanes started announcing themselves in the channel the team already watches, and the published release started doing the same. The rules that mattered were about failure and untrusted text, not formatting.
---
For a long time the most reliable part of our pipeline was also the quietest. A commit landed, the build ran, the app reached the testers, and the only way to know was to open a dashboard and look. The people who needed the build were not the people who opened dashboards.

This week that changed. A successful deploy now posts in the team channel with the tester link and the release notes. A published release posts too, with a link to the release page.

::motion pipeline

## A green job is not a message

The pipeline was not broken. That is what made it easy to ignore. Green means the machine did what it was told; it does not mean anyone found out. A build nobody installs is the same as a build that failed, except it also consumes an hour of CI.

The fix is not a monitoring system. It is a message in the place where people already are, at the moment the thing happens, carrying what they need to act on it: the install link, what changed, and the name of the person who should look.

## The platform integration could not carry it

Our source host can post to chat on its own, and we tried that first. It cannot attach the test link, because that link is produced by the deploy step and lives outside the host's model of the job. It also cannot mention a specific person, which is the difference between a notification and a note on a wall.

So the deploy lane posts to a chat webhook itself, after the upload succeeds. The hook URL and the tester's user id come from CI variables, not from the repository. That last part is not tidiness: a webhook URL in a repository is a credential, and a user id in a repository is a person's identity published forever.

## The announcement must never become a second failure point

Both announcements run after the thing they announce, and both are allowed to fail without failing the job.

That ordering matters more than it sounds. If the deploy uploads the build and then the notification throws, the build is already in the testers' hands; failing the lane would tell them the opposite. So the deploy lane catches the error, logs it, and stays green. The release announcement does the same, for a stronger reason: by the time it runs, the release is published and cannot be unpublished by a chat error.

A notification is a side effect of shipping. Treat it as a step that ships, and it will eventually lie about a build that went out.

## Pasted text is untrusted input

The release notes are written by a person and pasted into a command. They can contain anything, including `@everyone`. A chat client that parses mentions out of arbitrary text will happily ping the whole server because someone pasted a release note from somewhere else.

The announcement sends the notes with mention parsing turned off, so nothing inside the text can ping. The only pings it sends come from a separate field of numeric ids, held as a constant in the script and overridable for a one-off release. Numeric ids ping; text never does.

::fig pipeline-message

It is the same rule as any other input boundary, applied to a channel that people treat as trusted because it is internal. The text is data. It does not get to act.

## Two events, one channel

The deploy and the release are different moments. A deploy puts a build in someone's hands; a release declares a version finished. Both were silent, both now speak, and they speak in the same place with the same shape, so people learn one place to look.

What they carry is different on purpose. The deploy carries the tester link, the notes and the tester's name. The release carries the release page and the team ids that need to know. One is "try this", the other is "this is done".

## What I would keep

- Announce at the moment the thing succeeds, not on a schedule.
- Put the message where people already read, not where the build lives.
- A notification failure must not change the outcome of the job it describes.
- Keep the hook and the ids in CI variables.
- Mentions come from structured fields; pasted text is data.
- Every event that people need to know about gets a message, including the ones that are "only" a release.

Shipping is two acts: doing the thing, and making sure the right people know it happened. The pipeline was already good at the first one. The second one is a dozen lines and one habit.
