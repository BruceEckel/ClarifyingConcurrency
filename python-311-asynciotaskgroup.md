Although it is predated by other researchers, most of the interest and popularity of _structured concurrency_ seems to originate from the article [Notes on structured concurrency, or: Go statement considered harmful](https://vorpus.org/blog/notes-on-structured-concurrency-or-go-statement-considered-harmful/) by Nathaniel J. Smith. Smith went on to create the [Trio](https://trio.readthedocs.io/en/stable/) library for Python, inspired by his research and by other libraries such as [Curio](https://curio.readthedocs.io/en/latest/). Smith’s work has been used as the foundation for structured concurrency in other languages, such as Kotlin.

One of the primary things Trio does is automate the `join` process by placing all generated tasks inside a scope, so you never have to worry about explicitly joining tasks (that is, waiting for a group of tasks to finish before proceeding). Trio also guarantees proper cancellation, either when a task is explicitly cancelled or if one or more exceptions is thrown. Getting cancellation to work right is an issue that many concurrency libraries “leave as an exercise for the user.” Since this is a complicated subject, Smith believes that a good concurrency system should take care of it for you, and Trio does.

Thanks for reading Programming, Together & Alone! Subscribe for free to receive new posts and support my work.

I had settled on Trio for my current project, but yesterday I was thrown into confusion when I stumbled across _[task groups](https://docs.python.org/3/library/asyncio-task.html#task-groups)_ which were added in Python 3.11, along with their companion _[exception groups](https://docs.python.org/3/library/exceptions.html#exception-groups)_. From [PEP 654](https://peps.python.org/pep-0654):

> The Trio \[2\] library has a MultiError exception type which it raises to report a collection of errors. Work on this PEP was initially motivated by the difficulties in handling MultiErrors \[9\], which are detailed in a design document for an improved version, MultiError2 \[3\]. That document demonstrates how difficult it is to create an effective API for reporting and handling multiple errors without the language changes we are proposing (see also the Programming Without ‘except \*’ section.)
>
> Implementing a better task spawning API in asyncio, inspired by Trio nurseries, was the main motivation for this PEP.

This suggests that Trio ran into some issues that required PEP 654 to address. Trio was designed for Python 3.7 or newer, which means, in its current state, it cannot utilize exception groups. Thus, Python 3.11 appears to provide a better solution than Trio.

There’s some nice coverage of Python 3.11 task groups and exception groups [here](https://realpython.com/python311-exception-groups/).

Here’s an example using 3.11 task groups ( [source](https://github.com/BruceEckel/python-experiments/blob/main/task-group/src/sleeper-asyncio.py)):

[![](https://substack-post-media.s3.amazonaws.com/public/images/5c0b80a3-6845-4b8f-b949-53ad20260cdc_622x793.png)](https://substackcdn.com/image/fetch/f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F5c0b80a3-6845-4b8f-b949-53ad20260cdc_622x793.png)

`show_tasks()` allows us to track the async behavior using some of the instrumentation functions provided by the `asyncio` library. `nap()` displays information before and after it sleeps. Every async library has its own version of `sleep()`, as well as other functionality, because each library has its own way to indicate suspension points, which are also points to check for cancellation.

In `main()`, the for loop looks for a task that has a coroutine name (the function name being run as that task) of “main” so it can change the task name to “Main”; otherwise that name will usually be the less-informative “Task-1.” The calls to `create_task()` include a `name` assignment for the same reason.

We use `asyncio.TaskGroup()` as a context manager, which produces the scope that controls the lifetime of all the tasks created within it. That is, you see no calls to `join()` or `gather()` to wait for all the created tasks to finish—the context manager does that for you, in the same way that Trio’s context manager does it for its “nurseries.”

In the calls to `create_task()`, you pass what looks like a normal function call (e.g.: `nap("a", 5)`), which to my eye seems more readable than Trio’s approach, which we shall see shortly (perhaps this is a small detail but readability is important to me).

Here’s the output:

```
A[False] Main[True] B[False] C[False]
tasks created
-------------------------
A[True] Main[False] B[False] C[False]
A napping 5s
-------------------------
A[False] Main[False] B[True] C[False]
B napping 3s
-------------------------
A[False] Main[False] B[False] C[True]
C napping 1s
-------------------------
A[False] Main[False] B[False] C[True]
C woken after 1s
-------------------------
A[False] Main[False] B[True]
B woken after 3s
-------------------------
A[True] Main[False]
A woken after 5s
-------------------------
Main[True]
Tasks complete
-------------------------
```

Initially the asynchronous tasks have been queued and **Main** is the task that’s running. Remember that because of the GIL, there is only ever a single thread of execution which is driving all the different tasks. So, when **A** is running, **Main**, **B**, and **C** all show **False**.

At the end of the context-manager scope, after line 29 in the code, you’ll see that there is no call to `join()` or `gather()` or anything else that would stop and wait for all the tasks to finish—and yet the output shows that they _do_ all finish before that scope completes. This is an essential part of what makes a concurrency system _structured_—it guarantees that all tasks complete, but without relying on programmer intervention.

Here’s what the program looks like after translating to Trio ( [source](https://github.com/BruceEckel/python-experiments/blob/main/task-group/src/sleeper-trio.py)):

[![](https://substack-post-media.s3.amazonaws.com/public/images/77c31a52-207d-4ab8-afa6-e42161ae51dd_672x878.png)](https://substackcdn.com/image/fetch/f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F77c31a52-207d-4ab8-afa6-e42161ae51dd_672x878.png)

The instrumentation is a bit more awkward, but it looks roughly the same. `asyncio.TaskGroup()` becomes ` trio.open_nursery()`, and `create_task()` becomes `start_soon()`. Note that the `start_soon()` argument list is just the name of the function ( `nap`) and its arguments rather than the parenthesized and more natural function call we see with `create_task()`.

I do understand the point of calling something a “nursery” and that `start_soon()` reminds you that a task has only been added and isn’t running at that point, but my own preferences lean to the `asyncio` names.

The output is different because apparently the main thread cannot be seen from the child task perspective (I may well have missed something; please note it in the comments):

```
Main[True]
tasks created
-------------------------
A[False] B[False] C[True]
C napping 1s
-------------------------
A[False] B[True] C[False]
B napping 3s
-------------------------
A[True] B[False] C[False]
A napping 5s
-------------------------
A[False] B[False] C[True]
C woken after 1s
-------------------------
A[False] B[True]
B woken after 3s
-------------------------
A[True]
A woken after 5s
-------------------------
Main[True]
Tasks complete
-------------------------
```

One of the many complications with concurrency is that there tend to be multiple different concurrency libraries, each attempting to express the concepts in whatever the author considers “a better way.” If you commit to one of these libraries, you run the risk of discovering, after you’ve invested much time and effort, that it has a flaw that makes your work difficult or impossible. Smith’s work on Trio, as well as the other libraries like Curio that came before it, has certainly moved the state of the art forward not just for Python but for other languages as well. I admit a preference towards using “batteries included” libraries, and it seems like Python 3.11 `asyncio.TaskGroup` \+ exception groups are likely to solve problems that Trio, being anchored to Python 3.7, cannot. But I can’t be sure; when exception groups and task groups were mentioned on [Trio issues](https://github.com/python-trio/trio/issues/2357), one commenter said:

> Taskgroups are still a bolt-on to asyncio and there are several cases where they are ignored rather thoroughly. `create_server` is one example. Also, there's the arcane Protocol+Transport construct which Trio has replaced with a reasonable and much more accessible Stream concept, which asyncio also has acquired but seems to have no plans to migrate to.

But my sense is that there will likely be more effort focused on Python’s built-in `asyncio` library. Not that Trio will go away—for example, the `attrs` library is still maintained despite the incorporation of `dataclasses` into standard Python. But for one thing, it’s a lot easier to argue the use of a standard library than an add-on. Thus, it seems like a good choice to use `asyncio` exception groups and task groups, at least until I discover that it doesn’t do something essential. If you know something about this, please mention it in the comments.

Thanks for reading Programming, Together & Alone! Subscribe for free to receive new posts and support my work.

