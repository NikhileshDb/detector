class PresenceStabilizer:
    def __init__(
        self,
        visible_required: int,
        hidden_required: int,
    ):
        self.visible_required = (
            visible_required
        )

        self.hidden_required = (
            hidden_required
        )

        self._visible_count = 0
        self._hidden_count = 0

    def push(
        self,
        visible: bool,
    ) -> tuple[bool, bool]:

        if visible:
            self._visible_count += 1
            self._hidden_count = 0

        else:
            self._hidden_count += 1
            self._visible_count = 0

        stable_visible = (
            self._visible_count
            >= self.visible_required
        )

        stable_hidden = (
            self._hidden_count
            >= self.hidden_required
        )

        return (
            stable_visible,
            stable_hidden,
        )

    def reset(self):
        self._visible_count = 0
        self._hidden_count = 0
