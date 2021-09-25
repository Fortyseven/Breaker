#!/usr/bin/env python
"""
Breaker - a tool to help visualize cluttered HTML layouts.
"""
import argparse
import sys, os
from lxml import etree
from termcolor import colored

COLORS = [
    # 'grey',  # Shows up as 'black' in some terminals, but go for it if you want
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

##############################################################################
def process_element(e, level):
    """Processes a single DOM element"""
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
        indent_char * (level * indent) + "|",
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
    if not config.no_text:
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

##############################################################################
def dump_branch(el, level=0):
    """Recursively iterates through the DOM"""
    if el is None:
        return

    for e in el:
        if config.no_head and e.tag == 'head':
            continue
        else:
            out = process_element(e, level)

        if out:
            print(out)
        if len(e) > 0:
            dump_branch(e, level=level + 1)

##############################################################################
def main():
    global config

    parser = argparse.ArgumentParser(
        description='A tool to help with HTML layout analysis and visualization'
    )

    parser.add_argument('infile',
                        nargs='?',
                        help='HTML file, or use `-` for stdin',
                        type=argparse.FileType('r'),
                        default=sys.stdin
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
    parser.add_argument('--no-head',
                        help='Skip processing <head> tag',
                        action='store_true'
                        )
    parser.add_argument('--no-text',
                        help='Hide text snippet',
                        action='store_true'
                        )
    parser.add_argument('--no-color',
                        help='Disable colors',
                        action='store_true'
                        )

    args = parser.parse_args()
    config = args

    if args.no_color:
        os.environ['ANSI_COLORS_DISABLED'] = "1"

    file_in = args.infile
    html_input = ""

    with file_in as f:
        for line in f:
            html_input += line

    parsed = etree.fromstring(
        html_input,
        parser=etree.HTMLParser(recover=True)
    )

    dump_branch(parsed)


if __name__ == '__main__':
    main()
