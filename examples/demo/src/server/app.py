"""Taskly demo server: a tiny route table and the config keys it reads."""
from .version import SPEC_REV


def cfg(name, default=None):
    return {"port": 8080, "page_size": 20, "export_dir": "out"}.get(name, default)


def route(path):
    def deco(fn):
        ROUTES[path] = fn
        return fn
    return deco


ROUTES = {}


@route("/tasks")
def tasks():
    return {"page_size": cfg("page_size"), "rev": SPEC_REV}


@route("/search")
def search():
    return {"results": []}


@route("/export")
def export():
    return {"dir": cfg("export_dir")}


def listen():
    return cfg("port")
