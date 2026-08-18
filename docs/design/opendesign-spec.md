# OpenDesign 設計仕様(画面構成・UI/UX 正本)

> 本ドキュメントは OpenDesign が生成した画面設計プロトタイプ
> (`webui/Construction-Enterprise-OS---Standalone-_1_.html`、単一ファイル React SPA)から抽出した、本プロジェクトの**画面構成・UI/UX・デザイン仕様の起点**です。
> 実装(MVP)は本仕様と整合することを完了条件とします。

## 1. 設計ソースの来歴

| 項目 | 値 |
|---|---|
| 設計プロトタイプ | `webui/Construction-Enterprise-OS---Standalone-_1_.html`(約 9MB 単一ファイル、React 18 + Babel + Leaflet 1.9 同梱) |
| OpenDesign ハンドオフ | `webui/DESIGN-HANDOFF.md`・`webui/DESIGN-MANIFEST.json`・`webui/brand-spec.md`・`webui/index.html`(経営向け戦略レビューデッキ) |
| OpenDesign プロジェクト | `.od/projects/700407d7-5e4d-4746-a848-80404abfafa9` |
| 生成日 | 2026-08-18 |
| MVP 公開先 | `https://construction-os-mvp.mirai-dx-platform.com`(Pages プロジェクト `construction-os-mvp`、CI 自動デプロイ) |
| ブランド仕様 | OpenDesign がプロトタイプ CSS 変数から抽出(brand-spec.md) |

## 2. ブランドトークン

- ベース: スレート + ブルー。`--bg: #f8fafc` / `--fg: #0f172a` / `--accent: #1a56db`
- 状態色: `--ok: #16a34a`(稼働)/ `--warn: #f97316`(警戒)/ `--danger: #dc2626`(危険) — 状態は色ペア(10% tint 背景)で表現
- ダーク: サーフェスは `#0f172a`/`#1e293b`(グレーでなくネイビー)、アクセント `#3b82f6`
- フォント: 本文 `Noto Sans JP` / 数値・KPI・ラベルは `JetBrains Mono`(値と散文のハードスプリット)
- カード: 1px ボーダー + 12px radius、影は最小。密度優先

## 3. ロール定義(6 ロール)

| id | ラベル | 色 |
|---|---|---|
| admin | IT管理者 | #7c3aed |
| field | 現場監督 | #f97316 |
| exec | 経営層 | #1a56db |
| partner | 協力会社 | #16a34a |
| safety | 安全管理者 | #dc2626 |
| maintain | 維持管理 | #92400e |

ロール別デフォルト展開カテゴリ:
- admin: 共通基盤 / セキュリティ・監査 / システム管理
- field: 現場DX / 文書・図面管理 / 協力会社連携
- exec: ダッシュボード / ERP・経営管理
- partner: 協力会社連携
- safety: 現場DX / IoT・リアルタイム監視
- maintain: IoT / GIS / 文書

## 4. 画面構成(3 階層アコーディオンメニュー、全ルート)

### 4.1 ダッシュボード
| ページ | ルート |
|---|---|
| 全社統合 | `/dashboard` |
| 現場ダッシュボード | `/dashboard/field` |
| 経営ダッシュボード | `/dashboard/exec` |
| AI分析 | `/dashboard/ai` |
| KPI/アラート | `/dashboard/kpi`(バッジ 3) |

### 4.2 共通基盤(admin)
| ページ | ルート |
|---|---|
| Entra ID / AD連携 / MFA / SSO | `/common/auth/*` |
| ユーザー一覧 / 権限管理 | `/common/users` `/common/roles` |
| API一覧 / APIログ | `/common/api` `/common/api/logs` |
| マスタデータ / システム設定 | `/common/master` `/common/config` |

### 4.3 文書・図面管理
PDF管理 `/documents/pdf` ・ CAD図面 `/documents/cad` ・ BIM/CIM `/documents/bim` ・ 写真管理 `/documents/photo` ・ 動画管理 `/documents/video` ・ OCR `/documents/ocr` ・ 電子黒板 `/documents/board` ・ 電子納品 `/documents/deliver`(バッジ2)・ バージョン管理 `/documents/version` ・ AI文書検索 `/documents/ai-search`

