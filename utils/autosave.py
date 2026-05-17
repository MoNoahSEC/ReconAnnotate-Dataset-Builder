"""
Auto-save manager — periodic and event-driven project state persistence.
"""
import os
import json
from PyQt6.QtCore import QTimer, QObject, pyqtSignal


class AutoSaveManager(QObject):
    """Docstring"""
    auto_saved = pyqtSignal()

    AUTOSAVE_FILENAME = ".annotation_tool_autosave.json"

    def __init__(self, project_model, interval_ms: int = 60000, parent=None):
        """Docstring"""
        super().__init__(parent)
        self._project = project_model
        self._save_path = ""

        self._timer = QTimer(self)
        self._timer.setInterval(interval_ms)
        self._timer.timeout.connect(self.save)

    def start(self, folder: str):
        """Docstring"""
        self._save_path = os.path.join(folder, self.AUTOSAVE_FILENAME)
        self._timer.start()

    def stop(self):
        """Docstring"""
        self._timer.stop()

    def save(self):
        """Docstring"""
        if not self._save_path or not self._project.source_folder:
            return
        try:
            self._project.save_to_file(self._save_path)
            self.auto_saved.emit()
        except Exception as e:
            print(f"Auto-save failed: {e}")

    def save_now(self):
        """Docstring"""
        self.save()

    @classmethod
    def get_autosave_path(cls, folder: str) -> str:
        """Docstring"""
        return os.path.join(folder, cls.AUTOSAVE_FILENAME)

    @classmethod
    def has_autosave(cls, folder: str) -> bool:
        """Docstring"""
        return os.path.exists(cls.get_autosave_path(folder))

    @classmethod
    def load_autosave(cls, folder: str) -> dict:
        """Docstring"""
        path = cls.get_autosave_path(folder)
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    @classmethod
    def remove_autosave(cls, folder: str):
        """Docstring"""
        path = cls.get_autosave_path(folder)
        if os.path.exists(path):
            os.remove(path)
