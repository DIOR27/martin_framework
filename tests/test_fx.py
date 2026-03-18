import unittest

from martin import App, Container, fx
from martin.fx import FX_CSS, FadeIn, SlideIn, Transition
from martin_fx import Pulse


class FxTests(unittest.TestCase):
    def test_fx_submodule_is_reexported_from_martin(self):
        self.assertIs(fx.FadeIn, FadeIn)

    def test_alias_package_reexports_motion_helpers(self):
        pulse = Pulse(duration=1.5)
        css = pulse.to_css()
        self.assertIn("martin-fx-pulse", css["animation"])
        self.assertIn("infinite", css["animation"])

    def test_transition_and_animation_styles_render_expected_css(self):
        fade = FadeIn(duration=0.6, delay=0.15).to_css()
        slide = SlideIn(direction="left", distance=40).to_css()
        transition = Transition("transform", duration=0.3, timing="ease-out").to_css()

        self.assertEqual(
            fade["animation"],
            "martin-fx-fade-in 0.6s ease-out 0.15s 1 normal both",
        )
        self.assertEqual(slide["--martin-fx-x"], "40px")
        self.assertEqual(slide["--martin-fx-y"], "0")
        self.assertEqual(
            transition["transition"], "transform 0.3s ease-out 0s"
        )

    def test_app_injects_fx_stylesheet_automatically(self):
        app = App(
            build=lambda: Container(
                children=["Hola"],
                style=[FadeIn(), Transition()],
            )
        )
        html = app._render("/")
        self.assertIn("@keyframes martin-fx-fade-in", html)
        self.assertIn(FX_CSS, html)


if __name__ == "__main__":
    unittest.main()
