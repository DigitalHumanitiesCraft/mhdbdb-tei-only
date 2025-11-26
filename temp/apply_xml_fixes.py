from lxml import etree

def apply_final_fixes(tei_path):
    parser = etree.XMLParser(remove_blank_text=False)
    tree = etree.parse(tei_path, parser)
    root = tree.getroot()
    ns = {'tei': 'http://www.tei-c.org/ns/1.0'}
    
    fixes = {
        "AC1_27230_11": {"pos": "ADV"}, # vil
        "AC1_30160_4": {"pos": "VEX"}, # hetten
        "AC1_30170_2": {"pos": "VRB"}, # entenigten
        "AC1_30180_4": {"pos": "VEX"}, # wurden
        "AC1_30180_6": {"pos": "NEG"}, # nicht
        "AC1_30190_2": {"pos": "PRP"}, # umb
        "AC1_30200_4": {"pos": "PRP"}, # umb
        "AC1_30200_10": {"pos": "NEG"}, # nicht
        "AC1_30210_0": {"pos": "ADV"}, # vil
        "AC1_30210_10": {"pos": "DET"}, # vil (leut) - usually DET or ADJ. Let's go with DET for quantity.
        "AC1_30220_2": {"pos": "ADV"}, # dannoch
        "AC1_30220_5": {"pos": "ADJ"}, # ungemüet
        "AC1_30220_11": {"pos": "ADJ"}, # gedultig
        "AC1_30240_4": {"pos": "ADV"}, # vor
        "AC1_30250_0": {"pos": "ADV"}, # nu
        "AC1_30250_6": {"pos": "VEM"}, # müßen
        "AC1_30250_8": {"pos": "ADV"}, # hinnach
        "AC1_30250_10": {"pos": "ADV"}, # dannoch
        "AC1_30260_1": {"pos": "NOM"}, # tot
        "AC1_32120_12": {"pos": "ADV"} # nu
    }
    
    count = 0
    for xml_id, attrs in fixes.items():
        node = root.xpath(f'//*[@xml:id="{xml_id}"]', namespaces=ns)
        if node:
            w = node[0]
            for k, v in attrs.items():
                w.set(k, v)
            count += 1
            # Remove reason if present (since we are resolving to single)
            if w.get('reason'):
                del w.attrib['reason']
        else:
            print(f"Warning: ID {xml_id} not found.")
            
    print(f"Applied {count} fixes.")
    tree.write(tei_path, encoding='UTF-8', xml_declaration=True)

if __name__ == "__main__":
    apply_final_fixes("tei/AC1.disamb.tei.xml")
