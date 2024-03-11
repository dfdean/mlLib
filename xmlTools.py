################################################################################
# 
# Copyright (c) 2020-2024 Dawson Dean
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
################################################################################
#
# XML Tools
# These are tools for manipulating an XML file. They are similar to an XML
# library for Javascript.
################################################################################

import xml.dom
import xml.dom.minidom
from xml.dom.minidom import parseString



################################################################################
#
# [XMLTools_ParseStringToDOM]
#
################################################################################
def XMLTools_ParseStringToDOM(xmlStr):
    try:
        domObj = parseString(xmlStr)
    except xml.parsers.expat.ExpatError as err:
        print("XMLTools_ParseStringToDOM. Error from parsing string:")
        print("ExpatError:" + str(err))
        print("xmlStr=[" + xmlStr + "]")
        domObj = None
    except Exception:
        print("XMLTools_ParseStringToDOM. Error from parsing string:")
        print("xmlStr=[" + xmlStr + "]")
        domObj = None

    return domObj
# XMLTools_ParseStringToDOM




################################################################################
#
# [XMLTools_GetNamedElementInDocument]
#
################################################################################
def XMLTools_GetNamedElementInDocument(documentObj, nodeName):
    try:
        elementNode = documentObj.getElementsByTagName(nodeName)[0]
    except Exception:
        print("XMLTools_GetNamedElementInDocument. Required elements are missing: [" + nodeName + "]")
        elementNode = None

    return elementNode
# XMLTools_GetNamedElementInDocument






################################################################################
#
# [XMLTools_GetElementName]
#
################################################################################
def XMLTools_GetElementName(node):
    if (not node):
        return ""
    if (node.nodeType != xml.dom.Node.ELEMENT_NODE): 
        return ""

    return node.tagName
# XMLTools_GetElementName





################################################################################
#
# [XMLTools_GetChildNode]
#
################################################################################
def XMLTools_GetChildNode(parentNode, childName):
    if ((not parentNode) or (not childName)):
        return None

    # Normalize everything to lower case, so we can have a case-insensitive comparison.
    childName = childName.lower()

    for childNode in parentNode.childNodes:
        if (childNode.nodeType == xml.dom.Node.ELEMENT_NODE): 
            if (childNode.tagName.lower() == childName):
                return childNode

    return None
# XMLTools_GetChildNode





################################################################################
#
# [XMLTools_IsLeafNode]
#
################################################################################
def XMLTools_IsLeafNode(parentNode):
    if (not parentNode):
        return False

    for childNode in parentNode.childNodes:
        if (childNode.nodeType == xml.dom.Node.ELEMENT_NODE): 
            return False

    return True
# XMLTools_IsLeafNode





################################################################################
#
# [XMLTools_GetFirstChildNode]
#
################################################################################
def XMLTools_GetFirstChildNode(parentNode):
    if (not parentNode):
        return None

    for childNode in parentNode.childNodes:
        if (childNode.nodeType == xml.dom.Node.ELEMENT_NODE): 
            return childNode

    return None
# XMLTools_GetFirstChildNode





################################################################################
#
# [XMLTools_GetLastChildNode]
#
################################################################################
def XMLTools_GetLastChildNode(parentNode):
    resultNode = None

    if (not parentNode):
        return None

    for childNode in parentNode.childNodes:
        if (childNode.nodeType == xml.dom.Node.ELEMENT_NODE): 
            resultNode = childNode

    return resultNode
# XMLTools_GetLastChildNode





################################################################################
#
# [XMLTools_GetPeerNode]
#
################################################################################
def XMLTools_GetPeerNode(startNode, peerName):
    if ((not startNode) or (not peerName)):
        return None

    # Normalize everything to lower case, so we can have a case-insensitive comparison.
    peerName = peerName.lower()

    peerElement = startNode.nextSibling
    while (peerElement):
        # Look further at elements of type html-object/tag
        if (peerElement.nodeType == xml.dom.Node.ELEMENT_NODE):
            if (peerElement.tagName.lower() == peerName):
                return peerElement

        peerElement = peerElement.nextSibling
    # while (peerElement)

    return None
# XMLTools_GetPeerNode




################################################################################
#
# [XMLTools_GetAnyPeerNode]
#
################################################################################
def XMLTools_GetAnyPeerNode(startNode):
    if ((not startNode)):
        return None

    peerElement = startNode.nextSibling
    while (peerElement):
        # Look further at elements of type html-object/tag
        if (peerElement.nodeType == xml.dom.Node.ELEMENT_NODE):
            return peerElement

        peerElement = peerElement.nextSibling
    # while (peerElement)

    return None
# XMLTools_GetAnyPeerNode





