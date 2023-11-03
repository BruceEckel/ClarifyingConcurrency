Because of the Global Interpreter Lock (GIL), only one Python thread can run at a time. But the following example (available [here](https://github.com/BruceEckel/python-experiments/tree/main/threading)) shows that each Python thread allocates its own Operating System (OS) thread:

``` python
# lots_of_threads.py
import threading
from threading import Thread
import time

if __name__ == "__main__":
    threads = [
        Thread(target=lambda: time.sleep(10))
        for _ in range(99)
    ]
    for t in threads:
        t.start()
    print(f"""
    {threading.enumerate() = }
    {threading.main_thread() = }
    {threading.main_thread().native_id = }
    {threading.main_thread().is_alive() = }
    {threading.active_count() = }
    """)
    for t in threads:
        t.join()
```

If you run this you’ll see that each thread has its own OS thread. Since only one of these threads can run at any time, this seems like a waste of time and resources. Why not just allocate a single OS thread, and have it jump from one Python thread to the next? I asked around but everyone only guessed.

I’ve been getting a lot of value from the (free) Chat GPT-3.5, but friends have told me that the (20$/month) GPT-4 does a significantly better job. It’s clear that I’m going to use it a lot so I finally upgraded and this was the first question I asked. Not only is the answer notably better than the free version, I haven’t found any logical problems with the answer:

> While it’s true that Python's Global Interpreter Lock (GIL) restricts the execution of bytecodes to a single thread at a time in CPython, the usage of actual OS threads for Python threads isn’t redundant. Here’s why:
>
> 1\. **Concurrency vs. Parallelism**: Even though Python threads in CPython can’t achieve true parallelism due to the GIL, they can achieve concurrency. This means that while one thread is waiting (e.g., on I/O operations such as reading/writing from/to a file or network socket), another thread can run. This is where the OS thread model becomes useful, as it allows the OS scheduler to context-switch between threads when one is waiting.
>
> 2\. **Integration with C Extensions**: CPython allows interfacing with C/C++ extensions. These extensions can, in fact, release the GIL and perform true parallel computation if they are written to do so. By mapping Python threads to OS threads, such extensions can take advantage of multi-core processors once the GIL is released.
>
> 3\. **Utilizing Native OS APIs**: By using native OS threads, Python threads can utilize native OS APIs and primitives like mutexes and semaphores directly. This can be beneficial when interfacing with external libraries or when certain operations are more efficiently handled at the OS level.
>
> 4\. **Consistency across Implementations**: CPython isn’t the only Python implementation. Other implementations like Jython (Python for the Java platform) or IronPython (Python for .NET) don’t have a GIL and can achieve true thread-level parallelism. By defining threads at the level of the language (rather than an interpreter-specific concept), Python maintains consistency across different implementations.
>
> 5\. **External Interaction**: Applications often need to interact with external systems or libraries that expect or utilize OS-level threads. Having Python threads map to OS threads can simplify this interaction.
>
> 6\. **Simplicity**: The logic of managing a custom user-level threading system that multiplexes multiple Python-level threads over a single OS thread can be more complex than just using OS-level threads directly. The current approach is straightforward: create a new OS thread whenever a new Python thread is launched.
>
> While the GIL does impose limitations on CPU-bound parallelism in CPython, using OS threads for Python threads has its set of advantages, especially for I/O-bound tasks and for interacting with the outside world. If true parallelism for CPU-bound tasks is a requirement, developers often turn to multi-process architectures (using Python’s `multiprocessing` module) or other Python implementations like PyPy.

I asked why it included PyPy, since it has a GIL. It replied that PyPy did indeed have a GIL:

> … the reason PyPy often gets mentioned in discussions about performance is because its Just-In-Time (JIT) compiler can offer significant speed improvements for certain CPU-bound tasks compared to CPython, even with the presence of the GIL. This means that while it doesn't offer true multi-threaded parallelism, a single thread of execution might be substantially faster for specific operations or workloads.
>
> If you are seeking true parallelism in Python for CPU-bound tasks:
>
> 1. **Multiprocessing**: The `multiprocessing` module in Python allows you to create separate processes, each with its own Python interpreter and memory space. This is a common way to bypass the GIL and take full advantage of multi-core CPUs.
>
> 2. **Native Extensions**: You can write performance-critical sections of your code in languages like C or C++ as Python extensions. While executing these extensions, you can release the GIL to achieve parallelism.
>
> 3. **Alternative Languages and Tools**: Tools like Cython allow you to write Python-like code with type annotations that gets compiled to C, which can then be parallelized. Similarly, Numba is a JIT compiler that can help optimize specific portions of your Python code.
>
> 4. **Distributed Computing**: Libraries like Dask allow you to build parallel and distributed applications in Python, spanning across cores and even machines.

