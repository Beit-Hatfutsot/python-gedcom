from gedcom import Gedcom
from StringIO import StringIO


def test_empty_file():
    fd = StringIO()
    g = Gedcom(fd)
    assert len(g.as_list) == 0
    fd.close()


def test_header_only():
    fd = StringIO("""0 HEAD\r
1 SOUR FTW\r
2 VERS 3.40\r
2 NAME Family Tree Maker for Windows\r
2 CORP Broderbund Software, Banner Blue Division\r
3 ADDR 39500 Stevenson Pl.  #204\r
4 CONT Fremont, CA 95439\r
4 PHON (510) 794-6850\r
1 DEST FTW\r
1 DATE 28 Feb 2002\r
1 CHAR ANSI\r
1 SUBM @SUBM@\r
1 FILE E:\Fam\Wolf1130.GED\r
1 GEDC\r""")
    g = Gedcom(fd)
    assert len(g.as_list) == 13
    fd.close()
