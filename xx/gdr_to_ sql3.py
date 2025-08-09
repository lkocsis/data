from pydantic import Json
import os, requests, openpyxl
import pandas as pd
import sqlite3

from _py_lib import base_with_log, pog
Base = base_with_log(__file__)
def xlsx_down():
    print("Downloading file...")
    xid = "1pp9c01K5653ZIg-XJOvpRz8ZqFbvQr8Z"
    xurl = f"https://docs.google.com/spreadsheets/d/{xid}/export?format=xlsx"
    Db = "imf_weo.db"
    Table = "imf_weo"
    Json = "imf_weo.json"

    df = pd.read_excel(xurl, engine='openpyxl')
    pog(Table + " downloaded from " + xurl)
    pog(df.columns)
    conn = sqlite3.connect(Db)
    df.to_sql(Table, conn, if_exists="replace", index=False)
    df.to_json(Json, orient="records")

    pog(os.listdir(os.getcwd()))

    pog(Table + " stored in " + Db)
    df_loaded = pd.read_sql(f"SELECT * FROM {Table}", conn)

    pog(df_loaded.columns)

if __name__ == "__main__":
    xlsx_down()
