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


def creXtype(
    nic,
    typeName: str,
    typeCache: dict,
    name: str,
):
    """
    create a new type and update the cache if it is not already in the cache
    """
    if name in typeCache:
        return

    s, r = nic.create(typeName=typeName, name=name)
    if nic.validResponse(s):
        typeCache[name] = r.get("id")


def doNode(
    nic,
    item: dict,
    nodeTypeCache: dict,
    parent: int,
):
    print(item)

    what = "Node"
    xx = item.get("name")
    if xx is None:
        print(f"ERROR: {item}", file=sys.stderr)
        exit(101)

    nodeType = item.get("nType")
    creXtype(nic, "NodeType", nodeTypeCache, nodeType)

    data: dict = {
        "name": xx,
        "nType": nodeTypeCache[nodeType],
        "parent": parent,
        "description": item.get("description"),
        "payLoad": item.get("payLoad") or item,
    }
    print(data)
    nic.getAndUpdateOrInsert(what, data, force=True)


def doEdge(nic, item: list, edgeTypeCache: dict, nodeCache: dict):
    what = "Edge"
    if item[0] not in nodeCache or item[1] not in nodeCache:
        return

    edgeType = item[2]
    creXtype(nic, "EdgeType", edgeTypeCache, edgeType)

    data: dict = {
        "fromNode": nodeCache[item[0]],
        "toNode": nodeCache[item[1]],
        "eType": edgeTypeCache[item[2]],
        "description": "",
        "payLoad": item,
    }

    nic.getAndUpdateOrInsert(what, data, force=True)


def findParent(nic, parentPath):
    parents = parentPath.split(".")
    if parents[0] == "":
        parents = parents[1:]
    print(parents)

    nodeCache = nic.getAllByName(typeName="Node")
    for parent in parents:
        parentId = nodeCache[parent]
        if parentId is None:
            print(f"Fatal: parent not found: {parentPath}", file=sys.stderr)
            exit(101)
        print(parent, parentId)

    return parentId


def addNodesAndEdgesFromJsonData(nic, parentId: str, data: dict, verbose: bool = False):
    nodeCache = {}

    if "nodes" in data:
        nodeTypeCache = nic.getAllByName(typeName="NodeType")
        for item in data["nodes"]:
            nodeId = doNode(nic, item, nodeTypeCache, parentId)
            nodeCache[item["name"]] = nodeId

    if "edges" in data:
        edgeTypeCache = nic.getAllByName(typeName="EdgeType")
        for item in data["edges"]:
            doEdge(nic, item, edgeTypeCache, nodeCache)


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


def doOptions():
    try:
        opts, args = getopt.getopt(
            sys.argv[1:],
            "vhudi:",
            [
                "verbose",
                "help",
                "update",
                "delete",
                "inFile=",
            ],
        )
    except getopt.GetoptError as err:
        print(err)
        usage()
        sys.exit(2)

    verbose = False
    update = False
    delete = False
    inFile = None
    print(opts, args)

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
        else:
            assert False, "unhandled option"

    if inFile is None:
        print("you must specify a input file with -i or --inFile")
        usage()
        sys.exit(1)

    return (verbose, inFile, update, delete)


def xMain():
    (verbose, inFile, update, delete) = doOptions()
    verbose: bool = env.bool("VERBOSE", False)

    data: dict = loadJsonDataFromFile("testfileJsonData.json")

    nic = setupAppNodesInContext(verbose)

    parentPath = ".ReversingLabs.HublyData"
    parentId = findParent(nic, parentPath)
    addNodesAndEdgesFromJsonData(nic, parentId, data, verbose)


env = environ.Env()
environ.Env.read_env()

xMain()
