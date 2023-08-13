import utime as time


class DisplayLine:
    def __init__(self, num_visible_chars: int, autoscroll_speed_ms: int):
        self._num_visible_chars = num_visible_chars
        self._autoscroll_speed_ms = autoscroll_speed_ms
        self._last_autoscroll_on = 0  # Timestamp
        self.set_text("")

    def should_refresh(self) -> bool:
        if not self._text_getter_called:
            return True
        return self._should_autoscroll()

    def _should_autoscroll(self) -> bool:
        if not self._text_getter_called:
            return False

        if len(self._text) <= self._num_visible_chars:
            return False

        elapsed = abs(time.ticks_diff(time.ticks_ms(), self._last_autoscroll_on))
        return elapsed >= self._autoscroll_speed_ms

    def get_text(self) -> str:
        should_autoscroll = self._should_autoscroll()

        if not self._text_getter_called:
            self._text_getter_called = True
            self._last_autoscroll_on = time.ticks_ms()

        if should_autoscroll:
            self._text_head = (self._text_head + 1) % len(self._text)
            self._text_tail = (self._text_tail + 1) % len(self._text)
            self._last_autoscroll_on = time.ticks_ms()

        if self._text_tail < self._text_head:
            return self._text[self._text_head :] + self._text[: self._text_tail + 1]
        else:
            return self._text[self._text_head : self._text_tail + 1]

    def set_text(self, text: str):
        if len(text) < self._num_visible_chars:
            # Pad text so it has the same number of characters as the number of
            # visible characters per LCD line. This makes sure that any previous
            # text is overwritten when the new text is written to the LCD.
            self._text = "{:<{}}".format(text, self._num_visible_chars)
        elif len(text) > self._num_visible_chars:
            # If text has more characters than the number of visible characters,
            # add 3 spaces to the end of the text so there is a gap between the
            # end of the text and the start of the text when it loops around.
            self._text = text + "   "
        else:
            # If text has the same number of characters as the number of visible
            # characters, we can use it as is.
            self._text = text

        self._text_getter_called = False
        self._text_head = 0
        self._text_tail = self._num_visible_chars - 1