################################################################################
#
# [XMLTools_GetAnyPrevPeerNode]
#
################################################################################
def XMLTools_GetAnyPrevPeerNode(startNode):
    if (not startNode):
        return None

    peerElement = startNode.previousSibling
    while (peerElement):
        # Look further at elements of type html-object/tag
        if (peerElement.nodeType == xml.dom.Node.ELEMENT_NODE):
            return peerElement

        peerElement = peerElement.previousSibling
    # while (peerElement)

    return None
# XMLTools_GetAnyPrevPeerNode





################################################################################
#
# [XMLTools_GetAncestorNode]
#
################################################################################
def XMLTools_GetAncestorNode(childNode, ancestorName):
    if ((not childNode) or (not ancestorName)):
        return None

    # Normalize everything to lower case, so we can have a case-insensitive comparison.
    ancestorName = ancestorName.lower()

    parentNode = childNode.parentNode
    while (parentNode):
        # Look further at elements of type html-object/tag
        if (parentNode.nodeType == xml.dom.Node.ELEMENT_NODE):
            if (parentNode.tagName.lower() == ancestorName):
                return parentNode

        parentNode = parentNode.parentNode
    # while (parentNode)

    return None
# XMLTools_GetAncestorNode






################################################################################
#
# [XMLTools_GetTextContents]
#
################################################################################
def XMLTools_GetTextContents(parentNode):
    if (parentNode is None):
        return ""

    resultBytes = ""
    currentNode = parentNode.firstChild
    while (currentNode):
        if (currentNode.nodeType == 3):
            resultBytes = resultBytes + currentNode.nodeValue
        # End - if (currentNode.nodeType == 3)

        currentNode = currentNode.nextSibling
    # while (currentNode)

    # Convert any Unicode string to UTF-8
    resultStr = resultBytes
    # resultBytes.decode('utf-8')

    return resultStr
# End - XMLTools_GetTextContents





################################################################################
#
# [XMLTools_SetTextContents]
#
################################################################################
def XMLTools_SetTextContents(parentNode, contentsStr):
    if (parentNode):
        XMLTools_RemoveAllChildNodes(parentNode)
        textNode = parentNode.ownerDocument.createTextNode(contentsStr)
        parentNode.appendChild(textNode)
# End - XMLTools_SetTextContents





################################################################################
#
# [XMLTools_RemoveAllChildNodes]
#
################################################################################
def XMLTools_RemoveAllChildNodes(parentNode):
    if (not parentNode):
        return

    childElement = parentNode.firstChild
    while (childElement):
        nextChildElement = childElement.nextSibling
        parentNode.removeChild(childElement)
        childElement = nextChildElement
    # End - while (childElement)
# End - XMLTools_RemoveAllChildNodes






################################################################################
#
# [XMLTools_RemoveAllWhitespace]
#
################################################################################
def XMLTools_RemoveAllWhitespace(parentNode):
    if (parentNode is None):
        return

    childElement = parentNode.firstChild
    while (childElement):
        nextChildElement = childElement.nextSibling

        if (childElement.nodeType == 3):
            textStr = childElement.nodeValue
            if(textStr.lstrip() == ""):
                parentNode.removeChild(childElement)
        else:
            XMLTools_RemoveAllWhitespace(childElement)
        # End - if (childElement.nodeType == 3)

        childElement = nextChildElement
    # End - while (childElement)
# End - XMLTools_RemoveAllWhitespace





################################################################################
#
# [XMLTools_GetOrCreateChildNode]
#
################################################################################
def XMLTools_GetOrCreateChildNode(parentNode, childName):
    if ((not parentNode) or (not childName)):
        return None

    childNode = XMLTools_GetChildNode(parentNode, childName)
    if (childNode is None):
        childNode = parentNode.ownerDocument.createElement(childName)
        parentNode.appendChild(childNode)

    return childNode
# XMLTools_GetOrCreateChildNode





################################################################################
#
# [XMLTools_AppendNewChildNode]
#
################################################################################
def XMLTools_AppendNewChildNode(parentNode, childName):
    if ((not parentNode) or (not childName)):
        return None

    childNode = parentNode.ownerDocument.createElement(childName)
    parentNode.appendChild(childNode)

    return childNode
# XMLTools_AppendNewChildNode





################################################################################
#
# [XMLTools_SetAttribute]
#
################################################################################
def XMLTools_SetAttribute(elementNode, attrName, attrValue):
    if ((not elementNode) or (not attrName) or (not attrValue)):
        return

    # Remove old attrs with this name
    try:
        elementNode.removeAttribute(attrName)
    except Exception:
        pass

    attrNode = elementNode.ownerDocument.createAttribute(attrName)
    attrNode.value = attrValue
    elementNode.setAttributeNode(attrNode)
# XMLTools_SetAttribute




################################################################################
#
# [XMLTools_GetAttribute]
#
################################################################################
def XMLTools_GetAttribute(elementNode, attrName):
    if ((not elementNode) or (not attrName)):
        return ""

    resultStr = elementNode.getAttribute(attrName)
    if (resultStr is None):
        resultStr = ""

    return resultStr
