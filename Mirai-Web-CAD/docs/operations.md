# 運用・復旧メモ

## ローカル運用

```bash
npm run dev
```

`http://127.0.0.1:4174/`でSPAと`/api`を同一オリジン確認できます。ブラウザ保存はLocalStorageです。破損時は画面左ツールの「デモ初期化」またはブラウザDevToolsで`mirai-web-cad-mvp`キーを削除します。

## Build

```bash
npm run build
```

`dist/`は静的配信用成果物です。Cloudflare Pagesへ配信する場合は、build commandを`npm run build`、output directoryを`dist`にします。Functionsは`functions/api/[[path]].js`から`src/api-handler.js`を呼び出します。

Cloudflareローカル互換確認:

```bash
npm run build
wrangler pages dev dist --port=4176
curl http://127.0.0.1:4176/api/health
```

## Neon初期化

```bash
psql "$DATABASE_URL" -f migrations/0001_initial.sql
psql "$DATABASE_URL" -f seeds/demo.sql
```

注意:

- 本番DBへ適用する前にPreview/検証DBへ適用します
- 既存本番データ削除は行いません
- migrationは`create table if not exists`中心で、空DBに再実行できる形です

## Rollback

静的MVPのrollbackはCloudflare Pages/Workersの直前Versionへ戻します。DB migrationは破壊的変更を含めていないため、rollback時も既存テーブルを削除しません。

## 監視観点

- SPA 200応答
- Canvas描画が空白でないこと
- LocalStorage保存失敗の有無
- `/api/health`、認証fail-closed、書き込み監査ログを確認
- Neon接続後はDB mode、migration version、書き込み/再読込整合を確認

## 既知制約

- DWG/DXF/PDF実変換は未実装
- AIは外部LLMではなくルールベースのMVP提案
- Neon/Cloudflare/GitHubへの実デプロイは未接続
- Cloudflareローカル互換は確認済み。Cloudflare Preview公開はPages project作成/DeployのGateを通して実施する
- Cloudflare Preview: `https://mvp-round-2.mirai-web-cad.pages.dev/`
- 自動E2E、axe等のA11y検査、Visual Regressionは次Roundで追加予定
