# gradescope-cli

Submit files to Gradescope from the command line.

* Basic usage: `python3 gradescope.py <path-to-file>`
* This requires that you have the `pwinstall` and `selenium` packages installed on your computer. (You can install them using pip.)
* We also plan to distribute an executable version of this program in the future.

## Login credentials

This program attempts to read your email and password from `~/.gradescope`. If no such file exists, you will be prompted for your email and password after running the program. The `~/.gradescope` file should be two lines long, with the first line containing your email and the second line containing your password:

```
<email>
<password>
```

## Supported browsers

This program runs a browser in the background in order to access Gradescope. The default browser used is Firefox but you can override this with flags. We currently support Chrome and Edge in addition to Firefox.

* Chrome: `-c` or `--chrome`
* Edge: `-e` or `--edge`
* Firefox: `-f` or `--firefox`
 