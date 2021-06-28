all:
	xsltproc to-markdown.xsl boardgame-research.rdf > /tmp/contents.md
	cat HEADER.md /tmp/contents.md > README.md
	doctoc README.md