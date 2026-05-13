import unittest

from martin import Table


class TableWidgetTests(unittest.TestCase):
    def test_sorting_script_reorders_rows_in_dom(self):
        html = Table(
            headers=["Ciudad"],
            rows=[["Bogota"], ["Cali"], ["Medellin"]],
            sortable=True,
            page_size=2,
        ).render()
        self.assertIn("var _rowsEls=[];", html)
        self.assertIn('tbody.innerHTML=""', html)
        self.assertIn("tbody.appendChild(r);", html)
        self.assertNotIn('querySelectorAll("tr")', html)


if __name__ == "__main__":
    unittest.main()
