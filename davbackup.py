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

DEFAULT_CONFIG_FILE = "davbackup.json"

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
log.addHandler(ch)


def dav_walk(cnx, rmtdir):
    if not rmtdir.endswith("/"):
        rmtdir += "/"
    try:
        ls = cnx.ls(rmtdir)
    except easywebdav2.client.OperationFailed as err:
        log.error("Cannot list '{}'".format(rmtdir))
        log.exception(str(err))
        return

    dirlst = []
    filelst = []
    for elm in ls:
        log.debug(str(elm))
        full_name = name = urllib.parse.unquote(elm.name)
        if full_name.startswith(rmtdir):
            name = full_name[len(rmtdir):]
        if name == "": # we get the dir as one of the directories
            continue

        if elm.contenttype != "httpd/unix-directory":
            filelst.append(os.path.basename(name))
        else:
            dirlst.append(name)
    yield rmtdir, dirlst, filelst
    for dirname in dirlst:
        full_name = os.path.join(rmtdir, dirname)
        yield from dav_walk(cnx, full_name)


def try_download(cnx, cfg, rfile, lfile):
    "Download file, reconnecting if any errors"
    maxerrs = 3
    nerrs = 0
    while 1:
        try:
            log.info("[{0}] Downloading '{1}' -> '{2}'".format(nerrs, rfile, lfile))
            cnx.download(rfile, lfile)
            break
        except (WebdavException, ssl.SSLError) as xcp:
            nerrs += 1
            log.exception(str(xcp))
            if nerrs >= maxerrs:
                raise
            log.error("RETRYING with new connection.")
            cnx = easywebdav2.connect(cfg["server"], username=cfg["username"],
                            password=b64decode(cfg["password"]).rstrip(),
                            protocol=cfg["protocol"])
    return cnx
        

def dav_download(cfg, start, localtop):
    top_rmt = cfg["davstart"]
    if start != "/" and start != ".":
        top_rmt = os.path.join(top_rmt, start)
    if not top_rmt.endswith("/"):
        top_rmt += "/"

    cnx = easywebdav2.connect(cfg["server"], username=cfg["username"],
                            password=b64decode(cfg["password"]).rstrip(),
                            protocol=cfg["protocol"])
    log.info("Connected to server '{}'".format(cfg["server"]))

    for d, dirlst, filelst in dav_walk(cnx, top_rmt):
        base_d = d[len(top_rmt):]
        localdir = os.path.join(localtop, base_d)
        if not os.path.isdir(localdir):
            log.info("Creating dir '{}'".format(localdir))
            os.mkdir(localdir)
        for f in filelst:
            rfile = os.path.join(d, f)
            lfile = os.path.join(localdir, f)
            cnx  = try_download(cnx, cfg, rfile, lfile)


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
                shutil.move(dr, "{0}.{1:03d}".format(basedir, num+1))
        shutil.move(basedir, "{0}.{1:03d}".format(basedir, num))


def process_args(progname, args):
    p = argparse.ArgumentParser(prog=progname, description=__doc__)
    p.add_argument("--config", "-c", default=DEFAULT_CONFIG_FILE, metavar="FILE",
                help="Specify a config file other than the default.")
    p.add_argument("--destdir", "-d", default="ocbackup", metavar="DIR",
                help="Specify destination directory.")
    p.add_argument("--start", "-s", default=".", metavar="RMT_DIR",
                help="Download only the specified subtree.")
    return p.parse_args(args)


def main(args):
    if args:
        progname = os.path.basename(args[0])
    else:
        progname = os.path.basename(__file__)

    opts = process_args(progname, args[1:])

    start = datetime.now()
    log.info("{0} Started at {1}".format(progname,
                                    start.strftime("%A %F %H:%M:%S")))

    if os.path.isfile(opts.config):
        log.debug("Loading config '{}'".format(opts.config))
        with open(opts.config) as c:
            cfg = json.loads(c.read())
        log.debug("Config: " + str(cfg))
    else:
        log.error("Cannot find config file '{}'".format(opts.config))
        return 1

    shift_dirs(opts.destdir, cfg["nbackups"])

    dav_download(cfg, opts.start, opts.destdir)

    end = datetime.now()
    log.info("{0} Processing ended at {1}".format(progname,
                                    end.strftime("%A %F %H:%M:%S")))
    log.info("Total processing time: {}".format(str(end - start)))

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
