---
title: Every way out of an exam
tag: Behaviour
summary: A proctored exam has four exits, not one: the student finishes, the timer ends, the student leaves, or the server closes the paper. Most of the bugs lived in the edges between them, including one where leaving an exam quietly submitted an empty one.
---
When I say an exam has an Exit button, I mean the student can leave. When I say an exam has four exits, I mean the code has four ways out, and they do not agree about what leaving means. That disagreement is where most of a week went.

::motion doors

## Four doors, four rules

The student taps Submit. The timer runs out. The student taps Exit. The server closes the paper while the student is still in it. Each of those ends the exam, and each one carries a different obligation about what gets sent, what stays queued and what the student sees next.

The rule I ended with is narrow: only Submit and the timer finish an exam. Exit does not finish it. Leaving is not answering.

::fig exam-paths

The first version of the code did not say that out loud. A failed finish sat in a queue and retried itself; the retry could fire after the student had already left the screen, which meant something was being sent on behalf of a person who had walked away. Now a finish that fails while time remains is not retried, and a confirmed Exit withdraws a finish that was waiting. One door, one outcome.

The timer is the strange one. A failed finish is not retried while time is left, because there is still a paper to answer; the retry belongs to the moment the clock runs out. Once the timer ends the exam, a stored finish can go and there is nothing left for it to disturb. The timer ends the exam. It never acts for the student while they are still working.

## The exit that returned you to a locked paper

Under the assessment framework the device is held for the length of an assessment. Exit used to be handled inside the paper: tapping it while offline returned the student to the same paper, still on a locked device, with no way forward. The lock had done its job too well. There was nothing left to do and nowhere to go.

Now an offline Exit leaves the exam and the blocking report is sent later, when there is a connection. The student gets out; the school still learns what happened. Those are two different deliveries, and treating them as one was the bug.

A refused Exit is not queued, though. If the server says no, the answer is no, and the app does not keep asking in the background until it gets a different one.

## The empty paper that finished itself

The worst of the week was a screen that built itself. Pressing Exit popped the exam, and the popped screen's saved view was released on the next run loop, while the pop was still animating. The navigation stack asked itself to build the outgoing page one last time and got a brand new exam screen with no exam in it. That screen's timer had no end date, read as expired immediately, and sent a finish with an empty exam id. When the server refused, the app pushed the result page onto the home screen.

I fixed it the lazy way first: the empty exam page was made to build nothing, so nothing could finish. That hid the cause behind a screen that did nothing, and the next person to touch the stack would have had no idea why it was there. I replaced it the same day. The saved view is now released a second after the pop starts, which is longer than the animation, and the page builder is exactly what it was. The lesson is the usual one: a guard that returns empty is a note saying "something upstream is wrong". Fix upstream.

The result page had one more rule by then. A finish that lands late no longer pushes a result from outside the exam screen. The result belongs to the moment of finishing, on the screen where the student finished, not to a network callback that may arrive when they are somewhere else.

## One rule for the door I did not ship

I wrote a rule for the fourth door, the paper the server closes under the student, and then took it out again along with the test and the release note. It described behaviour that was not in the build. Leaving the rule in the spec would have made the spec a wish list, and the next person would have implemented against a sentence that no test backed.

That is the cheapest kind of honesty available in a week like this: if the code does not do it, the document does not say it does.

## What I keep from this

- Name the exits. An exam has more than one, and each one needs its own sentence.
- Leaving is not answering. Exit withdraws, it does not submit.
- A queue that retries on its own will eventually send something on behalf of someone who left.
- An offline exit and its report can travel separately.
- A guard that returns an empty screen is hiding a cause, not fixing it.

None of it is exam-specific. Every flow with a timer has doors, and the bugs live in what each door thinks it is allowed to send.
