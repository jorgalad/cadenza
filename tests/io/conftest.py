"""Shared fixtures for I/O tests."""

from __future__ import annotations

from pathlib import Path

import pytest


def write_xml(content: str, tmp_path: Path) -> Path:
    """Write XML content to a temp file and return the path."""
    p = tmp_path / "test.musicxml"
    p.write_text(content, encoding="utf-8")
    return p


SIMPLE_MUSICXML = """\
<?xml version="1.0" encoding="UTF-8"?>
<score-partwise version="4.0">
  <part-list>
    <score-part id="P1"><part-name>Piano</part-name></score-part>
  </part-list>
  <part id="P1">
    <measure number="1">
      <attributes>
        <divisions>4</divisions>
      </attributes>
      <note>
        <pitch><step>C</step><octave>4</octave></pitch>
        <duration>4</duration>
        <type>quarter</type>
      </note>
    </measure>
  </part>
</score-partwise>
"""

SHARP_FLAT_MUSICXML = """\
<?xml version="1.0" encoding="UTF-8"?>
<score-partwise version="4.0">
  <part-list>
    <score-part id="P1"><part-name>Piano</part-name></score-part>
  </part-list>
  <part id="P1">
    <measure number="1">
      <attributes>
        <divisions>4</divisions>
      </attributes>
      <note>
        <pitch><step>F</step><alter>1</alter><octave>4</octave></pitch>
        <duration>4</duration>
        <type>quarter</type>
      </note>
      <note>
        <pitch><step>E</step><alter>-1</alter><octave>4</octave></pitch>
        <duration>4</duration>
        <type>quarter</type>
      </note>
    </measure>
  </part>
</score-partwise>
"""

REST_MUSICXML = """\
<?xml version="1.0" encoding="UTF-8"?>
<score-partwise version="4.0">
  <part-list>
    <score-part id="P1"><part-name>Piano</part-name></score-part>
  </part-list>
  <part id="P1">
    <measure number="1">
      <attributes>
        <divisions>4</divisions>
      </attributes>
      <note>
        <rest/>
        <duration>4</duration>
        <type>quarter</type>
      </note>
    </measure>
  </part>
</score-partwise>
"""

TIED_NOTES_MUSICXML = """\
<?xml version="1.0" encoding="UTF-8"?>
<score-partwise version="4.0">
  <part-list>
    <score-part id="P1"><part-name>Piano</part-name></score-part>
  </part-list>
  <part id="P1">
    <measure number="1">
      <attributes>
        <divisions>4</divisions>
      </attributes>
      <note>
        <pitch><step>C</step><octave>4</octave></pitch>
        <duration>4</duration>
        <type>quarter</type>
        <tie type="start"/>
      </note>
      <note>
        <pitch><step>C</step><octave>4</octave></pitch>
        <duration>4</duration>
        <type>quarter</type>
        <tie type="stop"/>
      </note>
    </measure>
  </part>
</score-partwise>
"""

TIE_CHAIN_MUSICXML = """\
<?xml version="1.0" encoding="UTF-8"?>
<score-partwise version="4.0">
  <part-list>
    <score-part id="P1"><part-name>Piano</part-name></score-part>
  </part-list>
  <part id="P1">
    <measure number="1">
      <attributes>
        <divisions>4</divisions>
      </attributes>
      <note>
        <pitch><step>C</step><octave>4</octave></pitch>
        <duration>4</duration>
        <type>quarter</type>
        <tie type="start"/>
      </note>
      <note>
        <pitch><step>C</step><octave>4</octave></pitch>
        <duration>4</duration>
        <type>quarter</type>
        <tie type="stop"/>
        <tie type="start"/>
      </note>
      <note>
        <pitch><step>C</step><octave>4</octave></pitch>
        <duration>4</duration>
        <type>quarter</type>
        <tie type="stop"/>
      </note>
    </measure>
  </part>
</score-partwise>
"""

DYNAMICS_ARTICULATIONS_MUSICXML = """\
<?xml version="1.0" encoding="UTF-8"?>
<score-partwise version="4.0">
  <part-list>
    <score-part id="P1"><part-name>Piano</part-name></score-part>
  </part-list>
  <part id="P1">
    <measure number="1">
      <attributes>
        <divisions>4</divisions>
      </attributes>
      <direction placement="below">
        <direction-type>
          <dynamics><f/></dynamics>
        </direction-type>
      </direction>
      <note>
        <pitch><step>C</step><octave>4</octave></pitch>
        <duration>4</duration>
        <type>quarter</type>
        <notations>
          <articulations>
            <staccato/>
          </articulations>
        </notations>
      </note>
      <note>
        <pitch><step>D</step><octave>4</octave></pitch>
        <duration>4</duration>
        <type>quarter</type>
        <notations>
          <articulations>
            <accent/>
          </articulations>
        </notations>
      </note>
    </measure>
  </part>
</score-partwise>
"""

MULTIPART_MUSICXML = """\
<?xml version="1.0" encoding="UTF-8"?>
<score-partwise version="4.0">
  <part-list>
    <score-part id="P1"><part-name>Violin</part-name></score-part>
    <score-part id="P2"><part-name>Cello</part-name></score-part>
  </part-list>
  <part id="P1">
    <measure number="1">
      <attributes>
        <divisions>4</divisions>
      </attributes>
      <note>
        <pitch><step>E</step><octave>5</octave></pitch>
        <duration>4</duration>
        <type>quarter</type>
      </note>
    </measure>
  </part>
  <part id="P2">
    <measure number="1">
      <attributes>
        <divisions>4</divisions>
      </attributes>
      <note>
        <pitch><step>C</step><octave>3</octave></pitch>
        <duration>4</duration>
        <type>quarter</type>
      </note>
    </measure>
  </part>
</score-partwise>
"""

GRACE_NOTE_MUSICXML = """\
<?xml version="1.0" encoding="UTF-8"?>
<score-partwise version="4.0">
  <part-list>
    <score-part id="P1"><part-name>Piano</part-name></score-part>
  </part-list>
  <part id="P1">
    <measure number="1">
      <attributes>
        <divisions>4</divisions>
      </attributes>
      <note>
        <grace/>
        <pitch><step>D</step><octave>4</octave></pitch>
        <type>eighth</type>
      </note>
      <note>
        <pitch><step>C</step><octave>4</octave></pitch>
        <duration>4</duration>
        <type>quarter</type>
      </note>
    </measure>
  </part>
</score-partwise>
"""

VARYING_DIVISIONS_MUSICXML = """\
<?xml version="1.0" encoding="UTF-8"?>
<score-partwise version="4.0">
  <part-list>
    <score-part id="P1"><part-name>Piano</part-name></score-part>
  </part-list>
  <part id="P1">
    <measure number="1">
      <attributes>
        <divisions>2</divisions>
      </attributes>
      <note>
        <pitch><step>C</step><octave>4</octave></pitch>
        <duration>2</duration>
        <type>quarter</type>
      </note>
    </measure>
    <measure number="2">
      <attributes>
        <divisions>4</divisions>
      </attributes>
      <note>
        <pitch><step>D</step><octave>4</octave></pitch>
        <duration>4</duration>
        <type>quarter</type>
      </note>
    </measure>
  </part>
</score-partwise>
"""


@pytest.fixture
def tmp_musicxml_file(tmp_path: Path):
    """Factory fixture that writes XML content to a temp file."""
    def _write(content: str = SIMPLE_MUSICXML) -> Path:
        return write_xml(content, tmp_path)
    return _write
