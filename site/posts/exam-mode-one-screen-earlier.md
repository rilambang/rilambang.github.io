---
title: Exam mode, one screen earlier
tag: Platform rules
summary: The lock used to start inside the paper, after the questions were visible. Moving it into preparation closed that gap, and the blocked screen turned out to be a copy problem before it was a layout problem.
---
Exam mode in the school app I work on used to begin inside the paper. By the time it locked the device, the questions were already on screen. This week I moved the lock one step earlier, into preparation, where it can do its job before the assessment starts.

That sounds like a small reorder. It was not. Moving the lock exposed three states around it that had been wrong for as long as the lock existed, and the screen that shows them is where most of the work went.

## The framework fails closed, and that is the point

Apple's Automatic Assessment Configuration is the part of iOS that lets an app take the device for the length of an assessment. You create an `AEAssessmentSession` and start it, and until it ends the student is in your app: no app switcher, no Home, no notifications from anything else. The app needs an entitlement Apple grants by request, and no device management, so a student's own iPad can run it exactly like a school-owned one.

The property that matters is that it fails closed. If the session cannot start, because the entitlement is missing, the device does not support it or another session is already running, the call returns an error and nothing is locked. The only honest response is to refuse to open the paper. An assessment app that shows the questions anyway is not secure. It just has a lock icon somewhere in its settings.

The simulator cannot start a session at all. On a simulator every proctored exam therefore blocks, which looks like a bug in the test setup and is actually the design working. I mention it because it is the first thing anyone testing this will report.

## The lock was one screen too late

The old flow started the session inside the paper, after the question view had loaded. The lock was real. It was also late by exactly the window that mattered: the paper was on screen and the device was not yet locked. A student could leave, look something up, come back, and the app would only notice when the session finally began.

Preparation gained one step for exams the server marks as remote-blocked:

```
Welcome, Location, Activate exam mode, Ready, paper
```

Everything else keeps the shorter flow:

```
Welcome, Location, Ready, paper
```

Those exams never lock at all. The decision comes from the server, not the client, so a student cannot opt into the shorter path by choosing another device or clearing storage. The new step shows the state it is in: a shield that goes from "not active" to "active", and a button that changes from "Activate exam mode" to "Next". Once the lock is live the screen cannot offer to activate it again, because the indicator and the button read the same state.

::fig exam-lock-moves

## A refused start used to unlock the device

Starting the paper can be refused for reasons that have nothing to do with the student: the server rejects the attempt, the account is not eligible, another session is running. The old behaviour treated that as the end of the lock. The student stayed on the preparation screen, the device unlocked, and the lock prompt appeared later inside the paper. In between, they could roam the app mid-exam.

Now a refusal keeps the lock. The student stays on Ready, the error appears as its own toast, and the only way out is the back button, which ends the session explicitly. That felt backwards for a minute: the exam did not start, so why hold the device? Because the alternative is an unlocked student one tap from leaving, with the back button right there. The lock ends when the flow is abandoned on purpose, not when something fails.

## Eight hours is not cheating

The framework ends a session on its own after eight hours. A long paper can reach that limit, and when it did, the app saw "session ended" and treated it exactly like an isolation: a blocked screen, an accusation and a report against a student who had done nothing but keep working.

Now the expiry gets an opaque cover, a spinner and the line "Re-securing the assessment…" while a fresh session starts underneath. The paper comes back with the answers intact, and no report is filed. If the new session cannot start, the student lands on the blocked screen with the self-lock wording, and still no report, because nothing was accused. The session could not start, and that is a technical fact, not a verdict about a person.

## Two blocked screens, one layout

The app has two ways to be blocked, and they make different claims. The server can isolate a student: that is a judgement about behaviour, it applies to every exam, only a teacher or an institution admin can lift it, and reloading cannot help. Or the app's own lock is not running on an exam that requires it: that is a technical fact about this device, and reloading genuinely fixes it.

Both states share one layout. Illustration, spacing, typography and button are identical, and only the title and body change. That sameness is deliberate. The pixels were never the problem. The words were.

::fig exam-blocked

The two screens used to share their copy, and the shared copy described the self-lock case. So a student whose exam mode was on, and whose session had failed to renew, was told they had left the lock screen and offered a reload that could never clear it. The screen was making a claim about them that it had no evidence for.

The fix was to give each state its own words and its own title. The server block says "Assessment blocked" and names the human to contact. The self-lock says "Activate exam mode", the name the student already met in preparation, and tells them to reload. The reload button stays on both because the layout is shared, but it means two different things, and only one of them works.

That is the design lesson I keep coming back to: a screen that makes a claim about the user must know which claim it is making. Copy is behaviour. Sharing it between two states is a shared bug, and no visual polish fixes a sentence that accuses the wrong person.

## What testing this actually looks like

The simulator always blocks, and that is correctness, not a defect. Device verification is the only verification that counts for the session itself: start it, refuse it, watch a refusal hold the lock, renew after a long session, and confirm the renewal files no report. A simulator pass proves the blocked path and nothing about the lock.

UI snapshot references are references, not gates. Each records what a screen looked like when it was last touched, so a copy change is supposed to move it. Treating a reference as a test means either freezing wording that is wrong or teaching the team to re-record without reading. I re-recorded them, looked at the diff, and kept them out of the gate.

The pair is the test worth writing: the server block must never show the self-lock copy, and the self-lock block must never show the server copy. Each is one wrong string away from telling a student something false about themselves.

## The lock is the easy part

Starting an assessment session is a handful of lines. Keeping it honest is the rest: where it starts, what happens when it fails, what happens when the framework ends it at eight hours, and what the screen says when it is gone. The lock did not get stronger this week. It got earlier, and the states around it stopped lying.
