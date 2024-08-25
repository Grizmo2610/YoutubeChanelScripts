import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLineEdit, QVBoxLayout, QWidget, QLabel, QMessageBox
from Transcript import *
import pandas as pd

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Thiết lập kích thước và tiêu đề của cửa sổ
        self.setWindowTitle('Nhập YoutubeID')
        self.setGeometry(100, 100, 400, 200)

        # Tạo widget trung tâm
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Tạo layout
        layout = QVBoxLayout()

        # Tạo các widget
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText('Nhập YoutubeID ở đây')
        self.submit_button = QPushButton('Gửi')
        self.message_label = QLabel('')

        # Thêm các widget vào layout
        layout.addWidget(self.input_field)
        layout.addWidget(self.submit_button)
        layout.addWidget(self.message_label)

        # Đặt layout cho widget trung tâm
        central_widget.setLayout(layout)

        # Kết nối nút bấm với hàm xử lý
        self.submit_button.clicked.connect(self.handle_submit)

    def handle_submit(self):
        youtube_id = self.input_field.text()
        get_data(youtube_id)
        self.show_message('Đã gửi dữ liệu và hoàn tất!')

    def show_message(self, message):
        QMessageBox.information(self, 'Thông báo', message)

def get_data(youtube_id):
    # Hàm xử lý dữ liệu YoutubeID
    print(f'Nhận YoutubeID: {youtube_id}')
    
    hyperlinks = get_channel_videos_information(youtube_id)
    content = {'Title':[], 'Script': []}
    for idx, row in hyperlinks.iterrows():
        title = row['Title']
        link = row['Link']
        print(f'Getting Script: {title} - {idx + 1} / {len(hyperlinks)}')
        script = get_transcript(link)
        content['Title'].append(title)
        content['Script'].append(script)
        if idx == 2:
            break
    print('Get framework')
    scripts = pd.DataFrame(content)
    get_script_framework(scripts)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
