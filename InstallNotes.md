`Go` should work with Python 2.4, 2.5, 2.6, 2.7. I haven't yet put together a version for Python 3.


# Do I have it installed? #

If you have `go` installed you should be able to do this:

```
$ go --help
...go usage info...
```


# What version do I have installed? #

```
$ go --version
```


# How do I install/upgrade? #

Install with **one** of the following methods. (**WARNING**: I haven't tested this with pip and easy\_install. In particular the `go.bat` driver script for Windows is necessary. I'd appreciate hearing from anyone successfully using `go` having installed via pip and/or easy\_install.)

  * Install **with pip** (if you have it):

> `pip install go`

> More on `pip` [here](http://pip.openplans.org/).

  * Install **with easy\_install** (if you have it):

> `easy_install go`

> See good instructions here for installing easy\_install (part of setuptools) [here](http://turbogears.org/2.0/docs/main/DownloadInstall.html#setting-up-setuptools).

  * **Basic** (aka old school) installation:
    1. download the latest `go-$version.zip`
    1. unzip it
    1. run `python setup.py install` in the extracted directory

> For example, for version 1.2.1:
```
wget -q http://go.googlecode.com/files/go-1.2.1.zip
unzip go-1.2.1.zip
cd go-1.2.1
python setup.py install
```


# One-time Bash shell setup #

For users of `go` in a shell other than Windows' `cmd.exe`, there is a necessary one-time setup. Typing `go' must end up calling the Bash function `go' and **not** `go.py'
directly. This is how `go' can change the directory in your current shell. `go` will
detect when this is the case and will walk you through the process of adding an
appropriate `go` function to your environment.