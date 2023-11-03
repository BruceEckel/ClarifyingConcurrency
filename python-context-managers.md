Almost ten years ago I showed a brief introduction to context managers ( [Point 2 here](https://www.bruceeckel.com/2014/12/05/a-heaping-helping-of-python-goodness/)) and thought I would be using them a lot more. But it took the (annoyance and ugliness of the) repeated setup and cleanup when testing my parallelism code to remind me.

If you look at [PEP 343](https://peps.python.org/pep-0343/), the point of context managers is to “make it possible to factor out standard uses of try/finally statements.” I’ve always felt like `finally` was kind of tacked onto exception handling. It’s not about error handling, it’s about cleanup. Sure, you need to be able to ensure proper cleanup if an exception is thrown, but you need to ensure proper cleanup _however_ you leave a scope (I think we’ve relied on function calls as our primary unit of activity, which has distracted us from the more general concept of scope—this is especially clear when you look at [structured exception handling](https://vorpus.org/blog/notes-on-structured-concurrency-or-go-statement-considered-harmful/) and, I’m beginning to suspect, Rust’s _lifetimes_).

I’m currently convinced that the easiest/nicest way to write a context manager is using the `@contextmanager` function decorator, writing the function as a generator. But a generator is a function with a `yield`, and what are we yielding? If you look at my example from the earlier blog, you’ll see that I `yield` the directory that was passed in to the function, which doesn’t really make sense because (A) I never use it and (B) I already have that information. So it would have been fine to say this:

``` python
@contextmanager
def visitDir(d):
    old = os.getcwd()
    os.chdir(d)
    yield # No 'd'
    os.chdir(old)
```

That is, to `yield` nothing. This hands control back to the creator of the context so they can do their work, and when the context scope closes control returns to the context manager and it executes `os.chdir(old)`.

What would you `yield`, though? This is where the `as` keyword (added alongside `with` for context management) comes in. If you have a context manager cm and you create a context like this:

``` python
with cm() as x:
    ...
```

`x` is what is yielded from the context manager, and is available the rest of the scope.

The yielded object can be anything. In my concurrency examples, I needed to pass information into the scope and return information from that scope, so I created a new type called `Scenario` in [scenario\_tester.py](https://github.com/BruceEckel/python-experiments/blob/main/parallelism/scenario_tester.py):

``` python
from contextlib import contextmanager
from dataclasses import dataclass, field
import time
import os
from pprint import pformat

@dataclass
class Scenario:
    multiplier: int
    tasks: int
    args1: range = field(init=False)
    args2: list[int] = field(init=False)
    results: list[float] = field(default_factory=list)

    def __post_init__(self):
        self.args1 = range(self.tasks)
        self.args2 = [self.multiplier] * self.tasks

@contextmanager
def scenario():
    multiplier = 1  # Increase for longer computations
    logical_processors = os.cpu_count()
    print(f"{logical_processors = }")
    tasks = (logical_processors - 0) * 1  # Try different numbers
    print(f"{tasks = }")
    start = time.monotonic()
    scenario = Scenario(multiplier, tasks)
    try:
        yield scenario
    finally:
        elapsed = time.monotonic() - start
        print(
            f"""{pformat(list(scenario.results))}
              Elapsed time: {elapsed:.2f}s"""
        )
```

`Scenario` creates and provides `args1` and `args2` and captures `results` from the test. I use a `dataclass` here because it’s my default now—if you want to learn more, see my [Pycon presentation from 2022](https://www.youtube.com/watch?v=w77Kjs5dEko&ab_channel=PyConUS). The `__post_init__()` creates `args1` and `args2`, which are intentionally un-initialized by the `dataclass`-generated constructor.

The context manager function `scenario()` sets everything up and creates and yields a `Scenario` object, which is used inside the context. When the context scope ends, the `Scenario` object is still there so `scenario.results` can be extracted and displayed. Note that the `start` time was not included in the Scenario because it’s not needed inside the context, but it is still usable in `finally` because it’s in the scope of the context manager function.

The context manager eliminates all the extra code that I had written for each test. For example, see [with\_processes.py](https://github.com/BruceEckel/python-experiments/blob/main/parallelism/with_processes.py):

``` python
from concurrent.futures import ProcessPoolExecutor
from scenario_tester import scenario
from cpu_intensive import cpu_intensive

if __name__ == "__main__":
    with scenario() as scenario:
        with ProcessPoolExecutor() as executor:
            scenario.results = executor.map(
                cpu_intensive, scenario.args1, scenario.args2
            )
```

This looks nearly identical to [with\_threads.py](https://github.com/BruceEckel/python-experiments/blob/main/parallelism/with_threads.py):

``` python
from concurrent.futures import ThreadPoolExecutor
from scenario_tester import scenario
from cpu_intensive import cpu_intensive

if __name__ == "__main__":
    with scenario() as scenario:
        with ThreadPoolExecutor() as executor:
            scenario.results = executor.map(
                cpu_intensive, scenario.args1, scenario.args2
            )
```

The other examples are now similar.

Noting the remaining code duplication, we could go one step further and pass the executor type as a parameter to a function as in [function\_tester.py](https://github.com/BruceEckel/python-experiments/blob/main/parallelism/function_tester.py):

``` python
from concurrent.futures import ProcessPoolExecutor
from scenario_tester import scenario
from cpu_intensive import cpu_intensive

def test_cpu_intensive(ExecutorClass):
    with scenario() as s:
        with ExecutorClass() as executor:
            s.results = executor.map(cpu_intensive, s.args1, s.args2)

if __name__ == "__main__":
    test_cpu_intensive(ProcessPoolExecutor)
```

I didn’t do this because it wouldn’t work with [no\_concurrency.py](https://github.com/BruceEckel/python-experiments/blob/main/parallelism/no_concurrency.py), but I’m not sure that’s a good argument. Now that I’ve seen it, if I do more work with these [parallelism experiments](https://github.com/BruceEckel/python-experiments/tree/main/parallelism) I will probably change it.

