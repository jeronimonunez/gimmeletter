# GimmeLetter

Una aplicación de escritorio para músicos que permite crear sets de canciones y reproducirlos con scroll automático de letras y acordes.

## Características

- 📝 Gestión de canciones con letras y acordes
- 🎵 Creación y gestión de sets/setlists
- 📜 Scroll automático configurable
- 🎸 Transposición automática de acordes
- 🌓 Modo oscuro/claro
- 🔤 Tamaño de fuente ajustable
- 💻 Multiplataforma (Windows, macOS, Linux)

## Instalación

1. Clonar el repositorio
2. Instalar dependencias:
```bash
pip install -r requirements.txt
```

## Uso

```bash
python src/main.py
```

## Estructura del Proyecto

```
gimmeletter/
├── src/
│   ├── main.py              # Punto de entrada
│   ├── database/            # Gestión de base de datos
│   ├── ui/                  # Interfaces de usuario
│   └── utils/               # Utilidades (acordes, settings)
└── requirements.txt
```

## Tecnologías

- **PyQt6** - Interfaz gráfica
- **SQLite** - Base de datos local
- **Python 3.8+**
