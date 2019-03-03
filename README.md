DAVBACKUP
=========

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

A sample configuration file is provided with the name `davbackup.json.sample`. Rename and edit to suit your needs.

The configuration is a json file whose fields are self explanatory, except perhaps the `nbackups` field, explained below. Note that the password is base64 encoded. This makes it obscure, not secure, but the program is meant to be run on a trusted machine.

```
{
    "protocol": "https",
    "server": "nextcloud.samplesite.com",
    "username": "fred",
    "password": "YWJyYWNhZGFicmE=",
    "davstart": "/remote.php/dav/files/fred",
    "nbackups": 4
}

```

The field `nbackups` is the number of backups copy to keep. When the local directory exists already, it is presumed to contain a previous backup, and it is renamed with an extension .001, if a directory with a .001 extension exists, it is renamed to .002 and so on until the specified number of backups is reached. Directories that would have a higher number than the number of backups are simply deleted.

Installing
----------

Use the provided setup.py utility to install:

```
$ python3 setup.py install
```
Or simply use `pip` to install from the the Pypi site:
```
$ pip install davbackup
```


Running
-------

Once you have a valid configuration file as described above, just run:

```
    $ davbackup --config <configfile> --destdir <localdir>
```

You can use the arguments described above.

