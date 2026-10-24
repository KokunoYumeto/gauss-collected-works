"""Build one reader from typeset, editable LaTeX components."""
from pathlib import Path
import argparse,json
import fitz

def assemble(root,inputs,output):
    volume=json.loads((root/'volume.json').read_text(encoding='utf-8'))
    assert len(inputs)==len(volume['parts'])
    result=fitz.open();destinations={};native={};ranges=[];links=0
    for part,input_pdf in zip(volume['parts'],inputs):
        source=fitz.open(input_pdf);start=len(result)
        assert len(source)>0 and not source.is_encrypted
        result.insert_pdf(source,links=True,annots=True)
        links+=sum(len(p.get_links()) for p in source)
        for j,page in enumerate(source):
            for link in page.get_links():
                if link['kind']==fitz.LINK_NAMED:
                    result[start+j].insert_link(dict(kind=fitz.LINK_NAMED,**{'from':link['from']},nameddest=part['id']+':'+link['nameddest']))
        for name,d in source.resolve_names().items():
            assert 'page' in d and 0<=d['page']<len(source),(part['id'],name,d)
            value=dict(d,page=d['page']+start)
            destinations[part['id']+':'+name]=value
            if name.startswith('native-'):
                assert name not in native,name
                native[name]=value;destinations[name]=value
        ranges.append(dict(id=part['id'],start=start+1,end=len(result)))
        source.close()
    entries=[]
    for name,d in sorted(destinations.items()):
        x,y=d.get('to',(0,result[d['page']].rect.height));zoom=d.get('zoom',0)
        entries.append(f'{fitz.get_pdf_str(name)} [{result.page_xref(d["page"])} 0 R /XYZ {x:.8f} {y:.8f} {zoom:.8f}]')
    dx=result.get_new_xref();result.update_object(dx,'<< /Names ['+'\n'.join(entries)+'] >>')
    nx=result.get_new_xref();result.update_object(nx,f'<< /Dests {dx} 0 R >>');result.xref_set_key(result.pdf_catalog(),'Names',f'{nx} 0 R')
    toc=[]
    def mark(level,title,leaf):
        assert 'native-'+str(leaf) in native,leaf
        toc.append([level,title,native['native-'+str(leaf)]['page']+1])
    mark(1,'Titelblätter und Porträt',2)
    mark(1,'Arithmetik und Algebra',8)
    mark(1,'Analysis',40)
    for title,leaf in [
      ('De integratione formulae differentialis',42),
      ('Beweis eines von Euler aufgestellten Satzes über exacte Differentialausdrücke',72),
      ('Vier Notizen über Inversion der Potenzreihen',76),
      ('Neuer Beweis des Lagrangischen Lehrsatzes',83),
      ('Lagranges Lehrsatz, auf möglich lichtvollste Art abgeleitet',87),
      ('Entwicklung in eine Cosinusreihe',91),
      ('Schönes Theorem der Wahrscheinlichkeitsrechnung',95),
      ('Über das Wesen und die Definition der Functionen',97),
      ('Untersuchungen über die transcendenten Functionen',100),
      ('Inversion des elliptischen Integrals erster Gattung',103),
      ('Theorema elegantissimum',105),
      ('Drei Fragmente über elliptische Modulfunctionen',106),
      ('Weitere Fragmente über das Pentagramma mirificum',113)]:mark(2,title,leaf)
    for title,leaf in [('Numerisches Rechnen',126),('Wahrscheinlichkeitsrechnung',138),('Grundlagen der Geometrie',164),('Geometria Situs',276),('Aufgaben und Lehrsätze der elementaren Geometrie angehörig',294),('Verwendung complexer Grössen für die Geometrie',308),('Theorie der krummen Flächen',370),('Bemerkungen',460),('Berichtigungen',461),('Inhalt',462),('Verlagsanzeige',467)]:mark(1,title,leaf)
    result.set_toc(toc,collapse=1)
    result.set_metadata(dict(title=volume['title'],author='Carl Friedrich Gauss',subject='Nachträge zu den Bänden I, II, III. Originalsprachige Texte, historische Bemerkungen, Berichtigungen und Inhaltsverzeichnis.',keywords='Gauss, Werke, Band VIII, Mathematik, LaTeX',creator='LaTeX; PyMuPDF',producer='PyMuPDF'))
    result.xref_set_key(result.pdf_catalog(),'PageMode','/UseOutlines')
    output.parent.mkdir(parents=True,exist_ok=True)
    if output.exists():raise FileExistsError(output)
    result.save(output,garbage=4,deflate=True)
    report=dict(pages=len(result),parts=ranges,native_anchors=len(native),destinations=len(destinations),bookmarks=len(toc),source_links=links,output=str(output))
    result.close();return report

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--inputs',type=Path,help='JSON list of typeset component PDF paths');p.add_argument('--output',type=Path,default=Path('Gauss_Werke_VIII.pdf'));args=p.parse_args()
    root=Path(__file__).resolve().parent;volume=json.loads((root/'volume.json').read_text(encoding='utf-8'))
    inputs=json.loads(args.inputs.read_text(encoding='utf-8')) if args.inputs else [str(root/'parts'/part['id']/part['pdf']) for part in volume['parts']]
    print(json.dumps(assemble(root,inputs,args.output.resolve()),ensure_ascii=False))
