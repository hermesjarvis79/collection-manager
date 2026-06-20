"""
Collection Manager — Filename Parser
Cleans movie filenames by stripping release tags, codec info, group names, etc.
Uses regex patterns to extract clean title + year.
"""

import re
from typing import Tuple, Optional


class FilenameParser:
    """Parses and cleans movie filenames to extract title and year."""

    # Patterns applied to the RAW filename (dots still present)
    # Order matters — more specific patterns first
    RAW_PATTERNS = [
        # ── Audio with channel configs ──
        r'DDP\d+\.\d+',              # DDP5.1, DDP7.1
        r'DD\d+\.\d+',                # DD5.1
        r'DD\+\d+\.\d+',             # DD+5.1
        r'DTS-HD\.MA\.\d+\.\d+',     # DTS-HD.MA.7.1
        r'DTS-HD\.MA\d+\.\d+',      # DTS-HD.MA7.1
        r'DTS-HD\.\d+\.\d+',         # DTS-HD.7.1
        r'DTS\.\d+\.\d+',            # DTS.5.1
        r'DTS\d+\.\d+',              # DTS5.1
        r'TrueHD\.\d+\.\d+',         # TrueHD.7.1
        r'TrueHD\d+\.\d+',           # TrueHD7.1
        r'AAC\d+\.\d+',              # AAC2.0
        r'AC3\.\d+\.\d+',            # AC3.5.1
        r'FLAC\.\d+\.\d+',           # FLAC5.1
        r'MP3\.\d+\.\d+',            # MP3.1
        r'Atmos\.\d+\.\d+',          # Atmos.5.1

        # ── Resolution ──
        r'(?:2160p|1080p|720p|480p|360p|240p|4K|UHD)',

        # ── Codecs ──
        r'(?:x264|x265|HEVC|AVC|H\.?264|H\.?265|AV1|VP9)',

        # ── Sources / Rips ──
        r'(?:BluRay|Blu-Ray|WEB-DL|WEBRip|WEB|HDRip|DVDRip|DVDScr|HDTV|'
        r'PDTV|SDTV|CAM|TC|TS|TELESYNC|TELECINE|SCREENER)',

        # ── Simple audio ──
        r'(?:DDP|DD\+?|AC3|AAC|MP3|FLAC|Atmos|DTS(?:-HD)?|TrueHD|Stereo)',

        # ── HDR / Color ──
        r'(?:HDR(?:10)?\+?|SDR|DV|DoVi|HLG|10-?bit|8-?bit)',

        # ── Extras / Modifiers ──
        r'(?:REMUX|PROPER|REPACK|EXTENDED|UNRATED|DIRECTORS\.?CUT|'
        r'IMAX|REMASTERED|ANNIVERSARY|OPEN\.?MATTE|THEATRICAL)',

        # ── Language tags ──
        r'(?:MULTi|DUAL|ENG(?:LISH)?|FRENCH|SPANISH|GERMAN|ITALIAN|'
        r'PORTUGUESE|RUSSIAN|JAPANESE|KOREAN|HINDI|TURKISH)',

        # ── Site / Platform tags ──
        r'(?:NF|AMZN|DSNP|HULU|ATVP|MAX|HBO|CR|DSNY)',

        # ── Season/Episode ──
        r'S\d{1,4}E\d{1,4}',

        # ── Bracket/paren content ──
        r'\([^)]*\)',
        r'\[[^\]]*\]',
    ]

    _compiled_raw = None

    @classmethod
    def _get_raw_patterns(cls):
        if cls._compiled_raw is None:
            cls._compiled_raw = [
                re.compile(p, re.IGNORECASE) for p in cls.RAW_PATTERNS
            ]
        return cls._compiled_raw

    @classmethod
    def clean(cls, filename: str) -> Tuple[str, Optional[int]]:
        """
        Clean a movie filename and return (title, year).

        Examples:
            "The.Matrix.2024.2160p.NF.WEB-DL.DDP5.1.Atmos.H.265.mkv"
                -> ("The Matrix", 2024)
            "Inception.2010.1080p.BluRay.x264-YTS.mp4"
                -> ("Inception", 2010)
        """
        # Remove file extension
        name = re.sub(r'\.\w{2,4}$', '', filename)

        # Extract year before any transformations
        year = cls._extract_year(name)

        # Strip release group suffix early (e.g. -YTS, -NOGRP, -HONE, _SPARK)
        # Must happen before other patterns to avoid partial matches
        name = re.sub(r'[-_][A-Za-z0-9]+$', '', name)

        # Apply raw patterns (while dots are still separators)
        for pattern in cls._get_raw_patterns():
            name = pattern.sub('.', name)

        # Replace dots and underscores with spaces
        name = name.replace('.', ' ').replace('_', ' ')

        # Collapse whitespace
        name = re.sub(r'\s+', ' ', name).strip()

        # Remove orphaned dashes
        name = re.sub(r'\s*-\s*', ' ', name).strip()

        # Remove year from title (as standalone token, anywhere)
        if year:
            name = re.sub(rf'\b{year}\b', '', name).strip()
            name = re.sub(r'\s+', ' ', name).strip()

        return name, year

    @staticmethod
    def _extract_year(text: str) -> Optional[int]:
        """Extract a 4-digit year (1900-2099) from text.

        Prefers a year that is followed by a release tag (resolution, source,
        codec, etc.) so that titles containing years (e.g. "2001" in
        "2001 A Space Odyssey") are not mistaken for the release year.
        """
        year_re = re.compile(r'(?<!\d)((?:19|20)\d{2})(?!\d)')
        # Known tags that signal "the year just ended, tags start here"
        tag_signal = re.compile(
            r'(?:2160p|1080p|720p|480p|4K|UHD|BluRay|WEB-DL|WEBRip|HDTV|'
            r'x264|x265|AVC|H\.?264|H\.?265|HEVC|AV1|VP9|'
            r'DDP|DD\+?|AAC|Atmos|DTS|TrueHD|REMUX|PROPER|REPACK|IMAX)',
            re.IGNORECASE,
        )
        matches = list(year_re.finditer(text))
        if not matches:
            return None
        # Prefer a year immediately followed by a dot/underscore and a tag signal
        for m in matches:
            after = text[m.end():]
            if re.match(r'[._]', after) and tag_signal.match(re.sub(r'^[._]\s*', '', after)):
                return int(m.group(1))
        # Fallback: return the last valid year match
        return int(matches[-1].group(1))


