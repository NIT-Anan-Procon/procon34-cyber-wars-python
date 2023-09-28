from config.settings import *
from flask import Flask, jsonify, request
from .helpers import *
import mysql.connector


app = Flask(__name__, static_folder='.', static_url_path='')


@app.route('/', methods=["POST"])
def handle_request():
    try:
        conn = mysql.connector.connect(host=HOST, user=USER, password=PASSWORD, database=DATABASE)
        cursor = conn.cursor()

        global prompt
        prompt = get_prompt()

        chat_response = chat(prompt)

        # challengesテーブルから最大のchallenge_idを取得
        sql = "SELECT MAX(challenge_id) FROM challenges;"
        cursor.execute(sql)
        challenge_id = str(cursor.fetchone()[0] + 1)

        hint, answer = make_environment(chat_response, challenge_id)
        response = test(challenge_id)

        if response["message"] == "unsuccessful":
            # エラー時の処理
            cleanup_challenge(challenge_id)
            return handle_request()
        else:
            # 正常な場合、challengesテーブルに挿入
            sql = "INSERT INTO challenges (challenge_id, choice, hint) VALUES(%s, %s, %s, %s);"
            cursor.execute(sql, (challenge_id, answer, hint))
            conn.commit()

        cursor.close()
        conn.close()
        return jsonify(response), 200

    except Exception as e:
        print(chat_response)
        print(e)
        cleanup_challenge(challenge_id)
        conn.close()
        return handle_request()