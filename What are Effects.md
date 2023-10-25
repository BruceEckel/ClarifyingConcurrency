# What are Effects?

Imagine there's a circle surrounding you, representing a boundary (don't worry about the size; you have permission to resize your imaginary boundary as needed). Inside this boundary are things that you have control over in your life; things that are completely reliable and predictable, as much as that is possible. For example, you know how your toaster works, and its idiosyncrasies. Your stove, dishwasher, washing machine, shower---all these are under your control, and you can expect consistent and predictable results when you use them. You could stay in your house just using these devices, getting groceries delivered and never leaving. You would always know how things work and nothing would change. 

This becomes boring. We get stimulus and grow by connecting with the outside world, where things are unpredictable. The world outside the circle.

When you interact with a person, they are outside your circle of certainty, and you can't anticipate what will happen. If you say "hello" to someone they may respond pleasantly, neutrally or angrily, depending on their current situation and mood. If you ask someone the time of day, they might refer to a non-digital wristwatch (possibly not very accurate), a phone (probably quite accurate), or they may have no timepiece at all, or are too much in a hurry to tell you the time. They might just give you the time, but perhaps they want to talk---so you don't know how *long* it will take to get the time, and after you get it, it might no longer be usable.

Consider a more complex example. You are running a small storage company and you hire someone to store and fetch items for you. When you ask for a stored item, you're not sure how long it will take: the person might be on a break or moving slowly that day, the item might be near or far in the warehouse, or the person might already have a significant list of tasks to complete before they can get to your request. It's also possible that the item might not be there.  There are a number of degrees of unpredictability, and by knowing what they are you can compensate for them in various ways. If you just ignore these unpredictability factors, as we have traditionally done in programming, you can't compensate for them.

*Effects* are these unpredictability factors. When you call a function which is outside your circle of certainty, you initiate an operation that has unpredictable results; i.e. a function that may produce effects. If we know what these effects are, we can work with them to create a more reliable program. It doesn't end with reliability, though. If a system knows what the effects are for a particular function, it can provide other useful facilities.
## Errors are Effects

One kind of unpredictability that we *have* started to pay attention to is errors. As you cannot predict when an error will occur, these are a type of effect. Errors are very clear: if some aspect of a function call fails, it will report that failure as an error.

Exceptions are a problem here. Exceptions exist in a world outside of normal control flow, and when an exception is thrown, you can choose to catch it and handle it ... or ignore it, at which point it becomes a runtime error. What we want is for the compiler to ensure that we have properly dealt with all errors, at compile time. In addition, the further away you get from the site of a thrown exception, the less context information you have. Ideally, the compiler requires full error coverage at the site of each function call, rather than anywhere on the exception stack. You still have the *option* of passing the error on, but the compiler requires that choice to be made at the function call site.

The problem happens because we traditionally think of functions like this:
1. You pass any number of arguments to the function.
2. The function returns a single result.

We have always thought of the result as a single value: the answer you desire. In reality, you might not get that answer because there's a failure. To solve the problem, we *expand the result* to include not just the desired answer but also the failure information. Instead of returning a single value of the type of the desired answer, we return a structure containing the answer *plus* error information.

Now when you call such a function, you can't just grab the answer and go on your merry way. You are forced to unpack the returned structure, first looking for error information and dealing with that. Only if there is no error information do you take the answer and continue.

The result is typed, and that type information means that the compiler is able to track your code, and enforce that you have handled all the possible error conditions. The only way for errors to slip through the cracks is if you explicitly push them into those cracks. You must write the code that does that, and now that code is visible as a decision you've consciously made (ignoring an exception requires no code at all, so no one can see that you've done it).

By treating errors as effects, your programming system is able to guarantee that you are mitigating all those effects, thus producing a more reliable program.
## Pure Functions & Referential Transparency

What if a function is inside your "circle of certainty," and have no effects? It produces the same result for the same arguments, every time, with no surprises (errors). We call this a *pure function*, and it has special characteristics:

1. Because a pure function returns identical results for the same arguments, those results can reliably be placed in a lookup table, and a lookup in that table can be substituted for calling the function. This is called *referential transparency*.
2. Calling a pure function does not modify the effects of the function that calls it.

In contrast, if you're in a function that calls another function that has effects, those effects must be incorporated into the effects of the calling function.
## Other Kinds of Effects

Errors are a specific type of effect. A more general effect is seen when you call a "time" function. Getting the time is not a pure function because you get a different result every time you call it (the call could also fail if the underlying system doesn't include a clock, or if it has some kind of error). There's not much "mitigation" to do in this case, but you must be aware that any call to time means that your function cannot be treated as pure.

Now consider a database, the analogy of hiring a person to work storing and retrieving items in your warehouse. Here there are a number of effects that you need to mitigate:
1. You don't know how long the transaction will take. The database might currently be bogged down with requests.
2. You don't know if an item you want to retrieve is there.