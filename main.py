from ui.layout import AppLayout
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

if __name__ == '__main__':
    app = AppLayout()
    app.run()
