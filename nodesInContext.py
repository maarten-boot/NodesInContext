import requests
import yaml
import sys


class NodesInContextExceptions(Exception):
    pass


class NodesInContextUnsupportedApiType(NodesInContextExceptions):
    pass


class NodesInContextSchemaPathMissing(NodesInContextExceptions):
    pass


class NodesInContext:
    verbose: bool = False
    schema: dict

    host: str
    proto: str
    port: str
    user: str
    passw: str

    baseUrl: str

    def __init__(
        self,
        host: str,
        user: str,
        passw: str,
        proto: str = "https",
        port: int = 443,
        verbose: bool = False,
    ):
        self.verbose = verbose

        self.host = host
        self.proto = proto
        self.port = port
        self.user = user
        self.passw = passw

        self.baseUrl = self.getBaseUrl()
        self.schema = self.getSchemaFromHost()

    def __getJson(
        self,
        url: str,
    ):
        r = requests.get(url)

        data = None
        if r.status_code >= 200 and r.status_code <= 300:
            data = r.json()

        return data

    def __getText(
        self,
        url: str,
    ):
        r = requests.get(url)
        data = None
        if r.status_code >= 200 and r.status_code <= 300:
            data = r.text
        return data

    def __post(
        self,
        url: str,
        data: dict,
    ):
        headers = {
            "Content-type": "application/json",
            "Accept": "application/json",
        }
        r = requests.post(
            url,
            json=data,
            headers=headers,
        )

        if r.status_code >= 200 and r.status_code <= 300:
            return r.status_code, r.json()

        return r.status_code, r.text

    def getSchemaFromName(
        self,
        typeName: str,
    ):
        path = ["components", "schemas", typeName]
        z = self.schema
        for n in path:
            z = z.get(n)
            if z is None:
                s = ".".join(path)
                msg: str = f"missing path: {s}"
                raise NodesInContextSchemaPathMissing(msg)

        req = z.get("required")
        prop = z.get("properties")

        if self.verbose:
            print(f"required: {req}", file=sys.stderr)
            print(f"properties of {typeName}: {prop}", file=sys.stderr)

        return (prop, req)

    def getBaseUrl(self):
        baseUrl = f"{self.proto}://{self.user}:{self.passw}@{self.host}:{self.port}/"
        return baseUrl

    def getBaseUrlApp(self):
        return f"{self.baseUrl}api/aNode"

    def getSchemaFromHost(self):
        url = f"{self.baseUrl}api/schema"
        text = self.__getText(url)
        schema = yaml.safe_load(text)
        return schema

    def getAllOrByName(
        self,
        url: str,
        name: str | None,
    ):
        if name:
            url = url + f"?name={name}"
        r = self.__getJson(url)
        return r

    def getInfo(
        self,
        typeName: str,
        name: str | None,
    ):
        types = [
            "Node",
            "Edge",
            "NodeType",
            "EdgeType",
        ]
        if typeName not in types:
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

    def cre(
        self,
        typeName,
        **kwargs,
    ):
        prop, req = self.getSchemaFromName(typeName)

        # start with a empry data
        data = {}

        # first start with mandatory fields
        for n in req:
            if self.verbose:
                print(n, prop[n])

            if prop[n].get("readOnly"):  # readonly elements are not provided during create
                continue

            if prop[n].get("nullable"):  # treat nullable as optional by providing a default value
                data[n] = None
                if n in kwargs:
                    data[n] = kwargs[n]

            data[n] = kwargs[n]  # later raise a ex if not present as it is mandatory

        # now do all not mandatory arguments
        for n in prop:
            if n in req:  # tis we already did above so skip here
                continue
            if n in kwargs:
                data[n] = kwargs[n]

        if self.verbose:
            print(data, file=sys.stderr)

        url = f"{self.getBaseUrl()}/{typeName}/"
        r = self.__post(
            url=url,
            data=data,
        )

        return r

    def getAllByName(
        self,
        typeName: str,
    ) -> dict[str, int]:
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
