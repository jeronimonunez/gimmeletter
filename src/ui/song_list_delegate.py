"""
Delegate personalizado para items de lista de canciones con botón de menú contextual
"""

from PyQt6.QtWidgets import QStyledItemDelegate, QStyle
from PyQt6.QtCore import Qt, QRect
from PyQt6.QtGui import QFont


class SongListDelegate(QStyledItemDelegate):
    """Delegate personalizado para mostrar '⋯' en hover con botón clickeable"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.hovered_index = None
        self.button_hovered = False
        self.main_window = None  # Se establecerá después de la creación
    
    def paint(self, painter, option, index):
        # Pintar el item normalmente
        super().paint(painter, option, index)
        
        # Si el mouse está sobre este item, dibujar "⋯"
        if option.state & QStyle.StateFlag.State_MouseOver:
            painter.save()
            
            # Área del botón
            button_rect = self.get_button_rect(option.rect)
            
            # Dibujar fondo del botón si está en hover
            if self.button_hovered and self.hovered_index == index.row():
                painter.fillRect(button_rect, option.palette.color(option.palette.ColorGroup.Normal, option.palette.ColorRole.Mid))
            
            # Configurar fuente y color
            font = QFont()
            font.setPointSize(18)
            font.setBold(True)
            painter.setFont(font)
            
            # Color basado en si está seleccionado o no
            if option.state & QStyle.StateFlag.State_Selected:
                painter.setPen(option.palette.color(option.palette.ColorGroup.Normal, option.palette.ColorRole.HighlightedText))
            else:
                painter.setPen(option.palette.color(option.palette.ColorGroup.Normal, option.palette.ColorRole.Text))
            
            # Dibujar "⋯" centrado en el botón
            painter.drawText(button_rect, Qt.AlignmentFlag.AlignCenter, "⋯")
            
            painter.restore()
    
    def get_button_rect(self, item_rect):
        """Calcula el rectángulo del botón"""
        button_width = 40
        button_rect = QRect(item_rect)
        button_rect.setLeft(button_rect.right() - button_width - 10)
        button_rect.setRight(button_rect.right() - 10)
        # Centrar verticalmente con margen
        margin = 5
        button_rect.setTop(button_rect.top() + margin)
        button_rect.setBottom(button_rect.bottom() - margin)
        return button_rect
    
    def editorEvent(self, event, model, option, index):
        # Detectar movimiento del mouse para cambiar cursor
        if event.type() == event.Type.MouseMove:
            button_rect = self.get_button_rect(option.rect)
            pos = event.position().toPoint()
            
            was_hovered = self.button_hovered
            old_index = self.hovered_index
            
            if button_rect.contains(pos):
                self.button_hovered = True
                self.hovered_index = index.row()
                # Cambiar cursor a mano
                self.parent().viewport().setCursor(Qt.CursorShape.PointingHandCursor)
            else:
                self.button_hovered = False
                self.parent().viewport().setCursor(Qt.CursorShape.ArrowCursor)
            
            # Forzar repintado si cambió el estado
            if was_hovered != self.button_hovered or old_index != self.hovered_index:
                self.parent().viewport().update()
            
            return True
        
        # Detectar clicks en el área del botón "⋯"
        if event.type() == event.Type.MouseButtonRelease:
            button_rect = self.get_button_rect(option.rect)
            pos = event.position().toPoint()
            
            if button_rect.contains(pos):
                # Usar la referencia guardada a la ventana principal
                if self.main_window and hasattr(self.main_window, 'show_song_context_menu_at_item'):
                    # Calcular posición global del botón
                    global_pos = self.parent().viewport().mapToGlobal(pos)
                    # Mostrar menú en la posición del click
                    self.main_window.show_song_context_menu_at_item(index.row(), global_pos)
                return True
        
        return super().editorEvent(event, model, option, index)
