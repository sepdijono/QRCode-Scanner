import cv2
import os
import sys
import time
from typing import Any

import pyzbar.pyzbar as pyzbar
import requests
import ujson
from PyQt5 import QtCore
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import *
from PyQt5.QtWidgets import QLabel, QWidget, QVBoxLayout, QHBoxLayout, QDesktopWidget, \
    QPushButton
from dotenv import load_dotenv
# from pydantic import BaseModel

m_scan_type = [1, 2]

load_dotenv('.env')


class ThreadDataClass:
    id: int
    uid: str
    scanner_id: int
    scan_type: int
    scanned_id: str
    image: QImage

    def __init__(self, id, uid, scanner_id, scan_type, scanned_id, image):
        self.id = id
        self.uid = uid
        self.scanner_id = scanner_id
        self.scan_type = scan_type
        self.scanned_id = scanned_id
        self.image = image


class Auth:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.x_access_token = self.access_token()

    def access_token(self):
        url = f"{os.environ['BASE_URL']}/token"

        payload = (
            f"username={self.username}&password={self.password}&client_id=6779ef20e75817b79602&client_secret"
            f"=ZYDPLLBWSK3MVZYDPLLBWSK3MVQJSIYHB1OR2JXCY0X2C5UJ2QAR2MAAIT5QQJSIYHB1OR2JXCY0X2C5UJ2QAR2MAAIT5Q")
        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        response = requests.request("POST", url, headers=headers, data=payload)

        acc_token = str(ujson.loads(response.text)['access_token']).strip()
        return acc_token


