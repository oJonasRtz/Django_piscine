#!/usr/bin/python3


class Text(str):
    """
    A Text class to represent a text you could use with your HTML elements.

    Because directly using str class was too mainstream.
    """

    def __str__(self):
        s = super().__str__()
        
        #Escaping
        s = s.replace('<', '&lt;') \
            .replace('>', '&gt;') \
            .replace('"', '&quot;') \
            .replace("'", '&apos;')        
        #break lines
        s = s.replace('\n', '\n<br />\n')
                
        return s


class Elem:
    """
    Elem will permit us to represent our HTML elements.
    """
    class ValidationError(Exception):
        def __init__(self):
            super().__init__("ERROR")

    def __init__(self, tag='div', attr={}, content=None, tag_type='double'):
        self.tag = tag
        self.attr = attr
        self.content = []
        self.tag_type = tag_type

        if content is not None:
            self.add_content(content)

    def __str__(self):
        """
        The __str__() method will permit us to make a plain HTML representation
        of our elements.
        Make sure it renders everything (tag, attributes, embedded
        elements...).
        """
        attrs = self.__make_attr()
        
        if self.tag_type == 'double':
            content = self.__make_content()
            if content:
                return f"<{self.tag}{attrs}>{content}</{self.tag}>"
            return f"<{self.tag}{attrs}></{self.tag}>"
        elif self.tag_type == 'simple':
            return f"<{self.tag}{attrs} />"
        
        raise Elem.ValidationError

    def __make_attr(self):
        """
        Here is a function to render our elements attributes.
        """
        result = ''
        for pair in sorted(self.attr.items()):
            result += ' ' + str(pair[0]) + '="' + str(pair[1]) + '"'
        return result

    def __make_content(self):
        """
        Here is a method to render the content, including embedded elements.
        """

        if len(self.content) == 0:
            return ''
        result = '\n'
        for elem in self.content:
            lines = str(elem).split('\n')
            for line in lines:
                result += '  ' + line + '\n'
        return result

    def add_content(self, content):
        if not Elem.check_type(content):
            raise Elem.ValidationError
        if type(content) == list:
            self.content += [elem for elem in content if elem != Text('')]
        elif content != Text(''):
            self.content.append(content)

    @staticmethod
    def check_type(content):
        """
        Is this object a HTML-compatible Text instance or a Elem, or even a
        list of both?
        """
        return (isinstance(content, Elem) or type(content) == Text or
                (type(content) == list and all([type(elem) == Text or
                                                isinstance(elem, Elem)
                                                for elem in content])))


def main():
    html = Elem(tag='html', content=[
        Elem(tag='head', content=[
            Elem(tag='title', content=Text('"Hello ground!"'), tag_type='double')
        ], tag_type='double'),
        Elem(tag='body', content=[
            Elem(tag='h1', content=[
                Text('"Oh no, not again!"')
            ], tag_type='double'),
            Elem(tag='img', attr={
                'src': "http://i.imgur.com/pfp3T.jpg",
            }, tag_type='simple'),
        ], tag_type='double')
    ], tag_type='double')
    
    print(html)

if __name__ == '__main__':
    main()
