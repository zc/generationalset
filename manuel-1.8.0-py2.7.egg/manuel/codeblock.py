import re
import manuel
import textwrap

CODEBLOCK_START = re.compile(
    r'(^\.\.\s*(invisible-)?code(-block)?::?\s*python\b(?:\s*\:[\w-]+\:.*\n)*)',
    re.MULTILINE)
CODEBLOCK_END = re.compile(r'(\n\Z|\n(?=\S))')


class CodeBlock(object):
    def __init__(self, code, source):
        self.code = code
        self.source = source


def find_code_blocks(document):
    for region in document.find_regions(CODEBLOCK_START, CODEBLOCK_END):
        start_end = CODEBLOCK_START.search(region.source).end()
        source = textwrap.dedent(region.source[start_end:])
        source_location = '%s:%d' % (document.location, region.lineno)
        code = compile(source, source_location, 'exec', 0, True)
        document.claim_region(region)
        region.parsed = CodeBlock(code, source)


def execute_code_block(region, document, globs):
    if not isinstance(region.parsed, CodeBlock):
        return

    exec(region.parsed.code, globs)
    del globs['__builtins__'] # exec adds __builtins__, we don't want it


class Manuel(manuel.Manuel):
    def __init__(self):
        manuel.Manuel.__init__(self, [find_code_blocks], [execute_code_block])
