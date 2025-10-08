# twelite_parser.py
import struct

def parse_app_pal_message(line: str) -> dict:
    """
    TWE-Lite App_PALの1行メッセージを解析する。
    例: :78811501A20004D2000F0F16F00102FFFFFFFF
    """
    if not line.startswith(":"):
        return {}

    try:
        line = line.strip()[1:]  # ":"を除去
        # 16進文字列 → バイナリ
        raw = bytes.fromhex(line)

        # 仕様に基づいてフィールドを分解
        addr_src = raw[0:4].hex().upper()
        lqi = raw[4]
        seq = raw[5]
        time_sec = struct.unpack(">H", raw[6:8])[0]
        pal_id = raw[8]
        sensor_type = raw[9]

        # データ部（センサータイプによって異なる）
        sensor_data = {}
        if sensor_type == 0x01:  # PAL_AMB (環境)
            temp_raw = struct.unpack(">h", raw[10:12])[0]
            humid_raw = struct.unpack(">H", raw[12:14])[0]
            illum_raw = struct.unpack(">H", raw[14:16])[0]

            sensor_data["temperature"] = temp_raw / 100  # ℃
            sensor_data["humidity"] = humid_raw / 100    # %
            sensor_data["illuminance"] = illum_raw       # lux

        elif sensor_type == 0x02:  # PAL_MOT (加速度)
            x = struct.unpack(">h", raw[10:12])[0]
            y = struct.unpack(">h", raw[12:14])[0]
            z = struct.unpack(">h", raw[14:16])[0]

            sensor_data["accel_x"] = x
            sensor_data["accel_y"] = y
            sensor_data["accel_z"] = z

        # 必要に応じて他のPALタイプにも対応可能

        return {
            "src_addr": addr_src,
            "lqi": lqi,
            "seq": seq,
            "time_sec": time_sec,
            "pal_id": pal_id,
            "sensor_type": sensor_type,
            **sensor_data
        }

    except Exception:
        return {}

