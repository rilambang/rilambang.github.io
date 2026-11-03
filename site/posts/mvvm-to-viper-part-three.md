---
title: MVVM to VIPER, part three: a rename and a confession
tag: Architecture, part 3 of 3
summary: Third of three. VIPER fixed nothing Clean had not, except the last unowned thing, the screen. Six use cases, a router with one owner, forty-three packages down to nineteen, and the operations that made the migration survivable.
---
We did not adopt VIPER because it is better on paper. We adopted it because the view model had already become a presenter, and naming it one was the cheapest way to stop the next person putting rules back into it. This is the least reverent of the three parts.

## A rename is documentation

Twenty-two view models became presenters. That is the whole change in one line, and it is not small. Type names are the documentation that survives a rewrite: nobody opens the architecture document, and everybody reads autocomplete. After the rename, a file that says "this is a presenter" is harder to stuff business rules into. Not impossible, harder, and harder is what architecture is made of.

## Six use cases instead of one file

The rules moved out one at a time, each into an interactor named for what it does: load the questions, submit an answer, poll the status, report an isolation event, finish, flush the offline queue.

Each owns one rule, is testable with a fake, and can be reasoned about without loading the three thousand lines around it. The presenter kept what a presenter should have: view state, and the intent that changes it.

## The router, given an owner

Feature routers own one question, where does this button go, while the app-level coordinator still owns the stack itself. A VIPER router is often a god object in disguise, and the thing that prevents it is deciding once that there is exactly one owner above it.

This matters more here than in most apps, because navigation is a product rule: an exam gate, a consent screen, a state the student must not be able to pop back out of. That is the case where the ceremony earns itself.

::fig viper-owner

## The last wire type, and the views that came home

- **The finish payload became an entity.** The network layer can now change without touching a screen. The debt from part one, paid last.
- **The question views came home.** They had been sitting in the shared UI package, so any feature that wanted a checkbox imported the exam module's world. They moved into the exam feature, and the shared core lost three dependencies.
- **The tests came home too.** Fourteen suites moved into the feature package, which let us delete five test-only escape hatches that existed solely so app-side tests could reach presenter internals. Deleting an escape hatch is better architecture than adding a protocol to justify it.

## Forty-three to nineteen

One package per feature, exporting the same three products under unchanged names, so not one `import` line changed anywhere. That is the only reason a 43-to-19 consolidation landed as a series of boring commits, and boring commits are the only kind that land on a product a million people depend on.

::fig viper-nineteen

The layout is now something you can explain in ten seconds: entity and interactor in the domain, repository and mappers in data, view, presenter and router in the feature.

## What actually made the migration possible

Not the architecture. The operations around it.

- **A pilot and a script.** One feature was consolidated by hand, a merge script was written from the exact commands that worked, and the remaining slices ran through it. Mechanical batches do not get eight review loops. They get one reviewed script.
- **A lock file and a sync step.** A revision pinned per module, and a sync that fails loudly on drift. Without that, nineteen packages times eight engineers is a support desk.
- **A gate that could say no.** Device build, the full app suite, every package suite and lint, once at the end of a batch and not per slice. For the exam slice specifically, a real proctored exam on a real device: start, answer offline, restore the network, flush, finish, the isolation path. A simulator pass does not prove a queue replays.
- **A build-only rule for the mechanical work.** During the rename and consolidation the compiler was the gate, and the full suite ran once at the end. That sounds reckless. It was not: the changes were renames and file moves, and running a thousand tests after each of twenty-two renames turns a two-day job into two weeks. The rule had a written expiry date, and the full gate ran before anything shipped.

## What I would do differently

- **Price the ceremony, not only the boundary.** One package per feature with three targets inside would have given the same compiler walls with a third of the bookkeeping.
- **Do not clean the layer that is not hurting.** I improved data access for months while the screen kept growing. The screen was the problem.
- **Migrate the riskiest path first.** The exam is the app, and we did it last. Doing it first would have been scarier, and it would have found the real constraints, the offline queue, the gate and the isolation reporting, before three other slices depended on them.
- **Give navigation a deliberate owner on day one.** Every architecture lets the router drift into everything or nothing, and the decision costs five minutes.

## Choosing today

MVVM got the app to a million students. Clean made the data layer testable and the boundaries real, and cost us a module system. VIPER fixed nothing Clean had not already fixed. It made the last unowned thing, the screen, own its responsibilities, and made the architecture readable in autocomplete.

If you are choosing now: MVVM while the feature fits in one head, clean boundaries the moment a rule has to be tested without a screen, and VIPER when navigation is a product rule and not a detail. Here navigation is the product, so VIPER earned its ceremony. Most apps do not have that, and should not pay for it.

The architecture that wins is not the one with the most layers. It is the one where the compiler can tell the next engineer no without me in the room.
