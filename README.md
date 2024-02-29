# gradescope-submit

Submit files to Gradescope from the command line.

![gss logo](gss-logo.jpg)

To compile into executable, run the following commands:

```
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
pyinstaller --onefile -n gss gradescope.py
deactivate
```

This will create an executable called `gss` inside a folder called `dist`. You should then move the executable so that it is in your system's PATH.

One you have followed the steps above, you can submit any file to gradescope using `gss <path-to-file>`.

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
 
## Addition in Fork

This fork adds a `-s` flag standing for "same" which lets users automatically submit the the same assignment as last time.
