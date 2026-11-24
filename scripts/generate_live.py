#!/usr/bin/env python3
"""Generate the ``Live`` mock package from the PhotonicVelocity/LiveAPI ``.pyi`` stubs.

Usage:  python3 -I scripts/generate_live.py <stubs/<version>/Live dir> <output package dir>

The stubs are only parsed with ``ast``; nothing from them is imported or executed.
Needs Python 3.9+ (``ast.unparse``). The generated code itself runs on Python 3.7+.
"""
import ast
import collections
import copy
import re
import sys
from pathlib import Path

# Classes implemented by hand in Live/_impl.py instead of being generated.
HANDWRITTEN = {
    ("Base", "Vector"),
    ("Base", "Timer"),
    ("Base", "Text"),
    ("Browser", "BrowserItemIterator"),
}
PRIMITIVES = {"bool": "False", "int": "0", "float": "0.0", "str": "''", "bytes": "b''"}
EMPTY = {"tuple": "()", "Tuple": "()", "list": "[]", "List": "[]", "dict": "{}", "Dict": "{}"}
NONE_TYPES = {"object", "Any", "Callable", "Iterable", "Iterator", "Optional", "Self", "type"}


class Index:
    """Every class declared in the stubs, keyed by (module, qualified name)."""

    def __init__(self, modules):
        self.classes = {}
        self.top = collections.defaultdict(list)
        self.unresolved = collections.Counter()
        for mod, tree in modules.items():
            for node in tree.body:
                if isinstance(node, ast.ClassDef):
                    self.top[node.name].append(mod)
                    self._add(mod, node, "")

    def _add(self, mod, node, prefix):
        qual = prefix + node.name
        is_enum = any(ast.unparse(b) == "int" for b in node.bases)
        first = None
        if is_enum:
            for item in node.body:
                if isinstance(item, ast.AnnAssign):
                    first = ast.literal_eval(item.value)
                    break
        members = {}
        if is_enum:
            for item in node.body:
                if isinstance(item, ast.AnnAssign):
                    members[item.target.id] = ast.literal_eval(item.value)
        self.classes[(mod, qual)] = {"enum": is_enum, "first": first, "members": members}
        for item in node.body:
            if isinstance(item, ast.ClassDef):
                self._add(mod, item, qual + ".")

    def resolve(self, name, mod, chain):
        for qual in reversed(chain):
            if (mod, qual + "." + name) in self.classes:
                return mod, qual + "." + name
        if (mod, name) in self.classes:
            return mod, name
        owners = self.top.get(name, [])
        if len(owners) == 1:
            return owners[0], name
        if len(owners) > 1:
            self.unresolved["ambiguous:" + name] += 1
        return None

    def spec(self, ann, mod, chain):
        """Source text of the default value a property/method returning ``ann`` yields."""
        if ann is None or (isinstance(ann, ast.Constant) and ann.value is None):
            return "None"
        if isinstance(ann, ast.BinOp) and isinstance(ann.op, ast.BitOr):
            parts = []
            stack = [ann]
            while stack:
                n = stack.pop()
                if isinstance(n, ast.BinOp) and isinstance(n.op, ast.BitOr):
                    stack.extend([n.right, n.left])
                else:
                    parts.append(n)
            if any(isinstance(p, ast.Constant) and p.value is None for p in parts):
                return "None"
            return self.spec(parts[0], mod, chain)
        if isinstance(ann, ast.Subscript):
            base = ast.unparse(ann.value)
            if base in EMPTY:
                return EMPTY[base]
            if base in NONE_TYPES:
                return "None"
            return self.spec(ann.value, mod, chain)
        if isinstance(ann, ast.Attribute):
            return self.spec(ast.Name(id=ann.attr), mod, chain)
        if isinstance(ann, ast.Name):
            name = ann.id
            if name in PRIMITIVES:
                return PRIMITIVES[name]
            if name in EMPTY:
                return EMPTY[name]
            if name in NONE_TYPES:
                return "None"
            found = self.resolve(name, mod, chain)
            if found is None:
                self.unresolved[name] += 1
                return "None"
            info = self.classes[found]
            if info["enum"]:
                return "(%r, %r, %r)" % (found[0], found[1], info["first"])
            return "(%r, %r)" % found
        self.unresolved[ast.unparse(ann)] += 1
        return "None"


def flat_args(args, index, mod, chain):
    """Merge positional-only args (``/`` is not valid on 3.7) and inline enum defaults."""
    args = copy.deepcopy(args)
    args.args = args.posonlyargs + args.args
    args.posonlyargs = []

    class Inline(ast.NodeTransformer):
        def visit_Attribute(self, node):
            if isinstance(node.value, ast.Name):
                found = index.resolve(node.value.id, mod, chain)
                info = index.classes.get(found) if found else None
                if info and info["enum"] and node.attr in info["members"]:
                    return ast.Constant(info["members"][node.attr])
            return node

    args.defaults = [Inline().visit(d) for d in args.defaults]
    args.kw_defaults = [Inline().visit(d) if d is not None else None for d in args.kw_defaults]
    return args


