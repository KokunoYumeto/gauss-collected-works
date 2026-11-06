"""Add searchable CMEX10 character mappings without changing page graphics.

Usage: python pdf_text_mapping.py input.pdf output.pdf
Requires PyMuPDF and fontTools. The output must be a new file.
"""
from pathlib import Path
import io
import re
import sys
import fitz
from fontTools.cffLib import CFFFontSet
from fontTools import agl


def cmex_unicode(name):
    # Complete delimiters map to their characters; extensible pieces retain
    # separate private-use values because each is only part of a delimiter.
    if name in ('integraltext', 'integraldisplay'):
        return 0x222B
    if name in ('summationtext', 'summationdisplay'):
        return 0x2211
    for stem, value in [('parenleft', 0x28), ('parenright', 0x29),
                        ('bracketleft', 0x5B), ('bracketright', 0x5D),
                        ('braceleft', 0x7B), ('braceright', 0x7D)]:
        if name.startswith(stem) and name[len(stem):] in ('big', 'Big', 'bigg', 'Bigg'):
            return value
    known = agl.LEGACY_AGL2UV.get(name)
    if known and len(known) == 1:
        return known[0]
    pieces = ['bracehtipdownleft', 'bracehtipdownright',
              'bracehtipupleft', 'bracehtipupright']
    if name in pieces:
        return 0xE000 + pieces.index(name)
    raise ValueError('Unmapped CMEX10 glyph: ' + name)


def main(source, output):
    source, output = Path(source), Path(output)
    if output.exists() or source.resolve() == output.resolve():
        raise ValueError('The output must be a new file.')
    doc = fitz.open(source)
    fonts = {f[0]: f for page in doc for f in page.get_fonts(full=True)}
    changed = 0
    for xref, font in fonts.items():
        if font[3].split('+')[-1] != 'CMEX10':
            continue
        kind, _ = doc.xref_get_key(xref, 'ToUnicode')
        if kind == 'xref':
            continue
        _, extension, _, data = doc.extract_font(xref)
        if extension != 'cff':
            raise ValueError('Expected embedded CMEX10 CFF font.')
        cff = CFFFontSet()
        cff.decompile(io.BytesIO(data), None)
        encoding = cff[cff.fontNames[0]].Encoding
        if not isinstance(encoding, list) or len(encoding) != 256:
            raise ValueError('Expected an explicit single-byte CFF encoding.')
        pairs = [(code, cmex_unicode(name)) for code, name in enumerate(encoding)
                 if name != '.notdef']
        mapname = re.sub('[^A-Za-z0-9]', '', font[3]) + 'UTF16'
        cmap = ('/CIDInit /ProcSet findresource begin\n12 dict begin\nbegincmap\n'
                f'/CMapName /{mapname} def\n/CMapType 2 def\n'
                '/CIDSystemInfo << /Registry (Adobe) /Ordering (UCS) /Supplement 0 >> def\n'
                '1 begincodespacerange\n<00> <FF>\nendcodespacerange\n'
                f'{len(pairs)} beginbfchar\n' +
                '\n'.join(f'<{a:02X}> <{b:04X}>' for a, b in pairs) +
                '\nendbfchar\nendcmap\nCMapName currentdict /CMap defineresource pop\nend\nend\n')
        newxref = doc.get_new_xref()
        doc.update_object(newxref, '<<>>')
        doc.update_stream(newxref, cmap.encode('ascii'))
        doc.xref_set_key(xref, 'ToUnicode', f'{newxref} 0 R')
        changed += 1
    doc.save(output)
    doc.close()
    print(f'Wrote {output.name}; added {changed} CMEX10 text mapping(s).')


if __name__ == '__main__':
    if len(sys.argv) != 3:
        raise SystemExit(__doc__)
    main(sys.argv[1], sys.argv[2])
