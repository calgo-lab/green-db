import re
from html import escape
from typing import Any, Iterable, List, Optional, Tuple, get_type_hints

from markdown_it import MarkdownIt
from mdit_py_plugins.attrs import attrs_plugin

md = MarkdownIt().enable("table").use(attrs_plugin)
container_pattern = re.compile(r":([:]+)(.*)$", flags=re.MULTILINE)
seperator_pattern = re.compile(r"([#.])")


def render_markdown(txt: str) -> str:
    return md.render(txt)


def render_element(element: Any, **kwargs: Any) -> str:
    return element if isinstance(element, str) else element.render(**kwargs)


def render_elements(elements: list, **kwargs: Any) -> str:
    return "".join(render_element(element, **kwargs) for element in elements)


def render_tag(
    tag: str, id: Optional[str], cls: List[str], contents: str, attr: List[str] = []
) -> str:
    params = [escape(tag, False), *attr]
    if id:
        params.append(f'id="{escape(id)}"')
    if cls:
        params.append(f'class="{" ".join(map(escape, cls))}"')
    return f'<{" ".join(params)}>{contents}</{params[0]}>'


class Element:
    def __init__(
        self, parent: Any, level: int, html_tag: str, css_id: Optional[str], css_class: List[str]
    ):
        self.html_tag, self.css_id, self.css_class = html_tag, css_id, []
        attrs = get_type_hints(type(self))
        for cls in css_class:
            if "=" in cls:
                name, value = cls.split("=", 1)
                if name in attrs:
                    setattr(self, name, attrs[name](value))
                    continue
            self.css_class.append(cls)
        self.children: list = []
        self.level = level
        self.parent = parent.add_child(self)

    def on_close_parent(self) -> None:
        """gets called before the parent of `self` closes"""

    def on_add_to_parent(self, parent: Any) -> None:
        """gets called before `self` is added to `parent`"""

    def open(self) -> Any:
        return self

    def add_child(self, child: Any) -> Any:
        if hasattr(child, "on_add_to_parent"):
            child.on_add_to_parent(self)
        self.children.append(child)
        return self

    def close(self) -> Any:
        for child in self.children:
            if hasattr(child, "on_close_parent"):
                child.on_close_parent()
        return self.parent

    def render(self, **kwargs: Any) -> str:
        contents = render_elements(self.children, **kwargs)
        return render_tag(self.html_tag, self.css_id, self.css_class, contents)


class Document(Element):
    html_tag = "body"
    css_id = None
    css_class = []
    children = []
    parent = None
    level = 0

    def __init__(self, metadata: str):
        self.metadata = metadata


def close(parent: Any, level: int = 0) -> Any:
    while parent and parent.level >= level:
        parent = parent.close()
    return parent


def parse_rules(rules: str) -> Iterable[Tuple[str, Optional[str], List[str]]]:
    for rule in rules.split():
        segments = re.split(seperator_pattern, rule)
        html_tag = segments[0] or "div"
        seps = segments[1::2]
        keys = segments[2::2]
        css_ids = [key for sep, key in zip(seps, keys) if key and sep == "#"]
        css_class = [key for sep, key in zip(seps, keys) if key and sep == "."]
        yield html_tag, css_ids[-1] if css_ids else None, css_class


def parse_page(txt: str, element_map: dict = {}) -> Document:
    segments = re.split(container_pattern, txt)
    metadata = segments[0]
    colons = segments[1::3]
    rules = segments[2::3]
    texts = segments[3::3]
    result = Document(metadata)
    document = result.open()
    for colon, rule, markdown in zip(colons, rules, texts):
        document = close(document, len(colon))
        for html_tag, css_id, css_class in parse_rules(rule):
            element = element_map.get(html_tag, Element)
            document = element(document, len(colon), html_tag, css_id, css_class)
            document = document.open()
        if output := render_markdown(markdown):
            document = document.add_child(output)
    close(document)
    return result


def render_page(txt: str, element_map: dict = {}) -> str:
    return parse_page(txt, element_map).render()
