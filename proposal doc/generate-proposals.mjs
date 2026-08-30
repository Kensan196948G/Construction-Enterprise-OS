import { mkdir, writeFile } from "node:fs/promises";
import { fileURLToPath } from "node:url";
import path from "node:path";

const outDir = path.dirname(fileURLToPath(import.meta.url));

const groups = {
  business: { label: "事業者", icon: "🏢", accent: "#1457d9", soft: "#eaf1ff" },
  field: { label: "現場", icon: "👷", accent: "#b45309", soft: "#fff4df" },
  management: { label: "管理", icon: "📋", accent: "#0f766e", soft: "#e3f6f3" },
};

const proposals = [
  {
    no: "01", slug: "ゼネコン", group: "business", role: "ゼネコン", audience: "全社DX責任者・工事部門長・情報システム部門",
    headline: "現場の事実を、全社の意思決定へ。",
    lead: "工程・原価・安全・承認・文書・協力会社を、現場ごとの個別最適から全社でつながる業務基盤へ移行します。",
    decision: "まず代表1現場で、日報から原価見通しまでの情報連鎖を4〜6週間検証してください。",
    pains: [
      ["集計が遅い", "複数現場の進捗と原価がExcel・メール・個別システムに分散し、月次判断が後追いになる。"],
      ["承認が見えない", "稟議、施工計画、変更、支払の滞留箇所と責任者を横断して把握しにくい。"],
      ["証跡が切れる", "日報・写真・安全是正・図面改訂と、経営数値の根拠が別々に保管される。"],
    ],
    outcomes: ["工事別の工程・原価・安全・承認を同じ画面体系で確認", "現場入力から週報・月次報告までの転記を削減", "権限別ビューと承認履歴を前提に統制を設計"],
    flow: ["工事台帳", "日報・進捗", "安全・品質", "承認・変更", "原価見通し"],
    capabilities: [
      ["経営・現場ダッシュボード", "実装済み", "工事KPI、要承認、進捗をロール別に表示"],
      ["現場DX / 文書 / 安全", "実装済み", "一覧・検索・作成・編集・削除をMVPで体験可能"],
      ["ERP / 工事台帳 / ワークフロー", "PoCで検証", "自社の勘定・承認経路・管理粒度との適合を確認"],
      ["基幹・会計・全社DB連携", "導入時に実装", "API、データ移行、マスタ同期、監査設計が必要"],
    ],
    kpis: [["月次原価集計日数", "締めから速報確定まで"], ["原価差異の検知時間", "発生から責任者の認知まで"], ["承認リードタイム", "申請から完了まで／SLA達成率"], ["週報作成時間", "現場集計と転記に要する時間"], ["安全是正完了率", "期限内完了件数 ÷ 対象件数"]],
    pilot: ["代表現場と対象業務を決定。既存帳票・コード体系・基準KPIを棚卸し", "日報→安全→承認→原価の一連フローをMVPで再現し、差分を記録", "接続方式、権限、データ移行、全社展開条件を合意し投資判断"],
  },
  {
    no: "02", slug: "サブコン", group: "business", role: "サブコン", audience: "工事部門長・現場代理人・業務改善責任者",
    headline: "元請報告と自社管理を、一度の入力でつなぐ。",
    lead: "工程、作業員、重機、安全、出来高、請求を同じ業務線上に置き、現場の二重入力と報告待ちを減らします。",
    decision: "1工区・1工種を選び、朝礼から請求準備までの転記回数と所要時間を測定します。",
    pains: [["二重入力", "元請様式と自社様式に同じ進捗・人員・出来高を繰り返し入力する。"], ["変更が伝わらない", "工程や施工条件の変更が口頭・電話・チャットに散り、手戻りにつながる。"], ["請求準備が重い", "日報、出来高、写真、契約情報を月末に集め直して照合する。"]],
    outcomes: ["朝礼・KYから日報、写真、進捗、出来高まで連続して記録", "変更・承認・差戻しを状態と期限で確認", "契約・原価・請求の根拠を現場記録にひも付ける"],
    flow: ["朝礼・KY", "入場・配置", "日報・写真", "出来高確認", "請求準備"],
    capabilities: [["工程・日報・写真・出来形", "実装済み", "現場監督ビューを含むMVP操作を提供"], ["安全・IoT・アラート", "PoCで検証", "自社手順と通知閾値、責任分担を確認"], ["契約・原価・請求", "PoCで検証", "元請提出様式と自社管理項目の対応を検証"], ["元請システム・センサー接続", "導入時に実装", "接続先仕様、通信断、同期方式を設計"]],
    kpis: [["日報作成時間", "入力開始から提出まで"], ["当日報告率", "当日提出 ÷ 対象日報"], ["工程差異把握時間", "遅延発生から認知まで"], ["書類差戻し率", "差戻し件数 ÷ 提出件数"], ["請求準備日数", "締めから請求提出まで"]],
    pilot: ["対象工区、元請提出物、現場の入力者・承認者を確定", "朝礼→日報→出来高→請求のシナリオを試行し、転記と待ち時間を計測", "元請連携・オフライン・帳票出力の要件を整理し導入範囲を決定"],
  },
  {
    no: "03", slug: "専門工事会社", group: "business", role: "専門工事会社", audience: "代表者・工事責任者・安全書類担当者",
    headline: "入場から請求まで、現場事務を一本化。",
    lead: "作業員・資格・安全教育・提出書類・日報・契約・請求を現場単位でまとめ、少人数でも回る管理へ変えます。",
    decision: "1社・1現場・10〜30名規模で、スマートフォン入力の負荷と差戻し削減を確かめます。",
    pains: [["入場準備が煩雑", "作業員名簿、資格、安全教育、提出書類を現場ごとに作り直す。"], ["期限を追えない", "資格更新や書類期限が担当者の記憶と表計算に依存する。"], ["請求根拠が散在", "日報、写真、出来高、契約条件が別々で、確認と差戻しが増える。"]],
    outcomes: ["会社・作業員・資格・入退場情報を現場単位で整理", "日報・写真・安全記録と出来高・請求をつなぐ", "未提出・期限・差戻しを一覧で確認"],
    flow: ["会社登録", "資格・教育", "入退場", "日報・写真", "請求"],
    capabilities: [["協力会社6業務領域", "実装済み", "入退場、書類、教育、契約、請求をMVPで操作可能"], ["現場日報・写真・安全", "実装済み", "同じ画面体系で登録・検索・更新"], ["協力会社専用ビュー", "PoCで検証", "表示フィルタは実装済み。実務のデータ分離を検証"], ["電子契約・会計・端末間共有", "導入時に実装", "正式署名、API、業務DB接続が必要"]],
    kpis: [["新規入場手続時間", "登録開始から入場可まで"], ["未提出書類率", "未提出 ÷ 必須書類"], ["資格期限切れ件数", "就業対象者の期限切れ"], ["報告作成時間", "日報・写真提出に要する時間"], ["請求差戻し率", "差戻し件数 ÷ 請求件数"]],
    pilot: ["対象現場・作業員・提出書類を選び、現在時間を計測", "登録→入場→日報→書類→請求をスマートフォン中心で試行", "データ分離、電子契約、会計連携、正式帳票の導入要件を確定"],
  },
  {
    no: "04", slug: "現場作業員", group: "field", role: "現場作業員", audience: "職長・技能者・オペレーター",
    headline: "記録のために、作業を止めない。",
    lead: "今日の指示、安全確認、写真、実績報告を迷わない順番にまとめ、現場での入力時間と確認の往復を減らします。",
    decision: "一つの作業班で、朝礼から終業報告までを実機で試し、入力時間と迷いを測ります。",
    pains: [["情報を探す", "最新版の図面、作業指示、変更点が複数の連絡手段に分かれている。"], ["記録で手が止まる", "写真・日報・出来形を後からまとめて入力し、残業や漏れが生じる。"], ["危険が共有されにくい", "KYやヒヤリハットが紙で閉じ、他班への展開が遅れる。"]],
    outcomes: ["今日やること・注意点・必要図面を一つの入口で確認", "写真と実績を作業の流れでその場登録", "危険・不具合を記録し、監督の確認へ回す"],
    flow: ["指示確認", "KY・点検", "作業", "写真・出来形", "終業報告"],
    capabilities: [["現場DX画面・ローカルCRUD", "実装済み", "日報・写真・安全・出来形の画面操作をMVPで確認可能"], ["日報・進捗・品質API", "PoCで検証", "APIコードは存在。写真・作業指示は現状モック一覧"], ["作業員専用ビュー", "導入時に実装", "現行WebUIに専用ロールはなく、認証側site_workerとの対応設計が必要"], ["オフライン同期・通知", "導入時に実装", "通信断時の保存・再送と実通知を設計"]],
    kpis: [["日報入力時間", "1人・1日あたり"], ["当日入力率", "当日完了 ÷ 対象報告"], ["写真整理時間", "撮影から提出まで"], ["指示確認の往復", "電話・口頭確認の回数"], ["危険報告初動", "報告から確認まで"]],
    pilot: ["対象班の一日の行動と入力場面を観察し、基準時間を計測", "朝礼→作業→写真→終業報告をスマートフォンで試行", "入力削減、オフライン、端末、教育の条件を合意"],
  },
  {
    no: "05", slug: "現場監督", group: "field", role: "現場監督", audience: "現場代理人・監理技術者・工事主任",
    headline: "巡回しながら、現場を閉じる。",
    lead: "工程、日報、写真、出来形、安全、協力会社、承認を同じ場所で追い、事務所に戻ってからの再集計を減らします。",
    decision: "1工区で日次運用を再現し、確認待ち・差戻し・転記の発生箇所を見える化します。",
    pains: [["確認が分散", "進捗・人員・安全・写真を別々の台帳やチャットから集める。"], ["承認が詰まる", "提出済みか、誰で止まっているか、期限内かを一覧で追えない。"], ["帰社後に再入力", "現場で確認した内容を事務所で報告書や工程表へ転記する。"]],
    outcomes: ["工事一覧から進捗・工程・日報・写真・安全へ連続して確認", "承認待ち、差戻し、期限超過を状態で把握", "現場記録から週報・出来高・原価確認へ情報をつなぐ"],
    flow: ["朝の計画", "巡回・確認", "是正指示", "日報承認", "翌日調整"],
    capabilities: [["現場監督ロール", "実装済み", "ロール切替と表示をE2Eで検証済み"], ["進捗・日報・品質・安全", "実装済み", "業務画面とCRUDをMVPで体験可能"], ["承認・変更・SLA", "PoCで検証", "自社の承認者、代理、期限、差戻しを設計"], ["現場データ共有・外部連携", "導入時に実装", "業務DB、通知、協力会社・基幹接続が必要"]],
    kpis: [["巡回後の事務時間", "終業後の集計・転記時間"], ["日報当日承認率", "当日承認 ÷ 提出日報"], ["是正完了時間", "指摘から完了確認まで"], ["承認SLA達成率", "期限内完了 ÷ 対象申請"], ["工程差異更新頻度", "最新情報までの遅延"]],
    pilot: ["対象工区の朝礼・巡回・承認・報告の現行動線を計測", "日報、写真、安全是正、承認をMVPで一週間相当試行", "必要な通知、権限、帳票、連携と展開判定KPIを確定"],
  },
  {
    no: "06", slug: "協力会社", group: "field", role: "協力会社", audience: "協力会社責任者・職長・事務担当者",
    headline: "何を、いつまでに出すかが分かる。",
    lead: "入退場、資格、安全教育、提出書類、契約、請求を一つの窓口にまとめ、元請との確認往復を減らします。",
    decision: "1現場・数社で提出業務を試し、未提出率と差戻し理由を共同で測定します。",
    pains: [["窓口が多い", "書類・契約・請求の提出先と手段が担当や現場で異なる。"], ["状況が分からない", "提出済みでも受付・差戻し・承認の状態を確認できない。"], ["同じ情報を再提出", "会社・作業員・資格情報を現場ごとに何度も作成する。"]],
    outcomes: ["必要書類、期限、提出状態、差戻し理由を一覧化", "入退場・教育・資格と現場配置を同じ情報で管理", "契約から請求までの確認窓口を統一"],
    flow: ["招待・登録", "書類提出", "入場・教育", "実績報告", "請求確認"],
    capabilities: [["協力会社ポータル画面", "実装済み", "6領域の一覧・検索・CRUDをデモ可能"], ["会社・作業員・契約・請求", "実装済み", "MVPのブラウザ内データで操作可能"], ["協力会社ビュー", "PoCで検証", "表示フィルタの実務適合と使いやすさを確認"], ["会社間データ隔離・正式提出", "導入時に実装", "テナント境界、実認証、通知、証跡を設計"]],
    kpis: [["提出準備時間", "必要書類の収集・作成時間"], ["未提出率", "未提出 ÷ 必須書類"], ["差戻し率", "差戻し ÷ 提出件数"], ["問い合わせ回数", "状態確認の電話・メール"], ["請求承認日数", "提出から確定まで"]],
    pilot: ["参加会社と対象書類を限定し、提出・確認の現行時間を計測", "登録→提出→差戻し→再提出→請求を共同試行", "認証、会社間隔離、通知、正式帳票の受入条件を確定"],
  },
  {
    no: "07", slug: "経営層", group: "management", role: "経営層", audience: "社長・役員・事業本部長",
    headline: "現場の変化を、利益とリスクで見る。",
    lead: "進捗・原価・承認・安全を同じ基準で横断し、報告を待つ経営から、例外を先に判断する経営へ移行します。",
    decision: "全社展開を先に決めず、代表現場で『早く分かったことで変えられた判断』を検証します。",
    pains: [["数字が遅い", "現場報告と会計数値の時点・粒度が違い、着地見通しが月次になる。"], ["例外が埋もれる", "工程遅延、原価超過、安全、承認滞留を会議まで把握できない。"], ["投資効果が曖昧", "DXが画面導入で終わり、時間・利益・リスクの改善で評価されない。"]],
    outcomes: ["工事KPI、要承認、原価、安全を経営層ビューで横断", "注意すべき現場と判断待ちを例外中心で確認", "導入前後の時間・品質・統制KPIで投資効果を評価"],
    flow: ["全社俯瞰", "例外検知", "原因確認", "意思決定", "効果追跡"],
    capabilities: [["経営層ビュー", "実装済み", "ロール切替をE2Eで検証済み"], ["ERP・原価・BI・承認", "PoCで検証", "画面操作は可能。実データで指標定義を検証"], ["監査・権限の基盤", "PoCで検証", "認証API/JWT/RBACは実証済み。WebUI統合は次工程"], ["全社リアルタイム経営", "導入時に実装", "業務DB、会計連携、データ品質責任が必要"]],
    kpis: [["着地見通し更新日数", "最新予測までの遅延"], ["例外検知時間", "発生から経営認知まで"], ["承認リードタイム", "重要案件の決裁日数"], ["原価差異率", "予算と見通しの差"], ["是正完了率", "重要リスクの期限内完了"]],
    pilot: ["重要判断を3〜5種類に絞り、現在の情報到達時間を計測", "代表現場の進捗・原価・安全・承認を経営ビューでレビュー", "KPI改善、データ責任、投資額、段階展開のゲートを決定"],
  },
  {
    no: "08", slug: "管理部門", group: "management", role: "管理部門", audience: "経理・総務・安全・品質・法務・情報システム",
    headline: "集める管理から、流れを整える管理へ。",
    lead: "申請、原価、契約、文書、権限、監査を共通ルールで扱い、督促・照合・転記に使う時間を減らします。",
    decision: "差戻しが多い一つの手続を選び、申請から保管までの標準化を先行検証します。",
    pains: [["様式が揃わない", "部門・現場ごとに項目、命名、保存場所、承認経路が異なる。"], ["督促が手作業", "未提出・期限超過・差戻しをメールや表計算で個別に追う。"], ["監査準備が重い", "権限、承認、文書版、変更理由の証跡を後から集める。"]],
    outcomes: ["申請・承認・文書・原価の状態と期限を共通化", "ロールと権限を業務責任に合わせて整理", "監査に必要な履歴と根拠の保持方針を設計"],
    flow: ["受付", "形式確認", "承認", "台帳反映", "保管・監査"],
    capabilities: [["ワークフロー・文書版管理", "実装済み", "申請、承認、差戻し、文書CRUDをMVPで操作"], ["ERP・契約・請求", "PoCで検証", "自社ルール、勘定、締め、責任分界を確認"], ["認証・RBAC", "実装済み", "auth API、JWT、ロール・権限を実証済み"], ["管理部門ビュー・SSO・正式監査", "導入時に実装", "専用WebUIロール、実認証、保存期間、基幹連携が必要"]],
    kpis: [["差戻し率", "差戻し ÷ 申請件数"], ["督促件数", "人手による期限確認"], ["承認SLA達成率", "期限内完了 ÷ 対象申請"], ["転記時間", "台帳・会計への再入力時間"], ["監査証憑収集時間", "依頼から提出可能まで"]],
    pilot: ["対象手続の様式、権限、承認、保存、例外処理を棚卸し", "MVPで受付→差戻し→承認→保管を再現し、工数を測定", "SSO、監査、保存期間、基幹接続、運用責任を導入設計に反映"],
  },
  {
    no: "09", slug: "発注者・監理者", group: "management", role: "発注者・監理者", audience: "発注機関・CM・工事監理者・検査担当者",
    headline: "報告を受け取るだけでなく、根拠まで辿れる。",
    lead: "進捗、出来形、品質、安全、変更、承認、文書版を案件の共通線上に置き、説明可能な監理を支えます。",
    decision: "定例会議で扱う3つの確認事項を選び、資料作成と根拠確認の時間を比較します。",
    pains: [["資料の時点が違う", "工程、出来高、写真、品質資料が別々に更新され、同じ時点で比較しにくい。"], ["変更根拠を追いにくい", "指示、協議、承認、図面改訂、金額影響のつながりが切れる。"], ["検査準備が後追い", "必要な写真・出来形・品質証明を検査前に集め直す。"]],
    outcomes: ["進捗・出来形・写真・品質・安全を同じ案件単位で確認", "変更と承認の状態、期限、関連文書を追跡", "検査・説明に必要な根拠を日常記録から準備"],
    flow: ["計画確認", "進捗監理", "品質・出来形", "変更承認", "検査・引渡し"],
    capabilities: [["進捗・出来形・写真・品質", "実装済み", "関連画面とブラウザ内CRUDをデモ可能"], ["文書版・ワークフロー", "実装済み", "版管理、承認、差戻しの機能を確認可能"], ["発注者・監理者専用ビュー", "導入時に実装", "現行に専用ロールはなく、inspector/readonly等との対応設計が必要"], ["正式電子納品・署名・長期保存", "導入時に実装", "標準、帳票、署名、保存、監査の要件定義が必要"]],
    kpis: [["定例資料作成時間", "集計開始から配布まで"], ["根拠確認時間", "指摘から原資料確認まで"], ["変更承認日数", "協議開始から決裁まで"], ["検査差戻し率", "再提出・追加資料の割合"], ["是正期限内完了率", "品質・安全指摘の完了率"]],
    pilot: ["対象工事と定例・検査の確認項目、責任分界を確定", "進捗→品質→変更→承認→検査資料の流れを共同レビュー", "閲覧権限、正式性、電子納品、長期保存の導入条件を合意"],
  },
];

