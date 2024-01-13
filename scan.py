import cv2
import json
import pyshine as ps
import pyzbar.pyzbar as pyzbar
import requests
import ujson


def scan(acc_token, id: str):
    payloads = {}
    headers = {
        'access_token': acc_token,
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    url = f"http://127.0.0.1:8000/user/scan/{id}"

    response = requests.request("POST", url, headers=headers, data=payloads)
    r = json.loads(response.text)
    # print(r)
    au = {
        "id": r["id"],
        "uid": r["uid"],
        "fullname": f'{r["firstname"]} {r["lastname"]}',
        "address": r["address"],
        "scanner": r["scanner"]
    }
    return au


def qr_parsing(image):
    global x_token

    def draw_text(img, text,
                        font=cv2.FONT_HERSHEY_PLAIN,
                        pos=(0, 0),
                        font_scale=1.5,
                        background_RGB=(0, 250, 0),
                        text_RGB=(255, 250, 250)
                        ):
        if img.size == 0:
            return
        x, y = pos
        ps.putBText(img, text, text_offset_x=x, text_offset_y=y, font=font,
                    vspace=5, hspace=10, font_scale=font_scale,
                    background_RGB=background_RGB, text_RGB=text_RGB)
        return

    payloads = {}
    headers = {
        'access_token': x_token,
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    try:
        barcodes = pyzbar.decode(image)
        for barcode in barcodes:
            if barcode:
                l = 10
                t = 4
                data = barcode.data.decode("utf-8")
                rgb = (0, 255, 0)

                # original frame setting
                (x, y, w, h) = barcode.rect
                (xc, yc, w, h) = barcode.rect
                x1, y1 = x + w, y + h

                cv2.rectangle(image, (int(x), int(y)), (int(x) + int(w), int(y) + int(h)), rgb, 1)

                # Top left x,y
                cv2.line(image, (x, y), (x + l, y), rgb, t)
                cv2.line(image, (x, y), (x, y + l), rgb, t)
                # Top right x1,y
                cv2.line(image, (x1, y), (x1 - l, y), rgb, t)
                cv2.line(image, (x1, y), (x1, y + l), rgb, t)
                # Bottom left x,y1
                cv2.line(image, (x, y1), (x + l, y1), rgb, t)
                cv2.line(image, (x, y1), (x, y1 - l), rgb, t)
                # Bottom right x1,y1
                cv2.line(image, (x1, y1), (x1 - l, y1), rgb, t)
                cv2.line(image, (x1, y1), (x1, y1 - l), rgb, t)
                # draw stick
                # cv2.line(image, (x, y), (x, y - 7), rgb, 1)
                # cv2.line(image, (x, y - 7), (x + 12, y - 12), rgb, 1)

                text = f"{data}"
                id = text.replace('QR', '').strip()
                url = f"http://127.0.0.1:8000/user/scan/{id}"
                response = requests.request("POST", url, headers=headers, data=payloads)
                if response:
                    r = json.loads(response.text)
                    au = {
                        "id": r["id"],
                        "uid": r["uid"],
                        "fullname": f'{r["firstname"]} {r["lastname"]}',
                        "address": r["address"],
                        "scanner": r["scanner"]['moderator']
                    }
                    line1 = f"{au['id']}-{au['uid']}"
                    line2 = f"{au['fullname']}"
                    line3 = f"{au['address']}"
                    line4 = f"{au['scanner']['name']}-{au['scanner']['location']}"
                else:
                    line1 = ""
                    line2 = ""
                    line3 = ""
                    line4 = "Tidak terdaftar"

                y0, dy = 2, 2
                yy = y0 + dy
                rgb1 = (255, 255, 255)
                rgb2 = (0, 0, 0)
                cv2.putText(image, line1, (int(x), int(y) - (int(yy) + 30)),
                            cv2.FONT_HERSHEY_PLAIN,
                            .7, rgb, 1)
                cv2.putText(image, line2, (int(x), int(y) - (int(yy) + 20)),
                            cv2.FONT_HERSHEY_PLAIN,
                            .7, rgb, 1)
                cv2.putText(image, line3, (int(x), int(y) - (int(yy) + 10)),
                            cv2.FONT_HERSHEY_PLAIN,
                            .7, rgb, 1)
                cv2.putText(image, line4, (int(x), int(y) - (int(yy))),
                            cv2.FONT_HERSHEY_PLAIN,
                            .7, rgb, 1)
            else:
                pass
    except Exception as e:
        print(e)
        pass
    return image


def detect(cam):
    try:
        camera = cv2.VideoCapture(cam)
        if not camera.isOpened():
            raise NameError('Error: Could not open video.')
    except cv2.error as e:
        raise NameError('Error: ' + e)
    except Exception as e:
        raise NameError('Error: ' + e)
    else:
        pass

    cv2.namedWindow("camera", cv2.WND_PROP_FULLSCREEN)
    cv2.setWindowProperty("camera", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    cv2.moveWindow("camera", 2000, cam)

    while True:
        # Read current frame
        ret, frame = camera.read(cam)
        if ret:
            im = qr_parsing(frame)
            if cv2.waitKey(1) & 0xFF == 27:
                break
            cv2.imshow("camera", im)
        else:
            break

    camera.release()
    cv2.destroyAllWindows()


def token(username, password):
    url = "http://127.0.0.1:8000/token"

    payload = (
        f"username={username}&password={password}&client_id=6779ef20e75817b79602&client_secret"
        f"=ZYDPLLBWSK3MVZYDPLLBWSK3MVQJSIYHB1OR2JXCY0X2C5UJ2QAR2MAAIT5QQJSIYHB1OR2JXCY0X2C5UJ2QAR2MAAIT5Q")
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    acc_token = str(ujson.loads(response.text)['access_token']).strip()
    return acc_token


x_token = token("admin", "123123")
detect(0)
