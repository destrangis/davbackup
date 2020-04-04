"""
Download content from DAV server.
"""
import argparse
import sys
import os.path
import urllib
import shutil
import logging
import json
import ssl
from base64 import b64decode
from datetime import datetime
from glob import glob

import easywebdav2

VERSION = "0.1.3"
DEFAULT_CONFIG_FILE = "davbackup.json"
NO_BACKUP_FILE = "nobackup"

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
log.addHandler(ch)


class DavConnection:
    def __init__(self, cfg, max_attempts_conn=3, max_attempts_dnl=3):
        self.max_attempts_conn = max_attempts_conn
        self.max_attempts_dnl = max_attempts_dnl
        self.connection_incidents = 0
        self.download_incidents = 0
        self.total_size = 0
        self.server = cfg["server"]
        self.username = cfg["username"]
        self.password = password = b64decode(cfg["password"]).rstrip()
        self.protocol = cfg["protocol"]
        self.connection = None
        self.downloaded = 0

    def connect(self):
        attempt = 0
        while attempt < self.max_attempts_conn:
            attempt += 1
            try:
                self.connection = easywebdav2.connect(
                    self.server,
                    username=self.username,
                    password=self.password,
                    protocol=self.protocol,
                )
                break
            except Exception as xcp:
                self.connection = None
                self.connection_incidents += 1
                log.exception(str(xcp))

        if self.connection is None:
            raise easywebdav.ConnectionFailed(
                "Could not connect to "
                "'{0}://{1}' with username '{2}'".format(
                    self.protocol, self.server, self.username
                )
            )

        log.info("Connected to server '{}'".format(self.server))

    def list_dir(self, rmtdir):
        try:
            ls = self.connection.ls(rmtdir)
        except easywebdav2.client.OperationFailed as err:
            log.error("Cannot list '{}' skipping.".format(rmtdir))
            log.exception(str(err))
            return []

        return ls

    def download(self, rfile, lfile, size=0):
        done = False
        attempt = 0
        while attempt <= self.max_attempts_dnl:
            attempt += 1
            log.info("[{0}] Downloading '{1}' -> '{2}'".format(attempt, rfile, lfile))
            try:
                self.connection.download(rfile, lfile)
                done = True
                break
            except Exception as xcp:
                self.download_incidents += 1
                log.exception(str(xcp))
                log.error("RETRYING with new connection.")
                self.connect()

        if not done:
            raise RuntimeError("Too many failures. Exiting.")

        self.downloaded += 1
        self.total_size += size


def human_size(size):
    units = ["KB", "MB", "GB", "TB"]
    n = size
    lastu = "bytes"
    for u in units:
        lastn = n
        n = n / 1024
        if n < 1:
            return "{0:.5g} {1}".format(lastn, lastu)
        lastu = u
    else:
        return "{0:.5g} {1}".format(n, lastu)


def dav_walk(cnx, rmtdir):
    if not rmtdir.endswith("/"):
        rmtdir += "/"

    ls = cnx.list_dir(rmtdir)

    dirlst = []
    filelst = []
    for elm in ls:
        log.debug(str(elm))
        full_name = name = urllib.parse.unquote(elm.name)
        if full_name.startswith(rmtdir):
            name = full_name[len(rmtdir) :]
        if name == "":  # we get the dir as one of the directories
            continue

        if elm.contenttype != "httpd/unix-directory":
            filelst.append((os.path.basename(name), elm.size))
        else:
            dirlst.append(name)
    yield rmtdir, dirlst, filelst
    for dirname in dirlst:
        full_name = os.path.join(rmtdir, dirname)
        yield from dav_walk(cnx, full_name)


def dav_download(cfg, start, localtop):
    top_rmt = cfg["davstart"]
    if start != "/" and start != ".":
        top_rmt = os.path.join(top_rmt, start)
    if not top_rmt.endswith("/"):
        top_rmt += "/"

    cnx = DavConnection(cfg)
    cnx.connect()

    success = True
    try:
        for d, dirlst, filelst in dav_walk(cnx, top_rmt):
            base_d = d[len(top_rmt) :]
            localdir = os.path.join(localtop, base_d)
            if not os.path.isdir(localdir):
                log.info("Creating local dir '{}'".format(localdir))
                os.mkdir(localdir)
            for f, size in filelst:
                rfile = os.path.join(d, f)
                lfile = os.path.join(localdir, f)
                cnx.download(rfile, lfile, size)
    except Exception:
        success = False
    finally:
        log.info("Finished {}.".format("successfully" if success else "unsuccessfully"))
        log.info("{0:3d} Connection incidents".format(cnx.connection_incidents))
        log.info("{0:3d} Download incidents".format(cnx.download_incidents))
        log.info(
            "{0} Files downloaded. {1} Transferred.".format(
                cnx.downloaded, human_size(cnx.total_size)
            )
        )
    return success


def shift_dirs(basedir, nbackups):
    if os.path.isdir(basedir):
        ptrn = basedir + ".[0-9][0-9][0-9]"
        lst = sorted(glob(ptrn), reverse=True)
        num = 1
        for dr in lst:
            num = int(dr.split(".")[-1])
            if num >= int(nbackups):
                shutil.rmtree(dr)
            else:
                shutil.move(dr, "{0}.{1:03d}".format(basedir, num + 1))
        shutil.move(basedir, "{0}.{1:03d}".format(basedir, num))


def process_args(progname, args):
    p = argparse.ArgumentParser(prog=progname, description=__doc__)
    p.add_argument(
        "--config",
        "-c",
        default=DEFAULT_CONFIG_FILE,
        metavar="FILE",
        help="Specify a config file other than the default.",
    )
    p.add_argument(
        "--destdir",
        "-d",
        default="ocbackup",
        metavar="DIR",
        help="Specify destination directory.",
    )
    p.add_argument(
        "--start",
        "-s",
        default=".",
        metavar="RMT_DIR",
        help="Download only the specified subtree.",
    )
    p.add_argument(
        "--version",
        "-v",
        default=False,
        action="store_true",
        help="show program version and exit",
    )
    return p.parse_args(args)


def main(args=None):
    if args is None:
        args = sys.argv

    progname = os.path.basename(args[0])
    opts = process_args(progname, args[1:])
    if opts.version:
        print(VERSION)
        return 0

    start = datetime.now()
    log.info("{0} Started at {1}".format(progname, start.strftime("%A %F %H:%M:%S")))

    if os.path.isfile(opts.config):
        log.debug("Loading config '{}'".format(opts.config))
        with open(opts.config) as c:
            cfg = json.loads(c.read())
        log.debug("Config: " + str(cfg))
    else:
        log.error("Cannot find config file '{}'".format(opts.config))
        return 1

    nobackup = os.path.join(opts.destdir, NO_BACKUP_FILE)
    if os.path.isfile(nobackup):
        log.info("File '{}' found. Not performing backup.".format(nobackup))
        return 0

    shift_dirs(opts.destdir, cfg["nbackups"])

    success = dav_download(cfg, opts.start, opts.destdir)
    if not success:
        open(nobackup, "w").close()

    end = datetime.now()
    log.info(
        "{0} Processing ended at {1}".format(progname, end.strftime("%A %F %H:%M:%S"))
    )
    log.info("Total processing time: {}".format(str(end - start)))

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
