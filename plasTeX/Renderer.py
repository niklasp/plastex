#!/usr/bin/env python

import re
from Utils import *
from imagers.dvi2bitmap import DVI2Bitmap
from imagers.dvipng import DVIPNG

class Renderer(dict):
    def __init__(self, data={}):
        dict.__init__(self, data)
        self.imager = DVIPNG()
#       self.imager = DVI2Bitmap()


class RenderMixIn(object):
    """
    MixIn class to make macros renderable

    """

    renderer = None

    def toXML(self):
        """ 
        Dump the object as XML 

        Returns:
        string in XML format

        """
        # Only the content of DocumentFragments get rendered
        if isinstance(self, list):
            s = []
            for value in self:
                if hasattr(value, 'toXML'):
                    value = value.toXML()
                s.append('%s' % value)
            return ''.join(s)

        # Remap name into valid XML tag name
        name = self.nodeName
        name = name.replace('@','-')

        modifier = re.search(r'(\W*)$', name).group(1)
        if modifier:
            name = re.sub(r'(\W*)$', r'', name)
            modifier = ' modifier="%s"' % xmlstr(modifier)

        if not name:
            name = 'unknown'

        source = ''
#       if self._source.start is not None and self._source.end is not None:
#           source = ' source="%s,%s"' % (self._source.start, self._source.end)
#       if self._position:
            #source = ' source="%s,%s"' % (self._position[0], self._position[1])
#           source = ' source="%s"' % xmlstr(self.source)

        # Bail out early if the element is empty
        if not(self.attributes) and not(self.children):
            return '<%s%s%s/>' % (name, modifier, source)

        s = ['<%s%s%s>\n' % (name, modifier, source)]
            
        # Render attributes
        if self.attributes:
#           s.append('<args>\n')
            for key, value in self.attributes.items():
                if value is None:
                    s.append('    <plastex:arg name="%s"/>\n' % key)
                else:
                    if hasattr(value, 'toXML'):
                        value = value.toXML()
                    else:
                        value = xmlstr(value)
                    s.append('    <plastex:arg name="%s">%s</plastex:arg>\n' % (key, value))
#           s.append('</args>\n')

        # Render content
        if self.children:
#           s.append('<content>')
            for value in self.children:
                if hasattr(value, 'toXML'):
                    value = value.toXML()
                else: 
                    value = xmlstr(value)
                s.append(value)
#           s.append('</content>\n')
        s.append('</%s>' % name)
        return ''.join(s)
        
    def render(self, renderer=None, file=None):
        """ 
        Render the macro 

        Keyword Arguments:
        renderer -- rendering callable to use instead of the
            one supplied by the macro itself
        file -- file write to

        Returns:
        rendered output -- if no file was specified
        nothing -- if a file was specified

        """
        # Get filename to use
        if file is None:
            file = type(self).context.renderer.filename(self)

        if file is not None:
            status.info(' [%s' % file)

        # If we have a renderer, use it
        if renderer is not None:
            output = renderer(self)

        # Use renderer associated with class
        elif type(self).renderer is not None:
            output = type(self).renderer(self)

        # No renderer, just make something up
        else:
            output = '%s' % self
#           output = ''.join([str(x) for x in self])
#           if type(self) is not TeXFragment:
#               name = re.sub(r'\W', 'W', self.tagName)
#               output = '<%s>%s</%s>' % (name, output, name)

        # Write to given file
        if file is not None:
            if hasattr(file, 'write'):
                file.write(output)
            else:
                open(file,'w').write(output)
            status.info(']')
            return ''

        # No files, just return the output
        else:
            return output

    def __str__(self):
        s = []
        for child in self.children:
            if isinstance(child, basestring):
                s.append(child)
            else:
                s.append(child.render())
        return ''.join(s)

    __repr__ = __str__
