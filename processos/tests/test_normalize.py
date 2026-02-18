"""
Testes para funções de normalização SNI.
"""
import unittest
from processos.domain.governanca.normalize import (
    normalize_area_prefix, normalize_cap, normalize_numero_csv,
    resolve_prefixo_cap, resolve_prefixo_cp,
)


class TestNormalizeAreaPrefix(unittest.TestCase):

    def test_single_digit(self):
        self.assertEqual(normalize_area_prefix("1"), "01")
        self.assertEqual(normalize_area_prefix("9"), "09")

    def test_already_two_digits(self):
        self.assertEqual(normalize_area_prefix("01"), "01")
        self.assertEqual(normalize_area_prefix("09"), "09")

    def test_ten_plus(self):
        self.assertEqual(normalize_area_prefix("10"), "10")
        self.assertEqual(normalize_area_prefix("11"), "11")

    def test_subarea_single(self):
        self.assertEqual(normalize_area_prefix("5.1"), "05.01")
        self.assertEqual(normalize_area_prefix("5.3"), "05.03")

    def test_subarea_already_normalized(self):
        self.assertEqual(normalize_area_prefix("05.01"), "05.01")
        self.assertEqual(normalize_area_prefix("05.03"), "05.03")

    def test_whitespace(self):
        self.assertEqual(normalize_area_prefix(" 5.1 "), "05.01")
        self.assertEqual(normalize_area_prefix("  1  "), "01")

    def test_empty(self):
        self.assertEqual(normalize_area_prefix(""), "")
        self.assertEqual(normalize_area_prefix(None), "")

    def test_non_numeric(self):
        self.assertEqual(normalize_area_prefix("CGBEN"), "CGBEN")


class TestNormalizeCap(unittest.TestCase):

    def test_single_digit_area(self):
        self.assertEqual(normalize_cap("1.02.03.04.108"), "01.02.03.04.108")

    def test_already_normalized(self):
        self.assertEqual(normalize_cap("01.02.03.04.108"), "01.02.03.04.108")

    def test_area_nine(self):
        self.assertEqual(normalize_cap("9.01.01.01.001"), "09.01.01.01.001")

    def test_area_ten(self):
        self.assertEqual(normalize_cap("10.01.01.01.001"), "10.01.01.01.001")

    def test_empty(self):
        self.assertEqual(normalize_cap(""), "")
        self.assertEqual(normalize_cap(None), "")

    def test_whitespace(self):
        self.assertEqual(normalize_cap(" 1.02.03.04.108 "), "01.02.03.04.108")


class TestNormalizeNumeroCsv(unittest.TestCase):

    def test_basic(self):
        self.assertEqual(normalize_numero_csv("1.1.1.1"), "01.01.01.001")

    def test_larger_numbers(self):
        self.assertEqual(normalize_numero_csv("8.1.1.1"), "08.01.01.001")
        self.assertEqual(normalize_numero_csv("1.1.2.8"), "01.01.02.008")

    def test_already_padded(self):
        self.assertEqual(normalize_numero_csv("01.01.01.001"), "01.01.01.001")

    def test_wrong_segments(self):
        self.assertEqual(normalize_numero_csv("1.1.1"), "1.1.1")
        self.assertEqual(normalize_numero_csv("1.1.1.1.1"), "1.1.1.1.1")

    def test_empty(self):
        self.assertEqual(normalize_numero_csv(""), "")
        self.assertEqual(normalize_numero_csv(None), "")

    def test_non_numeric(self):
        self.assertEqual(normalize_numero_csv("a.b.c.d"), "a.b.c.d")


class TestResolvePrefixoCap(unittest.TestCase):

    def setUp(self):
        self.areas_map = {
            "CGBEN": "01",
            "DIGEP": "05",
            "DIGEP-RO": "05.01",
            "DIGEP-RR": "05.02",
            "CGRIS": "06",
            "COGES": "10",
        }

    def test_area_normal(self):
        self.assertEqual(resolve_prefixo_cap("CGBEN", self.areas_map), "01")
        self.assertEqual(resolve_prefixo_cap("CGRIS", self.areas_map), "06")
        self.assertEqual(resolve_prefixo_cap("COGES", self.areas_map), "10")

    def test_subarea_returns_parent(self):
        self.assertEqual(resolve_prefixo_cap("DIGEP-RO", self.areas_map), "05")
        self.assertEqual(resolve_prefixo_cap("DIGEP-RR", self.areas_map), "05")

    def test_area_pai_direta(self):
        self.assertEqual(resolve_prefixo_cap("DIGEP", self.areas_map), "05")

    def test_unknown_area(self):
        self.assertEqual(resolve_prefixo_cap("XPTO", self.areas_map), "XPTO")


class TestResolvePrefixoCp(unittest.TestCase):

    def setUp(self):
        self.areas_map = {
            "CGBEN": "01",
            "DIGEP": "05",
            "DIGEP-RO": "05.01",
            "DIGEP-RR": "05.02",
            "CGRIS": "06",
            "COATE": "03",
            "COGES": "10",
        }

    def test_area_normal(self):
        self.assertEqual(resolve_prefixo_cp("CGBEN", self.areas_map), "01")
        self.assertEqual(resolve_prefixo_cp("COATE", self.areas_map), "03")
        self.assertEqual(resolve_prefixo_cp("COGES", self.areas_map), "10")

    def test_subarea_includes_full_prefix(self):
        """CP inclui subárea (diferente do CAP que retorna só área pai)."""
        self.assertEqual(resolve_prefixo_cp("DIGEP-RO", self.areas_map), "05.01")
        self.assertEqual(resolve_prefixo_cp("DIGEP-RR", self.areas_map), "05.02")

    def test_area_pai_direta(self):
        self.assertEqual(resolve_prefixo_cp("DIGEP", self.areas_map), "05")

    def test_unknown_area_raises_valueerror(self):
        """Fail-fast: área desconhecida levanta ValueError."""
        with self.assertRaises(ValueError):
            resolve_prefixo_cp("XPTO", self.areas_map)

    def test_empty_area_raises_valueerror(self):
        with self.assertRaises(ValueError):
            resolve_prefixo_cp("", self.areas_map)


if __name__ == '__main__':
    unittest.main()
