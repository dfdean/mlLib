################################################################################
# 
# Copyright (c) 2020 Dawson Dean
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
from xml.dom import minidom




################################################################################
#
# [XMLTools_GetElementName]
#
################################################################################
def XMLTools_GetElementName(node):
    #print("XMLTools_GetElementName.")
    if (not node):
        return("")
    if (node.nodeType != xml.dom.Node.ELEMENT_NODE): 
        return("")

    return(node.tagName)
# XMLTools_GetElementName





################################################################################
#
# [XMLTools_GetChildNode]
#
################################################################################
def XMLTools_GetChildNode(parentNode, childName):
    #print("XMLTools_GetChildNode.  childName = " + str(childName))
    if ((not parentNode) or (not childName)):
        return(None)

    # Normalize everything to lower case, so we can have a case-insensitive comparison.
    childName = childName.lower()

    for childNode in parentNode.childNodes:
        #print("Examine one child.")
        #print("childNode.nodeType = " + str(childNode.nodeType))
        if (childNode.nodeType == xml.dom.Node.ELEMENT_NODE): 
            #print("childNode.tagName = " + str(childNode.tagName))
            if (childNode.tagName.lower() == childName):
                return(childNode)

    return(None)
# XMLTools_GetChildNode







################################################################################
#
# [XMLTools_GetFirstChildNode]
#
################################################################################
def XMLTools_GetFirstChildNode(parentNode):
    #print("XMLTools_GetFirstChildNode.")
    if (not parentNode):
        return(None)

    for childNode in parentNode.childNodes:
        #print("Examine one child.")
        #print("childNode.nodeType = " + str(childNode.nodeType))
        if (childNode.nodeType == xml.dom.Node.ELEMENT_NODE): 
            return(childNode)

    return(None)
# XMLTools_GetFirstChildNode






################################################################################
#
# [XMLTools_GetLastChildNode]
#
################################################################################
def XMLTools_GetLastChildNode(parentNode):
    resultNode = None

    #print("XMLTools_GetLastChildNode.")
    if (not parentNode):
        return(None)

    for childNode in parentNode.childNodes:
        #print("Examine one child.")
        #print("childNode.nodeType = " + str(childNode.nodeType))
        if (childNode.nodeType == xml.dom.Node.ELEMENT_NODE): 
            resultNode = childNode

    return(resultNode)
# XMLTools_GetLastChildNode





################################################################################
#
# [XMLTools_GetPeerNode]
#
################################################################################
def XMLTools_GetPeerNode(startNode, peerName):
    if ((not startNode) or (not peerName)):
        return(None)

    # Normalize everything to lower case, so we can have a case-insensitive comparison.
    peerName = peerName.lower()

    peerElement = startNode.nextSibling
    while (peerElement):
        # Look further at elements of type html-object/tag
        if (peerElement.nodeType == xml.dom.Node.ELEMENT_NODE):
            if (peerElement.tagName.lower() == peerName):
                return(peerElement)

        peerElement = peerElement.nextSibling
    # while (peerElement)

    return(None)
# XMLTools_GetPeerNode





################################################################################
#
# [XMLTools_GetAnyPeerNode]
#
################################################################################
def XMLTools_GetAnyPeerNode(startNode):
    if ((not startNode)):
        return(None)

    peerElement = startNode.nextSibling
    while (peerElement):
        # Look further at elements of type html-object/tag
        if (peerElement.nodeType == xml.dom.Node.ELEMENT_NODE):
            return(peerElement)

        peerElement = peerElement.nextSibling
    # while (peerElement)

    return(None)
# XMLTools_GetAnyPeerNode





################################################################################
#
# [XMLTools_GetAnyPrevPeerNode]
#
################################################################################
def XMLTools_GetAnyPrevPeerNode(startNode):
    if (not startNode):
        return(None)

    peerElement = startNode.previousSibling
    while (peerElement):
        # Look further at elements of type html-object/tag
        if (peerElement.nodeType == xml.dom.Node.ELEMENT_NODE):
            return(peerElement)

        peerElement = peerElement.previousSibling
    # while (peerElement)

    return(None)
# XMLTools_GetAnyPrevPeerNode





