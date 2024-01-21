import json
import os
import sys
from typing import Any

from anki.collection import SearchNode
from aqt import dialogs, gui_hooks, mw
from aqt.overview import Overview, OverviewContent
from aqt.qt import *
from bs4 import BeautifulSoup

sys.path.append(os.path.join(os.path.dirname(__file__), "vendor"))

from .consts import consts


def on_overview_will_render_content(
    overview: Overview, content: OverviewContent
) -> None:
    deck = mw.col.decks.by_name(content.deck)
    if not deck["dyn"]:
        return
    terms = [term[0] for term in deck["terms"] if term[0]]
    node = mw.col.group_searches(*terms, joiner="OR")
    excluded_nodes = (
        SearchNode(card_state=SearchNode.CARD_STATE_SUSPENDED),
        SearchNode(card_state=SearchNode.CARD_STATE_BURIED),
        mw.col.group_searches(
            SearchNode(deck="filtered"),
            SearchNode(negated=SearchNode(deck=deck["name"])),
        ),
    )
    search = mw.col.build_search_string(
        node, SearchNode(negated=mw.col.group_searches(*excluded_nodes, joiner="OR"))
    )
    cids = mw.col.find_cards(search)
    soup = BeautifulSoup(content.table, "html.parser")
    tr = soup.new_tag("tr")
    td1 = soup.new_tag("td")
    td1.append("Total matched:")
    tr.append(td1)
    td2 = soup.new_tag("td")
    a = soup.new_tag("a")
    a[
        "href"
    ] = f'javascript:void(pycmd("{consts.module}:browse:" + {json.dumps(search)}))'
    a.append(str(len(cids)))
    b = soup.new_tag("b")
    b.append(a)
    td2.append(b)
    tr.append(td2)
    table = soup.select_one("table table")
    table.append(tr)
    content.table = soup.decode()


def on_webview_did_receive_js_message(
    handled: tuple[bool, Any], message: str, context: Any
) -> tuple[bool, Any]:
    if not message.startswith(f"{consts.module}:"):
        return handled
    _, cmd, search = message.split(":", maxsplit=2)
    if cmd == "browse":
        dialogs.open("Browser", mw, search=(search,))

    return (True, None)


gui_hooks.overview_will_render_content.append(on_overview_will_render_content)
gui_hooks.webview_did_receive_js_message.append(on_webview_did_receive_js_message)
