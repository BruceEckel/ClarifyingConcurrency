This past week I held a short “developer retreat” (an unstructured gathering) where our (all two of us) goal was to experiment with Python’s upcoming “subinterpreters” feature. At Pycon I spent two sprint days working on this with Eric Snow, the engineer behind the proposals.

We started Sunday evening and immediately discovered that subinterpreters are a controversial topic. One maintainer of the NumPy library estimated it would take a year for NumPy to be rewritten to accommodate subinterpreters (an effort he did not welcome).

The per-interpreter GIL is still shown as being in 3.12, in [PEP 684](https://peps.python.org/pep-0684/), where its status is “accepted.” But I don't see 684 in either the "what's new" of [Python 3.12](https://docs.python.org/3.12/whatsnew/3.12.html) or [3.13](https://docs.python.org/3.13/whatsnew/3.13.html).

The companion is [PEP 554](https://peps.python.org/pep-0554/), which is what I was working with at Pycon. This is the module that provides an easy-access API to subinterpreters. I thought this was supposed to be in Python 3.12, but the PEP has a status of “draft,” and is slotted for Python 3.13, but again, I see no mention of it in the “what’s new” for 3.13.

A [May 24 article in InfoWorld](https://www.infoworld.com/article/3697018/the-best-new-features-and-fixes-in-python-3-12.html) says: “However, version 3.12 only includes the CPython internals to make this possible. There's still no end-user interface to subinterpreters. A standard library module, interpreters, is intended to do this, but it's now slated to appear in Python 3.13.” I note the phrase “now slated,” but I was unable to discover any discussions about this decision (either I wasn’t searching in the right place—very likely—or it wasn’t a public discussion).

We decided instead to explore the [Trio library](https://trio.readthedocs.io/en/stable/) and to learn more about [Rust](https://www.rust-lang.org/).