### 4.4 現場DX
| セクション | ページ |
|---|---|
| 工事管理(field/exec/safety) | 工事一覧 `/field/projects`・現場進捗 `/field/progress`・工程管理 `/field/schedule`・作業日報 `/field/daily`(バッジ5) |
| 現場作業(field/safety) | 現場写真 `/field/photos`・出来形管理 `/field/measure`・安全管理 `/field/safety`(バッジ!)・KY活動 `/field/ky` |
| リソース管理(field) | 重機管理 `/field/equipment`・作業員管理 `/field/workers`・現場ライブビュー `/field/live` |

### 4.5 協力会社連携(field/partner)
協力会社一覧 `/partner/list` ・ 入退場管理 `/partner/entry` ・ 提出書類 `/partner/docs`(バッジ4) ・ 安全教育 `/partner/education` ・ 契約管理 `/partner/contract` ・ 請求管理 `/partner/invoice`

### 4.6 GIS / 地図
工事位置 `/gis/projects` ・ 海域マップ `/gis/ocean` ・ 災害情報 `/gis/disaster` ・ ドローン地図 `/gis/drone` ・ 点群データ `/gis/pointcloud` ・ ハザードマップ `/gis/hazard` ・ リアルタイム位置 `/gis/realtime`

### 4.7 AI・分析基盤
AIチャット `/ai/chat` ・ ナレッジAI `/ai/knowledge` ・ OCR AI `/ai/ocr` ・ 画像解析AI `/ai/vision` ・ 予測AI `/ai/predict` ・ 異常検知AI `/ai/anomaly` ・ AI Agent `/ai/agent`

### 4.8 IoT・リアルタイム監視
センサ一覧 `/iot/sensors` ・ 気象情報 `/iot/weather` ・ 波浪監視 `/iot/wave` ・ 水位監視 `/iot/water` ・ IoT Gateway `/iot/gateway` ・ Edge AI `/iot/edge` ・ アラート管理 `/iot/alerts`(バッジ3) ・ リアルタイム監視 `/iot/realtime`

### 4.9 ERP・経営管理(exec)
原価管理 `/erp/cost` ・ 予算管理 `/erp/budget` ・ 契約管理 `/erp/contract` ・ 購買管理 `/erp/purchase` ・ 売上管理 `/erp/sales` ・ 労務管理 `/erp/labor` ・ 在庫管理 `/erp/stock` ・ 工事台帳 `/erp/ledger` ・ BIレポート `/erp/bi`

### 4.10 セキュリティ・監査(admin)
SIEM `/security/siem` ・ SOC `/security/soc` ・ VPN監視 `/security/vpn` ・ EDR `/security/edr` ・ OT監視 `/security/ot` ・ インシデント `/security/incident` ・ 監査レポート `/security/audit`

### 4.11 ワークフロー
承認一覧 `/workflow/approval`(バッジ5) ・ 稟議 `/workflow/ringi` ・ 作業許可 `/workflow/permit` ・ 電子決裁 `/workflow/esign` ・ 変更管理 `/workflow/change`

### 4.12 自動化・ロボティクス
自動施工 `/robotics/auto` ・ ドローン `/robotics/drone` ・ ROV `/robotics/rov` ・ デジタルツイン `/robotics/twin`

### 4.13 システム管理(admin)
サーバ監視 `/system/server` ・ DB管理 `/system/db` ・ バックアップ `/system/backup` ・ API状態 `/system/api-status` ・ DevOps/CI-CD `/system/devops`

## 5. ページ実装コンポーネント(プロトタイプ内)

- Main App Shell: ヘッダー(ブレッドクラム/通知パネル/ロール切替) + ルーティング + モバイルレスポンシブ
- Sidebar: 3 階層アコーディオン + ロールフィルタ
- Dashboard Page / 現場DX Page(+Sub-views) / Documents(PDF/Sub-views) / IoT(Sensors/Sub-views) / ERP(Cost/Sub-views) / 共通基盤 v2 / 協力会社連携 / セキュリティ・監査 v2 / AI・分析基盤 v2 / ワークフロー / GIS v2 / 自動化・ロボティクス v2 / システム管理
- 共通 UI: Slide Tab Panel、Icon System(SVG)、Dark Mode Theme Provider、Tweaks Panel(ロール・密度・サイドバーテーマ・ダーク切替)

