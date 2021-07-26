all:
	xsltproc to-markdown.xsl boardgame-research.rdf > /tmp/contents.md
	cat HEADER.md /tmp/contents.md FOOTER.md > README.md
	doctoc README.md