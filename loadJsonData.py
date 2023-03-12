#! /usr/bin/env python3

import sys
import json
import environ
import getopt

from nodesInContext import NodesInContext


def setupAppNodesInContext(verbose: bool = False):
    host: str = env.str("INVENTORY_HOST")
    user: str = env.str("INVENTORY_USER")
    passw: str = env.str("INVENTORY_PASS")
    proto: str = env.str("INVENTORY_PROTO")
    port: int = env.int("INVENTORY_PORT")

    nic = NodesInContext(
        host=host,
        user=user,
        passw=passw,
        proto=proto,
        port=port,
        verbose=verbose,
    )

    return nic


def loadJsonDataFromFile(fileName: str) -> dict:
    data: dict = {}
    with open(fileName) as f:
        data = json.load(f)

    return data


def usage():
    print(
        f"""
{sys.argv[0]}:
    --input <filename>  ; mandatory
        load the json file into the database specified by the .env data

    --ParentPath <ParentPathSring>  ; mandatory
        the namespace where the data will be loaded, the path will be created if needed [TODO]
        example .MyCompanyName.MyLoader

    --verbose           ; optional.
        if present switches on verbose reporting in the program, often used only for debugging.

    --update            ; optional.
        if present nodes and edges that exist but have no change will be updated anyway
        normally update happens only if the data is not identical with the existing record.

    --delete            ; optional.
        if present we try to delete any item not inserted or updated of the same parent and type

# the .env file must contain:
INVENTORY_HOST="glpi.rl.lan"
INVENTORY_PROTO="https"
INVENTORY_PORT="4482"
INVENTORY_USER="<the user that can read and write>"
INVENTORY_PASS="<the password of the user>"

# and can contain:
VERBOSE=True

"""
    )


def parseOptions():
    try:
        opts, args = getopt.getopt(
            sys.argv[1:],
            "vhudi:P:",
            [
                "verbose",
                "help",
                "update",
                "delete",
                "inFile=",
                "ParentPath=",
            ],
        )
        return opts, args
    except getopt.GetoptError as err:
        print(err)
        usage()
        sys.exit(2)


def doOptions():
    opts, args = parseOptions()

    verbose = False
    update = False
    delete = False
    inFile = None
    parentPath = None

    for o, a in opts:
        if o == "-v":
            verbose = True
        elif o in ("-h", "--help"):
            usage()
            sys.exit(1)
        elif o in ("-u", "--update"):
            update = True
        elif o in ("-d", "--delete"):
            delete = True
        elif o in ("-i", "--inFile"):
            inFile = a
        elif o in ("-P", "--ParentPath"):
            parentPath = a
        else:
            assert False, "unhandled option"

    if inFile is None:
        print("you must specify a input file with -i or --inFile")
        usage()
        sys.exit(1)

    if parentPath is None:
        print("you must specify a ParentPath with -P or --ParentPath")
        usage()
        sys.exit(1)

    return (verbose, inFile, update, delete, parentPath)


def xMain():
    (verbose, inFile, update, delete, parentPath) = doOptions()
    if bool(verbose) is False:
        verbose: bool = env.bool("VERBOSE", False)

    data: dict = loadJsonDataFromFile(inFile)

    nic = setupAppNodesInContext(verbose)

    parentId = nic.findParent(parentPath)
    nic.addNodesAndEdgesFromJsonData(parentId, data, verbose, update)


env = environ.Env()
environ.Env.read_env()

xMain()
