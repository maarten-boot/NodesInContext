import requests
import yaml
import sys
import logging


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
        self.verbose = verbose

    def _getJson(
        self,
        url: str,
    ):
        if self.verbose:
            print(url, file=sys.stderr)

        r = requests.get(url)
        data = None
        if r.status_code >= 200 and r.status_code < 300:
            data = r.json()
        return data

    def _getText(
        self,
        url: str,
    ):
        if self.verbose:
            print(url, file=sys.stderr)

        r = requests.get(url)
        data = None
        if r.status_code >= 200 and r.status_code < 300:
            data = r.text
        return data

    def _post(
        self,
        url: str,
        data: dict,
    ):
        headers = {
            "Content-type": "application/json",
            "Accept": "application/json",
        }

        if self.verbose:
            print(url, file=sys.stderr)
            print(data, file=sys.stderr)

        r = requests.post(
            url,
            json=data,
            headers=headers,
        )
        if r.status_code >= 200 and r.status_code < 300:
            return r.status_code, r.json()
        return r.status_code, r.text

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
        self.baseUrl = f"{self.proto}://{self.user}:{self.passw}@{self.host}:{self.port}/"
        return self.baseUrl

    def getBaseUrlApp(self):
        return f"{self.baseUrl}api/aNode"


class HavingSchema:
    verbose: bool
    schema: dict

    types: list
    patched: list

    def __init__(
        self,
        verbose: bool = False,
    ):
        self.verbose = verbose

    def getSchemaFromHost(self):
        url = f"{self.baseUrl}api/schema"
        text = self._getText(url)
        self.schema = yaml.safe_load(text)
        return self.schema

    def findPathInDict(
        self,
        data: dict,
        path: list,
    ):
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

    def getAllOrByName(
        self,
        url: str,
        name: str | None,
    ):
        if name:
            url = url + f"?name={name}"
        r = self._getJson(url)
        return r

    def getInfo(
        self,
        typeName: str,
        name: str | None,
    ):
        if typeName not in self.types:
            msg = f"typeNem not known: {typeName}"
            raise NodesInContextUnsupportedApiType(msg)

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

    def cre(self, typeName, **kwargs):
        data = {}

        self.__creRequired(typeName, data, **kwargs)
        self.__creOptional(typeName, data, **kwargs)

        url = f"{self.getBaseUrlApp()}/{typeName}/"
        return self._post(url=url, data=data)

    def getAllByName(self, typeName: str) -> dict[str, int]:
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
