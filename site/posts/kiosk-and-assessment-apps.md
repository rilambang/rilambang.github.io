---
title: Kiosk and assessment apps: what Apple will and won't let you lock
tag: Platform rules
summary: You don't own the device, iOS does. What an exam app can actually lock, what Apple already enforces, and the entitlement to ask for in week one.
---
In a proctored exam app the exam is the easy part. The hard part is that you don't own the device. iOS does, and every restriction you want has to be one Apple has already agreed to enforce.

Every team building assessment software starts with the same instinct: build the lock. Disable Home, block the app switcher, silence notifications, watch for screenshots, detect a second screen. It is a long list of interesting engineering, and almost all of it is either impossible or unnecessary.

::fig kiosk-lock

## Two questions decide everything

Before you write any anti-cheat, answer these:

- **Is the device supervised?** A supervised device is enrolled and managed by an organisation, so a school or testing centre owns it and can configure it centrally. A student's own iPad is not supervised and never will be.
- **Does the OS already have a mode for this?** If it does, your job is to turn it on correctly, not to reimplement it worse.

Those two questions split the problem cleanly, which is why a kiosk app is a smaller project than it looks.

## What Apple actually provides

For assessment software, Apple ships the Automatic Assessment Configuration framework. Its own summary is the clearest statement of scope: "Enter single-app mode and prevent students from accessing specific system features while taking an exam."

Three properties are worth knowing before you plan anything.

- **It needs no device management.** Apple's support documentation says that securing an iPad or Mac for testing with a supported app "requires no additional setup or management, such as a device management service." An app that adopts the framework locks the device into itself. That is the difference between shipping exam mode to every student and shipping it only to schools that run an MDM.
- **It is the app's decision, not the tester's.** The app turns it on, and while it is active the user cannot switch to another app. There is no setup flow for the exam taker to skip, because there is nothing for them to do.
- **Manual modes win, and that is a trap.** If Single App Mode or Guided Access is already on, "that feature supersedes assessment mode restrictions." A school that locked its iPads by hand is not getting your app's configuration. It is getting its own, which may be stricter or looser than you assume.

## The entitlement is lead time

The framework is gated by an entitlement you have to request: `com.apple.developer.automatic-assessment-configuration`, described as "a Boolean value that indicates whether an app may create an assessment session". Apple's documentation is explicit that you "must first get permission to use it" by submitting a request form. Without it, the session never begins and the app is just an app.

That is lead time on a product schedule, and it is the one item here that no amount of engineering removes. Ask in week one.

::fig kiosk-entitlement

Assessment mode arrived in iOS and iPadOS 13.4 and macOS 10.15.4, so the same framework answers the same product question on two platforms instead of two separate anti-cheat implementations.

## What is left is a product decision

Once you know what the OS will do, the remaining work is a policy conversation dressed up as engineering.

**What do you do with a violation?** A framework that prevents an action gives you a clean story. One that merely observes gives you three options: warn, log or ignore. Each is a different product. Finding out after the exam is not prevention, and telling a candidate they failed because of telemetry they cannot see is not a defensible process.

**What do you do when the lock fails?** Exam mode is a state the app enters, so it can also fail to enter: low battery, a crash, a force-quit, a restart. The honest design assumes the lock will break at least once and decides in advance what the exam does when it notices. An exam that silently carries on unlocked is worse than one that visibly stops.

**Who is the fallback?** Assessment mode covers the app. It does not cover a second phone on the desk, a written answer sheet or a person helping. Every proctoring system has a human layer eventually. Deciding where yours ends is cheaper than discovering it during an incident.

## What I would tell anyone starting

Read Apple's platform capabilities before you design a countermeasure. The countermeasures you invent are the ones that get rejected, break on OS updates, or quietly stop working on a device configured differently from what you assumed.

The interesting engineering in a proctored exam app is not the lock. It is the exam runtime: offline resilience, autosave that survives a crash, a submission that is idempotent, and a state machine that never loses a candidate's work. The lock is a configuration. Treat it like one, and spend your effort where the candidate actually feels it.
