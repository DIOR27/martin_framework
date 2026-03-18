import unittest

from martin import Carousel, CarouselItem, WordCloud


class ResponsiveWidgetsTests(unittest.TestCase):
    def test_carousel_uses_mobile_visible_logic(self):
        Carousel._id_counter = 0
        html = Carousel(
            items=[CarouselItem(image="/a.png"), CarouselItem(image="/b.png"), CarouselItem(image="/c.png")],
            mode="slides",
            visible=3,
            mobile_visible=1,
        ).render()
        self.assertIn("dvis=3", html)
        self.assertIn("mvis=1", html)
        self.assertIn("window.matchMedia", html)
        self.assertIn("n-curVis", html)
        self.assertIn("_syncMode()", html)

    def test_wordcloud_limits_wide_words_on_mobile(self):
        WordCloud._id_counter = 0
        html = WordCloud(words={"JavaScript": 8, "Python": 7}, width=600, height=280).render()
        self.assertIn("maxWordW", html)
        self.assertIn("word._drawSize=size", html)
        self.assertIn("drawSize=word._drawSize||word.size", html)
        self.assertIn("window.innerWidth-48", html)
        self.assertIn('canvas.style.width="100%"', html)
        self.assertIn('canvas.style.aspectRatio=W+"/"+H', html)
        self.assertIn("Segoe UI, Trebuchet MS, Helvetica Neue, Arial, sans-serif", html)


if __name__ == "__main__":
    unittest.main()
