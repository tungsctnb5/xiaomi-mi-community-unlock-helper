"""Timing inputs that keep their text area readable across Qt styles and DPI."""

from PySide6.QtCore import QEvent, QSize, Qt
from PySide6.QtWidgets import QGridLayout, QLabel, QLayout, QSizePolicy, QSpinBox, QVBoxLayout, QWidget


class TimingSpinBox(QSpinBox):
    def __init__(self, number, value, parent=None):
        super().__init__(parent)
        self.setObjectName(f"attemptOffset{number}")
        self.setAccessibleName(f"Attempt {number} arrival offset in milliseconds")
        self.setRange(-2000, 5000)
        self.setSuffix(" ms")
        self.setValue(value)
        self.setAlignment(Qt.AlignCenter)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.ensurePolished()
        self._update_minimum()

    def sizeHint(self):
        # Include the full signed value, suffix, padding and separate step buttons.
        metrics = self.fontMetrics()
        text_width = max(metrics.horizontalAdvance(f"{value} ms")
                         for value in (self.minimum(), self.maximum()))
        return super().sizeHint().expandedTo(
            QSize(max(160, text_width + 76), max(46, metrics.height() + 24)))

    def minimumSizeHint(self):
        return self.sizeHint()

    def _update_minimum(self):
        self.setMinimumSize(self.minimumSizeHint())
        self.updateGeometry()

    def changeEvent(self, event):
        super().changeEvent(event)
        if event.type() in (QEvent.FontChange, QEvent.StyleChange):
            self._update_minimum()


class AttemptFields(QWidget):
    """Four equal columns on wide windows, two columns on compact windows."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("attemptFields")
        self.grid = QGridLayout(self)
        # Let the widget shrink to its two-column minimum even after a wide layout.
        self.grid.setSizeConstraint(QLayout.SetNoConstraint)
        self.grid.setContentsMargins(0, 0, 0, 0)
        self.grid.setHorizontalSpacing(12)
        self.grid.setVerticalSpacing(12)
        self.spins = []
        self.fields = []
        self.columns = 0
        for number, value in enumerate((-100, 20, 120, 300), start=1):
            field = QWidget(self)
            field.setObjectName("attemptField")
            layout = QVBoxLayout(field)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(6)
            label = QLabel(f"Attempt {number}")
            label.setObjectName("fieldName")
            spin = TimingSpinBox(number, value, field)
            label.setBuddy(spin)
            layout.addWidget(label)
            layout.addWidget(spin)
            self.spins.append(spin)
            self.fields.append(field)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        self._arrange(2)

    def _arrange(self, columns):
        if columns == self.columns:
            return
        for field in self.fields:
            self.grid.removeWidget(field)
        for column in range(4):
            self.grid.setColumnStretch(column, int(column < columns))
        for index, field in enumerate(self.fields):
            self.grid.addWidget(field, index // columns, index % columns)
        self.columns = columns
        self.updateGeometry()

    def minimumSizeHint(self):
        if not self.fields:
            return super().minimumSizeHint()
        width = max(field.minimumSizeHint().width() for field in self.fields)
        return QSize(2 * width + 12, self.grid.minimumSize().height())

    def resizeEvent(self, event):
        super().resizeEvent(event)
        width = max(spin.minimumSizeHint().width() for spin in self.spins)
        self._arrange(4 if event.size().width() >= 4 * width + 36 else 2)
