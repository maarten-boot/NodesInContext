import requests
import yaml
import sys


class NodesInContextExceptions(Exception):
    pass


class NodesInContextUnsupportedApiType(NodesInContextExceptions):
    pass


class NodesInContextSchemaPathMissing(NodesInContextExceptions):
    pass


SPEC: str = """
components:
  schemas:
    Edge:
      type: object
      properties:
        id:
          type: integer
          readOnly: true
        description:
          type: string
          nullable: true
        eType:
          type: integer
        fromNode:
          type: integer
        toNode:
          type: integer
        payLoad:
          type: object
          additionalProperties: {}
          nullable: true
      required:
      - eType
      - fromNode
      - id
      - toNode
    EdgeType:
      type: object
      properties:
        id:
          type: integer
          readOnly: true
        name:
          type: string
          maxLength: 128
        description:
          type: string
          nullable: true
      required:
      - id
      - name
    Node:
      type: object
      properties:
        id:
          type: integer
          readOnly: true
        name:
          type: string
          maxLength: 128
        description:
          type: string
          nullable: true
        nType:
          type: integer
        parent:
          type: integer
          nullable: true
        payLoad:
          type: object
          additionalProperties: {}
          nullable: true
      required:
      - id
      - nType
      - name
      - parent
    NodeType:
      type: object
      properties:
        id:
          type: integer
          readOnly: true
        name:
          type: string
          maxLength: 128
        description:
          type: string
          nullable: true
      required:
      - id
      - name
    PatchedEdge:
      type: object
      properties:
        id:
          type: integer
          readOnly: true
        description:
          type: string
          nullable: true
        eType:
          type: integer
        fromNode:
          type: integer
        toNode:
          type: integer
        payLoad:
          type: object
          additionalProperties: {}
          nullable: true
    PatchedEdgeType:
      type: object
      properties:
        id:
          type: integer
          readOnly: true
        name:
          type: string
          maxLength: 128
        description:
          type: string
          nullable: true
    PatchedNode:
      type: object
      properties:
        id:
          type: integer
          readOnly: true
        name:
          type: string
          maxLength: 128
        description:
          type: string
          nullable: true
        nType:
          type: integer
        parent:
          type: integer
          nullable: true
        payLoad:
          type: object
          additionalProperties: {}
          nullable: true
    PatchedNodeType:
      type: object
      properties:
        id:
          type: integer
          readOnly: true
        name:
          type: string
          maxLength: 128
        description:
          type: string
          nullable: true
"""


class NodesInContext:
    verbose: bool = False
    spec: dict

    host: str
    proto: str
    port: str
    user: str
    passw: str

    baseUrl: str

    def __init__(
        self,
        verbose: bool = False,
    ):
        self.verbose = verbose

        self.spec = yaml.safe_load(SPEC)
        if self.verbose:
            print(self.spec, file=sys.stderr)

    def getSchema(self, name: str):
        path = ["components", "schemas", name]
        z = self.spec
        for n in path:
            z = z.get(n)
            if z is None:
                s = ".".join(path)
                msg: str = f"missing path: {s}"
                raise NodesInContextSchemaPathMissing(msg)

        req = z.get("required")
        prop = z.get("properties")

        return (prop, req)

    def setAccesData(
        self,
        host: str,
        user: str,
        passw: str,
        proto: str = "https",
        port: int = 443,
    ):
        self.host = host
        self.proto = host
        self.port = host
        self.user = user
        self.passw = passw
        self.baseUrl = f"{proto}://{user}:{passw}@{host}:{port}/"

    def getBaseUrl(self):
        return f"{self.baseUrl}api/aNode"

    def getAllOrByName(self, url: str, name: str | None):
        if name:
            url = url + f"?name={name}"
        r = requests.get(url)
        data = r.json()
        return data

    def post(self, url: str, data: dict):
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

        url = f"{self.getBaseUrl()}/{typeName}/"
        return self.getAllOrByName(url, name)

    def getEdgeInfo(
        self,
        fromNode: int,
        toNode: int,
        eType: int,
    ):
        # url = f"{self.getBaseUrl()}/Edge/"
        pass

    def cre(self, typeName, **kwargs):
        prop, req = self.getSchema(typeName)

        if self.verbose:
            print(f"required: {req}", file=sys.stderr)
            print(f"properties of {typeName}: {prop}", file=sys.stderr)

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
        r = self.post(
            url=url,
            data=data,
        )

        if self.verbose:
            print(r, file=sys.stderr)

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
