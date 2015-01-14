from docutils.parsers.rst import Directive

from docutils import nodes


class tabpanel(nodes.General, nodes.Element):
    pass


class tabcontent(nodes.General, nodes.Element):
    pass


class tab(nodes.General, nodes.Element):
    pass


class tablink(nodes.General, nodes.Element):
    pass


def visit_html_node(self, node):
    self.body.append(self.starttag(
        node, node['tag'], **node.get('attributes', {})))


def depart_html_node(self, node):
    self.body.append('</%s>\n' % (node['tag'],))


class TabsDirective(Directive):
    """
    Implementation of the C{tabs} directive.
    """

    has_content = True

    def run(self):
        node = tabpanel(attributes={"role": "tabpanel"}, tag='div')
        text = self.content
        self.state.nested_parse(text, self.content_offset, node,
                                match_titles=True)

        self.state.document.settings.record_dependencies.add(__file__)
        return [node]


def process_tab_node(node):
    tab_sections = node.children
    tabs = []
    headers = []
    for child in tab_sections:
        assert isinstance(child, nodes.section)
        assert isinstance(child.children[0], nodes.title)
        title = child.children[0]
        id = child['ids'][0]
        new_tab = tab(child.rawsource, *child.children[1:],
                      tag='div',
                      ids=child['ids'],
                      classes=["tab-pane"],
                      attributes={'role': 'tabpanel'})
        tabs.append(new_tab)
        link = tablink([], *title.children, refid=id,
                       tag='a',
                       attributes={
                           "aria-controls": id,
                           "role": "tab",
                           "data-toggle": "tab",
                           'href': '#' + id,
                           })
        header = nodes.list_item([], link, role="presentation")
        headers.append(header)
    tabs[0]['classes'] += ['active']

    node.children = [
        nodes.bullet_list([], *headers,
                          classes=["nav", "nav-tabs"], role="tablist"),
        tabcontent([], *tabs, tag='div', classes=["tab-content"])
    ]


def process_tab_nodes(app, doctree, fromdocname):

    for node in doctree.traverse(tabpanel):
        process_tab_node(node)


def setup(app):
    """
    Entry point for sphinx extension.
    """
    app.add_directive('tabs', TabsDirective)
    app.add_node(tabpanel,
                 html=(visit_html_node, depart_html_node))
    app.add_node(tabcontent,
                 html=(visit_html_node, depart_html_node))
    app.add_node(tab,
                 html=(visit_html_node, depart_html_node))
    app.add_node(tablink,
                 html=(visit_html_node, depart_html_node))
    app.connect('doctree-resolved', process_tab_nodes)
