---
title: MVVM to VIPER, part two: the wall, and the bill for it
tag: Architecture, part 2 of 3
summary: Second of three. Three targets per feature make the dependency graph a compiler fact, and forty-three packages make it a second product. The clean architecture win, and the cost I had not priced in.
---
The first correction was not a rewrite of the view model. It was a wall. The wall is the part I would keep from all three architectures. The bill that arrived with it is the part I would renegotiate.

## Three targets, one feature

Per feature: a domain target with the entities and repository protocols, a data target with the real repository, the mappers and the network, and a feature target with the view and its state. Separate local packages, with an acyclic graph between them.

The folder names are not the point. The point is that the dependency graph becomes a compiler fact. A presenter that tries to import the networking module does not get a review comment and a debate about layering. It gets a build error. That is a different category of enforcement from a convention document, and it is the only kind that survives a deadline.

## What the wall paid for

- **Rules became testable in milliseconds.** No UIKit, no network, no app: an interactor and a fake repository. A test that used to be an integration test became a unit test, which is the difference between running it on save and never running it.
- **Wire types stopped leaking.** A mapper moves the wire type to an entity and back, with round-trip tests. The day the backend renames a field, the diff is one file instead of eleven screens.
- **Reuse stopped meaning "copy".** The question types, multiple choice, essay, matching and drag and drop, moved behind their own models instead of being open-coded per screen. Three screens that had drifted apart became one behaviour.

None of that is decoration. On a product this size the first item alone pays for the wall: the rules that decide whether a student's answer survives a dropped connection are the rules most worth a test, and before this they were the hardest to test.

Then it over-delivered, the way architecture tends to.

## The bill: forty-three packages

Three layers per feature, times eight features, plus a dozen shared core modules, and the app had 43 sibling packages. Each came with its own repository, manifest, lock-file row, CI path entry and checkout to keep in sync.

::fig viper-forty-three

A single feature crossed three repositories. A cross-cutting change, a new answer state say, was a three-repository merge request with a lock bump, and a reviewer had to hold three diffs in their head to see one story. Nothing was wrong with any individual module. The count was the problem.

Clean boundaries are cheap per module and expensive per module count, and that exponent is what I had not priced. At 43, the module system had become a second product we maintained, with its own tooling, its own failure modes and its own drift.

## The quieter failure

Clean gave us a home for entities and repositories, and it did nothing for the screen. The view model still had three jobs, view state, use-case orchestration and navigation, and still had no rule about which was which.

That is the part worth saying plainly, because it is the part that gets lost in the diagram. The data layer got better, the screen did not change, and the screen was what generated the defects. We had improved the half of the architecture that was already tractable.

## What I would have kept cheaper

One package per feature, with the three layers as targets inside it. Same compiler walls, same testable domain, a third of the bookkeeping: one repository, one manifest, one lock row and one CI path per feature instead of three. The boundaries that mattered were between targets, not between repositories, and the repository split bought nothing a target did not already enforce.

::fig viper-bill

Part three is what happened when the screen finally got the same treatment, and why the honest name for it was a rename.
