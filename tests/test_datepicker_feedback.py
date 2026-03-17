import unittest

from martin import DatePicker


class DatePickerFeedbackTests(unittest.TestCase):
    def test_range_mode_updates_display_after_first_pick(self):
        DatePicker._id_counter = 0
        html = DatePicker(
            range=True,
            placeholder_start="¿Cuándo sales?",
            placeholder_end="¿Cuándo vuelves?",
        ).render()
        self.assertIn(
            "if(af==='start'||(!s1&&!s2)){s1=iso;s2='';af='end';updDisp();render();}",
            html,
        )


if __name__ == "__main__":
    unittest.main()