class QRScanner:
    def __init__(self):
        super().__init__()
        self.scan_type = 1
        self.AUTH = Auth('admin', '123123')
        self.col_registered = (0, 255, 0)
        self.col_unregistered = (255, 0, 0)
        self.rgb = self.col_registered
        self.last_scanned = {}

    def change_scan_type(self, s_type):
        if s_type in m_scan_type:
            self.scan_type = s_type
        else:
            print(f"Unable to change scan type, scan type value is between {m_scan_type}")

    def qr_parsing(self, image):
        try:
            payloads = {}
            headers = {
                'access_token': self.AUTH.x_access_token,
                'Content-Type': 'application/x-www-form-urlencoded'
            }

            barcodes = pyzbar.decode(image)
            for barcode in barcodes:
                if barcode:
                    l = 10
                    t = 4
                    data = barcode.data.decode("utf-8")
                    id = f"{data}".strip()
                    url = f"{os.environ['BASE_URL']}/user/scan/{id}"
                    response = requests.request("POST", url, headers=headers, data=payloads)
                    if response:
                        r = ujson.loads(response.text)
                        if 'id' in r:
                            scan_type = 1
                            scanned_id = f"{str(scan_type)}{r['id']}{r['str_date_scanned']}".replace('-', '')
                            au = {
                                "id": r["id"],
                                "uid": r["uid"],
                                "full_name": f'{r["firstname"]} {r["lastname"]}',
                                "address": r["address"],
                                "scanner": r["scanner"]['moderator'],
                                "scan_type": scan_type,
                                "scanned_id": scanned_id,
                            }
                            self.last_scanned = au
                            line1 = f"{au['id']}-{au['uid']}"
                            line2 = f"{au['full_name']}"
                            line3 = f"{au['address']}"
                            line4 = f"{au['scanner']['name']}-{au['scanner']['location']}"
                            self.rgb = (0, 255, 0)
                            hit_url = f"{os.environ['BASE_URL']}/hit/"
                            hit_payloads = ujson.dumps(au)
                            hit_headers = {
                                'access_token': self.AUTH.x_access_token,
                                'Content-Type': 'application/x-www-form-urlencoded'
                            }
                            r = requests.request("POST", hit_url, headers=hit_headers, data=hit_payloads)
                            if r.text:
                                loads_req = ujson.loads(r.text)
                                if 'uid' in loads_req:
                                    self.last_scanned = loads_req

                        else:
                            if r['message']['status_code'] == 404:
                                line1 = ""
                                line2 = ""
                                line3 = ""
                                line4 = "Tidak terdaftar"
                                self.rgb = self.col_unregistered
                    else:
                        line1 = ""
                        line2 = ""
                        line3 = ""
                        line4 = "Tidak terdaftar"
                        self.rgb = self.col_unregistered

                    # Barcode polygon
                    # polygons = barcode.polygon
                    # for polygon in polygons:
                    #     print(polygon)

                    # original frame setting
                    (x, y, w, h) = barcode.rect
                    (xc, yc, w, h) = barcode.rect
                    x1, y1 = x + w, y + h

                    cv2.rectangle(image, (int(x), int(y)), (int(x) + int(w), int(y) + int(h)), self.rgb, 1)
                    txt_indent = 12

                    # Top left x,y
                    cv2.line(image, (x, y), (x + l, y), self.rgb, t)
                    cv2.line(image, (x, y), (x, y + l), self.rgb, t)
                    # Top right x1,y
                    cv2.line(image, (x1, y), (x1 - l, y), self.rgb, t)
                    cv2.line(image, (x1, y), (x1, y + l), self.rgb, t)
                    # Bottom left x,y1
                    cv2.line(image, (x, y1), (x + l, y1), self.rgb, t)
                    cv2.line(image, (x, y1), (x, y1 - l), self.rgb, t)
                    # Bottom right x1,y1
                    cv2.line(image, (x1, y1), (x1 - l, y1), self.rgb, t)
                    cv2.line(image, (x1, y1), (x1, y1 - l), self.rgb, t)
                    # draw stick
                    cv2.line(image, (x, y), (x, y - 7), self.rgb, 1)
                    cv2.line(image, (x, y - 7), (x + 12, y - 12), self.rgb, 1)

                    y0, dy = 2, 2
                    yy = y0 + dy
                    rgb1 = (255, 255, 255)
                    rgb2 = (0, 0, 0)
                    x = x + txt_indent
                    y = y - txt_indent
                    cv2.putText(image, line1, (int(x), int(y) - (int(yy) + 30)),
                                cv2.FONT_HERSHEY_DUPLEX,
                                .5, self.rgb, 1)
                    cv2.putText(image, line2, (int(x), int(y) - (int(yy) + 20)),
                                cv2.FONT_HERSHEY_DUPLEX,
                                .5, self.rgb, 1)
                    cv2.putText(image, line3, (int(x), int(y) - (int(yy) + 10)),
                                cv2.FONT_HERSHEY_DUPLEX,
                                .5, self.rgb, 1)
                    cv2.putText(image, line4, (int(x), int(y) - (int(yy))),
                                cv2.FONT_HERSHEY_DUPLEX,
                                .5, self.rgb, 1)
                else:
                    pass
        except Exception as e:
            print(f'Exception: {e}')
            pass
        return image


