import asyncio
import threading
import time
from pathlib import Path

import cv2
import easyocr
import uvicorn

from api.app import create_app
from api.websocket_manager import ConnectionManager

from capture.camera_source import CameraSource

from config.roi_config import load_roi_config
from config.setup_rois import configure_rois

from detection.easyocr_number_recognizer import (
    EasyOcrNumberRecognizer,
)
from detection.game_status_recognizer import (
    GameStatusRecognizer,
)
from detection.reference_store import (
    load_reference,
    save_reference,
)
from detection.result_evidence_validator import (
    ResultEvidenceValidator,
)
from detection.result_stabilizer import (
    ResultStabilizer,
)
from detection.result_state_detector import (
    ResultStateDetector,
)
from detection.roi_processor import RoiProcessor
from detection.status_result_recognizer import (
    StatusResultRecognizer,
)

from detector.status import DetectorStatusHolder

from domain.detector_state import DetectorState
from domain.game_status import GameStatus
from domain.roulette_result import ResultEvidence
from domain.round_state_machine import RoundStateMachine

from events.event_publisher import EventPublisher
from events.event_types import (
    RoundStartedEvent,
    SpinConfirmedEvent,
    StateChangedEvent,
)

from storage.database import Database
from storage.models import SpinSource
from storage.round_repository import RoundRepository
from storage.spin_repository import SpinRepository


# ============================================================
# CONFIG
# ============================================================

ROI_CONFIG_PATH = "roi_config.json"

RESULT_REFERENCE_PATH = (
    "references/result_idle.png"
)

CAMERA_INDEX = 1

STATUS_OCR_INTERVAL_SECONDS = 0.30
RESULT_OCR_INTERVAL_SECONDS = 0.20

API_HOST = "0.0.0.0"
API_PORT = 8000


# ============================================================
# API SERVER (background thread)
# ============================================================

def start_api_server(app):
    """Runs Uvicorn on its own asyncio event loop in a background
    thread, so the blocking cv2 loop can keep the main thread (required
    for cv2's GUI calls on Windows)."""

    config = uvicorn.Config(
        app,
        host=API_HOST,
        port=API_PORT,
        log_level="warning",
    )

    server = uvicorn.Server(config)

    def run():
        asyncio.run(server.serve())

    thread = threading.Thread(
        target=run,
        daemon=True,
    )

    thread.start()

    return server, thread


# ============================================================
# DRAW ROI
# ============================================================

def draw_roi(
    frame,
    roi,
    label: str,
    color,
):

    cv2.rectangle(
        frame,
        (roi.x, roi.y),
        (
            roi.x + roi.width,
            roi.y + roi.height,
        ),
        color,
        2,
    )

    cv2.putText(
        frame,
        label,
        (
            roi.x,
            max(20, roi.y - 8),
        ),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        color,
        2,
    )


# ============================================================
# MAIN
# ============================================================

