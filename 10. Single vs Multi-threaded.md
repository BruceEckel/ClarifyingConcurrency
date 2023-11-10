As I continue delving into the vagaries of concurrency, two things become clear:

1. The programming community is still figuring it out. We are doing more experiments and some things like coroutines provide decent solutions for many situations, but no one universal answer has yet presented itself (and such an answer may not exist).

2. Right now concurrency is a bag of strategies that you apply depending on the details of the problem you are solving. Note that concurrency is a subset of the general problem of performance optimization, which is also a collection of strategies.

That said, we do seem to periodically gain insights. Both the ZIO (Scala) library and the JVM’s project Loom are able to provide concurrency _without_ requiring the programmer to mark suspension points explicitly in their code (as we must with **async/await**). In ZIO, whenever a flatmap occurs (whenever an _effect_ is applied), that task can be safely suspended. With Loom, I surmise that the JVM can suspend a task between JVM opcodes (possibly only certain opcodes, perhaps all—I’m purely guessing here).

_Somehow_ the underlying system must be able to determine safe suspension points (the underlying system can include one or both of the compiler and the runtime depending on your language and library). This allows it to save and restore only the tiny subset of state necessary for the current task. Without this information, the system must “save the world,” which is why threads are so limited in quantity and slow during context switches: they don’t know what subset of information needs saving, so they must save the whole stack. If the system knows more about the source code and the suspension points, it can save only what is necessary, typically a subset of the task’s local variables. This is a tiny amount compared to what a thread must save, so a system that determines safe suspension points (like **async**/ **await**) can have millions of tasks. With threads you are limited to, at best, thousands, and typically adds the need for thread-sharing schemes, which you don’t have to think about with **async**/ **await**.

When learning concurrency, especially if you start with the specific strategy of **async**/ **await**, it can be easy to fall into the mental model that the only thing that slows down your program is IO, which relies on external systems that are out of our control and take an unknown amount of time. This means that all **await** operations are ultimately connected to IO—even the timers used in calls to “sleep” are external to the CPU cores, just like the rest of IO. Thus, with **async/await**, all _blocking_ operations block because of IO.

It took me a while to get to the “understanding” that blocking == IO. Then I read something by John de Goes that pointed out this fundamental conceptual error. The important thing is that some task is taking _too long_, which is preventing the progress of other tasks. It doesn’t matter to your program _why_ that task is blocking the progress of the other tasks—yes, the culprit is very often IO, and IO operations are clearly visible, so it’s easy to treat IO as a suspension point. But just because IO is the easy target here, that does not mean that **async**/ **await** solves all your concurrency problems. It solves IO, but not the general problem of “a function that takes too long.”
## Problem Term: “Blocking”

_\[I’m working through these issues because I want to create consistent terminology throughout the book.\]_

The term _blocking_ deserves an aside here, because it is one of numerous terms casually used in multiple ways, confusing newcomers. Even in introductory narratives, these terms are often used with the attitude that “everyone obviously already knows this,” an attitude that those with the _curse of knowledge_ are unfortunately prone.

The general, and more intuitive meaning of _block_ is to _prevent the progress of other tasks_. Task B blocks the progress of Task A if A relies on some resource provided by B (including the answer to a calculation) that B is taking its time to produce. Note that this is the essential definition because, ultimately, the only reason we’re messing with concurrency is that we need to produce results more quickly. We’ve broken our program into tasks and we’re trying to get those tasks, working together, to produce results more quickly than the linear version of the program.

Writers will also say that something “is blocked,” which by itself is not terrible. In the above example, Task B _is blocking_ the progress of Task A, so Task A _is blocked by_ Task B.

_Is blocked_ appears to produce the unfortunate term _blocks_, as in “Task A blocks.” This is quite confusing because suddenly Task A seems to have a new internal quality that it can, what, block itself? Just randomly decide to stop? I suspect this situation arose because, initially, the majority of concurrency experts came from environments where only threads were available, and they were used to thinking in lower-level terms.

