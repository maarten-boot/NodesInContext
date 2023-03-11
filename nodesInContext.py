import requests
import yaml
import sys
import logging
from requests.auth import HTTPBasicAuth
from urllib3.exceptions import InsecureRequestWarning


class NodesInContextExceptions(Exception):
    pass


class NodesInContextUnsupportedApiType(NodesInContextExceptions):
    pass


class NodesInContextSchemaPathMissing(NodesInContextExceptions):
    pass


class UsingUrlData:
    verbose: bool

    host: str
    proto: str
    port: str
    user: str
    passw: str

    baseUrl: str

    def __init__(self, verbose: bool = False):
        super().__init__()

        requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)
        self.verbose = verbose

    def validResponse(self, code):
        return code >= 200 and code < 300

    def _getJson(self, url: str):
        if self.verbose:
            print(url, file=sys.stderr)

        r = requests.get(url, auth=self.auth, verify=False)
        if self.validResponse(r.status_code):
            return r.status_code, r.json()
        return r.status_code, r.text

    def _getText(self, url: str):
        if self.verbose:
            print(url, file=sys.stderr)

        r = requests.get(url, auth=self.auth, verify=False)
        if self.validResponse(r.status_code):
            return r.status_code, r.text
        return r.status_code, r.text

    def _postOrPutOrPatch(self, what: str, url: str, data: dict):
        headers = {
            "Content-type": "application/json",
            "Accept": "application/json",
        }

        if self.verbose:
            print(what, url, file=sys.stderr)
            print(data, file=sys.stderr)

        if what == "post":
            r = requests.post(url, json=data, headers=headers, auth=self.auth, verify=False)
        elif what == "put":
            r = requests.put(url, json=data, headers=headers, auth=self.auth, verify=False)
        elif what == "patch":
            r = requests.patch(url, json=data, headers=headers, auth=self.auth, verify=False)
        else:
            msg = f"Fatal: unknown verb: {what}"
            print(msg, file=sys.stderr)
            exit(101)

        if self.validResponse(r.status_code):
            return r.status_code, r.json()
        return r.status_code, r.text

    def _post(
        self,
        url: str,
        data: dict,
    ):
        return self._postOrPutOrPatch("post", url, data)

    def _put(
        self,
        url: str,
        data: dict,
    ):
        return self._postOrPutOrPatch("put", url, data)

    def _patch(
        self,
        url: str,
        data: dict,
    ):
        return self._postOrPutOrPatch("patch", url, data)

    def getBaseUrl(
        self,
        host: str,
        user: str,
        passw: str,
        proto: str = "https",
        port: int = 443,
    ):
        self.host = host
        self.proto = proto
        self.port = port
        self.user = user
        self.passw = passw

        self.baseUrl = f"{self.proto}://{self.host}:{self.port}/"
        self.auth = HTTPBasicAuth(self.user, self.passw)
        return self.baseUrl

    def getBaseUrlApp(self):
        return f"{self.baseUrl}api/aNode"


class HavingSchema:
    verbose: bool
    schema: dict

    types: list
    patched: list
    queryData: dict

    def __init__(
        self,
        verbose: bool = False,
    ):
        super().__init__()
        self.verbose = verbose

    def getSchemaFromHost(self):
        self.schema = {}
        url = f"{self.baseUrl}api/schema"
        s, text = self._getText(url)
        if not self.validResponse(s):
            msg: str = f"{s} {text} :: {url}"
            raise NodesInContextSchemaPathMissing(msg)

        self.schema = yaml.safe_load(text)
        return self.schema

    def findPathInDict(self, data: dict, path: list):
        zz = data
        for j in path:
            zz = zz.get(j)
            if zz is None:
                s = ".".join(path)
                msg: str = f"missing {j} in path: {s}"
                raise NodesInContextSchemaPathMissing(msg)
        return zz

    def getSchemaTypes(self):
        zz = self.findPathInDict(self.schema, ["components", "schemas"])
        self.types = []
        self.patched = []
        for n in zz:
            if n.startswith("Patched"):
                if n not in self.patched:
                    self.patched.append(n)
                continue
            if n not in self.types:
                self.types.append(n)

        return self.types, self.patched

    def getSchemaFromName(
        self,
        typeName: str,
    ):
        path = ["components", "schemas", typeName]
        z = self.findPathInDict(self.schema, path)
        req = z.get("required")
        prop = z.get("properties")

        if self.verbose:
            print(f"required: {req}", file=sys.stderr)
            print(f"properties of {typeName}: {prop}", file=sys.stderr)

        return (prop, req)

    def getQueryData(self):
        result = {}
        zz = self.getSchemaFromHost()
        for path in zz.get("paths"):
            curr = zz["paths"][path]
            for rType in curr:
                if rType != "get":
                    continue

                paramList = curr[rType].get("parameters")
                if paramList is None:
                    continue

                for param in paramList:
                    if param.get("in") != "query":
                        continue

                    item = path.split("/")[-2]
                    field = param.get("name")
                    sche = param.get("schema")
                    if item not in result:
                        result[item] = {}
                    result[item][field] = sche

        self.queryData = result
        return result