def main():

    # ========================================================
    # DATABASE
    # ========================================================

    database = Database()
    database.initialize()

    round_repository = RoundRepository(
        database
    )

    spin_repository = SpinRepository(
        database
    )

    # ========================================================
    # API / EVENTS
    # ========================================================

    connection_manager = ConnectionManager()

    detector_status_holder = DetectorStatusHolder()

    event_publisher = EventPublisher(
        connection_manager
    )

    api_app = create_app(
        database=database,
        round_repository=round_repository,
        spin_repository=spin_repository,
        connection_manager=connection_manager,
        event_publisher=event_publisher,
    )

    api_app.state.detector_status_holder = (
        detector_status_holder
    )

    api_server, api_thread = start_api_server(
        api_app
    )

    print(
        f"API running on "
        f"http://{API_HOST}:{API_PORT} "
        f"(docs at /docs)"
    )

    def publish_state():

        detector_status_holder.update(
            state_machine.state,
            state_machine.round_id,
        )

        event_publisher.publish(
            StateChangedEvent(
                state=state_machine.state.name,
                round_id=state_machine.round_id,
            )
        )

    # ========================================================
    # CAMERA
    # ========================================================

    source = CameraSource(
        camera_index=CAMERA_INDEX,
    )

    # ========================================================
    # STATE
    # ========================================================

    state_machine = RoundStateMachine()

    current_db_round_id = None

    latest_round = (
        round_repository.latest()
    )

    if latest_round is not None:

        state_machine.round_id = (
            latest_round.sequence
        )

        current_db_round_id = (
            latest_round.id
        )

        print(
            f"Resuming after round "
            f"{latest_round.sequence}"
        )

    # ========================================================
    # OCR
    # ========================================================

    print(
        "Initializing OCR..."
    )

    ocr_reader = easyocr.Reader(
        ["en"],
        gpu=True,
    )

    number_recognizer = (
        EasyOcrNumberRecognizer(
            reader=ocr_reader,
            min_confidence=0.60,
        )
    )

    status_result_recognizer = (
        StatusResultRecognizer(
            reader=ocr_reader,
            min_confidence=0.50,
        )
    )

    game_status_recognizer = (
        GameStatusRecognizer(
            reader=ocr_reader,
        )
    )

    evidence_validator = (
        ResultEvidenceValidator()
    )

    stabilizer = ResultStabilizer(
        required_matches=3,
    )

    # ========================================================
    # ROI / RESULT DETECTOR
    # ========================================================

    roi_config = None
    result_detector = None

    last_status_ocr_time = 0.0
    last_result_ocr_time = 0.0

    # Keep latest result evidence from status ROI.
    latest_status_result = None

    try:

        source.start()

        print()
        print(
            "================================"
        )
        print(
            " Roulette Analytics Detector"
        )
        print(
            "================================"
        )
        print()
        print(
            "Q = Quit"
        )
        print(
            "R = Configure ROIs"
        )
        print(
            "B = Capture result baseline"
        )
        print()

        # ====================================================
        # ROI CONFIG
        # ====================================================

        if Path(
            ROI_CONFIG_PATH
        ).exists():

            try:

                roi_config = (
                    load_roi_config(
                        ROI_CONFIG_PATH
                    )
                )

                print(
                    "Loaded ROI configuration."
                )

            except Exception as exc:

                print(
                    f"ROI config error: {exc}"
                )

        # ====================================================
        # RESULT REFERENCE
        # ====================================================

        reference = load_reference(
            RESULT_REFERENCE_PATH
        )

        if reference is not None:

            result_detector = (
                ResultStateDetector(
                    reference
                )
            )

            print(
                "Loaded result idle reference."
            )

        # ====================================================
        # MAIN LOOP
        # ====================================================

        while True:

            frame = source.read()

            if frame is None:
                continue

            preview = frame.copy()

            status_frame = None
            result_frame = None
            number_frame = None

            # =================================================
            # ROI
            # =================================================

            if roi_config is not None:

                status_frame = (
                    RoiProcessor.crop(
                        frame,
                        roi_config.countdown,
                    )
                )

                result_frame = (
                    RoiProcessor.crop(
                        frame,
                        roi_config.result,
                    )
                )

                number_frame = (
                    RoiProcessor.crop(
                        frame,
                        roi_config.number,
                    )
                )

                draw_roi(
                    preview,
                    roi_config.countdown,
                    "STATUS",
                    (255, 255, 0),
                )

                draw_roi(
                    preview,
                    roi_config.result,
                    "RESULT",
                    (0, 255, 0),
                )

                draw_roi(
                    preview,
                    roi_config.number,
                    "NUMBER",
                    (255, 0, 255),
                )

                cv2.imshow(
                    "Status ROI",
                    status_frame,
                )

                cv2.imshow(
                    "Result ROI",
                    result_frame,
                )

                cv2.imshow(
                    "Number ROI",
                    number_frame,
                )

            # =================================================
            # STATUS REGION OCR
            # =================================================

            if (
                status_frame
                is not None
            ):

                now = time.monotonic()

                if (
                    now
                    - last_status_ocr_time
                    >= STATUS_OCR_INTERVAL_SECONDS
                ):

                    last_status_ocr_time = now

                    # -----------------------------------------
                    # 1. GAME LIFECYCLE OCR
                    # -----------------------------------------

                    game_status = (
                        game_status_recognizer
                        .recognize(
                            status_frame
                        )
                    )

                    # -----------------------------------------
                    # 2. RESULT OCR
                    #
                    # This can detect:
                    #
                    # 23 RED
                    # 8 BLACK
                    # -----------------------------------------

                    latest_status_result = (
                        status_result_recognizer
                        .recognize(
                            status_frame
                        )
                    )

                    # =========================================
                    # PLACE YOUR BETS
                    # =========================================

                    if (
                        game_status
                        == GameStatus.PLACE_YOUR_BETS
                    ):

                        previous_detector_state = state_machine.state

                        event = (
                            state_machine
                            .on_place_your_bets()
                        )

                        if event is not None:

                            # ---------------------------------
                            # Previous round missing?
                            # ---------------------------------

                            if (
                                current_db_round_id
                                is not None
                                and previous_detector_state
                                not in {
                                    DetectorState.READING_RESULT,
                                    DetectorState.RESULT_CONFIRMED,
                                }
                            ):

                                previous_spin = (
                                    spin_repository
                                    .get_by_round(
                                        current_db_round_id
                                    )
                                )

                                if (
                                    previous_spin
                                    is None
                                ):

                                    round_repository.mark_missing(
                                        current_db_round_id
                                    )

                                    print(
                                        "Previous unresolved "
                                        "round marked MISSING."
                                    )

                            # ---------------------------------
                            # New round
                            # ---------------------------------

                            stored_round = (
                                round_repository
                                .create(
                                    sequence=(
                                        event.round_id
                                    )
                                )
                            )

                            current_db_round_id = (
                                stored_round.id
                            )

                            latest_status_result = None

                            stabilizer.reset_candidate()

                            print()
                            print(
                                "============================"
                            )
                            print(
                                f"ROUND "
                                f"{event.round_id} STARTED"
                            )
                            print(
                                f"DB ROUND ID: "
                                f"{current_db_round_id}"
                            )
                            print(
                                "============================"
                            )
                            print()

                            event_publisher.publish(
                                RoundStartedEvent(
                                    round_id=event.round_id
                                )
                            )

                            publish_state()

                    # =========================================
                    # BETS CLOSING
                    # =========================================

                    elif (
                        game_status
                        == GameStatus.BETS_CLOSING
                    ):

                        if (
                            state_machine
                            .on_bets_closing()
                        ):

                            print(
                                f"Round "
                                f"{state_machine.round_id}: "
                                "bets closing."
                            )

                            publish_state()

                    # =========================================
                    # BETS CLOSED
                    # =========================================

                    elif (
                        game_status
                        == GameStatus.BETS_CLOSED
                    ):

                        if (
                            state_machine
                            .on_bets_closed()
                        ):

                            stabilizer.reset_candidate()

                            if (
                                current_db_round_id
                                is not None
                            ):

                                round_repository.mark_waiting_for_result(
                                    current_db_round_id
                                )

                            print(
                                f"Round "
                                f"{state_machine.round_id}: "
                                "bets closed."
                            )

                            print(
                                "Waiting for result..."
                            )

                            publish_state()

                    # =========================================
                    # NEXT GAME SOON
                    # =========================================

                    elif (
                        game_status
                        == GameStatus.NEXT_GAME_SOON
                    ):

                        if (
                            state_machine
                            .on_next_game_soon()
                        ):

                            print(
                                f"Round "
                                f"{state_machine.round_id}: "
                                "next game soon."
                            )

                            publish_state()

                    # =========================================
                    # RESULT TEXT DETECTED
                    #
                    # Example:
                    #
                    # 23 RED
                    # =========================================

                    if (
                        latest_status_result
                        is not None
                    ):

                        if (
                            state_machine.state
                            in {
                                DetectorState.WAITING_FOR_RESULT,
                                DetectorState.BETS_CLOSING,
                                DetectorState.NEXT_GAME_SOON,
                            }
                        ):

                            entered = (
                                state_machine
                                .on_result_visible()
                            )

                            if entered:

                                stabilizer.reset_candidate()

                                print()
                                print(
                                    "Winning result text detected:"
                                )

                                print(
                                    f"{latest_status_result.number} "
                                    f"{latest_status_result.color.value}"
                                )

                                publish_state()

            # =================================================
            # DUAL RESULT OCR
            # =================================================

            if (
                status_frame
                is not None
                and number_frame
                is not None
                and state_machine.state
                == DetectorState.READING_RESULT
            ):

                now = time.monotonic()

                if (
                    now
                    - last_result_ocr_time
                    >= RESULT_OCR_INTERVAL_SECONDS
                ):

                    last_result_ocr_time = now

                    # -----------------------------------------
                    # STATUS RESULT
                    # -----------------------------------------

                    status_result = (
                        status_result_recognizer
                        .recognize(
                            status_frame
                        )
                    )

                    # -----------------------------------------
                    # NUMBER RESULT
                    # -----------------------------------------

                    number_result = (
                        number_recognizer
                        .recognize(
                            number_frame
                        )
                    )

                    if status_result:

                        print(
                            "STATUS RESULT: "
                            f"{status_result.number} "
                            f"{status_result.color.value} "
                            f"confidence="
                            f"{status_result.confidence:.3f}"
                        )

                    if number_result:

                        print(
                            "NUMBER ROI: "
                            f"{number_result.number} "
                            f"confidence="
                            f"{number_result.confidence:.3f}"
                        )

                    # -----------------------------------------
                    # EVIDENCE
                    # -----------------------------------------

                    evidence = ResultEvidence(

                        status_number=(
                            status_result.number
                            if status_result
                            else None
                        ),

                        status_color=(
                            status_result.color
                            if status_result
                            else None
                        ),

                        status_confidence=(
                            status_result.confidence
                            if status_result
                            else None
                        ),

                        number_roi_number=(
                            number_result.number
                            if number_result
                            else None
                        ),

                        number_roi_confidence=(
                            number_result.confidence
                            if number_result
                            else None
                        ),
                    )

                    validated = (
                        evidence_validator
                        .validate(
                            evidence
                        )
                    )

                    if validated:

                        print(
                            "VALIDATED: "
                            f"{validated.number} "
                            f"{validated.color.value}"
                        )

                    # -----------------------------------------
                    # STABILIZE
                    # -----------------------------------------

                    confirmed = (
                        stabilizer.push(
                            validated
                        )
                    )

                    if (
                        confirmed
                        is not None
                    ):

                        accepted = (
                            state_machine
                            .on_result_confirmed()
                        )

                        print(
                            f"DEBUG confirmed="
                            f"{confirmed.number}, "
                            f"accepted={accepted}, "
                            f"db_round="
                            f"{current_db_round_id}"
                        )

                        if accepted:

                            print()
                            print(
                                "================================"
                            )
                            print(
                                f"ROUND: "
                                f"{state_machine.round_id}"
                            )
                            print(
                                f"SPIN CONFIRMED: "
                                f"{confirmed.number}"
                            )
                            print(
                                f"COLOR: "
                                f"{confirmed.color.value}"
                            )
                            print(
                                f"CONFIDENCE: "
                                f"{confirmed.confidence:.3f}"
                            )
                            print(
                                "================================"
                            )

                            # =================================
                            # SAVE
                            # =================================

                            if (
                                current_db_round_id
                                is None
                            ):

                                print(
                                    "ERROR: no active DB round"
                                )

                            else:

                                existing_spin = (
                                    spin_repository
                                    .get_by_round(
                                        current_db_round_id
                                    )
                                )

                                if (
                                    existing_spin
                                    is None
                                ):

                                    stored_spin = (
                                        spin_repository
                                        .create(

                                            round_id=(
                                                current_db_round_id
                                            ),

                                            number=(
                                                confirmed.number
                                            ),

                                            color=(
                                                confirmed.color.value
                                            ),

                                            source=(
                                                SpinSource.AUTO
                                            ),

                                            confidence=(
                                                confirmed.confidence
                                            ),
                                        )
                                    )

                                    round_repository.mark_completed(
                                        current_db_round_id
                                    )

                                    print(
                                        f"Stored spin: "
                                        f"{stored_spin.id}"
                                    )

                                    publish_state()

                                    event_publisher.publish(
                                        SpinConfirmedEvent(
                                            round_id=(
                                                current_db_round_id
                                            ),
                                            number=(
                                                confirmed.number
                                            ),
                                            color=(
                                                confirmed.color.value
                                            ),
                                            confidence=(
                                                confirmed.confidence
                                            ),
                                        )
                                    )

                                else:

                                    print(
                                        "Duplicate spin ignored."
                                    )

            # =================================================
            # OVERLAY
            # =================================================

            cv2.putText(
                preview,
                (
                    f"State: "
                    f"{state_machine.state.name}"
                ),
                (30, 50),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 255, 255),
                2,
            )

            cv2.putText(
                preview,
                (
                    f"Round: "
                    f"{state_machine.round_id}"
                ),
                (30, 90),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 255, 255),
                2,
            )

            cv2.imshow(
                "Roulette Capture",
                preview,
            )

            # =================================================
            # KEYS
            # =================================================

            key = (
                cv2.waitKey(1)
                & 0xFF
            )

            if key == ord("q"):
                break

            if key == ord("r"):

                new_config = (
                    configure_rois(
                        frame,
                        ROI_CONFIG_PATH,
                    )
                )

                if new_config:

                    roi_config = (
                        new_config
                    )

            if (
                key == ord("b")
                and result_frame
                is not None
            ):

                save_reference(
                    result_frame,
                    RESULT_REFERENCE_PATH,
                )

                result_detector = (
                    ResultStateDetector(
                        result_frame
                    )
                )

                print(
                    "Result idle reference captured."
                )

    finally:

        source.stop()

        cv2.destroyAllWindows()

        api_server.should_exit = True

        api_thread.join(timeout=5)


if __name__ == "__main__":
    main()
