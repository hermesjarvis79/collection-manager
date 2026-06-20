"""
Tests for the filename parser module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.filename_parser import FilenameParser


class TestFilenameParser(unittest.TestCase):

    def test_the_matrix_2024(self):
        title, year = FilenameParser.clean(
            "The.Matrix.2024.2160p.NF.WEB-DL.DDP5.1.Atmos.H.265.mkv")
        self.assertEqual(title, "The Matrix")
        self.assertEqual(year, 2024)

    def test_inception_2010(self):
        title, year = FilenameParser.clean(
            "Inception.2010.1080p.BluRay.x264-YTS.mp4")
        self.assertEqual(title, "Inception")
        self.assertEqual(year, 2010)

    def test_the_adam_project_2022(self):
        title, year = FilenameParser.clean(
            "The.Adam.Project.2022.2160p.NF.WEB-DL.H265.SDR.DDP.Atmos.5.1.English-HONE.mkv")
        self.assertEqual(title, "The Adam Project")
        self.assertEqual(year, 2022)

    def test_dune_part_two_2024(self):
        title, year = FilenameParser.clean(
            "Dune.Part.Two.2024.IMAX.2160p.UHD.BluRay.Remux.HDR.DV.HEVC.DTS-HD.MA.7.1.mkv")
        self.assertEqual(title, "Dune Part Two")
        self.assertEqual(year, 2024)

    def test_oppenheimer_2023(self):
        title, year = FilenameParser.clean(
            "Oppenheimer.2023.1080p.WEB-DL.AAC2.0.H.264.mkv")
        self.assertEqual(title, "Oppenheimer")
        self.assertEqual(year, 2023)

    def test_no_time_to_die_2021(self):
        title, year = FilenameParser.clean(
            "No.Time.to.Die.2021.2160p.WEBRip.DDP5.1.Atmos.H.265-NOGRP.mkv")
        self.assertEqual(title, "No Time to Die")
        self.assertEqual(year, 2021)

    # ── Extra challenging test cases ──

    def test_underscore_separators_with_group(self):
        """Underscore-separated filename with underscore-prefixed release group."""
        title, year = FilenameParser.clean(
            "The_Wolf_of_Wall_Street_2013_1080p_BluRay_x264_SPARK.mkv")
        self.assertEqual(title, "The Wolf of Wall Street")
        self.assertEqual(year, 2013)

    def test_proper_tag(self):
        """PROPER release tag should be stripped."""
        title, year = FilenameParser.clean(
            "Aliens.1986.PROPER.1080p.BluRay.x264-DEPTH.mp4")
        self.assertEqual(title, "Aliens")
        self.assertEqual(year, 1986)

    def test_remux_with_dts_hd_ma(self):
        """Remux with DTS-HD MA audio and complex tag chain."""
        title, year = FilenameParser.clean(
            "Interstellar.2014.IMAX.1080p.BluRay.DTS-HD.MA.5.1.AVC.Remux-ETRG.mkv")
        self.assertEqual(title, "Interstellar")
        self.assertEqual(year, 2014)

    def test_year_in_title(self):
        """Title containing a year (2001) should not be confused with release year."""
        title, year = FilenameParser.clean(
            "2001.A.Space.Odyssey.1968.1080p.BluRay.x264-CLASSIC.mkv")
        self.assertEqual(title, "2001 A Space Odyssey")
        self.assertEqual(year, 1968)

    def test_webdl_aac_h264(self):
        """WEB-DL source with AAC audio and H.264 codec."""
        title, year = FilenameParser.clean(
            "The.Dark.Knight.2008.720p.WEB-DL.AAC2.0.H264-NTb.mkv")
        self.assertEqual(title, "The Dark Knight")
        self.assertEqual(year, 2008)


if __name__ == "__main__":
    unittest.main()
