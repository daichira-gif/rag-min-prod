# Dockerで動かす本格RAGアプリをゼロから構築した全記録（FastAPI + pgvector）

## はじめに

最近RAG（検索拡張生成）の勉強をしているのですが、せっかくならDockerとCI/CDの学習も兼ねて、アプリ作成～OSSとして公開までやってみようと思い、LLMに相談しながらイチから構築してみました。

この記事は、そのLLMとの対話を通じて、アプリケーションの骨格作成から、CI/CDパイプラインの構築、そして本番運用を見据えた様々な機能を実装し、その過程で遭遇した数々の問題を解決していくまでの全記録です。

> この記事は、LLMが作成した原稿を、人の目で確認・修正した上で公開したものです。

## 目指した構成：本番運用できるアプリの機能

今回、出来る限り「デモ」で終わらないアプリケーションを目指すため、以下の機能を実装することにしました。

- **FastAPI + pgvector**: 高速なWebフレームワークと、ベクトル検索に強いPostgreSQL拡張の組み合わせ。
- **Docker / docker-compose**: 誰でも簡単に環境構築ができ、どこでも同じ環境を再現可能にする。
- **CI/CD (GitHub Actions)**: コードの品質チェックやテスト、Dockerイメージのビルド・公開までを完全自動化。
- **A/Bテスト**: `PROMPT_VERSION_A/B` や `MODEL_VERSION_A/B` といった環境変数で、複数のプロンプトやモデルの性能を比較テストする仕組み。
- **セキュリティ**: 個人情報（PII）のマスキングや、プロンプトインジェクション攻撃の基礎的な防御機能。
- **可観測性 (Observability)**: 構造化ロギングやOpenTelemetryによるトレーシングに対応。

## 完成形：アプリケーションの動かし方

最終的に完成したアプリケーションは、以下の手順で誰でもすぐに動かすことができます。

### 1. リポジトリをクローン

まず、完成したプロジェクトをローカルマシンに持ってきます。

```bash
git clone https://github.com/daichira-gif/rag-min-prod.git
cd rag-min-prod
```

### 2. 環境変数の設定

設定ファイルのテンプレート（`.env.sample`）をコピーして、自分用の設定ファイル（`.env`）を作成します。

```bash
# Windows PowerShellの場合
Copy-Item .env.sample .env

# Mac/Linuxの場合
cp .env.sample .env
```

作成した`.env`ファイルを開き、必要な値を設定します。

> **【最重要】APIキーとセキュリティ**
> - デフォルトではOpenAIの埋め込みモデルを利用します。動作させるには、`OPENAI_API_KEY`にあなたのOpenAI APIキーを**必ず設定してください。**
> - もし過去にこのキーをGitHubにプッシュしてしまった場合は、**必ずそのキーを無効化（Revoke）し、新しいキーを再発行してください。**
>
> **【注意】OTelエンドポイント**
> - `OTEL_EXPORTER_OTLP_ENDPOINT` は、OpenTelemetryの送信先がない場合は**必ず空欄のまま**にしてください。不正なURIを設定すると起動時にエラーとなります。

### 3. サービスの起動

Docker Composeを使って、アプリケーションとデータベースのコンテナを起動します。`-d`オプションでバックグラウンドで起動します。

```bash
docker compose up --build -d
```

### 4. データベースの初期化

初回起動時のみ、データベースのテーブルを作成するための以下のコマンドを実行します。

```bash
docker compose exec db psql -U rag -d rag -f /docker-entrypoint-initdb.d/init_db.sql
```

### 5. 動作確認

ヘルスチェック用のAPIを叩き、アプリケーションが正常に起動しているか確認します。

```powershell
# PowerShellの場合 (推奨)
Invoke-RestMethod -Uri http://localhost:8000/health

# Mac/Linuxの場合
curl http://localhost:8000/health
```

`{"status":"ok"}` と返ってくれば、環境構築は成功です！

## 基本的な使い方と機能テスト

### 1. 知識の投入と検索（RAGの基本動作）

**PowerShellでの実行例 (推奨):**
```powershell
# ヘッダーとボディを定義
$h = @{"Content-Type"="application/json"; "x-user-id"="alice"}
$body_ingest = @{content="Gemini is a large language model created by Google."} | ConvertTo-Json
$body_query = @{query="Who created Gemini?"} | ConvertTo-Json

# 知識を投入
Invoke-RestMethod -Uri http://localhost:8000/ingest -Method Post -Headers $h -Body $body_ingest

# 質問する
Invoke-RestMethod -Uri http://localhost:8000/query -Method Post -Headers $h -Body $body_query
```