class QRScannerApp(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("QR Reader")
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        lay = QHBoxLayout(self.central_widget)
        self.setMinimumSize(640, 480)
        # self.setMaximumSize(640, 480)
        self.center()
        self.thread = {}

        # self.QRS = QRScanner()
        self.AUTH = Auth('admin', '123123')

        lay1 = QVBoxLayout()
        lay.addLayout(lay1)

        self.label_img1 = QLabel(self)
        pixmap = QPixmap()
        self.label_img1.setPixmap(pixmap)
        self.label_img1.setStyleSheet("border: 1px solid black;")
        # self.resize(pixmap.width(), pixmap.height())
        lay1.addWidget(self.label_img1, alignment=Qt.AlignCenter)

        self.button1 = QPushButton('Cam 1')
        self.button1.setCheckable(True)
        self.button1.setIcon(QIcon('camera.png'))
        self.button1.clicked.connect(self.worker1)
        # self.button1.setGeometry(200, 150, 100, 30)
        lay1.addWidget(self.button1)

        lay2 = QVBoxLayout()
        lay.addLayout(lay2)
        self.listWidget = QListWidget(None)
        self.listWidget.setMinimumWidth(self.listWidget.sizeHintForColumn(0))
        lay2.addWidget(self.listWidget)
        self.listWidget.setMinimumWidth(300)
        self.listWidget.setMaximumWidth(300)

        self.show()

    def resizeEvent(self, event):
        pixmap1 = self.label_img1.pixmap()
        self.pixmap = pixmap1.scaled(self.width(), self.height())
        self.label_img1.setPixmap(self.pixmap)
        self.label_img1.resize(self.width(), self.height())

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def worker1(self):
        def start_worker_1():
            self.thread[1] = ThreadClass(parent=None, index=1)
            self.thread[1].start()
            self.thread[1].any_signal.connect(self.my_function)

        def stop_worker_1():
            self.thread[1].stop()

        if self.button1.isChecked():
            start_worker_1()
            self.start_worker_2()
        else:
            stop_worker_1()
            self.stop_worker_2()

    def start_worker_2(self):
        self.thread[2] = ThreadClass(parent=None, index=2)
        self.thread[2].start()
        self.thread[2].any_signal.connect(self.my_function)

    def stop_worker_2(self):
        self.thread[2].stop()

    def my_function(self, au):
        index = self.sender().index
        if au:
            if index == 1:
                pixmap = QPixmap(au)
                self.label_img1.setPixmap(pixmap)
            elif index == 2:
                url = f"{os.environ['BASE_URL']}/hit/today"
                payloads = {}
                headers = {
                    'access_token': self.AUTH.x_access_token,
                    'Content-Type': 'application/x-www-form-urlencoded'
                }
                response = requests.request("GET", url, headers=headers, data=payloads)
                if response.text:
                    r = ujson.loads(response.text)
                    if 'count' in r:
                        for d in r['data']:
                            sch = f"{d['name']} {d['full_name']}"
                            if not self.listWidget.findItems(sch, Qt.MatchExactly):
                                QListWidgetItem(f"{d['name']} {d['full_name']}", self.listWidget)
                    else:
                        self.listWidget.clear()
                time.sleep(0.01)


class ThreadClass(QtCore.QThread):
    any_signal = QtCore.pyqtSignal(QImage)

    def __init__(self, parent=None, index=0):
        super(ThreadClass, self).__init__(parent)
        self.index = index
        self.is_running = True
        self.camera = {}
        self.QRS = QRScanner()
        # self.QRS = qrs

    def chk_cam(self, camera_index):
        cam = cv2.VideoCapture(int(camera_index))
        if not cam.isOpened():
            au = {"cam": camera_index, "status": {"exist": False, "is_reading": False}}
            return au
        else:
            try:
                is_reading, img = cam.read()
                w = cam.get(3)
                h = cam.get(4)
                if is_reading:
                    au = {"cam": camera_index, "status": {"exist": True, "is_reading": True}}
                    return au
                else:
                    au = {"cam": camera_index, "status": {"exist": True, "is_reading": False}}
            except Exception as e:
                print(e)
                pass
        return au

    def run(self):
        cam = 0
        try:
            self.camera = cv2.VideoCapture(cam)
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            if not self.camera.isOpened():
                raise NameError('Error: Could not open video.')
        except cv2.error as e:
            raise NameError('Error: ' + e)
        except Exception as e:
            raise NameError('Error: ' + e)
        else:
            pass

        display_res_rgb = (0, 0, 255)

        while True:
            ret, frame = self.camera.read()
            if ret:
                display_res = f"{str(frame.shape[0])}x{str(frame.shape[1])}"
                im = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                im = self.QRS.qr_parsing(im)
                if frame.shape[1] < 720:
                    im = cv2.putText(im, display_res, (int(10), int(30)),
                                     cv2.FONT_HERSHEY_PLAIN, .7, display_res_rgb, 1)
                else:
                    im = cv2.putText(im, display_res, (int(10), int(20)),
                                     cv2.FONT_HERSHEY_PLAIN, 1.3, display_res_rgb, 2)
                flipped_image = im
                qt_format = QImage(flipped_image.data,
                                   flipped_image.shape[1],
                                   flipped_image.shape[0],
                                   QImage.Format.Format_RGB888)
                pic = qt_format.scaled(1280, 1024, Qt.KeepAspectRatio)
                self.any_signal.emit(pic)

    def stop(self):
        self.is_running = False
        print('Stopping thread...', self.index)
        self.terminate()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = QRScannerApp()
    sys.exit(app.exec_())
