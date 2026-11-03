---
title: Splitting an app into local Swift packages: what breaks first
tag: Modularisation
summary: The files move in a day. The boundaries take a quarter. Here is the order things actually break in, and the one rule that keeps the first week from turning into a public-API explosion.
---
Moving files into packages takes a day. Getting the boundaries right takes a quarter. The gap between those two numbers is where most modularisation projects quietly stall.

I have done this on more than one app, and the failures are consistent enough to predict. This is the order they arrive in.

::fig split-file

## 1. Resources fail at runtime

The first casualty is anything that reads from the bundle: a JSON fixture, a font, a strings file, an asset catalogue image. Inside a package, code needs `Bundle.module`. Code that still reaches for `Bundle.main` compiles perfectly and returns nil at runtime.

This is the worst class of breakage in the whole migration. The compiler cannot see it, code review cannot see it, and a user usually finds it before a test does. Sweep for `Bundle.main` and `UIImage(named:)` before you move anything, and decide per call site whether it belongs to the package or the app.

## 2. `internal` becomes `public`, and everything gets worse

Once code lives in another module, `internal` is no longer enough. The tempting fix is to add `public` until it compiles. That is how you end up with a package that exposes forty types and enforces nothing, a boundary that exists on disk and nowhere else.

My test: if a package needs more than a handful of public symbols, it is not a module. It is a folder with a manifest.

So the real work is not moving code. It is designing the API you wish existed and then making the code fit behind it. Write the interface first. If it is awkward to write, the boundary is in the wrong place, and you found that out before the expensive part.

## 3. Build settings stop being inherited

A package does not inherit your app target's build settings. The Swift language version, the warnings you had silenced, optimisation flags, the deployment target: all of it is now declared in the manifest, and someone has to decide it on purpose. Do it in one pass, or spend a fortnight on warnings that appear in one module and not the one next to it.

## 4. Names collide immediately

Every codebase has a `User`, a `Config`, an `Extensions`, a `Logger`. In separate modules they are all legal and all ambiguous at every call site. Type names now have to say what they are. That sounds like a nit, and it is really a boundary leaking into every file that touches two modules.

## 5. Tests cannot see across the wall

`@testable import` works for a package's own tests. It does not let a test in one module reach into another's internals. That is the point, but it means tests that were quietly testing implementation details have to be rewritten against the public surface, or the surface has to grow to make the behaviour testable. The second option is usually right, and it is a useful signal that something is missing from the API.

## 6. The awkward middle, where people quit

For a while everything is public, nothing is faster, and there are more files than before. That is not the design failing. It is the design being incomplete. The end state of narrow public surfaces, small rebuilds and obvious ownership is what pays. Judge it there, not in week two.

## 7. Cycles surface, which is the point

The first genuinely valuable thing modularisation does is turn circular dependencies into compile errors. In one target, A using B and B using A is invisible. Across modules it cannot exist.

That error is not in your way. It is the design bug you had been hiding, finally unable to hide. The wrong fix is to merge the two modules so it compiles again.

::fig split-order

## The sequencing I would use again

- **Leaves first.** The things that depend on nothing: design tokens, models, a networking core, a logger. Low risk, and immediate proof the tooling works.
- **Then the middle.** Shared UI and shared services. This is where the API design conversation actually happens.
- **Feature modules last.** They need the seams below them settled, and they are the ones most likely to move again if those are not.
- **The app target ends up a shell.** Composition, navigation, configuration. If it still contains business logic, the split is not finished.

What I would do differently: agree the vocabulary and the public surface in writing before anyone moves code, and treat a change to either as a design decision, not a refactor. Moving files is mechanical. Everything that made the project worth doing is not.
