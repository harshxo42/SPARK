"""
tests/test_vision.py - SPARK Vision Module Test Suite
=====================================================
Run from the SPARK project root:
    python -m pytest tests/ -v

or without pytest:
    python tests/test_vision.py
"""

from __future__ import annotations

import io
import os
import sys
import tempfile
import unittest
from pathlib import Path

# Fix Windows console encoding so test output prints cleanly
if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf_8"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

# Ensure project root is on sys.path
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from PIL import Image
from vision import compare_images, DIFF_THRESHOLD


def _make_solid_image(colour: tuple, size=(100, 100)) -> str:
    """Create a temp PNG filled with a solid colour. Returns file path."""
    img = Image.new("RGB", size, colour)
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    img.save(tmp.name, "PNG")
    tmp.close()
    return tmp.name


class TestCompareImagesBasic(unittest.TestCase):

    def setUp(self):
        self.tmp_files = []

    def tearDown(self):
        for f in self.tmp_files:
            try:
                os.unlink(f)
            except OSError:
                pass

    def _tmp(self, colour, size=(100, 100)):
        p = _make_solid_image(colour, size)
        self.tmp_files.append(p)
        return p

    # ── Test 1: identical images → ~0 % change ───────────────────────────
    def test_identical_images_zero_change(self):
        p = self._tmp((80, 120, 160))
        result = compare_images(p, p)
        self.assertIn("highlighted_image", result)
        self.assertIn("summary", result)
        self.assertIn("change_percent", result)
        self.assertAlmostEqual(result["change_percent"], 0.0, places=1,
                               msg="Identical images should have ~0 % change")
        print(f"  PASS: Identical images -> {result['change_percent']:.2f}% change")

    # ── Test 2: completely different images → high change % ──────────────
    def test_different_images_high_change(self):
        p_dark = self._tmp((10, 10, 10))
        p_light = self._tmp((240, 240, 240))
        result = compare_images(p_dark, p_light)
        self.assertGreater(result["change_percent"], 80.0,
                           msg="Maximally different images should show very high change %")
        print(f"  PASS: Different images -> {result['change_percent']:.2f}% change")

    # ── Test 3: partial difference ────────────────────────────────────────
    def test_partial_difference(self):
        # Left half one colour, right half another
        ref = Image.new("RGB", (100, 100), (50, 100, 150))
        cur = Image.new("RGB", (100, 100), (50, 100, 150))
        # Paint right half differently in current
        for y in range(100):
            for x in range(50, 100):
                cur.putpixel((x, y), (220, 50, 30))

        ref_tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
        cur_tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
        ref.save(ref_tmp.name)
        cur.save(cur_tmp.name)
        ref_tmp.close()
        cur_tmp.close()
        self.tmp_files.extend([ref_tmp.name, cur_tmp.name])

        result = compare_images(ref_tmp.name, cur_tmp.name)
        # Expect ~50% of pixels to be highlighted
        self.assertGreater(result["change_percent"], 40.0)
        self.assertLess(result["change_percent"], 60.0)
        print(f"  PASS: Partial diff -> {result['change_percent']:.2f}% change (expect ~50%)")

    # ── Test 4: different sizes → should resize and succeed ──────────────
    def test_different_dimensions_resize(self):
        p_ref = self._tmp((100, 100, 100), size=(200, 200))
        p_cur = self._tmp((100, 100, 100), size=(100, 100))  # half size
        result = compare_images(p_ref, p_cur)
        self.assertIsInstance(result["change_percent"], float)
        self.assertEqual(result["highlighted_image"].size, (200, 200))
        print(f"  PASS: Different dimensions handled -> output size (200, 200), change {result['change_percent']:.2f}%")

    # ── Test 5: return types ──────────────────────────────────────────────
    def test_return_types(self):
        p = self._tmp((100, 150, 200))
        result = compare_images(p, p)
        self.assertIsInstance(result["highlighted_image"], Image.Image)
        self.assertIsInstance(result["summary"], str)
        self.assertIsInstance(result["change_percent"], float)
        self.assertGreater(len(result["summary"]), 10)
        print("  PASS: Return types correct (Image, str, float)")


