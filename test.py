# -*- coding: utf-8 -*-
import pytest
from gedcom import Gedcom, GedcomParseError
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
    g = Gedcom(stream=u"""0 head
1 sour אינה""".encode('utf-8'))
    assert g.as_list[1].value == u'אינה'

def test_bad_utf8_chars():
    stream = "0 HEAD "
    for i in (0x20d7, 0xa2d7, 0x91d7, 0xa8d7, 0x9520, 0xd79c, 0xd799, 0xd791,
              0xd7a0, 0xd799, 0xd790, 0xd79c, 0x20d7, 0x95d7, 0x9ed7, 0xa9d7,
              0x9d20, 0xd700,
             ):
        stream += chr(i / 0x100)+chr(i % 0x100)
    with pytest.raises(GedcomParseError):
        Gedcom(stream=stream)
    g = Gedcom(stream=stream, encoding='utf-8')
    assert g.as_list[0].value[-2:-1] == u"\ufffd"

def test_filename():
    g=Gedcom('test_data/1F94B7BF-65FC-42EA-AEF4-9B6087DD45DE.ged')
    assert len(g.as_list) == 37410
    assert len(g.as_dict.keys()) == 5156

