---
title: The iOS stack I actually reach for
tag: Tooling
summary: The stack I reach for on someone else's codebase, where every choice is priced by whether the next engineer can debug it at 3am.
---
Nobody hands you a blank project. You get a five-year-old codebase, a team, and one question that decides everything else: who is on call when this breaks at 3am? This is the stack I reach for then.

::fig stack-rows

## Language and concurrency

Swift, on the newest language mode the team can hold, with strict concurrency switched on rather than aspirational. Adopting it late costs more than adopting it early, because the cost grows with the code you already have. Everything is main-actor by default and explicitly off it only where work is genuinely expensive. The opposite default produces code that is concurrent by accident.

## UI

SwiftUI for new screens. UIKit where the platform still requires it, or where a table or collection needs control the declarative layer does not give yet. That is an honest position, not a religious one: a rewrite that ships beats a purity that does not.

Navigation has one owner. Always. Two systems that both think they own the stack produce the worst bugs to diagnose.

## Structure

Local Swift packages per seam, with the app target as a thin shell. The reason is not elegance. An unchanged module does not get rebuilt, and a circular dependency becomes a compile error instead of a convention nobody follows.

## Networking

Whatever the codebase already has, unless it is actively harmful. A second networking layer is a worse outcome than an imperfect first one. On a greenfield app I would use the platform's own concurrency tools over a reactive framework. On an existing app I leave the existing one alone until there is a reason to move it.

## Persistence

The platform's own persistence before a hand-rolled SQL layer, and a real constraint in the schema before validation in the app. Constraints are enforced under concurrency and app bugs are not. Where the data matters, the second copy of the truth is the one that goes stale.

## Strings

One string catalogue, referenced by key. Never a literal in a view. Not because of localisation, though that too, but because a literal in a view is unsearchable and permanent. It is the cheapest discipline on this list and the one most often skipped.

## Testing

Tests for logic, first and always: parsers, state machines, anything with a branch. They run in seconds and catch the regressions that matter. UI tests sparingly, on the flows that carry money or data, because they are slow and inherently flaky, and a flaky suite gets ignored, which is worse than having none.

A test that cannot fail is not a test. If I cannot describe the change that would turn it red, it is decoration.

## Third-party dependencies

Only for a problem the platform does not solve. The bar is not popularity. It is: can I read this library when it misbehaves, and will anyone still maintain it in two years? A small dependency I understand beats a large one I do not, and "we might need it later" has never once been true.

::fig stack-pages

## Build health

Treat build warnings as a budget, not as weather. A codebase with three hundred warnings cannot notice the three hundred and first, and one of those was going to tell you that a main-thread write had just become an act of faith.

## The meta-decision

I have changed stacks more than once, and each time the framework-specific knowledge expired faster than I expected. What survived is the habit underneath: prefer the boring choice, prefer the platform's own tool, prefer the option a new hire can debug on their first weekend on call, and leave the codebase so that the next person's hard problem is the interesting one, not the one you set up for them by being clever.
