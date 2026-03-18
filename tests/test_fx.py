import unittest

from martin import App, Container, fx
from martin.fx import (
    FX_CSS,
    FX_JS,
    FadeIn,
    HoverGlow,
    HoverLift,
    ReducedMotion,
    RevealOnScroll,
    SlideIn,
    Stagger,
    Transition,
)
from martin_fx import Pulse


class FxTests(unittest.TestCase):
    def test_fx_submodule_is_reexported_from_martin(self):
        self.assertIs(fx.FadeIn, FadeIn)
        self.assertIs(fx.HoverLift, HoverLift)

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
        self.assertEqual(transition["transition"], "transform 0.3s ease-out 0s")

    def test_hover_and_reveal_effects_inject_data_attrs(self):
        html = Container(
            "Hola",
            class_name="card-shell",
            style=[
                HoverLift(distance=10),
                HoverGlow("#22c55e"),
                RevealOnScroll(direction="right", distance=36, blur=8, once=False),
                ReducedMotion.all(),
            ],
        ).render()

        self.assertIn('class="card-shell"', html)
        self.assertIn('data-martin-fx-hover="transform shadow border"', html)
        self.assertIn('data-martin-fx-reveal="repeat"', html)
        self.assertIn('data-martin-fx-reduce="animation transition reveal hover"', html)
        self.assertIn("--martin-fx-reveal-x: -36px", html)
        self.assertIn("--martin-fx-reveal-blur: 8px", html)

    def test_stagger_delay_can_target_animation_and_transition(self):
        css = Stagger(index=3, step=0.1, start=0.05, target="both").to_css()
        self.assertEqual(css["animation-delay"], "0.35s")
        self.assertEqual(css["transition-delay"], "0.35s")
        self.assertEqual(Stagger.delay(2, step=0.08, start=0.04), "0.2s")

    def test_transition_hover_composition_returns_nested_style_list(self):
        html = Container(
            "CTA",
            style=Transition("transform", duration=0.28).hover(
                "translateY(-4px)", shadow="0 12px 24px rgba(0,0,0,0.12)"
            ),
        ).render()
        self.assertIn("transition: transform 0.28s ease 0s", html)
        self.assertIn('data-martin-fx-hover="transform shadow"', html)
        self.assertIn("--martin-fx-hover-transform: translateY(-4px)", html)

    def test_app_injects_fx_stylesheet_and_bootstrap_script_automatically(self):
        app = App(
            build=lambda: Container(
                children=["Hola"],
                style=[FadeIn(), Transition(), RevealOnScroll()],
            )
        )
        html = app._render("/")
        self.assertIn("@keyframes martin-fx-fade-in", html)
        self.assertIn(FX_CSS, html)
        self.assertIn(FX_JS, html)
        self.assertIn("window._martinFxInit", html)


if __name__ == "__main__":
    unittest.main()
