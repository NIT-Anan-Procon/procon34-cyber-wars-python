from config.settings import *
from config.settings import messages
from flask import Flask, jsonify, request
from .helpers import *
import mysql.connector
import sys
import traceback


app = Flask(__name__, static_folder='.', static_url_path='')


@app.route('/', methods=["POST"])
def handle_request():
    try:
        conn, cursor, prompt = initialize()
        chat_response = chat(prompt)

        # challengesテーブルから最大のchallenge_idを取得
        sql = "SELECT MAX(challenge_id), MAX(vulnerability_id) FROM challenges;"
        cursor.execute(sql)
        challenge_id, vulnerability_id = cursor.fetchone()
        challenge_id = "1" if challenge_id is None else str(challenge_id + 1)
        vulnerability_id = "1" if vulnerability_id is None else str(vulnerability_id + 1)

        hint, answer = make_environment(chat_response, challenge_id)
        answer = to_comma_separated(answer)
        response = test(challenge_id)

        goal = chat("どういう行動に対して脆弱なのか100字程度で教えて")

        if response["message"] == "unsuccessful":
            # エラー時の処理
            cleanup_challenge(challenge_id)
            return handle_request()
        else:
            # 正常な場合、challengesテーブルに挿入
            sql = "INSERT INTO challenges (challenge_id, vulnerability_id, goal, choice, hint) VALUES(%s, %s, %s, %s, %s);"
            cursor.execute(sql, (challenge_id, vulnerability_id, goal, answer, hint))
            conn.commit()

        cursor.close()
        conn.close()
        return jsonify(response), 200
    except Exception as e:
        print(chat_response)
        print(traceback.format_exc())
        cleanup_challenge(challenge_id)
        conn.close()
        return handle_request()