def call_parts(args, drop_self):
    names = [a.arg for a in args.posonlyargs + args.args]
    if drop_self:
        names = names[1:]
    positional = ["%s" % n for n in names]
    if args.vararg:
        positional.append("*" + args.vararg.arg)
    pos_src = "(" + "".join(p + ", " for p in positional) + ")"
    kw = ["%r: %s" % (a.arg, a.arg) for a in args.kwonlyargs]
    kw_src = "{" + ", ".join(kw)
    if args.kwarg:
        kw_src += (", " if kw else "") + "**" + args.kwarg.arg
    kw_src += "}"
    return pos_src, kw_src


def docstring(node, indent):
    text = ast.get_docstring(node, clean=True)
    if not text:
        return []
    pad = " " * indent
    if '"""' in text or "\\" in text:
        return [pad + repr(text)]
    if "\n" not in text:
        return [pad + '"""' + text + '"""']
    body = [pad + line if line else "" for line in text.split("\n")]
    return [pad + '"""' + text.split("\n")[0]] + body[1:] + [pad + '"""']


class ModuleWriter:
    def __init__(self, mod, tree, index):
        self.mod = mod
        self.tree = tree
        self.index = index
        self.imports = collections.defaultdict(set)
        self.lines = []

    def emit_function(self, node, indent, chain, is_method):
        pad = " " * indent
        name = node.name
        args = node.args
        arg_names = [a.arg for a in args.posonlyargs + args.args]
        ret = ast.unparse(node.returns) if node.returns else "None"
        sig = "(%s)" % ast.unparse(flat_args(args, self.index, self.mod, chain))
        decorators = [ast.unparse(d) for d in node.decorator_list]
        out = self.lines
        if "overload" in decorators:
            return
        is_getter = "property" in decorators
        setter = next((d for d in decorators if d.endswith(".setter")), None)
        if setter:
            prop = setter.split(".")[0]
            out.append("%s@%s.setter" % (pad, prop))
            out.append("%sdef %s%s -> None:" % (pad, name, sig))
            spec = self.index.spec(args.args[1].annotation if len(args.args) > 1 else None, self.mod, chain)
            out.append("%s    self._set(%r, %s, %s)" % (pad, name, arg_names[1], spec))
            out.append("")
            return
        if is_getter:
            out.append("%s@property" % pad)
            out.append("%sdef %s%s -> %s:" % (pad, name, sig, ret))
            out.extend(docstring(node, indent + 4))
            spec = self.index.spec(node.returns, self.mod, chain)
            out.append("%s    return self._get(%r, %s)" % (pad, name, spec))
            out.append("")
            return
        if name == "__init__":
            kwargs = ", ".join("%s=%s" % (a, a) for a in arg_names[1:])
            out.append("%sdef __init__%s -> None:" % (pad, sig))
            out.append("%s    super().__init__(%s)" % (pad, kwargs))
            out.append("")
            return
        if name.startswith("__") and name.endswith("__"):
            return
        listener = re.fullmatch(r"(add|remove)_(.+)_listener", name)
        has_listener = re.fullmatch(r"(.+)_has_listener", name)
        if is_method and len(arg_names) == 2 and arg_names[1] == "callback":
            if listener:
                out.append("%sdef %s%s -> None:" % (pad, name, sig))
                out.append("%s    self._%s_listener(%r, callback)" % (pad, listener.group(1), listener.group(2)))
                out.append("")
                return
            if has_listener:
                out.append("%sdef %s%s -> bool:" % (pad, name, sig))
                out.append("%s    return self._has_listener(%r, callback)" % (pad, has_listener.group(1)))
                out.append("")
                return
        pos, kw = call_parts(args, drop_self=is_method)
        spec = self.index.spec(node.returns, self.mod, chain)
        out.append("%sdef %s%s -> %s:" % (pad, name, sig, ret))
        out.extend(docstring(node, indent + 4))
        if is_method:
            out.append("%s    return self._call(%r, %s, %s, %s)" % (pad, name, pos, kw, spec))
        else:
            out.append("%s    return call_function(%r, %r, %s, %s, %s)" % (pad, self.mod, name, pos, kw, spec))
        out.append("")

    def class_bases(self, node):
        """Return (kind, base source list)."""
        bases = [ast.unparse(b) for b in node.bases]
        if "int" in bases:
            self.imports["enum"].add("IntEnum")
            return "enum", ["IntEnum"]
        if not bases:
            return "class", ["MockObject"]
        out = []
        kind = "class"
        for b in bases:
            root = b.split("[")[0]
            if root == "Vector":
                kind = "vector"
            if root in ("Exception",):
                out.append(root)
                continue
            head = root.split(".")[0]
            found = self.index.resolve(head, self.mod, [])
            if found is not None and "." in root and (found[0], root) in self.index.classes:
                if found[0] != self.mod:
                    self.imports["." + found[0]].add(head)
                out.append(root)
                continue
            if found is None:
                self.index.unresolved["base:" + root] += 1
                out.append("MockObject")
                continue
            if found[0] != self.mod:
                self.imports["." + found[0]].add(found[1])
            out.append(found[1])
        return kind, out

    def emit_class(self, node, indent, chain):
        pad = " " * indent
        qual = (chain[-1] + "." if chain else "") + node.name
        kind, bases = self.class_bases(node)
        self.lines.append("%sclass %s(%s):" % (pad, node.name, ", ".join(bases)))
        doc = docstring(node, indent + 4)
        self.lines.extend(doc)
        body_start = len(self.lines)
        sub_chain = chain + [qual]
        if kind == "enum":
            for item in node.body:
                if isinstance(item, ast.AnnAssign):
                    self.lines.append("%s    %s = %s" % (pad, item.target.id, ast.unparse(item.value)))
        elif kind == "vector":
            declared = {i.name for i in node.body if isinstance(i, ast.FunctionDef)}
            for method in ("append", "extend"):
                if method in declared:
                    self.lines.append("%s    def %s(self, value) -> None:" % (pad, method))
                    self.lines.append("%s        self._%s(value)" % (pad, method))
        else:
            nested = [n for n in node.body if isinstance(n, ast.ClassDef)]
            for sub in self.order(nested):
                self.emit_class(sub, indent + 4, sub_chain)
                self.lines.append("")
            for item in node.body:
                if isinstance(item, ast.FunctionDef):
                    self.emit_function(item, indent + 4, sub_chain, True)
        if len(self.lines) == body_start:
            self.lines.append("%s    pass" % pad)
        while self.lines and self.lines[-1] == "":
            self.lines.pop()

    def order(self, classes):
        """Order sibling classes so that bases defined in the same scope come first."""
        names = {c.name: c for c in classes}
        done, result = set(), []

        def visit(c):
            if c.name in done:
                return
            done.add(c.name)
            for b in c.bases:
                root = ast.unparse(b).split("[")[0]
                if root in names:
                    visit(names[root])
            result.append(c)

        for c in classes:
            visit(c)
        return result

    def render(self, header):
        classes = [n for n in self.tree.body if isinstance(n, ast.ClassDef)]
        functions = [n for n in self.tree.body if isinstance(n, ast.FunctionDef)]
        handwritten = sorted(n for m, n in HANDWRITTEN if m == self.mod)
        for node in self.order(classes):
            if (self.mod, node.name) in HANDWRITTEN:
                continue
            self.emit_class(node, 0, [])
            self.lines.extend(["", ""])
        for node in functions:
            self.emit_function(node, 0, [], False)
            self.lines.append("")
        exports = None
        for node in self.tree.body:
            if isinstance(node, ast.Assign) and any(
                isinstance(t, ast.Name) and t.id == "__all__" for t in node.targets
            ):
                exports = ast.literal_eval(node.value)
        head = [header, "from __future__ import annotations", ""]
        head.append("from typing import Any, Callable, Iterable, Iterator, Optional, Tuple  # noqa: F401")
        for module, names in sorted(self.imports.items()):
            head.append("from %s import %s" % (module, ", ".join(sorted(names))))
        head.append("from ._runtime import MockObject, call_function  # noqa: F401")
        if handwritten:
            head.append("from ._impl import %s" % ", ".join(handwritten))
        if self.mod != "Base":
            head.append("from .Base import Vector  # noqa: F401")
        head.extend(["", ""])
        tail = []
        if exports is not None:
            tail = ["", "__all__ = %r" % (exports,)]
        text = "\n".join(head + self.lines).rstrip() + "\n" + "\n".join(tail) + ("\n" if tail else "")
        return text


