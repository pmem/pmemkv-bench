# Contributing to pmemkv-bench

- [Opening New Issues](#opening-new-issues)
- [Code Style](#code-style)
- [Submitting Pull Requests](#submitting-pull-requests)

# Opening New Issues

Please log bugs or suggestions as [GitHub issues](https://github.com/pmem/pmemkv-bench/issues).
Details such as OS, pmemkv, libpmemobj-cpp and PMDK versions are always appreciated.

# Code Style

If you want to format your cpp code you can make adequate target:

```sh
make cppformat
```

for python scripts (using python's black formatter), use:

```sh
make pyformat
```

**NOTE**: We're using specific clang-format - version **11.0** is required.

# Submitting Pull Requests

We take outside code contributions to `pmemkv-bench` through GitHub pull requests.

**NOTE: If you do decide to implement code changes and contribute them,
please make sure you agree your contribution can be made available under the
[Apache-2.0 used for pmemkv-bench](LICENSE).**

**NOTE: Submitting your changes also means that you certify the following:**

```
Developer's Certificate of Origin 1.1

By making a contribution to this project, I certify that:

(a) The contribution was created in whole or in part by me and I
    have the right to submit it under the open source license
    indicated in the file; or

(b) The contribution is based upon previous work that, to the best
    of my knowledge, is covered under an appropriate open source
    license and I have the right under that license to submit that
    work with modifications, whether created in whole or in part
    by me, under the same open source license (unless I am
    permitted to submit under a different license), as indicated
    in the file; or

(c) The contribution was provided directly to me by some other
    person who certified (a), (b) or (c) and I have not modified
    it.

(d) I understand and agree that this project and the contribution
    are public and that a record of the contribution (including all
    personal information I submit with it, including my sign-off) is
    maintained indefinitely and may be redistributed consistent with
    this project or the open source license(s) involved.
```

In case of any doubt, the gatekeeper may ask you to certify the above in writing,
i.e. via email or by including a `Signed-off-by:` line at the bottom
of your commit comments.

To improve tracking of who is the author of the contribution, we kindly ask you
to use your real name (not an alias) when committing your changes to pmemkv-bench:
```
Author: Random J Developer <random@developer.example.org>
```
