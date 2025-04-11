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
			<xsl:text> </xsl:text>
			
			<!-- Extract year from date using different patterns -->
			<xsl:variable name="fullDate" select="../../*[@rdf:about=current()/@rdf:resource]/dc:date" />
			
			<!-- Try to extract year using different patterns -->
			<xsl:choose>
			    <!-- Match YYYY-MM-DD pattern -->
			    <xsl:when test="string-length($fullDate) >= 4 and string(number(substring($fullDate, 1, 4))) != 'NaN'">
			        <xsl:value-of select="substring($fullDate, 1, 4)"/>
			    </xsl:when>
			    
			    <!-- Match DD.MM.YYYY pattern -->
			    <xsl:when test="string-length($fullDate) >= 10 and contains($fullDate, '.') and string(number(substring($fullDate, string-length($fullDate)-3, 4))) != 'NaN'">
			        <xsl:value-of select="substring($fullDate, string-length($fullDate)-3, 4)"/>
			    </xsl:when>
			    
			    <!-- Match DD/MM/YYYY pattern -->
			    <xsl:when test="string-length($fullDate) >= 10 and contains($fullDate, '/') and string(number(substring($fullDate, string-length($fullDate)-3, 4))) != 'NaN'">
			        <xsl:value-of select="substring($fullDate, string-length($fullDate)-3, 4)"/>
			    </xsl:when>
			    
			    <!-- Match MM/YYYY pattern -->
			    <xsl:when test="string-length($fullDate) >= 7 and contains($fullDate, '/') and string(number(substring-after($fullDate, '/'))) != 'NaN'">
			        <xsl:value-of select="substring-after($fullDate, '/')"/>
			    </xsl:when>
			    
			    <!-- Match "Month YYYY" or "Month DD, YYYY" pattern -->
			    <xsl:when test="contains($fullDate, ',')">
			        <xsl:value-of select="normalize-space(substring-after($fullDate, ','))"/>
			    </xsl:when>
			    
			    <!-- Match "Month YYYY" without comma -->
			    <xsl:when test="string-length($fullDate) >= 4">
			        <!-- Look for the last 4 digits that could be a year -->
			        <xsl:variable name="lastFour" select="substring($fullDate, string-length($fullDate)-3, 4)"/>
			        <xsl:choose>
			            <xsl:when test="string(number($lastFour)) != 'NaN'">
			                <xsl:value-of select="$lastFour"/>
			            </xsl:when>
			            <xsl:otherwise>
			                <xsl:value-of select="$fullDate"/>
			            </xsl:otherwise>
			        </xsl:choose>
			    </xsl:when>
			    
			    <!-- Fallback to original date if no pattern matches -->
			    <xsl:otherwise>
			        <xsl:value-of select="$fullDate"/>
			    </xsl:otherwise>
			</xsl:choose>
			
			<xsl:text>)</xsl:text>
		</xsl:for-each>
	</xsl:for-each>
</xsl:template>
</xsl:stylesheet>