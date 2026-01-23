# chatbot_app.py の修正箇所

import google.generativeai as genai
import streamlit as st

# ----------------------------------------------------
# 0. .envファイルから環境変数をロード (削除またはコメントアウト)
# load_dotenv() 

# 1. Gemini クライアントの初期化
try:
    genai.configure(api_key=st.secrets["gemini_api_key"])
    model = genai.GenerativeModel("gemini-pro")
except Exception as e:
    st.error("Gemini APIキーが見つからないか、初期化に失敗しました。Streamlit Secretsを確認してください。")
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
    知識ベースに基づいて Gemini に回答を生成させる
    """

    system_prompt = (
        "あなたは、**東京確率セミナーの事務局を担当する、丁寧で親切な秘書AI**です。"
        "以下に提供されたセミナー情報のみに基づいて、ユーザーの質問に正確に回答してくださいペンギン。"
        "\n\n【ペルソナのルール】"
        "\n- 口調: 常に敬語（です・ます調）を使用してくださいペンギン。"
        "\n- すべての発言の語尾に必ず「ペンギン」を付けてくださいペンギン。"
        "\n- 回答は必ず提供されたウェブサイト情報の範囲内に限定してくださいペンギン。"
        "\n- 情報がない場合は「申し訳ございません。提供された情報には、その件に関する記載がございませんでしたペンギン。」と答えてくださいペンギン。"
        "\n\n【ウェブサイト情報】\n"
        f"{knowledge_base}"
    )

    prompt = f"""
{system_prompt}

【ユーザーの質問】
{user_prompt}
"""

    try:
        response = model.generate_content(
            prompt,
            generation_config={
                "temperature": 0.1,
            }
        )
        return response.text
    except Exception as e:
        return f"応答の生成中にエラーが発生しました: {e}"

# 4. Streamlit UIの構築
st.title("東京確率論セミナーのチャットボット 💬")

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
