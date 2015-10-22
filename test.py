# -*- coding: utf-8 -*-
from gedcom import Gedcom
from StringIO import StringIO


def test_empty_file():
    fd = StringIO()
    g = Gedcom(fd=fd)
    assert len(g.as_list) == 0
    fd.close()


def test_header_only():
    g = Gedcom(stream="""0 HEAD
1 SOUR FTW
2 VERS 3.40
2 NAME Family Tree Maker for Windows
2 CORP Broderbund Software, Banner Blue Division
3 ADDR 39500 Stevenson Pl.  #204
4 CONT Fremont, CA 95439
4 PHON (510) 794-6850
1 DEST FTW
1 DATE 28 Feb 2002
1 CHAR ANSI
1 SUBM @SUBM@
1 FILE E:\Fam\Wolf1130.GED
1 GEDC""")
    assert len(g.as_list) == 14

def test_extranewline():
    g = Gedcom(stream="""0 HEAD\r
1 SOUR FTW\r""")
    assert len(g.as_list) == 2

def test_utf8_chars():
    g = Gedcom(stream="""0 HEAD
1 SOUR אינה""")
    assert g.as_list[1].value == 'אינה'

