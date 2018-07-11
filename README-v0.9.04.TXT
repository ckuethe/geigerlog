DESCRIPTION version 0.9.04

GeigerLog (previously named just Geiger) is a Python based GUI program for
use with GQ Electronic's GMC-3xx line of Geiger counters (but
can be adapted to other data loggers as well). It now also supports
logging and history from the GMC-5xx Geiger counters.

Beyonf some bug fixes, this latest version got various improvements for
ease of handling and more flexibility for typical operations.

Also, it can now create a count rate histogram with Poisson fit, which greatly
helps to judge quality of logging. It also offers a FFT analysis
to inspect recordings for any periodic signal hidden within the data.

A GeigerLog-Manual is providing overview, quick intro, details and
documentation of principle problems of Geiger counters and the GQ
counters in particular.

GeigerLog is available in two versions:

- geigerlog-scripts-v0.9.04.zip

  provides the python scripts and resources (such as icons); it will
  run where a proper Python 2.7 and PyQt4 environment exists

- geigerlog-bundle-v0.9.04.zip

  is an All-In-One package, which in addition also provides the runtime
  environment. No Python installation is required. However, it is
  currently working only on Linux.

For installation and operating instructions see the manual.
