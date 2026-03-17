import unittest

from martin import Map


class MapLayeringTests(unittest.TestCase):
    def test_map_isolated_stacking_context(self):
        Map._id_counter = 0
        html = Map(search=True, geolocation=True).render()
        self.assertIn("isolation:isolate", html)
        self.assertIn("contain:paint", html)
        self.assertIn('z-index:30', html)
        self.assertIn("position:relative;z-index:1;width:100%", html)


if __name__ == "__main__":
    unittest.main()