const filenames = Object.fromEntries(proposals.map((p) => [p.no, `${p.no}_${p.slug}向け提案書.html`]));

const escapeHtml = (value) => String(value).replace(/[&<>"']/g, (ch) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[ch]);
const statusClass = (status) => status === "実装済み" ? "done" : status === "PoCで検証" ? "poc" : "next";

function commonStyle(accent, soft) {
  return `
    :root{--ink:#0b1f33;--muted:#5a6b7d;--paper:#f5f7f9;--white:#fff;--line:#d9e1e8;--accent:${accent};--soft:${soft};--safety:#f4b400;--red:#c9362b;--green:#16835a;--radius:16px}
    *{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:var(--paper);color:var(--ink);font-family:"Noto Sans JP","Hiragino Sans","Yu Gothic UI","Yu Gothic",system-ui,sans-serif;line-height:1.8;-webkit-font-smoothing:antialiased}
    a{color:inherit}.skip{position:fixed;top:8px;left:8px;z-index:99;padding:8px 12px;background:var(--ink);color:#fff;transform:translateY(-150%)}.skip:focus{transform:none}
    .topbar{position:sticky;top:0;z-index:20;background:rgba(245,247,249,.94);backdrop-filter:blur(12px);border-bottom:1px solid var(--line)}
    .topinner{max-width:1180px;margin:auto;min-height:68px;padding:10px 24px;display:flex;align-items:center;gap:22px}.brand{display:flex;align-items:center;gap:10px;text-decoration:none;font-weight:900;letter-spacing:-.02em}.brand-mark{display:grid;place-items:center;width:36px;height:36px;background:var(--ink);color:#fff;border-radius:8px;font:800 13px ui-monospace,monospace}.crumb{color:var(--muted);font-size:13px}.topnav{margin-left:auto;display:flex;align-items:center;gap:6px}.topnav a{padding:7px 10px;border-radius:8px;text-decoration:none;font-size:13px}.topnav a:hover{background:var(--soft)}
    main{overflow:hidden}.hero{position:relative;isolation:isolate;background:var(--ink);color:#fff}.hero:before{content:"";position:absolute;inset:0;z-index:-1;background:linear-gradient(105deg,transparent 42%,color-mix(in srgb,var(--accent) 28%,transparent)),repeating-linear-gradient(90deg,transparent 0 79px,rgba(255,255,255,.045) 80px),repeating-linear-gradient(0deg,transparent 0 79px,rgba(255,255,255,.045) 80px)}
    .hero-grid{max-width:1180px;margin:auto;padding:82px 24px 70px;display:grid;grid-template-columns:1.4fr .6fr;gap:70px;align-items:end}.eyebrow{display:flex;align-items:center;gap:10px;margin:0 0 22px;font:800 12px ui-monospace,monospace;letter-spacing:.14em;text-transform:uppercase;color:#cbd5e1}.eyebrow:before{content:"";width:36px;height:4px;background:var(--safety)}h1{max-width:850px;margin:0;font-size:clamp(42px,7vw,84px);line-height:1.08;letter-spacing:-.055em}.hero-lead{max-width:760px;margin:28px 0 0;color:#dbe5ef;font-size:clamp(17px,2.1vw,22px);line-height:1.75}.role-plate{border:1px solid rgba(255,255,255,.2);padding:22px;border-radius:var(--radius);background:rgba(255,255,255,.06)}.plate-label{margin:0;color:#aebdca;font:700 11px ui-monospace,monospace;letter-spacing:.13em}.plate-role{margin:8px 0 4px;font-size:29px;font-weight:900}.plate-audience{margin:0;color:#dbe5ef;font-size:13px}.stamp{display:inline-block;margin-top:18px;padding:5px 9px;border:2px solid var(--safety);color:#ffe084;transform:rotate(-2deg);font:800 12px ui-monospace,monospace;letter-spacing:.08em}
    .decision{background:var(--accent);color:#fff}.decision-inner{max-width:1180px;margin:auto;padding:20px 24px;display:grid;grid-template-columns:180px 1fr;gap:22px;align-items:center}.decision strong{font:800 12px ui-monospace,monospace;letter-spacing:.12em}.decision p{margin:0;font-size:18px;font-weight:700}
    .section{max-width:1180px;margin:auto;padding:88px 24px}.section-kicker{margin:0 0 10px;color:var(--accent);font:800 12px ui-monospace,monospace;letter-spacing:.14em}.section h2{margin:0 0 38px;font-size:clamp(30px,4.6vw,52px);line-height:1.25;letter-spacing:-.04em}.section-intro{max-width:760px;margin:-20px 0 36px;color:var(--muted);font-size:17px}.problem-grid,.outcome-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:16px}.problem,.outcome{background:#fff;border:1px solid var(--line);border-radius:var(--radius);padding:28px}.problem{border-top:5px solid var(--red)}.problem h3,.outcome h3{margin:0 0 10px;font-size:19px}.problem p,.outcome p{margin:0;color:var(--muted)}
    .change{background:#fff;border-block:1px solid var(--line)}.change-grid{display:grid;grid-template-columns:.85fr 1.15fr;gap:50px;align-items:start}.before{padding:28px;border:1px dashed #9ba9b7;border-radius:var(--radius);color:var(--muted)}.before h3{color:var(--ink);margin-top:0}.before ul{margin:0;padding-left:1.2em}.outcome-grid{grid-template-columns:1fr}.outcome{position:relative;padding-left:60px;border-color:color-mix(in srgb,var(--accent) 25%,var(--line))}.outcome:before{content:"✓";position:absolute;left:24px;top:25px;color:var(--accent);font-size:22px;font-weight:900}
    .route{display:grid;grid-template-columns:repeat(5,1fr);gap:0;list-style:none;padding:0;margin:0;counter-reset:route}.route li{position:relative;padding:56px 16px 18px;border-top:4px solid var(--accent);background:#fff;border-right:1px solid var(--line);font-weight:800;text-align:center}.route li:first-child{border-radius:var(--radius) 0 0 var(--radius)}.route li:last-child{border-radius:0 var(--radius) var(--radius) 0;border-right:0}.route li:before{counter-increment:route;content:"0" counter(route);position:absolute;top:13px;left:50%;transform:translateX(-50%);color:var(--accent);font:800 13px ui-monospace,monospace}.route li:not(:last-child):after{content:"›";position:absolute;right:-10px;top:48%;z-index:2;display:grid;place-items:center;width:20px;height:20px;border-radius:50%;background:var(--ink);color:#fff}
    .cap-table,.kpi-table{width:100%;border-collapse:separate;border-spacing:0;background:#fff;border:1px solid var(--line);border-radius:var(--radius);overflow:hidden}.cap-table th,.cap-table td,.kpi-table th,.kpi-table td{padding:17px 18px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}.cap-table tr:last-child td,.kpi-table tr:last-child td{border-bottom:0}.cap-table th,.kpi-table th{background:#edf1f5;font-size:12px;letter-spacing:.06em}.cap-table td:first-child,.kpi-table td:first-child{font-weight:800}.tag{display:inline-block;white-space:nowrap;padding:4px 9px;border-radius:99px;font-size:12px;font-weight:800}.tag.done{background:#e8f6ef;color:#096644}.tag.poc{background:#fff2cc;color:#7a5200}.tag.next{background:#eaf1ff;color:#184f9e}.note{margin-top:16px;padding:15px 18px;border-left:4px solid var(--safety);background:#fff8df;color:#624a00;font-size:14px}
    .measure{background:var(--ink);color:#fff}.measure .section-kicker{color:#8cb2ff}.measure-grid{display:grid;grid-template-columns:.8fr 1.2fr;gap:55px}.measure-copy p{color:#cbd5e1}.kpi-table{color:var(--ink)}.kpi-table td:last-child{color:var(--muted)}
    .pilot{display:grid;grid-template-columns:repeat(3,1fr);gap:18px}.phase{position:relative;background:#fff;border:1px solid var(--line);border-radius:var(--radius);padding:26px}.phase:before{content:"";position:absolute;left:26px;right:26px;top:0;height:5px;background:var(--accent)}.phase .days{color:var(--accent);font:800 12px ui-monospace,monospace}.phase h3{margin:9px 0 10px}.phase p{margin:0;color:var(--muted)}
    .boundary{background:#fff;border-block:1px solid var(--line)}.boundary-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:14px}.boundary-card{padding:22px;border-radius:14px;background:var(--paper);border:1px solid var(--line)}.boundary-card strong{display:block;margin-bottom:8px}.boundary-card p{margin:0;color:var(--muted);font-size:13px}.boundary-card:nth-child(1){border-top:4px solid var(--green)}.boundary-card:nth-child(2){border-top:4px solid var(--safety)}.boundary-card:nth-child(3){border-top:4px solid var(--accent)}.boundary-card:nth-child(4){border-top:4px solid #7c3aed}
    .cta{max-width:1180px;margin:72px auto;padding:0 24px}.cta-box{position:relative;overflow:hidden;border-radius:24px;background:var(--accent);color:#fff;padding:52px}.cta-box:after{content:"確認";position:absolute;right:-10px;bottom:-44px;font-size:150px;font-weight:900;opacity:.08;transform:rotate(-8deg)}.cta h2{max-width:720px;margin:0 0 18px;font-size:clamp(28px,4vw,48px);line-height:1.3}.cta p{max-width:730px;margin:0 0 26px}.cta a{display:inline-block;padding:12px 18px;background:#fff;color:var(--accent);border-radius:10px;text-decoration:none;font-weight:900}
    footer{border-top:1px solid var(--line);background:#eef2f5}.foot{max-width:1180px;margin:auto;padding:36px 24px}.foot p{margin:0 0 12px;color:var(--muted);font-size:12px}.role-links{display:flex;flex-wrap:wrap;gap:8px}.role-links a{padding:6px 10px;background:#fff;border:1px solid var(--line);border-radius:8px;text-decoration:none;font-size:12px}.role-links a[aria-current="page"]{background:var(--accent);color:#fff;border-color:var(--accent)}
    a:focus-visible,button:focus-visible{outline:3px solid var(--safety);outline-offset:3px}@media(max-width:850px){.topnav{display:none}.hero-grid{grid-template-columns:1fr;gap:35px;padding-top:58px}.decision-inner,.change-grid,.measure-grid{grid-template-columns:1fr}.problem-grid,.pilot,.boundary-grid{grid-template-columns:1fr 1fr}.route{grid-template-columns:1fr}.route li{border-right:0;border-bottom:1px solid var(--line);border-radius:0!important}.route li:first-child{border-radius:var(--radius) var(--radius) 0 0!important}.route li:last-child{border-radius:0 0 var(--radius) var(--radius)!important}.route li:not(:last-child):after{content:"↓";right:auto;left:50%;top:auto;bottom:-10px;transform:translateX(-50%)}}
    @media(max-width:560px){.topinner{padding-inline:16px}.crumb{display:none}.hero-grid,.section,.decision-inner,.foot,.cta{padding-left:18px;padding-right:18px}.hero-grid{padding-bottom:52px}h1{font-size:42px}.section{padding-top:64px;padding-bottom:64px}.problem-grid,.pilot,.boundary-grid{grid-template-columns:1fr}.cap-table thead{display:none}.cap-table,.cap-table tbody,.cap-table tr,.cap-table td{display:block;width:100%}.cap-table tr{padding:14px;border-bottom:1px solid var(--line)}.cap-table td{border:0;padding:5px}.cta-box{padding:34px 24px}.decision p{font-size:16px}}
    @media print{.topbar,.cta,.role-links{display:none!important}body{background:#fff}.hero{print-color-adjust:exact;-webkit-print-color-adjust:exact}.hero-grid,.section{padding-top:32px;padding-bottom:32px}.section{break-inside:avoid}.problem,.phase,.boundary-card{break-inside:avoid}}
    @media(prefers-reduced-motion:reduce){html{scroll-behavior:auto}}
  `;
}

function navLinks(currentNo) {
  return proposals.map((p) => `<a href="${encodeURI(filenames[p.no])}"${p.no === currentNo ? ' aria-current="page"' : ""}>${escapeHtml(p.role)}</a>`).join("");
}

function proposalHtml(p) {
  const g = groups[p.group];
  const title = `${p.role}向け提案書 | Construction Enterprise OS`;
  return `<!doctype html>
<html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="Construction Enterprise OS ${escapeHtml(p.role)}向け提案書"><title>${escapeHtml(title)}</title><style>${commonStyle(g.accent, g.soft)}</style></head>
<body><a class="skip" href="#main">本文へ移動</a>
<header class="topbar"><div class="topinner"><a class="brand" href="00_提案書一覧.html"><span class="brand-mark">CEOS</span><span>Construction Enterprise OS</span></a><span class="crumb">${g.icon} ${g.label} / ${escapeHtml(p.role)}</span><nav class="topnav" aria-label="ページ内"><a href="#value">提供価値</a><a href="#scope">対応範囲</a><a href="#pilot">導入案</a></nav></div></header>
<main id="main"><section class="hero"><div class="hero-grid"><div><p class="eyebrow">ROLE PROPOSAL / ${p.no}</p><h1>${escapeHtml(p.headline)}</h1><p class="hero-lead">${escapeHtml(p.lead)}</p></div><aside class="role-plate"><p class="plate-label">FOR</p><p class="plate-role">${g.icon} ${escapeHtml(p.role)}</p><p class="plate-audience">${escapeHtml(p.audience)}</p><span class="stamp">判断材料を一枚に</span></aside></div></section>
<section class="decision" aria-label="提案の要点"><div class="decision-inner"><strong>RECOMMENDATION</strong><p>${escapeHtml(p.decision)}</p></div></section>
<section class="section"><p class="section-kicker">CURRENT FRICTION</p><h2>いま、現場と判断の間で<br>情報が途切れています。</h2><div class="problem-grid">${p.pains.map(([h, d]) => `<article class="problem"><h3>${escapeHtml(h)}</h3><p>${escapeHtml(d)}</p></article>`).join("")}</div></section>
<section class="change" id="value"><div class="section change-grid"><div><p class="section-kicker">THE CHANGE</p><h2>業務を増やさず、<br>情報の流れを整える。</h2><div class="before"><h3>導入前の確認事項</h3><ul><li>現在の入力・転記・承認に要する時間</li><li>誰が正本を持ち、誰が更新するか</li><li>例外時の責任者と判断期限</li></ul></div></div><div class="outcome-grid">${p.outcomes.map((x) => `<article class="outcome"><h3>${escapeHtml(x)}</h3><p>既存業務を置き換える前に、MVP上で運用適合と効果を確認します。</p></article>`).join("")}</div></div></section>
<section class="section"><p class="section-kicker">ONE CONNECTED ROUTE</p><h2>${escapeHtml(p.role)}の業務を、<br>一つの工程線でつなぐ。</h2><ol class="route">${p.flow.map((x) => `<li>${escapeHtml(x)}</li>`).join("")}</ol></section>
<section class="section" id="scope"><p class="section-kicker">CAPABILITY &amp; STATUS</p><h2>できることと、<br>これから作ること。</h2><p class="section-intro">画面があることと、本番業務で成立することは同じではありません。現在の到達点を明示します。</p><table class="cap-table"><thead><tr><th>対象</th><th>現在地</th><th>提案上の扱い</th></tr></thead><tbody>${p.capabilities.map(([name, status, desc]) => `<tr><td>${escapeHtml(name)}</td><td><span class="tag ${statusClass(status)}">${escapeHtml(status)}</span></td><td>${escapeHtml(desc)}</td></tr>`).join("")}</tbody></table><p class="note"><strong>重要:</strong> MVPの金額・件数・精度はデモ用サンプルです。導入効果は、実データで基準値を測り、PoCで目標値を合意して評価します。</p></section>
<section class="measure"><div class="section measure-grid"><div class="measure-copy"><p class="section-kicker">MEASURE BEFORE SCALE</p><h2>導入効果は、<br>画面数ではなく業務KPIで。</h2><p>現在値 → PoC目標 → 実測結果を同じ定義で比較し、継続・修正・中止を判断します。削減率は事前に断定しません。</p></div><table class="kpi-table"><thead><tr><th>推奨KPI</th><th>測定定義</th></tr></thead><tbody>${p.kpis.map(([name, how]) => `<tr><td>${escapeHtml(name)}</td><td>${escapeHtml(how)}</td></tr>`).join("")}</tbody></table></div></section>
<section class="section" id="pilot"><p class="section-kicker">90-DAY ADOPTION PLAN</p><h2>小さく確かめ、<br>条件が揃ってから広げる。</h2><div class="pilot">${p.pilot.map((x, i) => `<article class="phase"><span class="days">${i === 0 ? "DAY 0–30" : i === 1 ? "DAY 31–60" : "DAY 61–90"}</span><h3>${i === 0 ? "現状と基準を揃える" : i === 1 ? "業務で検証する" : "導入判断を固める"}</h3><p>${escapeHtml(x)}</p></article>`).join("")}</div></section>
<section class="boundary"><div class="section"><p class="section-kicker">HONEST SCOPE</p><h2>提案の境界を、<br>最初から共有します。</h2><div class="boundary-grid"><article class="boundary-card"><strong>実装済み</strong><p>約90ルート、ロール表示、ブラウザ内CRUD、検索・KPI再集計、認証API/JWT/RBAC。</p></article><article class="boundary-card"><strong>PoCで検証</strong><p>実業務項目、入力負荷、承認経路、帳票適合、KPI改善、運用責任。</p></article><article class="boundary-card"><strong>導入時に実装</strong><p>業務DB/API、端末間共有、基幹・会計・センサー連携、SSO、正式監査。</p></article><article class="boundary-card"><strong>将来構想</strong><p>AI予測、BIM/CIM本格連携、デジタルツイン、自律施工。</p></article></div></div></section>
<section class="cta"><div class="cta-box"><h2>次の会議で決めるのは、導入ではなく「何を測るか」です。</h2><p>${escapeHtml(p.role)}の代表業務を一つ選び、現状時間・差戻し・待ち時間を確認する90分の適合整理から始めます。</p><a href="00_提案書一覧.html">他の役職向け提案書を見る</a></div></section></main>
<footer><div class="foot"><p>Construction Enterprise OS 役職別提案書 / ${escapeHtml(p.role)}向け / 2026-08-19時点。根拠: README.md、docs/requirements/mvp-scope.md、docs/design/opendesign-spec.md、docs/api/overview.md。最新の実装・運用状況は導入検討時に再確認してください。</p><nav class="role-links" aria-label="役職別提案書">${navLinks(p.no)}</nav></div></footer></body></html>`;
}

function indexHtml() {
  const card = (p) => { const g = groups[p.group]; return `<a class="card" href="${encodeURI(filenames[p.no])}" style="--card-accent:${g.accent};--card-soft:${g.soft}"><span class="card-no">${p.no}</span><span class="card-icon">${g.icon}</span><strong>${escapeHtml(p.role)}</strong><span>${escapeHtml(p.headline)}</span><em>提案書を開く →</em></a>`; };
  return `<!doctype html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="Construction Enterprise OS 役職別提案書一覧"><title>役職別提案書一覧 | Construction Enterprise OS</title><style>${commonStyle("#1457d9", "#eaf1ff")}
  .index-hero{background:var(--ink);color:#fff}.index-hero .section{padding-top:78px;padding-bottom:70px}.index-hero h1{max-width:900px}.index-hero p{max-width:760px;color:#dbe5ef;font-size:19px}.legend{display:flex;flex-wrap:wrap;gap:10px;margin-top:30px}.legend span{padding:7px 11px;border:1px solid rgba(255,255,255,.22);border-radius:99px;font-size:13px}.catalog{display:grid;grid-template-columns:repeat(3,1fr);gap:18px}.group-title{grid-column:1/-1;margin:34px 0 0;padding-bottom:12px;border-bottom:2px solid var(--line);font-size:22px}.group-title:first-child{margin-top:0}.card{position:relative;display:grid;grid-template-columns:auto 1fr;gap:5px 15px;min-height:220px;padding:25px;background:#fff;border:1px solid var(--line);border-top:5px solid var(--card-accent);border-radius:var(--radius);text-decoration:none;transition:transform .2s,border-color .2s}.card:hover{transform:translateY(-4px);border-color:var(--card-accent)}.card-no{position:absolute;right:18px;top:14px;color:#a2afbb;font:800 12px ui-monospace,monospace}.card-icon{grid-row:1/4;font-size:28px}.card strong{font-size:23px}.card span:not(.card-icon):not(.card-no){color:var(--muted)}.card em{align-self:end;color:var(--card-accent);font-style:normal;font-weight:900}.guide{display:grid;grid-template-columns:repeat(4,1fr);gap:12px}.guide article{padding:20px;background:#fff;border:1px solid var(--line);border-radius:14px}.guide strong{display:block;margin-bottom:6px}.guide p{margin:0;color:var(--muted);font-size:13px}@media(max-width:850px){.catalog{grid-template-columns:1fr 1fr}.guide{grid-template-columns:1fr 1fr}}@media(max-width:560px){.catalog,.guide{grid-template-columns:1fr}.index-hero h1{font-size:42px}}
  </style></head><body><a class="skip" href="#main">本文へ移動</a><header class="topbar"><div class="topinner"><a class="brand" href="00_提案書一覧.html"><span class="brand-mark">CEOS</span><span>Construction Enterprise OS</span></a><span class="crumb">役職別提案書</span></div></header><main id="main"><section class="index-hero"><div class="section"><p class="eyebrow">PROPOSAL LIBRARY / 9 ROLES</p><h1>同じシステムを、<br>それぞれの判断言語で。</h1><p>Construction Enterprise OSが解決する業務課題、現在の実装範囲、PoCで測るKPI、90日導入案を9つの立場ごとに整理しました。</p><div class="legend"><span>🏢 事業者</span><span>👷 現場</span><span>📋 管理</span><span>実装済み / PoC / 導入時 / 将来を分離</span></div></div></section><section class="section"><p class="section-kicker">SELECT YOUR ROLE</p><h2>あなたの立場から、<br>提案をお読みください。</h2><div class="catalog"><h3 class="group-title">🏢 事業者</h3>${proposals.filter(p=>p.group==="business").map(card).join("")}<h3 class="group-title">👷 現場</h3>${proposals.filter(p=>p.group==="field").map(card).join("")}<h3 class="group-title">📋 管理</h3>${proposals.filter(p=>p.group==="management").map(card).join("")}</div></section><section class="boundary"><div class="section"><p class="section-kicker">READING GUIDE</p><h2>提案書の読み方。</h2><div class="guide"><article><strong>実装済み</strong><p>現在のMVPやAPIで、操作またはコード・E2Eを確認できる範囲。</p></article><article><strong>PoCで検証</strong><p>自社の業務、入力負荷、帳票、KPIで成立性を確かめる範囲。</p></article><article><strong>導入時に実装</strong><p>業務DB、認証統合、外部接続、正式監査など本番化に必要な範囲。</p></article><article><strong>将来構想</strong><p>AI予測、BIM/CIM、自律施工など、現時点で効果を約束しない領域。</p></article></div><p class="note"><strong>現状:</strong> MVPは約90ルートと30超の業務コレクションをブラウザ内データで操作できます。auth APIのJWT/RBAC/Neon接続は実証済みですが、WebUIの業務データは本番DB正本ではありません。</p></div></section></main><footer><div class="foot"><p>Construction Enterprise OS 役職別提案書一覧 / 2026-08-19時点。外部フォント・画像・スクリプトを使用しない単体HTMLです。</p></div></footer></body></html>`;
}

await mkdir(outDir, { recursive: true });
await writeFile(path.join(outDir, "00_提案書一覧.html"), indexHtml(), "utf8");
for (const proposal of proposals) {
  await writeFile(path.join(outDir, filenames[proposal.no]), proposalHtml(proposal), "utf8");
}
console.log(`Generated ${proposals.length + 1} proposal HTML files in ${outDir}`);
