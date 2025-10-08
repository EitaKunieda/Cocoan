# app.py
import streamlit as st
import serial
import threading
import time
from Cocoan import parse_app_pal_message

st.set_page_config(page_title="TWE-Lite App_PAL 受信モニタ", layout="wide")

# --- グローバル変数 ---
ser = None
running = False
latest_data = []

def serial_reader():
    global ser, running, latest_data
    while running:
        if ser and ser.in_waiting > 0:
            line = ser.readline().decode(errors="ignore").strip()
            parsed = parse_app_pal_message(line)
            if parsed:
                latest_data.append(parsed)
                # 最大100件までに制限
                if len(latest_data) > 100:
                    latest_data = latest_data[-100:]
        time.sleep(0.05)

# --- UI ---
st.title("📡 TWE-Lite App_PAL 受信モニタ")

com_port = st.text_input("COMポートを入力 (例: COM3 または /dev/ttyUSB0)", "COM3")
baud_rate = st.number_input("ボーレート", value=115200, step=1)

col1, col2 = st.columns(2)
with col1:
    start_btn = st.button("接続開始")
with col2:
    stop_btn = st.button("停止")

if start_btn and not running:
    try:
        ser = serial.Serial(com_port, baud_rate, timeout=1)
        running = True
        t = threading.Thread(target=serial_reader, daemon=True)
        t.start()
        st.success(f"{com_port} に接続しました")
    except Exception as e:
        st.error(f"接続失敗: {e}")

if stop_btn and running:
    running = False
    if ser:
        ser.close()
    ser = None
    st.warning("接続を停止しました")

# --- データ表示 ---
st.subheader("📊 受信データ")

if latest_data:
    st.dataframe(latest_data[::-1], use_container_width=True)
else:
    st.info("まだデータがありません。")


