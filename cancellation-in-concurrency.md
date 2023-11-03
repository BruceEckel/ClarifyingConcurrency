_I started this post before the Rust Developer Retreat, thinking it would be fairly straightforward. But it opened some doors and created questions, and the deeper I went, the more questions opened up. During the retreat I also explored the way Rust handles cancellation for async, which is quite different. TLDR: Python’s asyncio makes cancellation quite easy, but the topic itself is messy and takes a while to understand._

Concurrency means starting with a program that takes too long to run and breaking it up into independently-running tasks, in the hopes that by doing so the program will make faster progress (this is by no means guaranteed). _How_ these tasks are executed varies depending on the strategy you use, but the basic idea of independently-running tasks is the foundation of concurrency.

In the best-case scenario, all tasks run to completion. But sometimes you need to cancel a task prematurely.

Because you now have a number of tasks, each running on its own, cancellation can be tricky. When you cancel a task, it cannot be in the midst of an operation that will leave allocated and/or unclosed resources. That is, it must clean up properly and not leave any evidence (side effects) that it ever ran. (Thus, [pure functions](https://en.wikipedia.org/wiki/Pure_function) can be safely cancelled at any point).

To achieve this, an independently-running task cannot simply be stopped. Only that task understands what proper shutdown means. To safely cancel a task, the task itself must periodically check to see whether a cancellation request has been sent to it.

## Pre-emptive multitasking

Because threads use preemptive multitasking, a thread-driven task can be interrupted _at any time_, whenever the operating system (OS) wants to perform a context switch (this is typically driven by a timer). The OS saves the registers and the stack which are restored when that task resumes. However, there is no sense of a “safe suspension point” when using a thread. That task could could have acquired a resource that needs to be released, or it could be in the midst of modifying something on the heap that it shares with the other tasks in the program (a.k.a. a _side effect_). Normally you might have a lock (mutex) protecting shared items, but a lock doesn’t protect against an abrupt termination of a task—in fact, you can end up stopping that task _after_ it has acquired a lock, which means it will never release that lock, permanently stopping any other task that needs to acquire that lock. Any resource you acquire that requires release when you are finished with it can end up being held indefinitely if a task is abruptly terminated. This produces the kind of slow resource leaks that leads to a “working system” that you “fix” by rebooting it at regular intervals.

Because of the heavy-handed nature of context switches when using threads, the language has no way to distinguish where it might be safe to check for cancellation. It simply doesn’t have the information about when the OS will receive the message from the timer telling it to do a context switch—that happens at runtime, and is unpredictable. This means that if the programmer needs to create a task that can be cancelled when using threads, that programmer must write custom code for that task and reason through its behavior, ideally understanding and finding all the corner cases that might cause problems. This requires a way to send a “shut down” message to that task. When the programmer knows that it’s safe, the task checks for the shut down message and performs clean-up and termination. As you might imagine, this job is rife with pitfalls and it takes an experienced thread programmer to get it right.

Unfortunately, just because you create a process for shutting down your task doesn’t prevent anyone from simply terminating it anyway, making all your careful work pointless.

Python’s **multiprocessing** library runs a task in a different OS process. What drives the task? That process’s thread. That task, running in a different process, also has the ability to make its own threads. So **multiprocessing** has the same issues as multithreading, just running in more OS processes. If you search for “terminate” in [the](https://docs.python.org/3/library/multiprocessing.html) **[multiprocessing](https://docs.python.org/3/library/multiprocessing.html)** [docs](https://docs.python.org/3/library/multiprocessing.html), you will see warnings about process termination throughout. In particular, the [programming guidelines section](https://docs.python.org/3/library/multiprocessing.html#programming-guidelines) contains a guideline titled “Avoid terminating processes”:

> Using the `Process.terminate` method to stop a process is liable to cause any shared resources (such as locks, semaphores, pipes and queues) currently being used by the process to become broken or unavailable to other processes.
>
> Therefore it is probably best to only consider using `Process.terminate` on processes which never use any shared resources.

In functional-programming terms, the only task that can work reliably in **multiprocessing** when termination is involved is a [pure function](https://en.wikipedia.org/wiki/Pure_function).

If you don’t know where context switching can happen, cancellation becomes quite complicated. As we will see, Python takes care of cancellation automatically and safely at coroutine suspension points. This is a huge advantage.

I note that coroutines generally use the term “cancel” (which sounds more like a request) while threads and **multiprocessing** use “terminate,” which has a more brutal sound to it—which fits for the way that you stop them (unless you add your own cancellation code and everyone respects it and never calls `terminate()`).

## Python coroutines

Python’s **asyncio** automatically performs cancellation checks at points in your code where the task can safely shut itself down. In an **asyncio** coroutine, these safe-cancellation points are the suspension points that occur any time you do an **await**. At these points the task is already being suspended, so they are the ideal places to (A) check for a cancellation request and (B) perform task shutdown.

Known suspension points require coroutine (vs. thread/process) support. Not every language that supports coroutines provides automated support for cancellation.

One of the dramatic benefits of using a cooperative multitasking system like Python’s **async** coroutines is that the suspension points—those that are marked with **await**—tell the compiler to generate code to save only necessary context information (typically local variables) rather than the entire stack, as threads do. This is the reason you can create vastly more coroutines than you can threads: each coroutine only saves the absolute minimum necessary information during a context switch. Also, coroutine systems typically work with a limited pool of threads, usually bounded by the number of cores you have—in Python’s case, a single thread because of the GIL ( _Global Interpreter Lock_). The thread used to drive the coroutines gets re-used without involving an OS thread context switch (normal OS thread context switching still happens, but it’s unrelated to executing the coroutines).

Coroutine suspension points are not only safe for context switching, but they are also safe as cancellation points. Because knowledge about suspension points is available to the compiler, it can automatically generate safe code to perform cancellation checking and task shutdown. Contrast this with the uncertainty of writing thread-termination code, and coroutines provide a huge advantage—even a concurrency novice can cancel a coroutine without any of the deep knowledge required to cancel a thread.

We want to demonstrate that Python **async** coroutines properly support cancellation. This will not be an exhaustive proof, but rather an exercise of the basic facilities. The code can be found [here](https://github.com/BruceEckel/python-experiments/tree/main/cancellation).

To verify that local objects get properly cleaned up during cancellation, we define an object that tracks its own creation and destruction:

```
# obj.py

class Obj:
    def __init__(self, id: str) -> None:
        self.id = id
        print(f"{self}")

    def __repr__(self):
        return f"[{self.id}]"

    def __del__(self):
        print(f"~{self}")
```

The `~` indicates that something is being cleaned up (reminiscent of C++).

Now we create a task that contains `Obj` creations in three places, interspersed with two `sleep()` suspension points:

```
# task.py
import asyncio
from obj import Obj

async def task(id: str, delay: int):
    print(f"starting task({id}, {delay})")
    o = Obj(id)
    if id == "G":
        print("Early return from G")
        return
    await asyncio.sleep(delay)
    op = Obj(id + "'")
    await asyncio.sleep(1.0)
    if id == "C":
        print("Self-cancelling C")
        raise asyncio.CancelledError
    opp = Obj(id + "''")
    print(
        f"~task({id}, {delay})"
        + f" containing {o}, {op} & {opp}"
    )
```

It’s important that `o`, `op` and `opp` are used in the final call to `print()` because otherwise they will be garbage collected before the end of the function.

When you have a reference to a task, you can call `cancel()` on that reference. The code generated for that task will check for and perform cancellation at the next suspension point. But what if you’re inside the task and need to end it? There are two options. The first is simply returning early from the function as seen in the code for `id == "G"`. You might not be able to complete the function with a `return`, however, and so in `id == "C"` we `raise asyncio.CancelledError`.

The `track()` function cancels a task or simply displays a message. In either case, it displays a list of currently “live” coroutines:

```
# track.py
import asyncio

def track(
    stop_task: asyncio.Task | None = None,
    msg: str = "",
) -> None:
    def display(s: str):
        print(s, end=": ")

    if msg:
        display("(" + msg + ")")
    if stop_task:
        name = stop_task.get_name()
        display(f"! {name}.cancel()")
        stop_task.cancel()
    for t in asyncio.all_tasks():
        print(f"{t.get_name()}", end=", ")
    print()
```

The `main()` program creates a group of tasks using a dictionary comprehension. It then cancels some of them at various later times. The calls to `sleep()` allow the other tasks to run and catch up with the new state of the system:

```
# cancellation.py
import asyncio
from task import task
from track import track

async def main():
    async with asyncio.TaskGroup() as tg:
        tasks = {
            id: tg.create_task(
                task(id, n + 1), name=id
            )
            for n, id in enumerate("ABCDEFG")
        }
        track(stop_task=tasks["A"])
        await asyncio.sleep(0.1)
        track(msg="After sleep")
        track(stop_task=tasks["B"])
        await asyncio.sleep(0.1)
        track(msg="After sleep")
        track(stop_task=tasks["F"])
        await asyncio.sleep(0.1)
        track(msg="After sleep")
        track(stop_task=tasks["D"])

asyncio.run(main())
```

A `TaskGroup` provides _structured concurrency_, so the scope created by the context manager cannot exit until all tasks created within that scope (using `tg`) have completed. Thus there are no calls to `join()` or `gather()`.

Here’s the output:

```
! A.cancel(): B, A, D, F, C, G, Task-1, E,
starting task(B, 2)
[B]
starting task(C, 3)
[C]
starting task(D, 4)
[D]
starting task(E, 5)
[E]
starting task(F, 6)
[F]
starting task(G, 7)
[G]
Early return from G
~[G]
(After sleep): B, D, E, F, C, Task-1,
! B.cancel(): B, D, E, F, C, Task-1,
(After sleep): D, E, F, C, Task-1,
! F.cancel(): D, E, F, C, Task-1,
(After sleep): D, Task-1, E, C,
! D.cancel(): D, Task-1, E, C,
[C']
Self-cancelling C
[E']
[E'']
~task(E, 5) containing [E], [E'] & [E'']
~[E]
~[E']
~[E'']
~[B]
~[C]
~[C']
~[D]
~[F]
```

`A` is cancelled immediately after it is created, and so never gets a chance to start—although it still appears in the task list ( `Task-1` is the thread for `main()`). The remaining tasks start, create their first `Obj` and get as far as their first `sleep()` suspension point. All except task `G`, which returns before it reaches `sleep()`, cleaning up its first `Obj` as it does so, indicated by `~[G]`.

After `main()`’s first `sleep()`, tasks `A` and `G` are no longer on the task list. You can see that every `Obj` that is created by a task is cleaned up, regardless of where the cancellation happens.

After creating `C’`, task `C` cancels itself by raising `CancelledError`. This is not treated as an ordinary exception; notice that I do not have any `except` clauses in the code to catch exceptions. And yet the `CancelledError` does not terminate the program and the only evidence we see of it is that task `C` terminates.

## Cancellation and Locks

What about the situation described earlier, where a task gets cancelled after acquiring a lock but before releasing that lock?

To test this we need to track the lifecycle of a lock, especially the “enter” method when a lock gets acquired and the “exit” method when it is released (code can be found [here](https://github.com/BruceEckel/python-experiments/tree/main/lock_cancellation/src)). We do this by inheriting from `asyncio.Lock`:

```
# trace_lock.py
import asyncio

class TraceLock(asyncio.Lock):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        print("Lock created.")

    async def __aenter__(self):
        print("Lock acquired.")
        await super().__aenter__()

    async def __aexit__(self, exc_type, exc_value, traceback):
        await super().__aexit__(exc_type, exc_value, traceback)
        print("Lock released.")

    def __del__(self):
        print("~Lock")
```

In the following code, `task_with_lock()` acquires a `TraceLock` and then `sleep()` s for five seconds. `main()` starts a task, waits for two seconds, then cancels that task—while `task_with_lock()` is still holding the lock.

```
# lock_cancellation.py
import asyncio
from trace_lock import TraceLock

async def task_with_lock(lock: TraceLock):
    async with lock:
        await asyncio.sleep(5)
        print("Sleep complete.")

async def main():
    lock = TraceLock()
    task = asyncio.create_task(task_with_lock(lock))
    await asyncio.sleep(2)
    print("cancelling task")
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        print("Task cancelled.")

asyncio.run(main())
```

Since we are not using a `TaskGroup` here, we must `await` the `task` so it runs to completion before `main()` exits. The `except` looks for a `CancelledError` which shows that even when it is not explicitly raised (as in task `C` in the previous example), `CancelledError` is used internally by Python to signal a cancellation.

The output verifies that a task holding a lock automatically releases it when cancelled:

```
Lock created.
Lock acquired.
cancelling task
Lock released.
Task cancelled.
~Lock
```

Because of the problems shown in this article, one of the impediments of thread programming (and I include `multiprocessing` here) is that it is very difficult to scale. Python coroutines are not simply daemon tasks that you fire off and forget about— `asyncio` tasks are guaranteed to cancel reliably, as well as handle errors (a topic for a later post). This makes coroutines much more composable and scalable than threads.