**Mac/Linuxでの実行例:**
```bash
# 知識を投入
curl -X POST http://localhost:8000/ingest \
  -H "Content-Type: application/json" \
  -d '{"content":"Gemini is a large language model created by Google."}'

# 質問する
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -H "x-user-id: alice" \
  -d '{"query":"Who created Gemini?"}'
```
成功すれば、応答JSONの`Context:`に投入した知識が含まれ、それに基づいた回答が返ってきます。

### 2. 自動テストの実行

プロジェクトに同梱されているテストスイートを実行します。`PYTHONPATH`の設定が必須です。

```bash
docker compose exec -e PYTHONPATH=. app pytest -v
```
`4 passed` のように表示されれば成功です。

## 今回躓いたポイント(Tips集)

アプリケーションをゼロから構築する過程は、まさに問題解決の連続でした。その中でも印象的なトラブルシューティングの記録をTipsとして共有します。

### Tip 1: RAG検索が機能しない → 複数原因の切り分け

データを投入できるのに、検索で全く情報がヒットしない、という最も解決に時間がかかった問題です。LLMと仮説検証を繰り返しました。

- **原因A：DBへのデータ不整合**
  - **症状:** `/query`で500エラーが頻発。エラーログには`operator does not exist: vector <=> numeric[]`。
  - **診断:** PythonのリストがPostgreSQL側で`vector`型として認識されていないことが原因と特定。`pgvector`の型アダプタ（`register_vector`）を正しく適用することで解決。
- **原因B：データが保存されていない**
  - **症状:** 500エラーは解消されたが、検索結果が常に空になる。
  - **診断:** アプリケーションのアーキテクチャ変更の際に、DB接続の`autocommit`設定が漏れていたことをLLMが指摘。これにより、`/ingest`のデータが実際にはDBに保存されていなかったことが判明。`conn.autocommit = True`を追加して解決。
- **原因C：DBインデックスの罠**
  - **症状:** `autocommit`を修正しても、まだ検索結果が空になる。
  - **診断:** 最終的に、`init_db.sql`で作成される`ivfflat`インデックスが、データが数件しかない場合にうまく機能せず、検索結果を0件にしてしまうという結論に到達。インデックス作成処理を`init_db.sql`から削除し、確実な全件検索に切り替えることで、ついに問題は完全に解決しました。
  - **将来的な対策:** 大量のデータを投入した後は、`ANALYZE documents;`を実行したり、インデックスを再作成するのが定石です。または、`ivfflat`の代わりに`hnsw`インデックスの利用を検討するのも良いでしょう。

### Tip 2: GitHubのPush Protectionに学ぶ

開発初期、誤って`.env`ファイルをコミットしてしまい、GitHubのPush Protection機能にプッシュをブロックされました。LLMに相談したところ、これはセキュリティ上非常に良いことであり、正しい`.gitignore`の設定方法と、一度コミットしてしまった秘密情報を履歴からクリーンにする方法（今回はローカルリポジトリの再作成）、そして**漏洩したキーは直ちに無効化・再発行する**という鉄則を学びました。

### Tip 3: CI/CD環境特有のエラーを解決する

ローカルでは成功するテストが、GitHub Actions上では`ModuleNotFoundError`やベクトル次元の不一致エラーで失敗しました。

- **`ModuleNotFoundError`:** CI環境で`pytest`が`src`フォルダの場所を認識できていないのが原因でした。`ci.yml`のテスト実行ステップに`env: { PYTHONPATH: . }`を追加して解決。
- **次元不一致エラー:** CIが使うモデル（384次元）とDBスキーマ（1536次元）の定義が異なっていました。`ci.yml`内で`sed`コマンドを使い、テスト実行時だけ動的にDBスキーマの次元数を書き換えることで、ローカル環境に影響を与えずにCIをパスさせる堅牢な解決策を実装しました。

### Tip 4: Windows固有の落とし穴

Windows + Docker Desktop + WSL2という環境では、特有の「ハマりどころ」があります。

- **PowerShellの`curl`:** `curl`は`Invoke-WebRequest`のエイリアスです。APIテストには、JSONを自動でパースしてくれる`Invoke-RestMethod`を使うのが最も確実で、トラブルが少ないです。
- **OneDrive配下でのビルド:** `C:\Users\ユーザー名\OneDrive`配下で`docker build`を行うと、ファイルの同期・ロックが原因で予期せぬエラーが発生することがあります。プロジェクトは`C:\dev`のような、同期対象外のディレクトリに置くのが安全です。
- **Dockerの不調:** PCのスリープからの復帰後などにDockerの調子が悪くなったら、`wsl --shutdown` → Docker Desktopを再起動 → `docker builder prune -af`で大抵は回復します。

## まとめ

本番品質を意識したRAGアプリケーションをゼロから構築する旅は、多くの発見と学びに満ちていました。
この記事で紹介したアプリケーションと、問題解決の記録が、これからRAGアプリ開発に挑戦する方々の助けになれば、幸いです。
