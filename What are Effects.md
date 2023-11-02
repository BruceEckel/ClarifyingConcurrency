Imagine there’s a circle surrounding you, representing a boundary (don’t worry about the size; you have permission to resize your imaginary boundary as needed). Inside this boundary are things that you have control over in your life; things that are completely reliable and predictable, as much as that is possible. For example, you know how your toaster works, and its idiosyncrasies. Your stove, dishwasher, washing machine, shower—all these are under your control, and you can expect consistent and predictable results when you use them. You could stay in your house just using these devices, getting groceries delivered and never leaving. You would always know how things work and nothing would change.

This becomes boring. We get stimulus and grow by connecting with the outside world, where things are unpredictable. The world outside the circle.

When you interact with a person, they are outside your circle of certainty, and you can’t anticipate what will happen. If you say “hello” to someone they may respond pleasantly, neutrally or angrily, depending on their current situation and mood. If you ask someone the time of day, they might refer to a non-digital wristwatch (not very accurate), a phone (quite accurate), or they may have no timepiece at all, or are too much in a hurry to tell you the time. They might just give you the time, but perhaps they want to talk—so you don’t know how *long* it will take to get the time, and after you finish this time-retrieval transaction, that time may no longer be usable.

Consider a more complex example. You run a small storage company and you hire someone to store and fetch items for you. When you ask for a stored item, the person might bring back the item, or a reason they couldn’t get it. Also, you’re not sure how long it will take: the person might be on a break or moving slowly that day, the item might be near or far in the warehouse, or the person might already have a significant list of tasks to complete before they can get to your request. It’s also possible that the item might not be there.  There are a number of degrees of unpredictability, and by knowing what they are you can compensate for them in various ways. If you just ignore these unpredictability factors, as we have traditionally done in programming, you can’t compensate for them.

*Effects* are these unpredictability factors. When you call a function which is outside your circle of certainty, you initiate an operation that has unpredictable results; i.e. a function that may produce effects. If we know what these effects are, we can work with them to create a more reliable program. It doesn’t end with reliability, though. If a system knows what the effects are for a particular function, it can provide other useful facilities.

An effect either changes the world outside your scope (your “circle of certainty”), or observes the world. Effects often change *and* observe the world.
## Errors are Effects

One kind of unpredictability that we *have* started to pay attention to is errors. As you cannot predict when an error will occur, these are a type of effect. Errors are very clear: if some aspect of a function call fails, it will report that failure as an error.

Exceptions are a problem here. Exceptions exist in a world outside normal function control flow. When an exception is thrown, you can choose to catch it and handle it … or ignore it, at which point it becomes a runtime error. What we want is for the type system to ensure that we have properly dealt with all errors, *before* the program runs.

The further away you get from the site of a thrown exception, the less context information you have. We’d like the type system to require full error coverage at the site of each function call, rather than anywhere on the exception stack. You still have the *option* of passing the error on, but the type system requires that choice to be made at the function call site.

The problem happens because we traditionally think of functions like this:

1. You pass any number of arguments to the function.
2. The function returns a single result.

We have always thought of the result as a single value: the answer you desire. In reality, you might not get that answer because there’s a failure, or the answer might not exist. To report errors without using exceptions, we *expand the result* to include not just the desired answer but also the failure information. Instead of returning a single value of the type of the desired answer, we return a structure containing the answer *plus* error information.

Now, when you call such a function, you can’t just grab the answer and go on your merry way. You are forced to unpack the returned structure. If there’s an error, you must deal with it. Only if there is no error information do you take the answer and continue.

The result is typed, and that type information means that the type system is able to track your code, and enforce that you have handled all possible error conditions. The only way for errors to slip through the cracks is if you explicitly push them into those cracks. You must write the code that does that, and now that code is visible and discoverable as a decision you’ve consciously made (ignoring an exception requires no code at all, so no one can see that you’ve done it).

By treating errors as effects, your programming system is able to guarantee that you mitigate all those effects, thus producing a more reliable program.
## Pure Functions & Referential Transparency