When we have coroutines (such as **async/await**), the idea of one task blocking another still exists. Since we now have a cooperative system, a task suspends itself rather than being stopped by an external force (i.e., the OS thread scheduler). So it is more useful to say that, when a task is blocked by another task, _it suspends itself_ or perhaps simply _yields_ (a thread clearly doesn’t “yield” because that implies choice, and the core is forcibly snatched away from the thread during a context switch).
### Another problem term: “Thread”

While I’m on the subject of terminology, _thread_ is another challenge. Ultimately, _everything_ is run by a thread—when the OS creates a process, it also creates a “main” thread to execute the code in that process.

Here’s the first problem with the way the term “thread” is used:

> This main thread can in turn spawn other threads to run tasks concurrently.

Notice how casually I conflated “thread” with “code that is being run by that thread.” It’s actually the latter that spawns the thread and saying that “the thread did it,” while on some level sort-of correct, is confusing. But you’ll see this all the time and you have to mentally say “the thread is just the mechanism that’s driving the task.”

Original concurrency systems directly hand you OS threads, with the OS controlling the (preemptive) context switches. But coroutines are cooperative and the context switches happen at known points (rather than at any instant, as with threads). With threads, the “execution mechanism” is grabbed away from the task by the OS. With coroutines, the execution mechanism (called the _event loop_ in Python) is voluntarily yielded whenever an **async** function is called.

So the second problem is that, even though everything is ultimately driven by a thread, OS thread context switches are controlled by the OS and happen at any instant. Coroutines use their own, higher-level system to voluntarily produce context switches at safe suspension points. Other systems call these higher-level-and-voluntary but still thread-like elements by a different name, such as _green threads_ or _virtual threads_ or _fibers_ or _user-mode_ _threads_ or _lightweight threads_, etc. Apparently people really wanted to hold on to the idea of threads—which, again, _are_ actually driving everything, so that’s confusing—while at the same time replacing the concept of OS context switching with cooperative context switching. Plus, OS context switching is still going on, just not in a way that affects the coroutine, so that’s… also confusing.

The coroutine abstraction hides both the idea that the OS thread is driving everything _and_ the awareness of the OS context switches. So holding on to the term _thread_ is confusing and counter-productive for novices, and adds cognitive load to experts. I acknowledge that the majority of articles treat the term _thread_ casually, but I think it would be useful to have a term that abstracts the idea of _execution mechanism_ (something like “executor” might work, even with existing usage). I think this would also discourage the conflation of the execution mechanism with the code that is being executed.
## Coroutines vs. Parallelism

