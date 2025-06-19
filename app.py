
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import pytz
import os

# ファイル名
FILENAME = 'kintai.xlsx'

# 日本時間
def now_jst():
    return datetime.now(pytz.timezone('Asia/Tokyo'))

# Excel初期化
def init_excel():
    if not os.path.exists(FILENAME):
        df = pd.DataFrame(columns=["氏名", "日付", "出勤時刻", "退勤時刻", "勤務時間"])
        df.to_excel(FILENAME, index=False)

def read_data():
    return pd.read_excel(FILENAME)

def save_data(df):
    df.to_excel(FILENAME, index=False)

def record_attendance(name, status):
    now = now_jst()
    date_str = now.strftime('%Y-%m-%d')
    time_str = now.strftime('%H:%M:%S')

    df = read_data()

    if status == '出勤':
        df = pd.concat([df, pd.DataFrame([[name, date_str, time_str, '', '']], columns=df.columns)], ignore_index=True)
        save_data(df)
        return f"{name} さんの出勤を記録しました（{time_str}）"

    elif status == '退勤':
        mask = (df["氏名"] == name) & (df["日付"] == date_str) & (df["退勤時刻"] == '')
        if mask.any():
            idx = df[mask].index[-1]
            df.at[idx, "退勤時刻"] = time_str

            try:
                in_time = datetime.strptime(df.at[idx, "出勤時刻"], '%H:%M:%S')
                out_time = datetime.strptime(time_str, '%H:%M:%S')
                if out_time < in_time:
                    out_time += timedelta(days=1)
                duration = out_time - in_time
                hours, rem = divmod(duration.total_seconds(), 3600)
                minutes = rem // 60
                df.at[idx, "勤務時間"] = f"{int(hours)}時間{int(minutes)}分"
                save_data(df)
                return f"{name} さんの退勤を記録しました（{time_str}｜{int(hours)}時間{int(minutes)}分）"
            except Exception as e:
                return "エラー: 時間の計算に失敗しました"
        else:
            return "退勤対象が見つかりません"

# アプリ起動処理
init_excel()
st.title("📋 簡易勤怠管理アプリ")

name = st.text_input("氏名を入力してください")

col1, col2 = st.columns(2)

if col1.button("🔴 出勤", use_container_width=True):
    if name.strip():
        msg = record_attendance(name.strip(), '出勤')
        st.success(msg)
    else:
        st.warning("氏名を入力してください")

if col2.button("🔵 退勤", use_container_width=True):
    if name.strip():
        msg = record_attendance(name.strip(), '退勤')
        st.success(msg)
    else:
        st.warning("氏名を入力してください")

# 勤怠履歴の表示とダウンロード
with st.expander("📖 勤怠履歴を表示する"):
    st.dataframe(read_data())
    st.download_button("📥 Excelファイルをダウンロード", data=open(FILENAME, "rb"), file_name=FILENAME)
