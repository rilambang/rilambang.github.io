---
title: UIKit to SwiftUI without a rewrite
tag: Migration
summary: The migration succeeds or fails on one decision: who owns navigation. Everything else is a sequence of small, reversible steps.
---
The migration succeeds or fails on one decision: who owns navigation. Get that right and the rest is a sequence of small, reversible steps. Get it wrong and you have two systems that each half-know where you are.

I have taken more than one shipped app across this boundary. Nobody regrets the destination. People regret the order.

::fig uikit-chrome

## Do not start with the app shell

The instinct is to rewrite the root and let the screens follow. That inverts the risk. The shell is what every screen depends on, and it is the one part you cannot ship incrementally.

Start with leaf screens: a detail view, a settings page, a form. Screens that do not own navigation are the safe unit of migration, because a failure costs you one screen, not the app.

## Pick one direction of interop at a time

The two directions are not symmetric and should not be started together.

- **UIKit shell, SwiftUI leaves.** A view controller hosts a SwiftUI view. This is the low-risk direction and where a migration should begin.
- **SwiftUI shell, UIKit leaves.** A SwiftUI view wraps a UIKit component. It is necessary for the handful of things SwiftUI still does badly, and it is the direction that piles up if you are careless.

Whichever you are in, know which it is. A codebase doing both everywhere, with no rule, has no migration at all.

## Navigation is the seam, so give it exactly one owner

This decision decides whether the migration is a project or a permanent tax. Two systems that both believe they own the stack produce bugs that are very hard to diagnose: a screen that appears twice, a back button that does nothing, state that resets on pop.

Keep navigation in one place for the whole migration, whether that is the UIKit navigation controller or a SwiftUI stack driven by a coordinator. The other side renders content and reports events. It does not push.

## State: pass data in, events out

Do not let the two worlds observe each other's state. A view controller watching a SwiftUI observable object, or a SwiftUI view holding a reference to a view controller and polling it, is a future bug in both directions.

The contract that survives is simple: the parent passes a value in and receives callbacks out. That is enough for almost every screen, and it keeps either side replaceable.

::fig uikit-contract

## What actually bites

- **Keyboard avoidance.** Two systems, two opinions, one screen. It is the most common source of visual regressions during the swap and deserves its own pass.
- **List identity.** A list that reuses cells and a list that keys on identity behave differently on update. Missing or unstable identity produces animations and state loss that look like a rendering bug and are not.
- **Lifecycle timing.** "Appeared" does not mean the same instant in both systems. Code that starts work on appear and cancels on disappear will behave differently, and the difference shows up on a slow network, not at your desk.
- **Measurement.** Geometry readers used for layout maths are a smell in a declarative system. Most of the time the layout you were computing by hand is a two-line native layout, and the manual version is the expensive one.

## Availability is part of the plan

Everything you adopt has to exist on your deployment target, and anything newer needs a working fallback, not an `#available` that silently renders nothing. Write down the minimum supported version and treat every adoption above it as a decision with a cost.

## How you know it is finished

The app target compiles without importing the old UI framework outside the places the platform genuinely requires it. Until then you have a mixed app. That is a perfectly good state to ship from, but it is a state, not an outcome. Name the finish line, or the migration becomes the architecture.
