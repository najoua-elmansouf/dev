import sys
import pandas as pd
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QFileDialog, QLabel, QInputDialog
from PyQt5.QtGui import QPixmap, QImage, QPainter, QPen
from PyQt5.QtCore import QRect, Qt
import tabula
import fitz

class TableExtractor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Table Extractor")
        self.setGeometry(100, 100, 800, 600)

        self.pdf_path = None
        self.pdf_page = None
        self.selected_area = QRect()
        self.is_selecting_area = False

        self.select_pdf_button = QPushButton("Select PDF", self)
        self.select_pdf_button.setGeometry(50, 50, 200, 50)
        self.select_pdf_button.clicked.connect(self.select_pdf)

        self.select_page_button = QPushButton("Select Page", self)
        self.select_page_button.setGeometry(50, 150, 200, 50)
        self.select_page_button.clicked.connect(self.select_page)

        self.select_area_button = QPushButton("Select Table Area", self)
        self.select_area_button.setGeometry(50, 250, 200, 50)
        self.select_area_button.clicked.connect(self.select_area)

        self.extract_button = QPushButton("Extract Table", self)
        self.extract_button.setGeometry(50, 350, 200, 50)
        self.extract_button.clicked.connect(self.extract_table)

        self.label = QLabel(self)
        self.label.setGeometry(300, 50, 450, 500)

    def select_pdf(self):
        file_dialog = QFileDialog()
        self.pdf_path, _ = file_dialog.getOpenFileName(self, "Select PDF")
        print("Selected PDF:", self.pdf_path)

    def select_page(self):
        if self.pdf_path:
            doc = fitz.open(self.pdf_path)
            page_count = doc.page_count
            page, ok = QInputDialog.getInt(self, "Select Page", "Page (1 to {}):".format(page_count), min=1, max=page_count)
            if ok:
                self.pdf_page = page
                print("Selected Page:", self.pdf_page)
            else:
                print("Page selection canceled.")
        else:
            print("Please select a PDF first.")

    def select_area(self):
        if self.pdf_path and self.pdf_page:
            self.is_selecting_area = True
            print("Please manually select the table area by clicking and dragging the mouse.")
        else:
            print("Please select a PDF and page first.")

    def mousePressEvent(self, event):
        if self.pdf_path and self.pdf_page and self.is_selecting_area:
            self.selected_area.setTopLeft(event.pos())
            self.update()  

    def mouseReleaseEvent(self, event):
        if self.pdf_path and self.pdf_page and self.is_selecting_area:
            self.selected_area.setBottomRight(event.pos())
            self.is_selecting_area = False
            self.update()  

            
            doc = fitz.open(self.pdf_path)
            page = doc.load_page(self.pdf_page - 1)
            display_list = page.get_displaylist()
            page_width = display_list.rect.width
            page_height = display_list.rect.height
            selected_width = self.selected_area.width()
            selected_height = self.selected_area.height()
            scale_x = page_width / self.label.width()
            scale_y = page_height / self.label.height()
            selected_width_scaled = int(selected_width * scale_x)
            selected_height_scaled = int(selected_height * scale_y)
            self.selected_area.setWidth(selected_width_scaled)
            self.selected_area.setHeight(selected_height_scaled)

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        if self.pdf_path and self.pdf_page and not self.selected_area.isNull():
            doc = fitz.open(self.pdf_path)
            page = doc.load_page(self.pdf_page - 1)
            pix = page.get_pixmap()
            image = QImage(pix.samples, pix.width, pix.height, pix.stride, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(image)
            painter.drawPixmap(self.label.geometry(), pixmap)
            painter.setPen(QPen(Qt.red, 2, Qt.SolidLine))
            painter.drawRect(self.selected_area)

    def extract_table(self):
        if self.pdf_path and self.pdf_page and not self.selected_area.isNull():
            area = [
                self.selected_area.topLeft().y(),
                self.selected_area.topLeft().x(),
                self.selected_area.bottomRight().y(),
                self.selected_area.bottomRight().x()
            ]
            dfs = tabula.read_pdf(self.pdf_path, stream=True, pages=self.pdf_page, area=area)
            if len(dfs) > 0:
                table_data = dfs[0]  
                df = pd.DataFrame(table_data)
                print(df)
            else:
                print("No table found in the selected area.")
        else:
            print("Please select a PDF, page, and table area first.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TableExtractor()
    window.show()
    sys.exit(app.exec_())
