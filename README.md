DAVBACKUP
=========

Use this program instead of the old 'ocbackup' shell script.


Downloads an entire tree from a DAV server. This can be used to make backups from an owncloud/nextcloud server.

Usage
-----

```
    $ python3 davbackup.py --help
    usage: davbackup.py [-h] [--config FILE] [--destdir DIR] [--start RMT_DIR]
    
    Download content from DAV server.
    
    optional arguments:
      -h, --help            show this help message and exit
      --config FILE, -c FILE
                            Specify a config file other than the default.
      --destdir DIR, -d DIR
                            Specify destination directory.
      --start RMT_DIR, -s RMT_DIR
                            Download only the specified subtree.
```

Configuration file
------------------

The configuration is a json file whose fields are self explanatory, except perhaps the `nbackups` field, explained below. Note that the password is base64 encoded. This makes it obscure, not secure, but the program is meant to be run on a trusted machine.

```
    {
        "protocol": "https",
        "server": "oc.destrangis.com",
        "username": "jl",
        "password": "YWJyYWNhZGFicmE=",
        "davstart": "/remote.php/dav/files/jl",
        "nbackups": 4
    }
```

The field `nbackups` is the number of backups copy to keep. When the local directory exists already, it is presumed to contain a previous backup, and it is renamed with an extension .001, if a directory with a .001 extension exists, it is renamed to .002 and so on until the specified number of backups is reached. Directories that would have a higher number than the number of backups are simply deleted.

Installing
----------

Create a directory where the program is going to run from. Copy the files in this package, then run:

```
    $ bash ./install.sh
```

This will create a virtual environment and install the necessary dependencies.


Running
-------

Just run:

```
    $ bash ./run.sh <args>
```

Where args are the same arguments as described above. This command activates the virtual environment and then runs the `davbackup.py` program. You cannot run the `davbackup.py` program directly unless you activate the virtual environment first.

