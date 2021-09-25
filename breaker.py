#!/usr/bin/env python

# import requests
import argparse
from lxml import etree
from termcolor import colored

COLORS = [
    # 'grey',
    'red',
    'green',
    'yellow',
    'blue',
    'magenta',
    'cyan',
    'white'
]

config = {}

class_instances = {}
class_instance_color_ptr = 0

def process_element(e, level):
    global class_instance_color_ptr, class_instances

    out = ''
    comment = None

    is_comment = isinstance(e, etree._Comment)

    # comments
    if is_comment:
        comment = e.text.strip()
        # return out

    if config.only_comments:
        if comment:
            return colored(comment, 'green')
        return None

    # indentation
    indent_char = '-'

    indent = config.indent_size

    if config.indent_doubling:
        indent *= int(level / 2)

    out += colored(
        indent_char * (level * indent),
        COLORS[level % len(COLORS)]
    )

    if is_comment:
        return out + colored(e.text, 'white', 'on_red', attrs=['bold'])

    # tag
    tag = colored(e.tag.upper(), 'white', attrs=['bold'])
    if (tag):
        out += tag

    # id
    id_ = e.get('id') or ''
    out += colored('#%s' % id_ if id_ else '',
                   'red', 'on_grey', attrs=['bold'])

    # classes
    classes = e.get('class').split() if 'class' in e.keys() else ''
    classes = list(map(lambda i: '.' + i, list(classes)))

    if len(classes):
        coded_classes = []

        for class_ in classes:
            if not class_ in class_instances:
                class_instances[class_] = class_instance_color_ptr % len(
                    COLORS)
                class_instance_color_ptr += 1

            coded_classes.append(
                colored(class_, COLORS[class_instances[class_]])
            )

        out += ' (' if len(coded_classes) else ''
        out += ''.join(coded_classes)
        out += ')' if len(coded_classes) else ''

    # data attributes
    if config.show_data:
        data_attribs = []
        for k in e.keys():
            if k[:5] == 'data-':
                data_attribs.append('%s=\'%s\'' % (k, e.get(k)))
        if len(data_attribs):
            out += ' {' + colored(', '.join(data_attribs),
                                  'green', attrs=['bold']) + '}'

    # inner text
    if not config.hide_text:
        if e.text and e.text.strip():
            out += ' ' + colored(
                e.text.strip()[:10] + '...',
                attrs=['reverse']
            )

    is_empty = not e.text or e.text.strip() == ''

    if config.skip_empty_tags and is_empty:
        return None
    else:
        return out


def dump_branch(el, level=0):
    for e in el:
        if config.skip_head and e.tag == 'head':
            continue
        else:
            out = process_element(e, level)

        if out:
            print(out)
        if len(e) > 0:
            dump_branch(e, level=level + 1)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='HTML layout analysis'
    )

    parser.add_argument('html_file',
                        help='HTML file',
                        type=str
                        )
    parser.add_argument('--skip-empty-tags',
                        help='Skip empty tags',
                        action='store_true'
                        )
    parser.add_argument('--indent-size',
                        help='Indentation size',
                        type=int,
                        default=4
                        )
    parser.add_argument('--indent-doubling',
                        help='Double indent size each level',
                        action='store_true'
                        )
    parser.add_argument('--show-data',
                        help='Show data* attributes',
                        action='store_true'
                        )
    parser.add_argument('--only-comments',
                        help='Only show comments',
                        action='store_true'
                        )
    parser.add_argument('--skip-head',
                        help='Only show comments',
                        action='store_true'
                        )
    parser.add_argument('--hide-text',
                        help='Hide text snippet',
                        action='store_true'
                        )

    args = parser.parse_args()

    config = args

    infile = args.html_file

    with open(infile, 'r') as f:
        parsed = etree.fromstring(
            f.read(),
            parser=etree.HTMLParser(recover=True)
        )

    dump_branch(parsed)