---
title: Build time is a dependency-graph problem, not a machine problem
tag: Build systems
summary: Faster hardware buys you a constant factor. The graph is the exponent. Why the first fix is almost always deleting a script phase, and what to measure before you touch anything.
---
Every slow-build meeting starts with someone proposing a faster Mac. A faster Mac buys a constant factor, which is the cheap half of the problem. What multiplies it is the dependency graph.

Apple's own guidance on incremental build performance is blunt on this: the things that break incrementality are the things that make the build redo work it did not need to redo. That is a graph problem.

## Measure the build, not the vibe

Before you change a setting, get the timing summary from a build and look at where the time goes. Two facts usually fall out at once:

- One or two tasks dominate, and they are not the compiler.
- The build compiles far more than the change touched.

Both point at structure, not hardware.

## The usual culprit is a Run Script phase

A script phase with no declared inputs and outputs runs on every build. It does not matter that the script is quick. The cost is not its runtime. It is that it invalidates downstream work and forces the build to redo it. Five lines of script can be responsible for minutes.

::fig build-edges

Three responses, in order of preference:

- **Delete it.** A surprising share of script phases do something the build system already does, or copy a file that should be a build setting.
- **Declare inputs and outputs.** If the script generates something, tell the build system what it reads and writes so it can be skipped when neither changed.
- **Move it off the critical path.** Earlier in the pipeline, or out of the build entirely.

## Then ask what a change invalidates

In a single-target app the answer is usually "everything downstream", which means most of the app. A change to a shared file in a large target can recompile a majority of the codebase, not because the compiler is slow but because the unit of work is the target.

Splitting the target is the fix, and it works for a structural reason: an unchanged module is genuinely unchanged, and the build system can skip it. The case you live in, the incremental build, hundreds of times a day, gets faster by an order of magnitude and not by a percentage.

::fig build-bars

## Whole-module optimisation and the debug and release asymmetry

Whole-module compilation is faster for a clean build and much worse for an incremental one, because the module is the unit that has to be redone. Debug and release builds therefore want opposite things, and a setting that is right for one is wrong for the other. Decide per configuration.

## Type-checking hot spots are real and local

One expression the type checker cannot resolve quickly, such as a large literal, deeply nested operators or a long chain of overloaded calls, can take longer to compile than the rest of its file. The compiler will tell you if you ask. The fix is to simplify the expression or name the type. It is a small, contained edit with an outsized effect.

## Asset catalogues

Assets are compiled, and a large catalogue that changes often is a step you pay for repeatedly. Keeping generated or throwaway assets out of it is not style. It is build time.

## What I tell a team staring at a slow build

- Get the timing summary. Guess nothing.
- Delete or declare script phases. It is almost always the cheapest win.
- Split the target so unchanged code can be skipped.
- Fix the one or two type-checking hot spots the compiler names.
- Only then consider hardware or caching, and expect a constant factor, not a step change.

The uncomfortable part is that the first four are all structural. The build is slow because the code is shaped in a way that makes it slow, and no machine fixes a shape.