# ── Quick test ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    test_files = [
        # Original 6 test cases
        ("The.Matrix.2024.2160p.NF.WEB-DL.DDP5.1.Atmos.H.265.mkv",
         "The Matrix", 2024),
        ("Inception.2010.1080p.BluRay.x264-YTS.mp4",
         "Inception", 2010),
        ("The.Adam.Project.2022.2160p.NF.WEB-DL.H265.SDR.DDP.Atmos.5.1.English-HONE.mkv",
         "The Adam Project", 2022),
        ("Dune.Part.Two.2024.IMAX.2160p.UHD.BluRay.Remux.HDR.DV.HEVC.DTS-HD.MA.7.1.mkv",
         "Dune Part Two", 2024),
        ("Oppenheimer.2023.1080p.WEB-DL.AAC2.0.H.264.mkv",
         "Oppenheimer", 2023),
        ("No.Time.to.Die.2021.2160p.WEBRip.DDP5.1.Atmos.H.265-NOGRP.mkv",
         "No Time to Die", 2021),
        # Extra 5 challenging test cases
        ("The_Wolf_of_Wall_Street_2013_1080p_BluRay_x264_SPARK.mkv",
         "The Wolf of Wall Street", 2013),
        ("Aliens.1986.PROPER.1080p.BluRay.x264-DEPTH.mp4",
         "Aliens", 1986),
        ("Interstellar.2014.IMAX.1080p.BluRay.DTS-HD.MA.5.1.AVC.Remux-ETRG.mkv",
         "Interstellar", 2014),
        ("2001.A.Space.Odyssey.1968.1080p.BluRay.x264-CLASSIC.mkv",
         "2001 A Space Odyssey", 1968),
        ("The.Dark.Knight.2008.720p.WEB-DL.AAC2.0.H264-NTb.mkv",
         "The Dark Knight", 2008),
    ]

    all_pass = True
    for filename, expected_title, expected_year in test_files:
        title, year = FilenameParser.clean(filename)
        status = "PASS" if title == expected_title and year == expected_year else "FAIL"
        if status == "FAIL":
            all_pass = False
        print(f"  {status} {filename[:60]:60s}")
        if status == "FAIL":
            print(f"    Expected: \"{expected_title}\" ({expected_year})")
            print(f"    Got:      \"{title}\" ({year})")

    print(f"\n  {'All tests passed!' if all_pass else 'Some tests FAILED.'}")