## 6. 主要業務フロー(設計が想定する導線)

1. **経営/現場ダッシュボード**: 全社統合 → 現場・経営・AI・KPI 各ビュー(数値は Mono フォント、状態は色ペア)
2. **現場DX**: 工事一覧 → 進捗/工程/日報 → 写真/出来形/安全/KY → 重機/作業員/ライブ
3. **文書管理**: PDF/CAD/BIM ブラウズ → OCR/電子黒板/電子納品/バージョン管理/AI検索
4. **協力会社連携**: 一覧 → 入退場/書類/安全教育 → 契約/請求
5. **ワークフロー**: 承認一覧(稟議/作業許可/電子決裁/変更管理)
6. **ERP**: 原価/予算 → 契約/購買/売上 → 労務/在庫/台帳/BI
7. **IoT**: センサ/気象/波浪/水位 → アラート → リアルタイム監視(安全管理・維持管理ロール向け)

## 7. UI 状態・アクセシビリティ仕様

- 状態: ローディング(空状態)/エラー/権限なし(ロールフィルタ)/バッジ(未読・アラート数)
- レスポンシブ: ヘッダーのモバイルメニューボタン(`mobile-menu-btn`)、`hide-mobile` クラスでパンくず省略、サイドバー開閉
- キーボード: アコーディオン/タブパネル/ドロップダウンはフォーカス可能なボタン操作
- 通知: 承認依頼/IoTアラート/文書更新/AI通知(未読表示)
- ダークモード: CSS カスタムプロパティ切替(`--bg` 等)

## 8. 差分・注意点

- プロトタイプは**静的ダミーデータ**(モック)のみ。実装ではバックエンド API + Neon DB へ置換する
- 旧 Next.js 実装のルート(`/projects`, `/safety`, `/settings/*` 等)と本設計のルートは一部異なる — MVP では本設計のルートを正とする
- 本設計の各ページはタブパネル構成(v2)を採用 — 実装は Slide Tab Panel 相当の UI で統一する

## 9. E2E 検証結果(2026-08-18、Cloudflare Preview 実機)

`e2e/mvp.spec.ts`(Playwright、desktop + mobile の 2 プロジェクト計 18 テスト)を
`https://construction-os-mvp.mirai-dx-platform.com` に対して実行し **18/18 PASS**。

- ホーム: タイトル・サイドバー・ダッシュボード KPI(進行中工事/要承認/品川タワー新築工事)
- SPA フォールバック: 直接 URL でもアプリ起動(`_redirects` の `/* /index.html 200`)
- ワークフロー: 承認一覧・稟議タブ・SLA 達成率・承認依頼データの表示
- 現場DX: 工事一覧のダミーデータ表示
- ロール切替: 現場監督ビュー → 経営層ビュー(サイドバーバッジ反映)
- 通知パネル: 未読バッジ → パネル表示(すべて既読/承認依頼)
- モバイル(390×844): ハンバーガーメニューでサイドバー操作
- キーボード: Tab フォーカス移動
- ダークモード: テーマ変数切替後もコンテンツ表示

CI: `.github/workflows/e2e.yml`(main への `webui/**` push / workflow_dispatch で自動実行)

## 10. 残存リスク・既知の課題(要改善)

| # | 課題 | 影響 | 対応方針 |
|---|---|---|---|
| 1 | サイドバー展開時に別要素がポインタイベントを横取り(稟議等のボタンがクリック不能) | マウス操作の一部が不能(キーボード操作は可) | 実装(Next.js 化)時に z-index/レイアウトを是正。E2E は focus+Enter で回避 |
| 2 | ルーティングが state ベースで URL と同期しない | ディープリンク/共有/リロードでホームに戻る | 実装時に Next.js ルーターへ置換 |
| 3 | データは静的ダミーのみ(API/DB 未接続) | 実データ操作は不可 | バックエンド API + Neon への置換(次フェーズ) |
| 4 | 認証はダミー(ロール切替のみ)。実認証(JWT/Neon)は未接続 | 権限境界の実証なし | auth サービス + Neon の接続(次フェーズ) |
