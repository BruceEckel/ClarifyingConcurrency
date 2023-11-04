Go’s default concurrency model appears to be “the simplest approach,” which means:

1. Every goroutine is a daemon thread. It’s certainly simple to ignore task completion, cancellation, and error handling. Unfinished tasks are terminated when the program ends, so it doesn’t matter if terminating a task puts the program in an undefined state. If you need completion, cancellation, or error handling, you add it yourself with more complicated code.

2. Every goroutine only uses communicating sequential processes (CSP). This prevents data races with the least amount of cognitive overhead. CSP works great as long as you’re not moving so much data that it impacts your program. Again, for the majority of Go programs this is a fine default, and again, you can use other approaches by adding more complicated code.

The statement “every goroutine is a daemon thread” might sound odd at first, because every concurrency system has a way to start a task, and that task will keep running until it either ends on its own or is terminated by an external agent. What makes something a daemon is that it “runs in the background.” In particular, daemons don’t have a connection with the task/process/thread that started them. In Unix, daemons are typically started by a process that then exits, leaving the daemon with no parent process to control it. It just keeps running in the background.

Let’s look at how Go does things:

``` go
package main

import (
	"fmt"
	"time"
)

func accumulate(s string, n int) int {
	sum := 0
	for ; n > 0; n-- {
		sum += n
		fmt.Printf("%s: %d\n", s, sum)
	}
	return sum
}

func main() {
	fmt.Printf("Total: %d\n", accumulate("A", 5))
	go accumulate("B", 4)
	time.Sleep(100 * time.Millisecond)
}
```

Following the normal model for functions, `accumulate()` takes arguments and returns a result. In the first line of `main()`, we call `accumulate()` and display that result. But in the second line, we use the `go` statement, and _this statement doesn’t return anything_. I get no “handle” back from starting a goroutine, which means I have no connection with that goroutine that would allow me to wait for it to finish, cancel it, receive errors from it, or _to receive its return value_. The fact that I don’t get a handle back from the `go` statement is what makes it a daemon, as it automatically consigns goroutines to the background, with no connection to the code that starts them.

The above program doesn’t produce errors. In particular, you don’t get a notification telling you that using `accumulate()` as a goroutine means the return value is ignored—that value is quietly dropped on the floor. This has implications:

- Although Go eliminates [red/blue function coloring](https://journal.stuffwithstuff.com/2015/02/01/what-color-is-your-function/), goroutines introduce a similar issue because you must pay attention to whether your function has a return value, and know that calling it as a goroutine produces different behavior than calling it as a normal function. This compromise keeps things simple for beginners because they don’t need to know details about creating non-daemon tasks, such as futures/promises.

- The basic concept of a function is violated when it is used as a goroutine. Such functions no longer take inputs and produce an output, but do _everything_ via side effects. If you write a function that might be used as a goroutine, you must write it differently. It is not as simple as saying “any function can be used as a goroutine.” (The Pascal language has keywords to differentiate functions, which return values, from procedures, which don’t. This distinction always puzzled me, because you can just write a function that doesn’t return anything. Now I wonder if this wasn’t intended to eventually support something like goroutines).
## The Easy Concurrency Model

Go’s defaults are a great fit for a certain set of programs. If Go’s goal is to enable programmers to “program concurrently without knowing about concurrency,” then I must admit they’ve done an admirable job. But it seems to me that Go has been pitched (or at least, absorbed by the Go community) as a general purpose language suitable for all applications.

Concurrency is the area where I see the most incidences of the Dunning-Kruger effect (i.e.: you learn a little and think you know a lot). There are so many different strategies/niches in the concurrency world that it is extremely easy to learn one of those and immediately think that you understand concurrency. A big giveaway here is when someone declares concurrency to be “easy.” Understand that this person has reached a happy place where they’ve gotten something working after being told that concurrency is a big, scary thing. Telling them “actually, concurrency is still big and scary” will not be gratefully received—they want to stay in that happy place and you’re rocking the boat.

I wonder what happens when all these Go programmers who have been existing in this happy concurrency world encounter its limits. The logical solution would be to understand Go’s limits and choose a different technology when it no longer fits. But that requires knowing enough about concurrency that you can see and understand those limits.

If you’re invested in Go, you want to keep using Go. You incrementally learn more and add more complexity to your program as needed. Like all incremental complexity, this seems perfectly rational in the moment—why not add a little bit of complexity rather than making fundamental technology changes? Lots of projects totter along like this, regularly incrementing their complexity, and never reach the “aha” moment when they realize they’ve pushed that technology beyond its boundaries. Will the company see the necessity of rewriting the project so it can continue to expand, or will they keep complexifying the current project one feature at a time?

From a cultural standpoint, Go’s approach might be excellent. Get everyone started with a relatively-foolproof model. Give them experience with basic concurrency before moving on to more complicated issues. This is generally how we teach, to keep from intimidating and overwhelming students. Remember, a primary reason for C++’s success is that it allows programming in C, offering C programmers a gentler transition into the language instead of forcing them to adapt to a completely new paradigm. This was important in an age when C was the only language someone might have learned (that person often having started in assembly language).

My experience of concurrency is that it lives in a different universe than programming languages. It is a leaky abstraction and you can easily encounter operating system or even hardware details. Concurrency is a collection of strategies, and these are often dramatically different from each other.

Learning the (possibly) easiest approach (daemons + CSP) is certainly a reasonable way to onboard new concurrency programmers, but I am curious to see what happens after time, when projects mature enough to hit the boundaries of that approach.

