# Fish Detection System with Flask & OpenCV

此專案為一個基於 Flask 架構的即時魚隻偵測系統，使用 OpenCV 進行影像處理與偵測，並透過網頁串流顯示畫面與穩定後的魚隻數量。

## 📷 功能介紹

- 🎯 實時魚隻偵測（透過背景減除與形態學處理）
- 🧠 自動過濾非魚類物體（面積、比例、圓形度）
- 🕒 偵測僅在每日 15:00 ~ 21:00 啟動，節省資源
- 📈 使用滑動平均來穩定魚數計算
- 🌐 提供網頁介面與即時影片串流

## 📦 環境需求

- Python 3.7+
- OpenCV
- Flask
- NumPy

## 🔧 安裝步驟

```bash
# 建議使用虛擬環境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安裝必要套件
pip install -r requirements.txt
```

如無 `requirements.txt`，可手動安裝：

```bash
pip install flask opencv-python numpy
```

## 🚀 執行方式

```bash
python app.py
```

啟動後開啟瀏覽器進入：
```
http://localhost:5000
```
![Demo](static/demo.gif)

## 🧪 API 路徑

- `/`：主頁，顯示影片串流
- `/video_feed`：提供即時影像串流（MIME: `multipart/x-mixed-replace`）
- `/detection_status`：回傳偵測是否啟用（JSON 格式）

## 📁 專案結構

```
├── app.py               # 主程式
├── templates/
│   └── index.html       # 前端模板
├── static/              # 可放前端圖示、CSS 等資源（若有）
└── README.md            # 使用說明文件
```

## 🛡️ 注意事項

- 攝影機裝置須可正常啟動。
- 預設僅於每日 15:00~21:00 偵測魚隻，其他時間無影像串流。

## 🐟 展望功能

- 儲存每日魚隻數據
- 識別不同魚種
- 前端顯示歷史統計圖表

---

Made with 🐠 by Justin
