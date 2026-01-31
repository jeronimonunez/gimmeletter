#!/usr/bin/env python3
"""
GimmeLetter - Aplicación de scroll automático para letras y acordes
Punto de entrada principal
"""

import sys
from PyQt6.QtWidgets import QApplication
from src.ui.main_window import MainWindow


def main():
    """Función principal"""
    app = QApplication(sys.argv)
    app.setApplicationName("GimmeLetter")
    app.setOrganizationName("GimmeLetter")
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
