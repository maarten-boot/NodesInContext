#! /usr/bin/env python3

import sys
import ldap
import environ
import json

"""
dump all users: objectclass user and not computer

dump all groups [todo]

create links between users and groups [todo]

write json to stdout
"""


def prepLdapConnect(base: str, verbose: bool = False):
    ldap.set_option(ldap.OPT_REFERRALS, 0)
    ldap.protocol_version = 3

    conn = ldap.initialize(env.str("LDAP_URL"))
    conn.set_option(ldap.OPT_REFERRALS, 0)  # to search the object and all its descendants

    try:
        login = env.str("LDAP_LOGIN")

        conn.simple_bind_s(
            login,
            env.str("LDAP_PASSWORD"),
        )
        r = conn.search_st(  # s t means synchronous with timeout
            base,
            ldap.SCOPE_SUBTREE,
            f"(&(objectClass=person)(userPrincipalName={login}))",
            ["cn"],
            0,
            30,
        )
        if verbose:
            print(r, file=sys.stderr)
    except ldap.INVALID_CREDENTIALS as e:
        print(f"wrong password provided: {e}", file=sys.stderr)
        exit(1)

    return conn


def prepPageControl(size: int = 1000):

    if size > 1000:
        size = 1000

    if size < 250:
        size = 250

    page_control = ldap.controls.libldap.SimplePagedResultsControl(
        True,
        size=size,
        cookie="",
    )
    return page_control


def ldapSearchWithPages(
    conn,
    base: str,
    page_control,
    searchStr: str,
    resultSet: list,
):

    response = conn.search_ext(
        base,
        ldap.SCOPE_SUBTREE,
        searchStr,
        resultSet,
        serverctrls=[page_control],
    )

    result = []
    pages = 0
    while True:
        pages += 1
        rtype, rdata, rmsgid, serverctrls = conn.result3(response)
        result.extend(rdata)

        controls = [control for control in serverctrls if control.controlType == ldap.controls.libldap.SimplePagedResultsControl.controlType]
        if not controls:
            print("The server ignores RFC 2696 control")
            break

        if not controls[0].cookie:
            break

        page_control.cookie = controls[0].cookie
        response = conn.search_ext(
            base,
            ldap.SCOPE_SUBTREE,
            searchStr,
            resultSet,
            serverctrls=[page_control],
        )
    return result


def doOneUserItem(item):
    data = {
        "cn": None,
        "nType": "ldapPerson",
    }
    cn = item[0]
    if cn is None or cn == "None":
        return None

    data["cn"] = cn
    for k, v in item[1].items():
        if len(v) == 1:
            j = v[0]
            j = j.decode("unicode-escape").encode("latin1").decode("utf-8")
            data[k] = j
        else:
            data[k] = []
            for j in v:
                j = j.decode("unicode-escape").encode("latin1").decode("utf-8")
                data[k].append(j)
    return data


def doOneGroupItem(item):
    data = {
        "cn": None,
        "nType": "ldapGroup",
    }
    cn = item[0]
    if cn is None or cn == "None":
        return None

    data["cn"] = cn
    for k, v in item[1].items():
        if len(v) == 1:
            j = v[0]
            j = j.decode("unicode-escape").encode("latin1").decode("utf-8")
            data[k] = j
        else:
            data[k] = []
            for j in v:
                j = j.decode("unicode-escape").encode("latin1").decode("utf-8")
                data[k].append(j)
    return data


def searchUsersNotComputers(
    conn,
    base: str,
    page_control,
):
    searchStr = "(&(objectclass=user)(!(objectclass=computer)))"
    resultSet = [
        "ufn",
        "samaccountname",
        "mail",
        "sn",
        "givenname",
        "displayName",
        "memberof",
        "description",
        "name",
        "userPrincipalName",
    ]

    return ldapSearchWithPages(
        conn,
        base,
        page_control,
        searchStr,
        resultSet,
    )


def searchGroups(
    conn,
    base: str,
    page_control,
):
    searchStr = "(objectclass=group)"
    resultSet = [
        "name",
        "description",
        "distinguishedName",
        "ufn",
        "member",
        "samaccountname",
    ]

    return ldapSearchWithPages(
        conn,
        base,
        page_control,
        searchStr,
        resultSet,
    )


def xMain():
    base = env.str("LDAP_BASE")

    conn = prepLdapConnect(base)
    page_control = prepPageControl(1000)

    users = searchUsersNotComputers(conn, base, page_control)
    groups = searchGroups(conn, base, page_control)

    dd = {
        "nodes": [],
        "edges": [],
    }

    for item in users:
        data = doOneUserItem(item)
        if data:
            dd["nodes"].append(data)
    for item in groups:
        data = doOneGroupItem(item)
        if data:
            dd["nodes"].append(data)

    print(json.dumps(dd, indent=4))


env = environ.Env()
environ.Env.read_env()
xMain()
