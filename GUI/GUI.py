import sys, os, json, subprocess, random, requests
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QMessageBox,
    QDialog,
    QTableWidgetItem,
    QHeaderView,
    QWidget,
    QVBoxLayout,
    QTextEdit,
    QPlainTextEdit
)
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtCore import Qt, QProcess, pyqtSignal, QTextStream, QObject, QThread
from PyQt6.QtGui import QIcon, QTextCursor
from utils import crawler
from utils.word_cloud.demo import draw_word_cloud_picture
from main_window import Ui_MainWindow


class Worker(QObject):
    finished = pyqtSignal()
    output = pyqtSignal(str)

    def __init__(self):
        super().__init__()

    def crawl_data(self):
        process = subprocess.Popen([sys.executable, "D:/VSCODE/InformationContentSecurityLab/WeiboSpider/weibospider/run_spider.py"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
        for line in process.stdout:
            self.output.emit(line.strip())
        process.communicate()
        self.finished.emit()

    def crawl_comments(self):
        process = subprocess.Popen([sys.executable, "D:/VSCODE/InformationContentSecurityLab/GUI/utils/weibospider/run_spider.py"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
        for line in process.stdout:
            self.output.emit(line.strip())
        process.communicate()
        self.finished.emit()

class EmittingStream(QObject):
    textWritten = pyqtSignal(str)

    def write(self, text):
        self.textWritten.emit(str(text))


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        icon_dir = os.path.dirname(__file__)
        icon_path = os.path.join(icon_dir, "bender.ico")
        self.setWindowIcon(QIcon(icon_path))
        self.setupUi(self)

        sys.stdout = EmittingStream(textWritten=self.normalOutputWritten)

        self.worker = Worker()
        self.worker.output.connect(self.update_output)
        self.worker.finished.connect(self.script_finished)

    def normalOutputWritten(self, text):
        cursor = self.plainTextEdit.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        cursor.insertText(text)
        self.plainTextEdit.setTextCursor(cursor)
        self.plainTextEdit.ensureCursorVisible()

    # 更新热搜话题
    def update_hot_topics(self):
        hot_topics = crawler.find_hot_topics(self)
        # print(hot_topics)
        self.listWidget.addItems(hot_topics)
        # 自动调整 ListWidget 大小
        self.listWidget.adjustSize()

    # 选取项变化时的槽函数
    def on_list_widget_item_selection_changed(self):
        selected_keyword = self.listWidget.currentItem().text()
        self.populate_table_widget(selected_keyword)

    # 将选取项添加到QTableWidget
    def populate_table_widget(self, keyword):
        # 清空表格
        self.tableWidget.clear()

        # 设置表格的行数和列数
        self.tableWidget.setRowCount(0)  # 设置为0以清除之前的行
        # 列名列表
        column_names = ['Keyword', 'Created At', 'User Nickname', 'Content', 'URL', 'ID']
        # 设置列数
        self.tableWidget.setColumnCount(len(column_names))
        # 设置列名
        self.tableWidget.setHorizontalHeaderLabels(column_names)
        # 加载.jsonl文件数据
        data = []
        file_dirname = 'D:\VSCODE\InformationContentSecurityLab\WeiboSpider\weibospider\output'
        file_name = 'tweets.jsonl'
        file_path = os.path.join(file_dirname, file_name)
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                item = json.loads(line)
                data.append(item)
        # 添加匹配的数据到表格
        row_count = 0
        # 打开文件以写入模式

        # 获取当前脚本的绝对路径
        script_path = os.path.abspath(__file__)
        # 获取要写入的.txt文件的绝对路径
        txt_file_path = os.path.join(os.path.dirname(script_path), 'utils', 'word_cloud', 'doc', 'temp.txt')
        with open(txt_file_path, 'w', encoding='utf-8') as file:
            for item in data:
                if item.get("keyword") == keyword:
                    keyword = item.get("keyword")
                    created_at = item.get("created_at")
                    user_nick_name = item.get("user").get("nick_name")
                    content = item.get("content")
                    url = item.get("url")
                    _id = item.get("_id")

                    # 在表格中添加新行
                    row_count = self.tableWidget.rowCount()
                    self.tableWidget.insertRow(row_count)

                    # 在表格中设置单元格内容
                    self.tableWidget.setItem(row_count, 0, QTableWidgetItem(keyword))
                    self.tableWidget.setItem(row_count, 1, QTableWidgetItem(created_at))
                    self.tableWidget.setItem(row_count, 2, QTableWidgetItem(user_nick_name))
                    self.tableWidget.setItem(row_count, 3, QTableWidgetItem(content))
                    self.tableWidget.setItem(row_count, 4, QTableWidgetItem(url))
                    self.tableWidget.setItem(row_count, 5, QTableWidgetItem(_id))

                    row_count += 1
                    # 将 content 内容写入文件
                    file.write(content + '\n')
        # 调整表格的大小
        self.tableWidget.resizeColumnsToContents()
        self.tableWidget.resizeRowsToContents()

    # 生成词云
    def gen_word_cloud(self):
        try:
            draw_word_cloud_picture()
        except ValueError as e:
            # 异常处理代码
            error_message = str(e)  # 获取异常消息
            QMessageBox.critical(None, "错误", f"用于生成词云图的输入内容为空，无法生成词云图！：{error_message}")

    # 爬取热搜
    def crawl_hot_topics(self):
        self.plainTextEdit.clear()
        self.worker.crawl_data()

    def update_output(self, line):
        self.plainTextEdit.appendPlainText(line)

    def script_finished(self):
        self.plainTextEdit.appendPlainText("Script execution finished.")

    def gen_positive_comment(self):
        # 打开特定文件名，返回文件名和路径
        file_name = 'D:/VSCODE/InformationContentSecurityLab/GUI/utils/sinaweibopy3/positive_comments.txt'
        with open(file_name, "r", encoding="utf-8") as f:
            lines = f.readlines()
            line = random.choice(lines)
            self.textEdit.setText(line)

    def publish_comment(self):
        comment = self.textEdit.toPlainText()
        id = self.lineEdit.text()
        if not id:
            QMessageBox.critical(self, "错误", "ID为空，请重新输入ID")
            return
        url = "https://api.weibo.com/2/comments/create.json"
        params = {
            'access_token': '2.00XywhYI0xvh2e66647bf75c0tvgBF',	# 刚才请求到的access_token
            'id': id,
            'comment': comment,
            'rip':'111.42.148.191'
        }
        
        response = requests.post(url=url, data=params)
        # 设置消息框的标题和内容
        message_box = QMessageBox()
        message_box.setWindowTitle("提示")
        message_box.setText('评论发布成功！')
        # 显示消息框
        message_box.exec()

    # 爬取评论
    def crawl_comments(self):
        url = self.lineEdit_2.text()
        if not url:
            QMessageBox.critical(self, "错误", "网址为空，请重新输入")
            return
        code = url.split('/')[-1]
        with open('D:/VSCODE/InformationContentSecurityLab/GUI/utils/weibospider/output/comments_tweetsid.txt', "w") as f:
            f.write(code)
        self.plainTextEdit.clear()
        self.worker.crawl_comments()

    # 评论分析
    def analyze_comments(self):
        from utils.weibonlp.analyze_comments import analyze_comments
        analyze_comments()

if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    mainwindow = MainWindow()
    mainwindow.update_hot_topics()
    mainwindow.show()
    sys.exit(app.exec())
