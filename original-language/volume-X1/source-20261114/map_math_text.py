"""Supply missing CMEX ToUnicode maps without changing the rendered content.

Requires PyMuPDF, fontTools and a TeX installation. Character identities come
from the installed LaTeX Project glyphtounicode-cmex.tex, whose credits include
Han The Thanh, Peter Selinger and Ross Moore. This script reads that file;
it does not redistribute or modify it. Size variation selectors are omitted
from copied text. Historical notation remains in the editable TeX sources.
"""
from pathlib import Path
import argparse
import io
import re
import subprocess

import fitz
from fontTools.cffLib import CFFFontSet


def supply_maps(pdf, glyph_map):
    entries = re.findall(r"\\pdfglyphtounicode\{([^}]+)\}\{([^}]+)\}",
                         glyph_map.read_text(encoding="utf-8"))
    glyphs = {name: "".join(chr(int(c, 16)) for c in codes.split()
                          if not 0xFE00 <= int(c, 16) <= 0xFE0F)
              for name, codes in entries}
    document = fitz.open(pdf)
    seen, changed = set(), []
    for page in document:
        for font in page.get_fonts():
            xref = font[0]
            if xref in seen:
                continue
            seen.add(xref)
            if "CMEX" not in font[3] or document.xref_get_key(xref, "ToUnicode")[0] != "null":
                continue
            cff = CFFFontSet()
            cff.decompile(io.BytesIO(document.extract_font(xref)[3]), None)
            encoding = cff[cff.fontNames[0]].Encoding
            mappings = []
            for code, name in enumerate(encoding):
                if name == ".notdef":
                    continue
                if name not in glyphs:
                    raise ValueError(f"No Unicode mapping for {name}")
                value = glyphs[name].encode("utf-16-be").hex().upper()
                mappings.append(f"<{code:02X}> <{value}>")
            cmap = ("/CIDInit /ProcSet findresource begin\n12 dict begin\nbegincmap\n"
                    "/CIDSystemInfo << /Registry (Adobe) /Ordering (UCS) /Supplement 0 >> def\n"
                    "/CMapName /CMEX-UTF16 def\n/CMapType 2 def\n"
                    "1 begincodespacerange\n<00> <FF>\nendcodespacerange\n"
                    f"{len(mappings)} beginbfchar\n" + "\n".join(mappings) +
                    "\nendbfchar\nendcmap\nCMapName currentdict /CMap defineresource pop\nend\nend\n")
            cmap_xref = document.get_new_xref()
            document.update_object(cmap_xref, "<<>>")
            document.update_stream(cmap_xref, cmap.encode("ascii"))
            document.xref_set_key(xref, "ToUnicode", f"{cmap_xref} 0 R")
            changed.append((font[3], len(mappings)))
    if changed:
        document.saveIncr()
    document.close()
    return changed


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pdf", type=Path)
    parser.add_argument("--glyph-map", type=Path)
    args = parser.parse_args()
    glyph_map = args.glyph_map or Path(subprocess.check_output(
        ["kpsewhich", "glyphtounicode-cmex.tex"], text=True).strip())
    print(supply_maps(args.pdf, glyph_map))