In the [Wikipedia Article on Coroutines](https://en.wikipedia.org/wiki/Coroutine), it says:

> “Coroutines provide concurrency, because they allow tasks to be performed out of order or in a changeable order, without changing the overall outcome, but they do not provide parallelism, because they do not execute multiple tasks simultaneously.”

This certainly fits with Python’s event loop, which only ever runs one thing at a time—this constraint is often attributed to Python’s _global interpreter lock_ (GIL), but the above definition makes it appear that non-parallelism is intrinsic to the definition of coroutines.

But is this true? Java’s original green threads (abandoned in 2000) shared a single operating system thread. But in Go, [coroutines automatically run in parallel](https://www.digitalocean.com/community/tutorials/how-to-run-multiple-functions-concurrently-in-go) (I occasionally look at Go but only find it interesting for its design choices).

By default, Rust’s **tokio** library uses multiple threads for its coroutines, although you can tell it to use a single thread. [Here’s an example](https://github.com/BruceEckel/rust-experiments/tree/main/tokio_scheduler_threads) that tests both:

``` rust
use rand::rngs::StdRng;
use rand::{Rng, SeedableRng};
use std::ops::Range;
use std::thread;
use std::time::Instant;
use tokio::runtime::{Builder, Runtime};

// Upper & lower percent AND random range:
const SPAN: Range<i32> = 0..100;

#[derive(Copy, Clone)]
pub struct YieldPercent {
    value: i32,
    // 'value' is private: outside this
    // module you cannot create a
    // YieldPercent using the
    // default constructor, as in
    // YieldPercent{ value: 10 }
}

impl YieldPercent {
    // You are forced to go through new():
    pub fn new(value: i32) -> Self {
        Self {
            value: value
                .clamp(SPAN.start, SPAN.end),
        }
    }
    pub fn list(values: &[i32]) -> Vec<Self> {
        values
            .iter()
            .map(|&value| Self::new(value))
            .collect()
    }
    pub fn value(&self) -> i32 {
        self.value
    }
}

pub async fn rand_int(
    rng: &mut StdRng,
    yield_percent: YieldPercent,
) -> i32 {
    let random = rng.gen_range(SPAN);
    // Probability-based context switch:
    if random < yield_percent.value() {
        tokio::task::yield_now().await;
    }
    random
}

pub async fn calculation(
    name: &str,
    yield_percent: YieldPercent,
) {
    println!(
        "\nStart '{}' with yield_percent {}",
        name,
        yield_percent.value()
    );
    let current_thread = thread::current();
    println!(
        "'{}' on thread {:?} (id: {:?})",
        name,
        current_thread.name().unwrap_or("X"),
        current_thread.id()
    );
    let start = Instant::now();
    let mut rng: StdRng =
        SeedableRng::from_seed([42; 32]);
    let mut sum = 0;
    for _ in 0..1_000_000 {
        sum +=
            rand_int(&mut rng, yield_percent)
                .await;
    }
    println!(
        "Task '{}' ends after {:?}: {}",
        name,
        start.elapsed(),
        sum
    );
}

pub fn run_tasks(
    rt: &Runtime,
    yield_percent: YieldPercent,
) {
    let start = Instant::now();
    rt.block_on(async {
        let _ = tokio::try_join!(
            tokio::spawn(calculation(
                "one",
                yield_percent
            )),
            tokio::spawn(calculation(
                "two",
                yield_percent
            ))
        );
    });
    println!(
        "=> Elapsed: {:?}",
        start.elapsed()
    );
}

fn main() {
    let yields = YieldPercent::list(&[
        0, 5, 25, 50, 75, 100,
    ]);
    println!("Single-threaded tokio async");
    let rts = Builder::new_current_thread()
        .enable_all()
        .build()
        .unwrap();
    for yld in &yields {
        run_tasks(&rts, *yld);
    }

    println!("\nTwo-threaded tokio async");
    let rtm = Builder::new_multi_thread()
        .enable_all()
        .worker_threads(2)
        .build()
        .unwrap();
    for yld in &yields {
        run_tasks(&rtm, *yld);
    }
}
```
`const SPAN` ensures that the two ranges in the program vary together.

A `YieldPercent` can only be created using a `value` within `SPAN`. Because the `YieldPercent ` type guarantees this is true, I never have to test it for correctness (if you test for correctness of a value in multiple places, those checks can easily get out of sync). `YieldPercent` has the conventional `new()`, which uses `clamp()` so any value less than `SPAN.start` is set to `SPAN.start`, and any value greater than `SPAN.end` is set to `SPAN.end`. `YieldPercent` also contains a utility function `list()` that takes an array of `i32` and produces a `Vec` of `YieldPercent` objects. Note that `YieldPercent` is very small (the size of an `i32`), immutable, and implements `Copy`, so it is passed by value everywhere.

`rand_int()` produces a random number while giving the opportunity to yield (context switch) based on the `yield_percent` argument.

`calculation()` sums a million random numbers, repeating the random-generator seed for each call to `calculation()` so it produces the same result each time. It also displays information about the thread it is using.

`run_tasks()` uses a `Runtime` object to run two `calculation()` tasks against each other, timing them.

In `main()`, we create a `Vec` of `YieldPercent` objects called `yields`, then create two different `Runtime` objects, with `rts` using a single thread and `rtm` using two threads. `run_tasks()` is then run with each different value in `yields`. This way we can see the effect of different percentages of context switching.

Here’s the output, produced with `cargo run --release`:

```
Single-threaded tokio async

Start 'one' with yield_percent 0
'one' on thread "main" (id: ThreadId(1))
Task 'one' ends after 4.3511ms: 49485726

Start 'two' with yield_percent 0
'two' on thread "main" (id: ThreadId(1))
Task 'two' ends after 4.2649ms: 49485726
=> Elapsed: 8.6717ms

Start 'one' with yield_percent 5
'one' on thread "main" (id: ThreadId(1))

Start 'two' with yield_percent 5
'two' on thread "main" (id: ThreadId(1))
Task 'one' ends after 61.4586ms: 49485726
Task 'two' ends after 61.4661ms: 49485726
=> Elapsed: 61.4813ms

Start 'one' with yield_percent 25
'one' on thread "main" (id: ThreadId(1))

Start 'two' with yield_percent 25
'two' on thread "main" (id: ThreadId(1))
Task 'one' ends after 282.5204ms: 49485726
Task 'two' ends after 282.5307ms: 49485726
=> Elapsed: 282.548ms

Start 'one' with yield_percent 50
'one' on thread "main" (id: ThreadId(1))

Start 'two' with yield_percent 50
'two' on thread "main" (id: ThreadId(1))
Task 'one' ends after 559.6368ms: 49485726
Task 'two' ends after 559.6491ms: 49485726
=> Elapsed: 559.668ms

Start 'one' with yield_percent 75
'one' on thread "main" (id: ThreadId(1))

Start 'two' with yield_percent 75
'two' on thread "main" (id: ThreadId(1))
Task 'two' ends after 809.8934ms: 49485726
Task 'one' ends after 809.9119ms: 49485726
=> Elapsed: 809.926ms

Start 'one' with yield_percent 100
'one' on thread "main" (id: ThreadId(1))

Start 'two' with yield_percent 100
'two' on thread "main" (id: ThreadId(1))
Task 'one' ends after 1.080246s: 49485726
Task 'two' ends after 1.0802555s: 49485726
=> Elapsed: 1.0802734s

Two-threaded tokio async

Start 'one' with yield_percent 0

Start 'two' with yield_percent 0
'two' on thread "tokio-runtime-worker" (id: ThreadId(3))
'one' on thread "tokio-runtime-worker" (id: ThreadId(2))
Task 'two' ends after 4.3716ms: 49485726
Task 'one' ends after 4.5575ms: 49485726
=> Elapsed: 4.9515ms

Start 'one' with yield_percent 5
'one' on thread "tokio-runtime-worker" (id: ThreadId(2))

Start 'two' with yield_percent 5
'two' on thread "tokio-runtime-worker" (id: ThreadId(2))
Task 'two' ends after 19.0891ms: 49485726
Task 'one' ends after 19.739ms: 49485726
=> Elapsed: 19.8095ms

Start 'one' with yield_percent 25
'one' on thread "tokio-runtime-worker" (id: ThreadId(3))

Start 'two' with yield_percent 25
'two' on thread "tokio-runtime-worker" (id: ThreadId(2))
Task 'two' ends after 42.3526ms: 49485726
Task 'one' ends after 141.691ms: 49485726
=> Elapsed: 141.7936ms

Start 'one' with yield_percent 50
'one' on thread "tokio-runtime-worker" (id: ThreadId(3))

Start 'two' with yield_percent 50
'two' on thread "tokio-runtime-worker" (id: ThreadId(2))
Task 'two' ends after 110.8632ms: 49485726
Task 'one' ends after 205.8676ms: 49485726
=> Elapsed: 205.9513ms

Start 'one' with yield_percent 75
'one' on thread "tokio-runtime-worker" (id: ThreadId(3))

Start 'two' with yield_percent 75
'two' on thread "tokio-runtime-worker" (id: ThreadId(3))
Task 'two' ends after 167.3673ms: 49485726
Task 'one' ends after 208.3749ms: 49485726
=> Elapsed: 208.4066ms

Start 'one' with yield_percent 100
'one' on thread "tokio-runtime-worker" (id: ThreadId(3))

Start 'two' with yield_percent 100
'two' on thread "tokio-runtime-worker" (id: ThreadId(2))
Task 'two' ends after 203.9844ms: 49485726
Task 'one' ends after 450.9418ms: 49485726
=> Elapsed: 450.9891ms
```
When there’s only one thread and no yielding (a `yield_percent` of zero), Task one runs to completion before Task two can start. If the `yield_percent` is nonzero, the two tasks interleave. If there are two threads, the tasks interleave even with a `yield_percent` of zero.

If there’s only one thread, the task runs on “main,” otherwise two new “runtime worker” threads are allocated.

If we plot the results ( [plotting code](https://github.com/BruceEckel/rust-experiments/tree/main/tokio_scheduler_threads/plot)) we see a very linear relationship between `yield_percent` and elapsed time:

[![](https://substack-post-media.s3.amazonaws.com/public/images/61cb1156-9908-4b6d-9fd9-610399b566fe_1000x600.png)](https://substackcdn.com/image/fetch/f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F61cb1156-9908-4b6d-9fd9-610399b566fe_1000x600.png)

This plot indicates that using multiple threads to drive your coroutines is an obvious win. At least, in Rust it is.

Context switching seems quite expensive. Note, however, that `rand_int()` is a very small function so the context switch becomes a significant part of that task. If your task contains more activity, the context switch will have less of an impact. In addition we are context-switching a million times per call to `calculation()`, and it’s more likely that you’ll make vastly fewer **async** calls. Also, `calculation()` is a CPU-intensive activity so coroutines don’t buy you much when using a single core. Notice that it isn’t obvious that **async** calls will speed things up. This is the type of subtle thinking you must cultivate in order to understand concurrency issues.

## The Simplicity of Single-Threaded Async

The previous example makes it seem obvious that you should use multiple threads to drive your coroutines as Go and `tokio` do. I spent several hours with ChatGPT trying to create a Rust example that would generate a data race before discovering, [in the Rustonomicon](https://doc.rust-lang.org/nomicon/races.html):

> Safe Rust guarantees an absence of data races, which are defined as:
>
> - two or more threads concurrently accessing a location of memory
>
> - one or more of them is a write
>
> - one or more of them is unsynchronized
>
>
> A data race has Undefined Behavior, and is therefore impossible to perform in Safe Rust. Data races are _mostly_ prevented through Rust's ownership system: it’s impossible to alias a mutable reference, so it’s impossible to perform a data race.

This is a huge win for the ownership system—and further observation that ownership is not just about eliminating the garbage collector. My guess is that only pure functional languages have previously been able to eliminate data races.

This guarantee is also why it is safe for **tokio** to run coroutines in parallel using multiple threads.

In the Go language it’s [relatively easy to create a data race](https://go.dev/play/p/t92HqjRl7cv). Go contains a “race detector” tool that helps find these ( `go run -race`). Go also emphasizes that you should design your goroutines using _communicating sequential processes_ (CSP), even going so far as to make channels a built-in type.

Note that even though Rust (in its normal “safe” mode) guarantees that you cannot have data races, you can still produce _logical_ races, deadlocks in particular. For example, you can write [Dining Philosophers in Rust](https://github.com/BruceEckel/rust-experiments/tree/main/race_conditions/dining_philosophers).

Python was not originally designed with concurrency in mind. Because everything is mutable by default, it’s easy to accidentally produce data race conditions. Because of the GIL, only one Python coroutines can run at a time—each coroutine can suspend and resume multiple times during its execution, handing the event loop back so another coroutine can run until it reaches one of its suspension points. This can reduce the incidence of data races because only one task can modify data at any one moment. Of course, if your task reads a variable, then suspends, then writes data back into that variable, another task might modify that variable while your task is suspended. So the GIL _helps_ but doesn’t eliminate the problem. If you have a particularly nasty concurrency system that you want to ensure is correct, you might consider creating an Python extension in Rust using [PyO3](https://pyo3.rs/) (ChatGPT does a pretty nice job of both translating your Python code to Rust and telling you how to configure your Rust project to generate the Python extension). That way your concurrent code will be verified by Rust to be data-race free. Note that your Rust extension can [release the GIL](https://pyo3.rs/v0.9.2/parallelism) while it’s not making Python API calls.
### Thread Confinement: Taking it to the Extreme

Most Graphical User Interface (GUI) systems use a design called _thread confinement_ to completely prevent data races. Your display device is a big shared resource, and using mutexes would be prohibitively expensive.

With thread confinement, each task is placed on a work queue. The execution mechanism, driven by a single thread, takes each task off the queue and _runs it to completion_ before fetching the next task. This means there can never be any interleaving between tasks, so the shared data (the display) is only ever modified by a single task at a time.

Even though the concept of “task” is used in thread confinement, this is not concurrency, because only one task can ever be active at a time. It’s like a weird kind of parallelism—all the tasks are independent and _could_ easily be run on multiple cores, except for the design requirement that they cannot be run concurrently to prevent data races on the display.

Thread confinement is the reason that GUI systems warn against creating long-running tasks. Since each task in the queue runs to completion, a long-running task prevents updates by other tasks in the queue, making the display appear frozen.
## What’s the Best Default?

In the [episode of Happy Path Programming where we interview John de Goes](https://podcasters.spotify.com/pod/show/happypathprogramming/episodes/85-Scala--Rust--and-Durable-Computing-with-John-De-Goes-e29ca1s), we spend the last 20 minutes exploring his ideas around this issue. He points out that—of course—“it depends on the problem you’re solving.”

The most common case, he argues, is writing business software. That is also the situation where you’re likely to get the least-experienced concurrency programmers, so the default choice is important here, to keep those programmers from making difficult mistakes. That default is single-threaded coroutines, because only ever running one of those coroutines at a time, together with known safe suspension points, lowers the chance that one coroutine will step on the data of another—but by no means eliminates it (Rust sidesteps this constraint, as does Go as long as you stick religiously to CSP).

Finally, notice how the author of the Wikipedia quote was certain that coroutines “do not execute multiple tasks simultaneously.” The topic of concurrency is rife with these kinds of misunderstandings, delivered authoritatively. That’s a big reason I’m writing this book: to give you the foundation necessary to see through these kinds of conceptual variations. I can’t fix the problem—the literature is out there, each with its own mental-model skew. But I can give you the tools to parse that literature without giving up in abject confusion.
## **References:**

- [Here’s an article](https://maciej.codes/2022-06-09-local-async.html) that talks about exactly this problem in Rust, and states that concurrency systems should be single-threaded by default. \[I am unsure of this conclusion because the ownership model eliminates data races\].

- [The State of Async Rust](https://corrode.dev/blog/async/) states: “Multi-threaded-by-default runtimes cause accidental complexity completely unrelated to the task of writing async code.” The article also makes a case for, in Rust, choosing threads before async.

- [This goes further](https://www.chiark.greenend.org.uk/~ianmdlvl/rust-polyglot/async.html): “I recommend using ordinary (synchronous) Rust, with multithreading where you need concurrency, unless you have a reason to do otherwise.”

