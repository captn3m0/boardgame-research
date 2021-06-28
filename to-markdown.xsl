<?xml version = "1.0" encoding = "UTF-8"?>
<xsl:stylesheet version = "1.0" 
xmlns:xsl = "http://www.w3.org/1999/XSL/Transform"
xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
xmlns:z="http://www.zotero.org/namespaces/export#"
xmlns:dcterms="http://purl.org/dc/terms/"
xmlns:dc="http://purl.org/dc/elements/1.1/"
xmlns:bib="http://purl.org/net/biblio#"
xmlns:vcard="http://nwalsh.com/rdf/vCard#"
xmlns:foaf="http://xmlns.com/foaf/0.1/"
xmlns:link="http://purl.org/rss/1.0/modules/link/"
xmlns:prism="http://prismstandard.org/namespaces/1.2/basic/"
>
<xsl:output method="text" 
	omit-xml-declaration = "yes"
	standalone="yes"
	indent="no"
/>

<xsl:template match = "/">
	<!-- <xsl:text>**Table of Contents**</xsl:text> -->

	<xsl:for-each select="rdf:RDF/z:Collection">
		<xsl:text>&#10;&#10;# </xsl:text><xsl:value-of select = "dc:title"/>
		<!-- Newline -->
		<xsl:for-each select="dcterms:hasPart">
			<xsl:text>&#10;- [</xsl:text>
			<xsl:value-of select="../../*[@rdf:about=current()/@rdf:resource]/dc:title" />
			<xsl:text>](</xsl:text>
			<xsl:value-of select="../../*[@rdf:about=current()/@rdf:resource]//dcterms:URI/rdf:value" />
			<xsl:text>) (</xsl:text>
			<xsl:value-of select="../../*[@rdf:about=current()/@rdf:resource]/z:itemType" />
			<xsl:text>)</xsl:text>
			<!-- <xsl:text>&#10;</xsl:text> -->
		</xsl:for-each>
	</xsl:for-each>

</xsl:template>
</xsl:stylesheet>


