import re

import cv2


from domain.game_status import GameStatus


class GameStatusRecognizer:
    def __init__(
        self,
        reader,
    ):
        self.reader = reader

    def recognize(
        self,
        frame,
    ) -> GameStatus:

        gray = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2GRAY,
        )

        results = self.reader.readtext(
            gray,
            detail=0,
            paragraph=True,
        )

        if not results:
            return GameStatus.UNKNOWN

        raw_text = " ".join(results)

        normalized = self._normalize(
            raw_text
        )

        print(
            f"GAME STATUS OCR: {normalized}"
        )

        # -------------------------
        # PLACE YOUR BETS
        # -------------------------

        if (
            "PLACE" in normalized
            and "BET" in normalized
        ):
            return (
                GameStatus.PLACE_YOUR_BETS
            )

        # -------------------------
        # BETS CLOSING
        # -------------------------

        if (
            "BET" in normalized
            and "CLOSING" in normalized
        ):
            return (
                GameStatus.BETS_CLOSING
            )

        # -------------------------
        # BETS CLOSED
        # -------------------------

        if (
            "BET" in normalized
            and "CLOSED" in normalized
        ):
            return (
                GameStatus.BETS_CLOSED
            )

        # -------------------------
        # NEXT GAME SOON
        # -------------------------

        if (
            "NEXT" in normalized
            and "GAME" in normalized
        ):
            return (
                GameStatus.NEXT_GAME_SOON
            )

        return GameStatus.UNKNOWN

    def _normalize(
        self,
        text: str,
    ) -> str:

        value = text.upper()

        value = value.replace(
            "\n",
            " ",
        )

        value = re.sub(
            r"\s+",
            " ",
            value,
        )

        return value.strip()
