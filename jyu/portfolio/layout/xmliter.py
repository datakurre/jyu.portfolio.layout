from lxml import etree, html
from repoze.xmliter.utils import getXMLSerializer

def getHTMLSerializer(iterable, pretty_print=False, encoding=None):
    """Convenience method to create an XMLSerializer instance using the HTML
    parser and string serialization. If the doctype is XHTML or XHTML
    transitional, use the XML serializer.
    """
    serializer = getXMLSerializer(
                        iterable,
                        parser=html.HTMLParser,
                        serializer=html.tostring,
                        pretty_print=pretty_print,
                        encoding=encoding,
                    )
    if serializer.tree.docinfo.doctype and 'XHTML' in serializer.tree.docinfo.doctype:
        # MONKEYPATCH FIXME: etree.tostring breaks <script/>-tags, which contain
        # with CDATA javascript. Don't use etree.tostring, if any found.
        # 
        # The long story:
        # 
        # Some formwidgets on Plone do still use inline javascript, and some of them
        # contain CDATA. Unfortunately, <![CDATA[]]> parsed with html.HTMLParser will
        # break when serialized with etree.tostring. Yet, <![CDATA[]]> must remain
        # commented within <script/> (e.g. //<![CDATA[ or /* <![CDATA[ */), because
        # Plone delivers text/html, not application/xhtml+xml, which is required to
        # properly handle <![CDATA[]]>!
        if len(serializer.tree.xpath("//script[contains(text(), '<![CDATA[')]")) == 0:
            serializer.serializer = etree.tostring

    return serializer