What if a function is inside your “circle of certainty,” and has no effects? It produces the same result for the same arguments, every time, with no surprises. We call this a *pure function*, and it behaves like a function in mathematics. A pure function has no **observable effect** other than simply returning a value. Note the use of “observable” here—all kinds of mutations might be happening behind the scenes, but as long as we cannot observe them, they are not effects.

A pure function has special characteristics:

1. Because a pure function returns identical results for the same arguments, those results can reliably be placed in a lookup table, and a lookup in that table can be substituted for calling the function. This is called *referential transparency*.
2. Calling a pure function does not change the effects of the function that calls it. In contrast, if you’re in a function that calls another function that has effects, those effects must be incorporated into the effects of the calling function.
## Other Kinds of Effects

Errors are a specific type of effect. A more general effect is seen when you call a “time” function. Getting the time is not a pure function because you get a different result every time you call it (the call could also fail if the underlying system doesn’t include a clock, or if it has some kind of error). There’s not much “mitigation” to do in this case, but you must be aware that any call to time means that your function cannot be treated as pure.

Now consider a database, the analogy of hiring a person to store and retrieve items in your warehouse. There are a number of effects you need to mitigate:

1. You don’t know how long the transaction will take. The database might currently be bogged down with requests.
2. The network or database connection might fail, and your request doesn’t get there.
3. You don’t know if an item you want to retrieve is there.
4. There might already be an item in the location where you want to store something.
5. ... And a number of other things can go wrong when dealing with a database.

Numbers 1 and 2 are mixed together: if a transaction takes too long, how do you know whether the database is simply busy or if your request hasn’t gotten through because of a network problem? And consider number 3: it’s often expected that an item might not be there, which means it isn’t necessarily an error and should be reported in a different way.

If you make a call to a database, the result is unpredictable (which means the function you are writing is impure because it calls the database). Mitigating these effects will not make your function pure, but it can reduce the number of effects that “leak out” into anything that calls your function.

Effects are a kind of bookkeeping system that allow you to keep track of and mitigate the unpredictabilities in your program. An *effect system* provides tools to automate tracking and mitigation, but even if you are not using an effect system it can be useful to think in terms of effects.
## Returning (not Raising) Exceptions

Throwing an exception is like sending up a flare. It’s not the normal way to communicate. More importantly, it assumes that someone happens to be looking in your direction when the flare goes off. If not, your message can be lost.

Our goal is to include error information in the package returned from a function call, together with the “answer” from a successful call. We could certainly make up our own set of error indicators, or perhaps just return a string. But why throw away all the work that’s already been done creating the different types of exceptions? It makes much more sense to use those—plus it allows us to easily interact with the existing exception system, by catching exceptions and incorporating them in our error reporting.

However, we want to deal with errors directly and never throw our own exceptions. So our function will not `raise` any exceptions, but will instead return `Exception` objects. As far as we are concerned, these objects no longer have the amazing ability to act as “flares.” They are simply a convenient way for us to denote error information.
## Expressing Effects in Code