class TestCompareImagesErrors(unittest.TestCase):

    # ── Test 6: missing reference file ───────────────────────────────────
    def test_missing_reference_raises_file_not_found(self):
        with self.assertRaises(FileNotFoundError) as ctx:
            compare_images("/nonexistent/reference.png", "/nonexistent/current.png")
        self.assertIn("Reference image not found", str(ctx.exception))
        print("  PASS: Missing reference -> FileNotFoundError")

    # ── Test 7: missing current file ─────────────────────────────────────
    def test_missing_current_raises_file_not_found(self):
        # Create a valid reference first
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
        Image.new("RGB", (50, 50), (100, 100, 100)).save(tmp.name)
        tmp.close()
        try:
            with self.assertRaises(FileNotFoundError) as ctx:
                compare_images(tmp.name, "/nonexistent/current.png")
            self.assertIn("Current image not found", str(ctx.exception))
            print("  PASS: Missing current -> FileNotFoundError")
        finally:
            os.unlink(tmp.name)

    # ── Test 8: unreadable (invalid) file ────────────────────────────────
    def test_invalid_image_raises_value_error(self):
        # Write a non-image text file
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".png", mode="w")
        tmp.write("this is not an image file")
        tmp.close()
        tmp2 = tempfile.NamedTemporaryFile(delete=False, suffix=".png", mode="w")
        tmp2.write("this is also not an image")
        tmp2.close()
        try:
            with self.assertRaises((ValueError, Exception)):
                compare_images(tmp.name, tmp2.name)
            print("  PASS: Invalid image file -> ValueError (or similar)")
        finally:
            os.unlink(tmp.name)
            os.unlink(tmp2.name)

    # ── Test 9: summary contains percentage ──────────────────────────────
    def test_summary_contains_percentage(self):
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
        Image.new("RGB", (80, 80), (60, 60, 60)).save(tmp.name)
        tmp.close()
        try:
            result = compare_images(tmp.name, tmp.name)
            self.assertIn("%", result["summary"])
            print(f"  PASS: Summary contains '%': '{result['summary'][:60]}...'")
        finally:
            os.unlink(tmp.name)

    # ── Test 10: sample images (if generated) ────────────────────────────
    def test_sample_images_produce_nonzero_change(self):
        ref_path = ROOT / "assets" / "reference.png"
        cur_path = ROOT / "assets" / "current.png"
        if not ref_path.exists() or not cur_path.exists():
            self.skipTest("Sample images not generated yet — run sample_generator.py first")
        result = compare_images(str(ref_path), str(cur_path))
        self.assertGreater(
            result["change_percent"], 0.5,
            "Sample images should produce visible differences",
        )
        print(f"  PASS: Sample images -> {result['change_percent']:.2f}% visual change")


class TestDatabase(unittest.TestCase):
    """Basic database tests."""

    @classmethod
    def setUpClass(cls):
        import database as db_mod
        cls.db = db_mod

    def test_save_and_retrieve_record(self):
        record_id = self.db.save_record(
            gearbox_case="TEST-UNIT-001",
            technician_name="Test Engineer",
            inspection_date="2026-10-27",
            change_percent=12.5,
            comparison_summary="Test comparison summary.",
            observations="Test observation.",
            repair_actions="No action required.",
            status="Pending Review",
        )
        self.assertIsInstance(record_id, int)
        self.assertGreater(record_id, 0)

        rec = self.db.get_record_by_id(record_id)
        self.assertIsNotNone(rec)
        self.assertEqual(rec["gearbox_case"], "TEST-UNIT-001")
        self.assertEqual(rec["technician_name"], "Test Engineer")
        self.assertAlmostEqual(rec["change_percent"], 12.5)
        print(f"  PASS: Record saved (ID={record_id}) and retrieved correctly")

    def test_status_update(self):
        record_id = self.db.save_record(
            gearbox_case="TEST-STATUS-001",
            technician_name="Tester",
            inspection_date="2026-10-27",
            status="Pending Review",
        )
        self.db.update_status(record_id, "Completed")
        rec = self.db.get_record_by_id(record_id)
        self.assertEqual(rec["status"], "Completed")
        print(f"  PASS: Status update works (ID={record_id})")

    def test_get_all_records_returns_list(self):
        recs = self.db.get_all_records()
        self.assertIsInstance(recs, list)
        print(f"  PASS: get_all_records() returned {len(recs)} records")

    def test_count_by_status(self):
        counts = self.db.count_by_status()
        self.assertIn("Total", counts)
        self.assertIsInstance(counts["Total"], int)
        print(f"  PASS: count_by_status() -> {counts}")

    def test_filter_by_status(self):
        self.db.save_record(
            gearbox_case="TEST-FILTER",
            technician_name="Filter Test",
            inspection_date="2026-10-27",
            status="In Progress",
        )
        recs = self.db.get_all_records("In Progress")
        self.assertTrue(all(r["status"] == "In Progress" for r in recs))
        print(f"  PASS: Filter by 'In Progress' -> {len(recs)} record(s)")

    def test_restart_persistence(self):
        """Records saved in an earlier test are still visible (same DB)."""
        recs = self.db.get_all_records()
        self.assertGreater(len(recs), 0, "Records should persist across module reloads")
        print(f"  PASS: Persistence check -> {len(recs)} records found in DB")


if __name__ == "__main__":
    print("=" * 60)
    print("SPARK Test Suite")
    print("=" * 60)
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    suite.addTests(loader.loadTestsFromTestCase(TestCompareImagesBasic))
    suite.addTests(loader.loadTestsFromTestCase(TestCompareImagesErrors))
    suite.addTests(loader.loadTestsFromTestCase(TestDatabase))
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)
