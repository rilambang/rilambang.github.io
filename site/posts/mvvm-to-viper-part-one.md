---
title: MVVM to VIPER, part one: when the view model is the app
tag: Architecture, part 1 of 3
summary: First of three. What MVVM gets right, what the proctored exam screen's view model quietly took ownership of, and why a pattern that works at five screens stops being local at fifty.
---
The review comment that started this was one I wrote on my own diff: why does the exam view model know the network layer, the router, the answer queue and the invigilator? I had no good answer, so the next three architecture passes were spent earning one. This is part one of three.

The app is a proctored exam client. A million students sit exams on it, usually on school Wi-Fi, usually with someone watching. That prices every decision differently. A failed exam is not a bad afternoon, and the modules have to keep shipping while the structure moves underneath them.

## MVVM is the right answer at the size you meet it

A screen, some published state, a service in the initialiser. The whole feature fits in your head, and so does the diff. That is where most of us meet MVVM, and it is why most of us are right to use it.

The trouble is not that MVVM is wrong. It is a rendering pattern with no opinion about anything else: where a rule lives, who owns navigation, which layer may speak in which data shape. Nature abhors that vacuum, and the nearest thing to fill it is the view model.

## What one file ended up owning

Grow a feature for a year and the list stops being a list of one screen's concerns:

- what state each question is in: answered, flagged as unsure, untouched;
- the rule for when an answer is allowed to leave the device;
- the offline answer queue and its retry pump;
- navigation through the exam gate, including the paths that must not be reachable;
- and the HTTP calls, because importing the network manager was one line and a review away.

None of those arrived as an architectural decision. Each arrived as the smallest possible change to get a story done, in the file that was already open. That is how a view model becomes an app.

::fig mvvm-absorbs

## The tell is the wire type

You can date the moment a screen stopped owning its own shape. It is when the backend's payload shows up at the seam where the UI decides something.

Ours took the API's finish request, a JSON shape with the server's field names on it, straight to where the screen said "finish". Nothing crashed. It just meant the screen was now authored by someone else's schema, and the day that schema changed, the change landed in the UI. A screen that speaks wire types cannot be reused, cannot be tested alone, and cannot be reasoned about without the API documentation open.

::fig mvvm-wire

## Testing takes the shape of the code

Because the rules lived in a file that also knew about UIKit, the network and navigation, testing one rule meant building all of it: construct the view model, mock the network manager, subscribe to a Combine sink and hope the thing you cared about fires before the test times out.

Fourteen exam suites lived inside the app test target for exactly this reason. A rule about the offline answer queue, pure logic that could run in milliseconds, could not be tested without building the app it was embedded in.

## Why I would still defend it

At five screens and two engineers, MVVM is not a compromise. It is the cheapest thing that works, and every alternative is overhead you have not earned yet. The pattern did not fail here. It held exactly as long as the feature fit inside one file, and it kept holding for a while after it stopped fitting, because everyone was polite about it.

## Where it breaks

It breaks on blast radius, not on taste. When every rule can reach everything, no change is local. A tweak to the answer state can touch the gate, the queue and the reporting path, and the review has to reason about all of it at once. Nobody wrote that down anywhere. It just became true.

That is not a skill problem and discipline does not fix it. It is fixed by making some things impossible to import. Part two is the wall we built, and the bill that came with it.
