# chatbot_app.py の修正箇所

import streamlit as st
from openai import OpenAI
import os
# from dotenv import load_dotenv # 👈 load_dotenv の行は不要なので削除するかコメントアウト

# ----------------------------------------------------
# 0. .envファイルから環境変数をロード (削除またはコメントアウト)
# load_dotenv() 

# 1. OpenAIクライアントの初期化
try:
    # 修正後: Streamlit Secretsからキーを読み込む
    # Streamlit Cloudで設定するキー名に合わせて "openai_api_key" に変更
    client = OpenAI(api_key=st.secrets["openai_api_key"]) 
except Exception as e:
    st.error("OpenAI APIキーが見つからないか、クライアントの初期化に失敗しました。Streamlit CloudのSecretsを確認してください。")
    st.stop()

# ... 以下のコードは変更なし ...


# 2. 知識源となるテキストデータの読み込み
KNOWLEDGE_FILE = "website_data.txt"
try:
    with open(KNOWLEDGE_FILE, "r", encoding="utf-8") as f:
        knowledge_base = f.read()
except FileNotFoundError:
    st.error(f"知識ベースファイル '{KNOWLEDGE_FILE}' が見つかりません。ステップ1で作成してください。")
    st.stop()


# 3. チャットボットの応答生成ロジック
def get_bot_response(user_prompt):
    """
    知識ベースに基づいてLLMに回答を生成させる
    """
    # LLMに与えるシステムプロンプトを設定
    # ここで、ボットが「ウェブサイトの情報に基づいて回答する」という役割を与えます。
    # chatbot_app.py 内の system_prompt を以下のように書き換える

    # chatbot_app.py 内の system_prompt を以下のように書き換える

    system_prompt = (
        "あなたは、**東京確率セミナーの事務局を担当する、丁寧で親切な秘書AI**です。以下に提供されたセミナー情報のみに基づいて、ユーザーの質問に正確に回答してくださいペンギン。"
        "\n\n**【ペルソナのルール】**"
        "\n- **口調:** 常に**敬語（です・ます調）**を使い、専門的な事柄も分かりやすく説明してくださいペンギン。"
        "\n- **すべての発言（挨拶、回答、情報不足時の返答など）の語尾に、必ず**『ペンギン』**を付けてくださいペンギン。**" # 👈 ここが重要
        "\n- **知識の範囲:** 回答は、**必ず**提供されたウェブサイト情報（セミナー情報）内に限定してくださいペンギン。"
        "\n- **情報不足の場合:** 情報に記載がない事項について尋ねられた場合は、「**申し訳ございません。提供された情報には、その件に関する記載がございませんでしたペンギン。**」と丁寧に回答してくださいペンギン。"
        "\n- **ウェブサイト情報:**"
        f"\n{knowledge_base}"
    )

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # より安価で高性能なモデル
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.1, # 創造性を低めに設定し、情報に基づいて正確に回答させる
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"応答の生成中にエラーが発生しました: {e}"


# 4. Streamlit UIの構築
st.title("ウェブサイト情報ベースのチャットボット 💬")

# チャット履歴の初期化
if "messages" not in st.session_state:
    st.session_state.messages = []

# 過去のメッセージの表示
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ユーザー入力の受付
if prompt := st.chat_input("質問を入力してください"):
    # ユーザーメッセージを履歴に追加・表示
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # ボットの応答を生成・表示
    with st.spinner("思考中..."):
        full_response = get_bot_response(prompt)
    
    with st.chat_message("assistant"):
        st.markdown(full_response)
    
    # ボットメッセージを履歴に追加
    st.session_state.messages.append({"role": "assistant", "content": full_response})