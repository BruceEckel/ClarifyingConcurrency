My Pycon presentation this Spring was titled _[Rethinking Objects](https://us.pycon.org/2023/schedule/presentation/46/)_ (video [here](https://youtu.be/2Ul6WlKPcgY?si=-r01IzGi6_msA2rA)). Much of the research involved looking at how different languages treated inheritance. The current trend seems to be the functional approach of (ideally immutable) data structures with associated functions that can be called using OO method syntax. Rust and Go follow this pattern—the only way to create a custom data type is using structs, and there is no concept of inheritance with structs. If you want to create a struct that includes a “base” struct, you simply include an element of that “base” in your new struct (which is exactly what OO languages do, plus some syntax sugar that produces messy consequences like multiple inheritance). Go even has an “embedding” feature that makes the embedded element’s members appear as if they were native elements of the new struct—except, alas, for the constructor, making that feature feel partially-designed.

Rust’s approach is the cleanest and most elegant I have seen (I have yet to see a Rust feature that hasn’t seemed extremely well thought-out). The generalized association between a struct and the operations on that struct is the _trait_ (in simple cases you may want to just provide an implementation for a struct without using traits). Traits are apparently the same as _type classes_ in Scala, which I’ve never intuitively understood. Traits, however, seem quite straightforward to me (and perhaps I’ll someday look at a type class and think “ah, these are just traits, only more confusing”).

I have resisted Rust for a _long_ time. I’ve done my time with C and C++, I’m an adult now, and adults use garbage collectors. A language that makes the programmer do all the work of dealing with object lifetimes by hand, _just_ to eliminate the garbage collector? ( _I now know that lifetimes are about far more than just the garbage collector._) Nope, not interested. I can only imagine how low-level everything is—and people commonly describe Rust as a low-level language.

Except it turns out that creating Python extensions is _very_ powerful using Rust and the [PyO3 library](https://pyo3.rs/) In fact, it’s the only time I’ve been successful writing a Python extension. So, that’s attractive.

When I saw traits I began to doubt Rust’s “low-level” description. After the conference I fell into a Rust-hole and obsessed about the language for about two months. I explored the online “Rust books,” watched a lot of YouTube videos, and began using ChatGPT to create examples when I wondered about something. Everything I learned reinforced the idea that the Rust designers had extensive knowledge and made excellent choices, considering the impact and interactivity of each feature. I am quite impressed by the sophistication of this language.

Eventually I reached a point where I seemed to understand all the keywords I encountered. Although I certainly don’t consider myself a Rust expert at this point, I am comfortable reading pretty much any Rust code. My usage of the language is primarily limited to things that requires speed, and the dominant use-case for that is Python extensions. For development speed, I’m always going to reach for Python first when solving a problem, and only if performance is a problem will I consider optimizations like a Rust extension—or a concurrency solution.

Also, I generally start by asking ChatGPT for a solution—it walks you through the steps when creating a PyO3 extension. Of course it doesn’t always get it right and I have to ask it for fixes or repair the code by hand, but it does a surprisingly good job and always seems to be a better way to get started than writing from scratch.

In August I held the Rust Developer Retreat where a handful of people showed up and we geeked about Rust for five days (and also enjoyed the delights of Crested Butte). This inspired me to create a list of things that we like about Rust:

- **You don’t have to think about the build system, or how to set up a project.** `cargo new` does it all for you. Rust has become the gold standard here, with others trying to create build systems based on cargo (For example, see the [rye](https://rye-up.com/) project for Python). After my [struggles with Gradle](https://www.bruceeckel.com/2021/01/02/the-problem-with-gradle/), I really don’t want to have to fight with the build system every time I want to create the simplest example.

- **Testing is built in**. You don’t have to choose and install a test framework. `cargo` even sets up a basic test example for you. Also, tests can be included in the same file, by placing them in a `module` that is automatically excluded when building the production version.

- **Because of the type system, “compiling” usually means “it works.”** Rust’s type system is quite tight, and definitely helped me understand why I didn’t appreciate type systems so much in the past—a language like Java that has a “type plus anything can be null” system is too incomplete to be all that helpful. Perhaps better than no type system at all, but a system with gaping holes inspires a lot less confidence than one like Rust that aspires to have no holes at all.

- **Using the** `Result` **type instead of exceptions prevents errors from being lost.**

- **The type system and lifetime system can greatly reduce concurrency errors.** Of course, with concurrency you can …

- When cancelling a task, the compiler ensures that locks are released and resources are cleaned up (example).

- **Rust doesn’t have variance annotations**. This is possible because of Rust’s lifetime system. I have explained covariance and contravariance on numerous occasions and as soon as I’m done it starts slipping away from me. Not requiring variance annotations is a big win.

- **You don’t have to tune the garbage collector.** At the retreat, Gordon mentioned the amount of time he had spent tuning the JVM runtime during deployments. Because there’s no garbage collector and no runtime, and because your Rust program is already as fast as it’s likely to be, there’s nothing to tune.

- **No second-class citizens**. I stubbornly test things on Windows—by a large margin, the most common OS in the world—because I don’t want to use tools that exclude that population. Some tools have a clear MacOS bias and might only run on that OS. Rust feels to me like every OS is a first-class citizen, and the experience of using it is universal across platforms. (I just found out that the Zig language can cross-compile executables for all platforms from any platform; that’s a neat trick it would be nice to see in Rust someday).

