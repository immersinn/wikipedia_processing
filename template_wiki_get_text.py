

import re
import nltk

"""Opens w/
{{..words..
|
|
...
}}

Also:
{{...}}

Also:
re.match(r'\[\[[a-zA-Z]+:', line)


if article[count].startswith('\|'):
                # Find end of box
                found = False
                count += 1
                while not found:
                    if article[count] == '}}':
                        found = True
                    count += 1
            else:
                content.append(line)
                count += 1


       start = count
        lcount = len(re.findall('\{\{', article[count]))
        rcount = len(re.findall('\}\}', article[count]))
        count += 1
        try:
            while not lcount == rcount:
                lcount += len(re.findall('\{\{', article[count]))
                rcount += len(re.findall('\}\}', article[count]))
                count += 1
        except IndexError:
            ADDFLAG = False
            count = len(article) + 1
        if article[start].startswith('{{cite'):
            for c in article[start:count]:
                content.append(c)


"""

def findLineSpans(content, article, count, start_tag, end_tag, ADDFLAG):
    """

    """
    start = count
    lcount = len(re.findall(start_tag, article[count]))
    rcount = len(re.findall(end_tag, article[count]))
    count += 1
    try:
        while not lcount == rcount:
            lcount += len(re.findall(start_tag, article[count]))
            rcount += len(re.findall(end_tag, article[count]))
            count += 1
    except IndexError:
        ADDFLAG = False
        count = len(article) + 1
        
    if article[start].startswith('{{cite'):
        for c in article[start:count]:
            content.append(c)
    elif start == count - 1:
        content.append(article[start])

    return content, count, ADDFLAG
    

contents = []
for article in texts:
    ADDFLAG = True
    content = []
    count = 0
    if len(article) >= 20:
        while count < len(article):
            line = article[count]
            if not line:
                count += 1
            elif line.startswith('|'):
                count += 1
            elif line.startswith('}}'):
                count += 1
            elif line.startswith('{{'):
                if line.endswith('}}'):
                    count += 1
                else:
                    start_tag = re.compile('\{\{')
                    end_tag = re.compile('\}\}')
                    content, count, ADDFLAG = \
                             findLineSpans(content, article, count,
                                           start_tag, end_tag,
                                           ADDFLAG)
            elif line.startswith('&lt;'):
                start_tag = re.compile('&lt;')
                end_tag = re.compile('&gt;')
                content, count, ADDFLAG = \
                         findLineSpans(content, article, count,
                                       start_tag, end_tag,
                                       ADDFLAG)
            elif re.match(r'\[\[[a-zA-Z]+:', line):
                # Found a file, cetegory, image, etc.
                count += 1
            else:
                content.append(line)
                count += 1
    else:
        ADDFLAG = False
    if ADDFLAG:
        contents.append(content)
