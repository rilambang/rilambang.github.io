---
title: One sign-in across the app and the web
tag: Architecture
summary: A web page hands its session to the app, and the app has to decide who just arrived. The link carries a token that names nobody, so the answer has to come from the profile. Two rules collided inside a day, and the resolution was to stop reading the token at all.
---
Last week I spent two days on a link. A student opens a school page in a browser on a phone that already has the app, signs in there, and the page hands the session to the app. From the outside it is one tap. Inside, it is an identity question with a timing problem attached: who is already signed in on this device, is that the same person who signed in on the web, and what does the app show while it finds out?

::motion handoff

## The exchange returns a token, not a name

The hand-off is a deep link with a short-lived code. The app sends the code to the backend, gets a session token back, and stores it. That is the whole mechanism, and it is the first place a design can go wrong, because the token is opaque. It authenticates a session. It does not tell the client whose session it is.

The first version I shipped worked around that with a hint: the link carried a student id, and if it matched the profile already cached on the device, the app skipped Login and went straight in. That shortcut is a client trusting a string it was handed. It also meant two code paths before any screen appeared, and both of them could be wrong in different ways.

I removed it. The rule I wrote down then was blunt: every signed-in device lands on Login. No hint, no same-student comparison, no client-side identity. If the app does not need to know whose token it holds, it cannot get that wrong.

## Then the rule changed, and the design changed with it

Before I finished, the product rule arrived, and it disagreed: nobody signed in gets an automatic sign-in, the same student in app and web should go straight through, and only a different student should see Login.

I think the second rule is the better one. It is the rule a person can feel. But it needs identity, and the token still does not carry one. What I did not do was bring back the hint. The app exchanges the code, fetches the profile the new session belongs to, and compares that with the profile cached before the hand-off. Same student, straight in. Different student, or a profile that cannot be matched, and the new session is signed out underneath the syncing cover before the app lands on Login.

The token stays opaque. The profile is the identity. A claim inside a URL is not.

::fig handoff-id

## The tick is the promise, and it belongs on every path

The acceptance criteria had an odd split: every one of the eight scenarios said "the account synchronization succeeds", but only the different-student path actually showed the success tick. The straight-in paths dropped the cover so fast that the tick never appeared, which meant the screen told a different story depending on which door you came through.

Now every path shows the same cover, the same tick, and then the destination it earned. The tick is the promise that the account moved. Whether the next screen is the assessment list or Login is a separate decision, made after the promise is kept.

## Offline is its own sentence

A hand-off with no connection fails the exchange, and the snackbar fell back to the login error, because the offline case carries no message from the server. So a student on a weak connection was told their sign-in was wrong when the truth was that nothing had been sent.

The fix was one string in the error catalogue: connection lost, not sign-in failed. But the useful part is the rule underneath it. An absent reply means not yet. A client that reads silence as a verdict will keep telling people the wrong thing about their own account, and the person has no way to tell the difference.

## What the hand-off may not do

A junk code now fails the exchange and signs nobody out. That is deliberate. The link arrives from a browser and anyone can craft one; if a bad code ended the session already on the device, a stranger could end a student's session by sending them a link.

The four rules I would apply to the next hand-off:

- Identity comes from the profile the server returns, never from the link.
- A missing reply is not a failure.
- The success tick belongs on every path, not just the awkward one.
- A bad code fails the hand-off, never the session.

The screen did not get more complex. It got one honest destination and one honest cover in front of it, which is most of what a sign-in is.