Perhaps the clearest way to produce a combined return value is with a *type union*, together with pattern matching. Fortunately, Python is one of the languages that supports this. We’ll start by defining our own `Exception` (code examples [here](https://github.com/BruceEckel/python-experiments/tree/main/effects)):
```python
# my_error.py


class MyError(Exception):
    pass
```
Type unions are demonstrated in both the `fallible()` return type and the type for the `results` list:
```python
# type_union.py
from typing import List
from my_error import MyError


def fallible(n: int) -> str | TabError | ValueError | MyError | None:
    return results[n] if n in range(len(results)) else None


results: List[str | TabError | ValueError | MyError] = [
    "eeny",
    TabError("after eeny"),
    "meeny",
    ValueError("after meeny"),
    "miney",
    MyError("after miney"),
]


if __name__ == "__main__":
    for n in range(len(results) + 1):
        match fallible(n):
            case str(s):
                print(f"{n}: Success -> {s}")
            case TabError() as e:
                print(f"{n}: Tab Error ->", e)
            case ValueError() as e:
                print(f"{n}: Value Error ->", e)
            case MyError() as e:
                print(f"{n}: My Error ->", e)
            case None:
                print(f"{n}: No result")
```
The return type for `fallible()` is a type union: it can be either a `str` or a `TabError` or a `ValueError` or a `MyError` or `None`. The returned object can carry a single value that can be any one of these types.

`fallible()` indexes into the `results` list. If the `n` argument indexes outside of `results` then `fallible()` returns `None`.

Without the type annotation, Python would treat the `results` list as a collection of `object` because it contains more than one type. Python doesn’t automatically figure out the type union for you. Without the annotation on `results`, MyPy complains.

In `__main__`, we call `fallible()` for all the elements in `results`—plus one, to demonstrate `None` behavior. The pattern match responds accordingly to each possible return type.

Here we encounter a problem: Compiled languages that support pattern matching (for example Scala, Rust and Kotlin) also enforce exhaustive matching. In our case, if we left off the match for `ValueError`, the type checker would tell us we hadn’t accounted for `ValueError`, which is one of the types that the annotation for `fallible()` says it can return. An inexhaustive pattern match is an error.

Unfortunately, the current versions of MyPy and PyRight do not enforce exhaustive matching. It’s possible for them to do so, but they have not advanced that far yet, which means you don’t get the safety provided by exhaustive matching. This is unfortunate, but we can hope that these tools, or some new one, will eventually provide this benefit.
## Returning a `Result` Object

What we would really like to use for `Result` is an enumeration, but unfortunately Python’s `Enum` is fairly limited: it creates a single immutable object. We need to create a new `Result` for each call to `fallible()`, and we can’t do that with Python’s `Enum` (Rust’s enumerations are complete, and allow this). So instead, we create a `dataclass` that can hold either the answer or an error:
```python
# my_result.py
from dataclasses import dataclass
from typing import Generic, TypeVar

T = TypeVar("T")  # Any type
E = TypeVar("E", bound=Exception)  # Only Exceptions


@dataclass(frozen=True)
class Result(Generic[T, E]):
    value: T | E


@dataclass(frozen=True)
class Ok(Result[T, E]):
    def __post_init__(self):
        assert not isinstance(self.value, Exception)

    def __repr__(self) -> str:
        return f"Ok({self.value!r})"


@dataclass(frozen=True)
class Err(Result[T, E]):
    def __post_init__(self):
        assert isinstance(self.value, Exception)

    def __repr__(self) -> str:
        return f"Err({self.value!r})"
```

A `TypeVar` allows you to create a type variable, which can be used as a stand-in for any type. It’s Python’s way to create generic classes or functions.

- `T = TypeVar("T")` is a generic type variable that can represent any type.
- `E = TypeVar("E", bound=Exception)` is bounded to the `Exception` class—it can be any subtype of `Exception`.

`Result` is a generic class that can hold an answer value of type `T` or an exception of type `E`. The `Generic[T, E]` in the class definition indicates that `Result` is parameterized by two types: `T` and `E`.

`Ok` is a subclass of `Result` representing a successful result. `Err` represents a failed result or an error. The `__post_init__` methods guarantee that you cannot have an `Ok` object holding an exception or an `Err` object that does *not* hold an exception.

Now `fallible()` can return `Result` objects:
```python
# return_result.py
from typing import List
from my_error import MyError
from my_result import Result, Ok, Err


def fallible(n: int) -> Result[str, Exception] | None:
    return results[n] if n in range(len(results)) else None


results: List[Result[str, Exception]] = [
    Ok("eeny"),
    Err(TabError("after eeny")),
    Ok("meeny"),
    Err(ValueError("after meeny")),
    Ok("miney"),
    Err(MyError("after miney")),
]

if __name__ == "__main__":
    for n in range(len(results) + 1):
        result = fallible(n)

        match result:
            case None:
                print(f"{n}: No result")
            case Ok(value):
                print(f"{n}: Success -> {value}")
            case Err(TabError() as e):
                print(f"{n}: Tab Error ->", e)
            case Err(ValueError() as e):
                print(f"{n}: Value Error ->", e)
            case Err(MyError() as e):
                print(f"{n}: My Error ->", e)
            case Err(Exception() as e):
                print(f"{n}: Unknown Error ->", e)

        print(f"{result}\n" + "-" * 25)
```

Now our `results` list  contains `Result[str, Exception]`, which must then either be an `Ok` or an `Err`. `fallible()` returns a `Result[str, Exception]`, but as before it can also return `None`, which is expressed by a type union. The pattern match in `__main__` checks for all possible types returned from `fallible()`.

Notice the `Err` cases in the pattern match, for example `case Err(TabError() as e)`. The `TabError() as e` allows us to capture the specific type of exception inside `Err` and then just use it as `e`.

There’s a Python library called [result](https://github.com/rustedpy/result/tree/master)which is designed after Rust’s built-in `Result` that matches the basic structure of `my_result.py` (although `result` is far more sophisticated). `return_result.py` can be used with this library by changing the `from my_result` import to `from result`. Here we test both versions and ensure that the outputs are identical:
```python
# test_both.py
import io
import sys
from pathlib import Path


# Returns the output from exec(code)
def exec_o(code: str) -> str:
    buffer = io.StringIO()
    sys.stdout = buffer
    try:
        exec(code, globals())
    finally:
        # Reset stdout
        sys.stdout = sys.__stdout__
    return buffer.getvalue()


if __name__ == "__main__":
    code = Path("return_result.py").read_text()
    output1 = exec_o(code)
    print(output1)

    modified = code.replace("my_result", "result")
    output2 = exec_o(modified)

    assert output1 == output2
```
The argument to `exec_o()` is a `str` that contains a Python program. This program is run using Python’s built-in `exec()`, and the output of that program which normally goes to standard output is captured and returned from `exec_o()`.

In `__main__` we run the original `return_result.py`, capturing and displaying the output. Then we replace `my_result` with `result`, so we are now importing the sophisticated `result` library, and the program is executed again. This time we don’t display the output but instead ensure that it is identical to the output for `my_result`. Here’s what you see when you run it:
```
0: Success -> eeny
Ok('eeny')
-------------------------
1: Tab Error -> after eeny
Err(TabError('after eeny'))
-------------------------
2: Success -> meeny
Ok('meeny')
-------------------------
3: Value Error -> after meeny
Err(ValueError('after meeny'))
-------------------------
4: Success -> miney
Ok('miney')
-------------------------
5: My Error -> after miney
Err(MyError('after miney'))
-------------------------
6: No result
None
-------------------------
```
You can see that the returned objects are either `Ok` or `Err` and the pattern match captures all the different types that come back from `fallible()`.
## More Sophisticated Features

The [Result](https://pypi.org/project/result/) library includes significantly more functionality than my oversimplified `my_result.py` provides. One of the most interesting is the `and_then()` function. Suppose you have a set of operations, like this:

```python
# operations.py
from result import Result, Ok, Err


def get_number(s: str) -> Result[int, Exception]:
    try:
        return Ok(int(s))
    except ValueError:
        return Err(ValueError(f"Can't convert {s}"))


def double(n: int) -> Result[int, Exception]:
    return Ok(n * 2)


def to_string(n: int) -> Result[str, Exception]:
    try:
        return Ok(str(n))
    except Exception as e:
        return Err(e)
```

Each operation returns a `Result` object. If we call several of these operations and perform `Result` analysis for each call, coding becomes tedious. `and_then()` automatically checks for errors, so you can write code like this:

```python
# flatmap.py
from result import Ok, Err
from operations import get_number, double, to_string

if __name__ == "__main__":
    result = (
        Ok("5")  # Try Ok("Bob")
        .and_then(get_number)
        .and_then(double)
        .and_then(to_string)
    )

    match result:
        case Ok(value):
            print(f"Success: {value}")
        case Err(e):
            print(f"Error: {e}")
```

Notice the chained `and_then()` operations. For each `and_then()`, an error causes the entire `result` calculation to stop—no more `and_then()`s will be executed—and an `Err` will be the value for `Result`. This makes programming with `Result` easier and clearer.

The file is called `flatmap.py` because this is the common term, which is also often named `and_then()` or `bind()`.