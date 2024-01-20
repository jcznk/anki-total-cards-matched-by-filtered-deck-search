import os
import sys

from anki.collection import SearchNode
from aqt import gui_hooks, mw
from aqt.overview import Overview, OverviewContent
from aqt.qt import *
from bs4 import BeautifulSoup

sys.path.append(os.path.join(os.path.dirname(__file__), "vendor"))


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
        node, SearchNode(negated=mw.col.group_searches(*excluded_nodes))
    )
    cids = mw.col.find_cards(search)
    soup = BeautifulSoup(content.table, "html.parser")
    tr = soup.new_tag("tr")
    td1 = soup.new_tag("td")
    td1.append("Total matched:")
    tr.append(td1)
    td2 = soup.new_tag("td")
    b = soup.new_tag("b")
    b.append(str(len(cids)))
    td2.append(b)
    tr.append(td2)
    table = soup.select_one("table table")
    table.append(tr)
    content.table = table.decode()


gui_hooks.overview_will_render_content.append(on_overview_will_render_content)
