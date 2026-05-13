import unittest

from martin import Table


class TableExportTests(unittest.TestCase):
    def test_export_buttons_and_public_api_are_rendered(self):
        html = Table(
            headers=["Nombre", "Ciudad"],
            rows=[["Ana", "Bogota"], ["Luis", "Quito"]],
            searchable=True,
            sortable=True,
            page_size=10,
            export_formats=["csv", "json", "excel", "pdf"],
            export_filename="usuarios",
        ).render()
        self.assertIn('data-export="csv"', html)
        self.assertIn('data-export="json"', html)
        self.assertIn('data-export="excel"', html)
        self.assertIn('data-export="pdf"', html)
        self.assertIn('window[uid+"_export"]', html)
        self.assertIn("function _doCsv()", html)
        self.assertIn("function _doJson()", html)
        self.assertIn("function _doExcel()", html)
        self.assertIn("function _doPdf()", html)
        self.assertIn("var _exportFilename=", html)

    def test_true_export_formats_enables_all(self):
        html = Table(
            headers=["A"],
            rows=[["1"]],
            export_formats=True,
        ).render()
        self.assertIn('data-export="csv"', html)
        self.assertIn('data-export="json"', html)
        self.assertIn('data-export="excel"', html)
        self.assertIn('data-export="pdf"', html)


if __name__ == "__main__":
    unittest.main()
