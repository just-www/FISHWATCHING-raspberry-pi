from flask import Flask, Response, render_template, jsonify
import cv2
import numpy as np
from datetime import datetime

app = Flask(__name__)

# 初始化攝影機
cap = cv2.VideoCapture(0)

# 背景減除器 (調整參數)
fgbg = cv2.createBackgroundSubtractorMOG2(history=700, varThreshold=30, detectShadows=False)

# 核心形態學運算所需的結構元素
kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))

# 設定固定的參數
min_area = 280
max_area = 10000
min_aspect_ratio = 0.5
max_aspect_ratio = 3.1
min_circularity = 0.03

# 初始化一個滑動窗口來保存過去的魚數目
fish_count_history = []
window_size = 10  # 定義滑動窗口的大小


@app.route('/')
def index():
    # 用來顯示網頁的主頁
    return render_template('index.html')


def is_within_active_hours():
    # Get the current time
    current_time = datetime.now().time()
    # Define active hours: 3 PM to 9 PM
    start_time = datetime.strptime("15:00", "%H:%M").time()
    end_time = datetime.strptime("21:00", "%H:%M").time()

    # Check if the current time is within the active hours
    return start_time <= current_time <= end_time


@app.route('/detection_status')
def detection_status():
    # 回傳是否在偵測時間內
    status = {'active': is_within_active_hours()}
    return jsonify(status)


def generate_frames():
    while True:
        if is_within_active_hours():
            # 讀取影像
            ret, frame = cap.read()
            if not ret:
                break

            # 影像縮放
            frame_resized = cv2.resize(frame, (640, 480))

            # 背景減除
            fgmask = fgbg.apply(frame_resized)

            # 影像平滑化
            blurred = cv2.GaussianBlur(fgmask, (5, 5), 0)

            # 形態學處理：開運算和閉運算
            morph_open = cv2.morphologyEx(blurred, cv2.MORPH_OPEN, kernel)
            morph_close = cv2.morphologyEx(morph_open, cv2.MORPH_CLOSE, kernel)

            # 二值化
            _, thresh = cv2.threshold(morph_close, 127, 255, cv2.THRESH_BINARY)

            # 偵測輪廓
            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            # 計算當前幀中的魚的數目
            fish_count = 0

            for contour in contours:
                # 計算輪廓面積，過濾面積不符合範圍的輪廓
                area = cv2.contourArea(contour)
                if area < min_area or area > max_area:
                    continue

                # 計算輪廓的邊界框
                x, y, w, h = cv2.boundingRect(contour)

                # 計算長寬比，過濾不符合長寬比範圍的輪廓
                aspect_ratio = float(w) / h
                if not (min_aspect_ratio < aspect_ratio < max_aspect_ratio):
                    continue

                # 計算圓形度，過濾不符合圓形度範圍的輪廓
                perimeter = cv2.arcLength(contour, True)
                if perimeter > 0:
                    circularity = 4 * np.pi * (area / (perimeter ** 2))
                    if circularity < min_circularity:
                        continue

                    # 偵測到魚，增加魚數量
                    fish_count += 1

                    # 繪製邊界框
                    cv2.rectangle(frame_resized, (x, y), (x + w, y + h), (0, 255, 0), 2)

            # 更新滑動窗口中的魚數目
            fish_count_history.append(fish_count)
            if len(fish_count_history) > window_size:
                fish_count_history.pop(0)  # 保持滑動窗口大小固定

            # 計算滑動窗口中的平均魚數
            stable_fish_count = int(np.mean(fish_count_history))

            # 在影像上顯示穩定後的魚數目
            cv2.putText(frame_resized, f'Stable Fish Count: {stable_fish_count}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            # 將影像編碼為 JPEG 格式
            ret, buffer = cv2.imencode('.jpg', frame_resized)
            frame = buffer.tobytes()

            # 生成帶有 MIME 類型 multipart/x-mixed-replace 的 HTTP 響應
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        else:
            # Outside the active hours, yield nothing (handled by front-end)
            break


@app.route('/video_feed')
def video_feed():
    # 使用 generate_frames 函數提供影像流
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
