"""
Alarm Service – plays alert sound for high/critical threats (Windows)
"""
import threading
import platform


def play_alarm(duration_ms: int = 3000, freq: int = 1000):
    """Play an alarm beep in a background thread (Windows only)."""
    if platform.system() != "Windows":
        return

    def _beep():
        try:
            import winsound
            for _ in range(3):
                winsound.Beep(freq, duration_ms)
        except Exception:
            pass

    t = threading.Thread(target=_beep, daemon=True)
    t.start()
