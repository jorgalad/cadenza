"""File I/O endpoints -- MusicXML and MIDI import/export."""

from __future__ import annotations

import io
import os
import tempfile

from fastapi import APIRouter, File, UploadFile
from fastapi.responses import StreamingResponse

from cadenza.api.helpers import _parse_phrase, _phrase_response, _score_response
from cadenza.api.schemas import ExportMidiRequest, ExportPhraseRequest
from cadenza.core.score import Score
from cadenza.io import export_musicxml, import_musicxml

router = APIRouter(prefix="/v1/io", tags=["io"])


@router.post(
    "/import-musicxml",
    response_model=None,
    summary="Import MusicXML file",
    description="Upload a MusicXML file and receive the parsed phrase or score data with import warnings.",
)
async def import_musicxml_endpoint(file: UploadFile = File(...)) -> dict:
    content = await file.read()
    tmp = tempfile.NamedTemporaryFile(suffix=".xml", delete=False)
    try:
        tmp.write(content)
        tmp.close()
        result, warnings = import_musicxml(tmp.name)
        if isinstance(result, Score):
            response = _score_response(result)
        else:
            response = _phrase_response(result)
        response["warnings"] = [
            {"element": w.element, "position": w.position, "message": w.message}
            for w in warnings
        ]
        return response
    finally:
        os.unlink(tmp.name)


@router.post(
    "/export-musicxml",
    response_model=None,
    summary="Export phrase as MusicXML",
    description="Convert a CN phrase to MusicXML format and return as a downloadable XML file.",
)
def export_musicxml_endpoint(req: ExportPhraseRequest) -> StreamingResponse:
    phrase = _parse_phrase(req.phrase)
    tmp = tempfile.NamedTemporaryFile(suffix=".xml", delete=False)
    try:
        tmp.close()
        export_musicxml(phrase, tmp.name)
        with open(tmp.name, "rb") as f:
            xml_bytes = f.read()
    finally:
        os.unlink(tmp.name)
    return StreamingResponse(
        io.BytesIO(xml_bytes),
        media_type="application/xml",
        headers={"Content-Disposition": "attachment; filename=export.xml"},
    )


# MIDI endpoints -- only available if mido is installed
try:
    from fastapi import Form

    from cadenza.io import export_midi, import_midi

    @router.post(
        "/import-midi",
        response_model=None,
        summary="Import MIDI file",
        description="Upload a MIDI file and receive the parsed phrase or score data with import warnings.",
    )
    async def import_midi_endpoint(
        file: UploadFile = File(...),
        grid: str = Form("16"),
        prefer_sharps: bool = Form(False),
    ) -> dict:
        content = await file.read()
        tmp = tempfile.NamedTemporaryFile(suffix=".mid", delete=False)
        try:
            tmp.write(content)
            tmp.close()
            result, warnings = import_midi(tmp.name, grid, prefer_sharps)
            if isinstance(result, Score):
                response = _score_response(result)
            else:
                response = _phrase_response(result)
            response["warnings"] = [
                {"element": w.element, "position": w.position, "message": w.message}
                for w in warnings
            ]
            return response
        finally:
            os.unlink(tmp.name)

    @router.post(
        "/export-midi",
        response_model=None,
        summary="Export phrase as MIDI",
        description="Convert a CN phrase to MIDI format and return as a downloadable MIDI file.",
    )
    def export_midi_endpoint(req: ExportMidiRequest) -> StreamingResponse:
        phrase = _parse_phrase(req.phrase)
        tmp = tempfile.NamedTemporaryFile(suffix=".mid", delete=False)
        try:
            tmp.close()
            export_midi(phrase, tmp.name, req.tempo)
            with open(tmp.name, "rb") as f:
                midi_bytes = f.read()
        finally:
            os.unlink(tmp.name)
        return StreamingResponse(
            io.BytesIO(midi_bytes),
            media_type="application/octet-stream",
            headers={"Content-Disposition": "attachment; filename=export.mid"},
        )

except ImportError:
    pass  # MIDI endpoints not available without mido