# XMLTools_GetAttribute



################################################################################
#
# [XMLTools_AddChildNodeWithText]
#
################################################################################
def XMLTools_AddChildNodeWithText(parentNode, childName, textStr):
    childNode = XMLTools_GetOrCreateChildNode(parentNode, childName)
    if (childNode is None):
        return

    XMLTools_SetTextContents(childNode, textStr)
# XMLTools_AddChildNodeWithText




################################################################################
#
# [XMLTools_GetChildNodeText]
#
################################################################################
def XMLTools_GetChildNodeText(parentNode, childName):
    childNode = XMLTools_GetChildNode(parentNode, childName)
    if (childNode is None):
        return ""

    textStr = XMLTools_GetTextContents(childNode)
    return textStr
# XMLTools_GetChildNodeText




################################################################################
#
# [XMLTools_GetChildNodeTextAsStr]
#
################################################################################
def XMLTools_GetChildNodeTextAsStr(parentNode, childName, defaultStr):
    childNode = XMLTools_GetChildNode(parentNode, childName)
    if (childNode is None):
        return defaultStr

    textStr = XMLTools_GetTextContents(childNode)
    textStr = textStr.lstrip()

    return textStr
# XMLTools_GetChildNodeTextAsStr




################################################################################
#
# [XMLTools_GetChildNodeTextAsInt]
#
################################################################################
def XMLTools_GetChildNodeTextAsInt(parentNode, childName, defaultVal):
    childNode = XMLTools_GetChildNode(parentNode, childName)
    if (childNode is None):
        return defaultVal

    textStr = XMLTools_GetTextContents(childNode)
    if ((textStr is None) or (textStr == "")):
        return defaultVal

    textStr = textStr.lstrip()
    if ((textStr is None) or (textStr == "")):
        return defaultVal

    try:
        resultInt = int(textStr)
        return resultInt
    except Exception:
        return defaultVal
# XMLTools_GetChildNodeTextAsInt




################################################################################
#
# [XMLTools_GetChildNodeTextAsFloat]
#
################################################################################
def XMLTools_GetChildNodeTextAsFloat(parentNode, childName, defaultVal):
    childNode = XMLTools_GetChildNode(parentNode, childName)
    if (childNode is None):
        return defaultVal

    textStr = XMLTools_GetTextContents(childNode)
    textStr = textStr.lstrip()

    try:
        resultFloat = float(textStr)
        return resultFloat
    except Exception:
        pass

    try:
        resultInt = int(textStr)
        resultFloat = float(resultInt)
        return resultFloat
    except Exception:
        return defaultVal
# XMLTools_GetChildNodeTextAsFloat




################################################################################
#
# [XMLTools_GetChildNodeTextAsBool]
#
################################################################################
def XMLTools_GetChildNodeTextAsBool(parentNode, childName, defaultVal):
    childNode = XMLTools_GetChildNode(parentNode, childName)
    if (childNode is None):
        return defaultVal

    textStr = XMLTools_GetTextContents(childNode)
    textStr = textStr.lower().lstrip().rstrip()

    # We don't know what default is, so explicitly test for True and False.
    if (textStr in ("true", "1", "yes")):
        return True
    if (textStr in ("false", "0", "no")):
        return False

    return defaultVal
# XMLTools_GetChildNodeTextAsBool




################################################################################
#
# [XMLTools_SetChildNodeTextAsBool]
#
################################################################################
def XMLTools_SetChildNodeTextAsBool(parentNode, childName, fValue):
    childNode = XMLTools_GetChildNode(parentNode, childName)
    if (childNode is None):
        return

    if (fValue):
        fValueStr = "true"
    else:
        fValueStr = "false"
    XMLTools_SetTextContents(childNode, fValueStr)
# XMLTools_SetChildNodeTextAsBool



################################################################################
#
# [XMLTools_SetChildNodeWithNumber]
#
################################################################################
def XMLTools_SetChildNodeWithNumber(parentNode, childName, newVal):
    childNode = XMLTools_GetChildNode(parentNode, childName)
    if (childNode is None):
        return

    XMLTools_SetTextContents(childNode, str(newVal))
# XMLTools_SetChildNodeWithNumber




#####################################################
#
# [XMLTools_GetChildNodeFromPath
#
#####################################################
def XMLTools_GetChildNodeFromPath(rootXMLNode, pathName):
    pathNameList = pathName.split("/")
    currentXMLNode = rootXMLNode
    for component in pathNameList:
        currentXMLNode = XMLTools_GetChildNode(currentXMLNode, component)
        if (currentXMLNode is None):
            return None
    # End - for component in pathNameList:

    return currentXMLNode
# End XMLTools_GetChildNodeFromPath


