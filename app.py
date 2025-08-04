import streamlit as st
import os
from dotenv import load_dotenv
from openai import OpenAI # OpenAIの新しいPythonライブラリを使用

# .envファイルから環境変数を読み込む
# これにより、OPENAI_API_KEYがos.environから利用可能になる
load_dotenv()

# OpenAI APIキーの取得
# ローカルでは.envから、Streamlit CloudではSecretsから読み込まれる
api_key = os.getenv("OPENAI_API_KEY")

# APIキーが設定されていない場合の警告
if not api_key:
    st.error("OpenAI APIキーが設定されていません。.envファイルまたはStreamlit CloudのSecretsに設定してください。")
    st.stop() # APIキーがない場合はアプリの実行を停止

# OpenAIクライアントの初期化
client = OpenAI(api_key=api_key)

# --- Webアプリの概要と操作方法 ---
st.set_page_config(page_title="専門家チャットアプリ", layout="centered") # ページ設定

st.title("🤖 専門家チャットアプリ")
st.markdown("""
このアプリは、あなたの質問に対して、選択した専門家の視点からLLM（大規模言語モデル）が回答します。
以下の手順でご利用ください：

1.  **専門家を選択:** ラジオボタンから、回答してほしい専門家の種類を選びます。
2.  **質問を入力:** 下のテキストボックスに質問を入力します。
3.  **送信:** 「回答を生成」ボタンをクリックすると、LLMが回答を生成します。

様々な専門家になりきったLLMの回答をお楽しみください！
""")

# --- 専門家の種類とシステムメッセージの定義 ---
# ラジオボタンで選択される専門家と、それに対応するシステムメッセージを定義します。
# システムメッセージは、LLMにその役割を指示するために使用されます。
expert_roles = {
    "ITコンサルタント": "あなたはITコンサルタントです。技術的な課題解決、システム導入、DX推進に関する専門知識を持ち、論理的かつ実践的なアドバイスを提供します。",
    "料理研究家": "あなたは料理研究家です。食材の知識、調理法、栄養バランス、食文化に精通しており、美味しくて健康的なレシピや食に関する情報を提供します。",
    "歴史学者": "あなたは歴史学者です。世界史、日本史、文化史など幅広い歴史的知識を持ち、客観的な事実に基づいた深い洞察と解説を提供します。",
    "キャリアアドバイザー": "あなたはキャリアアドバイザーです。個人のスキル、経験、興味を考慮し、転職、キャリアアップ、自己成長に関する具体的なアドバイスとサポートを提供します。",
}

# --- LLMとのやり取りを行う関数 ---
# 入力テキストと選択された専門家（システムメッセージ）を受け取り、LLMの回答を返す
def get_llm_response(user_input: str, expert_system_message: str) -> str:
    """
    LLM（大規模言語モデル）にプロンプトを渡し、回答を取得する関数。

    Args:
        user_input (str): ユーザーからの入力テキスト（質問）。
        expert_system_message (str): LLMに振る舞わせる専門家のシステムメッセージ。

    Returns:
        str: LLMからの回答テキスト。
    """
    try:
        # ChatCompletion APIを呼び出す
        # messagesリストで会話のコンテキストを定義
        response = client.chat.completions.create(
            model="gpt-3.5-turbo", # 使用するLLMモデルを指定
            messages=[
                {"role": "system", "content": expert_system_message}, # 専門家の役割を設定
                {"role": "user", "content": user_input} # ユーザーの質問
            ],
            temperature=0.7, # 回答の創造性（0.0-1.0、高いほど創造的）
            max_tokens=500,  # 生成される回答の最大トークン数
        )
        # 回答テキストを抽出して返す
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"LLMからの回答取得中にエラーが発生しました: {e}")
        return "回答の取得に失敗しました。"

# --- Streamlit UIの構築 ---

# ラジオボタンで専門家を選択
selected_expert = st.radio(
    "回答してほしい専門家を選択してください:",
    list(expert_roles.keys()), # expert_rolesのキーをラジオボタンの選択肢にする
    index=0 # デフォルトで最初の専門家を選択
)

# ユーザーからの入力フォーム
user_question = st.text_area("ここに質問を入力してください:", height=150)

# 回答生成ボタン
if st.button("回答を生成"):
    if user_question:
        with st.spinner("専門家が回答を考えています..."): # 処理中にスピナーを表示
            # 選択された専門家に応じたシステムメッセージを取得
            system_message_for_llm = expert_roles[selected_expert]
            
            # LLMとのやり取り関数を呼び出す
            llm_answer = get_llm_response(user_question, system_message_for_llm)
            
            # 回答を画面に表示
            st.subheader(f"✨ {selected_expert}からの回答:")
            st.write(llm_answer)
    else:
        st.warning("質問を入力してください。")