################################################################################
#
# [XMLTools_GetAncestorNode]
#
################################################################################
def XMLTools_GetAncestorNode(childNode, ancestorName):
    if ((not childNode) or (not ancestorName)):
        return(None)

    # Normalize everything to lower case, so we can have a case-insensitive comparison.
    ancestorName = ancestorName.lower()

    parentNode = childNode.parentNode
    while (parentNode):
        #LogEvent("XMLTools_GetAncestorNode. parentNode.nodeType=" + parentNode.nodeType);
        # Look further at elements of type html-object/tag
        if (parentNode.nodeType == xml.dom.Node.ELEMENT_NODE):
            if (parentNode.tagName.lower() == ancestorName):
                return(parentNode)

        parentNode = parentNode.parentNode
    # while (parentNode)

    return(None)
# XMLTools_GetAncestorNode






################################################################################
#
# [XMLTools_GetTextContents]
#
################################################################################
def XMLTools_GetTextContents(parentNode):
    #print("XMLTools_GetTextContents")

    if (parentNode is None):
        print("XMLTools_GetTextContents. ERROR!. parentNode == None")
        return("")

    resultBytes = ""
    currentNode = parentNode.firstChild;
    while (currentNode):
        # LogEvent("XMLTools_GetTextContents.currentNode.nodeType=" + currentNode.nodeType)
        if (currentNode.nodeType == 3):
            #LogEvent("XMLTools_GetTextContents. currentNode.nodeValue=" + currentNode.nodeValue)
            resultBytes = resultBytes + currentNode.nodeValue
        # End - if (currentNode.nodeType == 3)

        currentNode = currentNode.nextSibling
    # while (currentNode)

    #print("XMLTools_GetTextContents. raw resultBytes=" + resultBytes)

    # Convert any Unicode string to UTF-8
    resultStr = resultBytes
    # resultBytes.decode('utf-8')

    #print("XMLTools_GetTextContents. resultStr=" + resultStr)
    return(resultStr)
# End - XMLTools_GetTextContents






################################################################################
#
# [XMLTools_SetTextContents]
#
################################################################################
def XMLTools_SetTextContents(parentNode, str):
    if (parentNode):
        XMLTools_RemoveAllChildNodes(parentNode)
        textNode = parentNode.ownerDocument.createTextNode(str)
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
# [XMLTools_GetOrCreateChildNode]
#
################################################################################
def XMLTools_GetOrCreateChildNode(parentNode, childName):
    #print("XMLTools_GetOrCreateChildNode.  childName = " + str(childName))
    if ((not parentNode) or (not childName)):
        return(None)

    childNode = XMLTools_GetChildNode(parentNode, childName)
    if (None == childNode):
        childNode = parentNode.ownerDocument.createElement(childName)
        parentNode.appendChild(childNode)

    return(childNode)
# XMLTools_GetOrCreateChildNode






################################################################################
#
# [XMLTools_AddChildNodeWithText]
#
################################################################################
def XMLTools_AddChildNodeWithText(parentNode, childName, textStr):
    childNode = XMLTools_GetOrCreateChildNode(parentNode, childName)
    if (None == childNode):
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
    if (None == childNode):
        return("")

    textStr = XMLTools_GetTextContents(childNode)
    return(textStr)
# XMLTools_GetChildNodeText






################################################################################
#
# [XMLTools_AddChildNodeWithArrayText]
#
################################################################################
def XMLTools_AddChildNodeWithArrayText(parentNode, childName, valArray):
    arrayStr = ""
    for value in valArray:
        arrayStr = arrayStr + str(value) + ","
    arrayStr = arrayStr[:-1]

    XMLTools_AddChildNodeWithText(parentNode, childName, arrayStr)
# End - XMLTools_AddChildNodeWithArrayText






################################################################################
#
# [XMLTools_GetChildNodeArray]
#
################################################################################
def XMLTools_GetChildNodeArray(parentNode, childName):
    arrayStr = XMLTools_GetChildNodeText(parentNode, childName)
    valStrArray = arrayStr.split(',')
    
    valueArray = []
    for valStr in valStrArray:
        valueArray.append(float(valStr))

    return valueArray
# End - XMLTools_GetChildNodeArray







################################################################################
# Test Code
################################################################################
#print("XML Done!")



