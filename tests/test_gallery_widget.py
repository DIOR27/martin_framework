import unittest

from martin import Gallery, GalleryItem


class GalleryWidgetTests(unittest.TestCase):
    def test_lightbox_opens_clicked_index_not_uid_number(self):
        html = Gallery(
            id="gal_2",
            items=[
                GalleryItem("/a.svg", title="A"),
                GalleryItem("/b.svg", title="B"),
                GalleryItem("/c.svg", title="C"),
                GalleryItem("/d.svg", title="D"),
                GalleryItem("/e.svg", title="E"),
            ],
            lightbox=True,
        ).render()

        self.assertIn("_galOpenFn('gal_2',4)", html)
        self.assertIn('onclick="_galCloseFn(\'gal_2\')"', html)
        self.assertIn('onclick="_galPrevFn(\'gal_2\')"', html)
        self.assertIn('onclick="_galNextFn(\'gal_2\')"', html)
        self.assertNotIn("oc.match(/[0-9]+/)", html)

    def test_masonry_has_responsive_columns_and_inline_blocks(self):
        html = Gallery(
            items=[
                GalleryItem("/a.svg", title="A"),
                GalleryItem("/b.svg", title="B"),
                GalleryItem("/c.svg", title="C"),
            ],
            columns=3,
            masonry=True,
            gap=12,
        ).render()

        self.assertIn("column-count:3;", html)
        self.assertIn("@media(max-width:960px)", html)
        self.assertIn("column-count:2!important;", html)
        self.assertIn("@media(max-width:640px)", html)
        self.assertIn("column-count:1!important;", html)
        self.assertIn("display:inline-block;width:100%;vertical-align:top;", html)


if __name__ == "__main__":
    unittest.main()