class NodesInContext(
    HavingSchema,
    UsingUrlData,
):
    verbose: bool = False

    def __init__(
        self,
        host: str,
        user: str,
        passw: str,
        proto: str = "https",
        port: int = 443,
        verbose: bool = False,
    ):
        super().__init__(verbose=verbose)

        self.verbose = verbose
        if 0:
            logging.warning("Watch out!")

        self.getBaseUrl(host=host, proto=proto, port=port, user=user, passw=passw)
        self.getSchemaFromHost()
        self.getSchemaTypes()
        self.getQueryData()

    def getAllOrByName(self, url: str, name: str | None):
        if name:
            url = url + f"?name={name}"
        s, r = self._getJson(url)
        if self.validResponse(s):
            return r
        raise NodesInContextUnsupportedApiType(f"{s, r}")

    def validateTypeName(self, typeName: str):
        if typeName not in self.types:
            msg = f"typeName not known: {typeName}"
            raise NodesInContextSchemaPathMissing(msg)

    def getInfo(self, typeName: str, name: str | None):
        self.validateTypeName(typeName)

        url = f"{self.getBaseUrlApp()}/{typeName}/"
        return self.getAllOrByName(url, name)

    def getEdgeInfo(
        self,
        fromNode: int,
        toNode: int,
        eType: int,
    ):
        # url = f"{self.getBaseUrl()}/Edge/"
        pass

    def __creRequired(self, typeName: str, data: dict, **kwargs):
        prop, req = self.getSchemaFromName(typeName)

        # first start with mandatory fields
        for n in req:
            if self.verbose:
                print(n, prop[n], file=sys.stderr)

            if prop[n].get("readOnly"):  # readonly elements are not provided during create
                continue

            if prop[n].get("nullable"):  # treat nullable as optional by providing a default value
                data[n] = None
                if n in kwargs:
                    data[n] = kwargs[n]

            data[n] = kwargs[n]  # later raise a ex if not present as it is mandatory

    def __creOptional(self, typeName: str, data: dict, **kwargs):
        prop, req = self.getSchemaFromName(typeName)

        # now do all not mandatory arguments
        for n in prop:
            if n in req:  # tis we already did above so skip here
                continue
            if n in kwargs:
                data[n] = kwargs[n]

    def create(self, typeName: str, **kwargs):
        self.validateTypeName(typeName)

        data = {}
        self.__creRequired(typeName, data, **kwargs)
        self.__creOptional(typeName, data, **kwargs)
        url = f"{self.getBaseUrlApp()}/{typeName}/"

        s, r = self._post(url=url, data=data)
        if not self.validResponse(s):
            raise NodesInContextUnsupportedApiType(f"{s, r}")
        return s, r

    def update(self, typeName: str, **kwargs):
        self.validateTypeName(typeName)

        if "id" not in kwargs:
            msg = "FATAL: missing id in data"
            raise NodesInContextSchemaPathMissing(msg)
        xid = kwargs["id"]

        data = {}
        self.__creRequired(typeName, data, **kwargs)
        self.__creOptional(typeName, data, **kwargs)

        url = f"{self.getBaseUrlApp()}/{typeName}/{xid}/"
        s, r = self._patch(url=url, data=data)
        if not self.validResponse(s):
            raise NodesInContextUnsupportedApiType(f"{s, r}")
        return s, r

    def getAllByName(self, typeName: str) -> dict[str, int]:
        self.validateTypeName(typeName)

        rr: dict[str, int] = {}
        # this only works for items with a name
        d = self.getInfo(typeName, None)  # all
        for item in d:
            idInt = item.get("id")
            name = item.get("name")
            if name and idInt:
                rr[name] = idInt

        if self.verbose:
            print(rr, file=sys.stderr)

        return rr

    def query(self, typeName: str, unique: bool, **kwargs) -> list:
        # query may find multiple as string matching is icontains
        self.validateTypeName(typeName)

        if typeName not in self.queryData:
            msg: str = f"unknown typeName in queryData {typeName}"
            raise NodesInContextSchemaPathMissing(msg)

        # find required query parameters
        myParams = self.queryData[typeName]
        zz = {}
        for name in myParams:
            if name in kwargs:
                zz[name] = kwargs[name]

        # build a url from the collected parameters
        url = self.getBaseUrlApp() + "/" + typeName + "?"
        ll = []
        for k, v in zz.items():
            ll.append(f"{k}={v}")
        url = url + "&".join(ll)

        # do the query
        s, r = self._getJson(url)
        if not self.validResponse(s):
            raise NodesInContextUnsupportedApiType(f"{s, r}")

        if not unique:
            return s, r

        # you now may want to find the exact match
        for item in r:
            found = True
            for k, v in zz.items():
                if item[k] != v:
                    found = False
            if found:
                return s, [item]
        return s, []  # just in case

    def dataHasChanged(self, nData: dict, oData: dict):
        # oData comes fresh from the database, nData is what we want to update with
        for k, v in oData.items():
            if k not in nData:
                continue  # ignore fields not being updated
            if nData[k] != v:
                return True
        return False

    def getAndUpdateOrInsert(self, what: str, data: dict, force: bool = False):
        s, rr = self.query(what, unique=True, **data)
        if not self.validResponse(s):
            raise NodesInContextUnsupportedApiType(f"{s, rr}")

        if len(rr) > 1:
            # name might be a partial match so aa will find aa and aa_bb
            raise NodesInContextUnsupportedApiType(f" multiple returns {s, rr} :: {what} {data} {rr}")

        if len(rr) == 1:
            if force is False:
                if not self.dataHasChanged(data, rr[0]):
                    if self.verbose:
                        print(f"no change for {what}, {rr[0]['id']}", file=sys.stderr)
                    return s, data

            # TODO: if nothing changed we dont need to update
            data["id"] = rr[0]["id"]
            s, r = self.update(what, **data)
            if not self.validResponse(s):
                raise NodesInContextUnsupportedApiType(f"{s, r} :: {what} {data} {rr}")

            if self.verbose:
                print("Update", what, r, file=sys.stderr)

            return s, r

        s, r = self.create(what, **data)
        if not self.validResponse(s):
            raise NodesInContextUnsupportedApiType(f"{s, r} :: {what} {data} {rr}")

        if self.verbose:
            print("Create", what, r, file=sys.stderr)

        return s, r
