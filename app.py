import logging
import sys

from PyQt6 import QtWidgets

from .main_window import FootingRebuildMainWindow


def main():
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(name)s %(levelname)s: %(message)s',
    )
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle('Fusion')
    window = FootingRebuildMainWindow()
    window.show()
    return app.exec()


if __name__ == '__main__':
    raise SystemExit(main())