def main(argv):
    if len(argv) != 3:
        print(__doc__)
        return 2
    stubs, out = Path(argv[1]), Path(argv[2])
    version = stubs.parent.name
    modules = {}
    for path in sorted(stubs.glob("*.pyi")):
        if path.stem != "__init__":
            modules[path.stem] = ast.parse(path.read_text(encoding="utf-8"))
    index = Index(modules)
    header = "# Generated by scripts/generate_live.py from the LiveAPI %s stubs. Do not edit." % version
    out.mkdir(parents=True, exist_ok=True)
    for mod, tree in modules.items():
        (out / (mod + ".py")).write_text(ModuleWriter(mod, tree, index).render(header), encoding="utf-8")
    init = [header, "from . import _runtime  # noqa: F401"]
    init += ["from . import %s  # noqa: F401" % m for m in modules]
    init += ["from . import _behaviors  # noqa: F401", "from ._runtime import call_log, reset  # noqa: F401", ""]
    init.append("__all__ = %r" % (sorted(modules) + ["call_log", "reset"],))
    (out / "__init__.py").write_text("\n".join(init) + "\n", encoding="utf-8")
    n_classes = len([1 for (m, q) in index.classes])
    print("generated %d modules, %d classes (stubs %s)" % (len(modules), n_classes, version))
    if index.unresolved:
        print("unresolved types (defaulted to None):")
        for name, count in index.unresolved.most_common():
            print("  %-40s %d" % (name, count))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
