The most common things you'll do with `go` are adding new shortcuts:

```
$ pwd
/some/ridiculously/long/or/hard/to/type/dir
$ go -a foo
```

listing the shortcuts you've created:

```
[~]$ go --list
                    Go Shortcuts
                    ============

Default shortcuts:
  .                     .
  ..                    ..
  ...                   ../..
  tmp                   /tmp
  ~                     /Users/trentm

Custom shortcuts:
  cgi-bin               /Library/WebServer/CGI-Executables
  foo                   /some/ridiculously/long/or/hard/to/type/dir
  pysite                /Library/Frameworks/Python.framework/Versions/2.6/lib/python2.6/site-packages
  www                   /Users/trentm/Sites
```

and switching to directories using those shortcuts:

```
[~]$ go pysite
[/Library/Frameworks/Python.framework/Versions/2.6/lib/python2.6/site-packages]$ go foo
[/some/ridiculously/long/or/hard/to/type/dir]$ go www
[~/Sites]$ 
```

Run `go --help` for full usage details or just
[take a look at the `go.py` script](http://code.google.com/p/go-tool/source/browse/trunk/lib/go.py):


```
$ go --help
Quick directory changing.

Usage:
    go <shortcut>[/sub/dir/path]    # change directories
                                    # same as "go -c ..."
    go -c|-o|-a|-d|-s ...           # cd, open, add, delete, set
    go --list [<pattern>]           # list matching shortcuts

Options:
    -h, --help                      print this help and exit
    -V, --version                   print verion info and exit

    -c, --cd <path>                 cd to shortcut path in shell
    -s, --set <shortcut> <dir>      set a shortcut to <dir>
    -a, --add-current <shortcut>    add shortcut to current directory
    -d, --delete <shortcut>         delete the named shortcut
    -o, --open <path>               open the given shortcut path in
                                    explorer (Windows only)
    -l, --list [<pattern>]          list current shortcuts

...
```