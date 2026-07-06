# Design Idea: riela package の配布・インストール体験の刷新とコンテナノード実行

Status: implemented foundation / release publication pending CI
Date: 2026-07-06
Updated: 2026-07-07
Scope: riela CLI (tacogips/riela) + riela-packages registry (tacogips/riela-packages)

## 0. 2026-07-07 implementation status

- `registry-index.json` generation and check tasks are implemented in
  `riela-packages`, and Riela can consume index records for search/install.
- `.rielapkg` archive packing, archive SHA256 metadata, and release-scoped
  `registry-index.json` generation are implemented. The GitHub Actions release
  workflow publishes those assets to the fixed `registry-packages` release.
- `riela-lock.json`, `riela package ci`, and locked archive replay are
  implemented in Riela.
- `execution.kind: "container"` add-ons are executable through the Riela
  container resolver. Apple Container, Docker, Podman, and configured custom
  runtime drivers are available.
- Shared node add-ons are projected under
  `~/.riela/addons/<namespace>/<name>/<version>`; the older
  `~/.riela/content-ad/addons/...` path is read as a compatibility fallback.
- `riela doctor`, `riela setup container`, `riela node search/install/run`, and
  `rrun` are implemented foundations.
- `@tacogips/pdf-to-images-addon` is the first packaged container node add-on
  for PDF page rendering. Its GHCR image digest is intentionally left unpinned
  until the image workflow publishes the first remote image.
- The container image workflow uploads per-package digest JSON artifacts so
  maintainers can pin `execution.imageDigest` without a second GHCR lookup, and
  `task package:check-release-publication` verifies the fixed
  `registry-packages` release after archive publication.

## 1. 解決したい要望

1. riela package をもっと使いやすく・インストールしやすくする
2. node 単位でのインストール・プロジェクト横断の再利用
3. Dockerfile (Containerfile) で定義された node をワンクリックで使えるようにする
   (例: YouTube 動画ダウンロードノード。yt-dlp / ffmpeg 等を手動インストール不要に)
4. エンジニアでない Mac ユーザでも Apple Container を簡単に導入できる
   (可能なら riela 自身からインストールできる)
5. npm のような node / workflow / instance の再利用・配布基盤をゼロから作るべきか?の判断

## 2. 現状の整理(2026-07-06 時点の事実)

### 配布・インストール

- レジストリ = GitHub リポジトリ(デフォルト `tacogips/riela-packages`)。
  設定は `~/.riela/workflow-packages/registries.json`、キャッシュは
  `~/.riela/registries/<id>/` に git clone。
- riela ソース側(impl-plan `package-manager-ux-gap-closure.md`, 2026-07-06 実装済)では
  依存の深さ優先解決・`riela package registry sync`・検索フィールド拡張まで到達。
  ただし Homebrew 配布版 0.1.17 には未反映(依存は手動インストール)。
- 中央インデックスファイルは当初無かったが、現在は `registry-index.json`
  を生成・検証するタスクを追加済み。
- 整合性は MD5 checksum + sha256 integrity digest。署名は無し。
- アーカイブ形式 `.rielapkg`(ZIP)は pack/validate/import に加えて、
  GitHub Releases 向けの配布アセットと SHA256 pin 付き index 生成まで実装済み。

### node / add-on

- add-on 実行種別: `declarative` / `native-bundle` / `local-command` / `container`。
  `container` は Riela 側の resolver と runtime driver で実行可能になった。
  `containerfilePath` はローカル開発ビルド fallback、`image`/`imageDigest`
  は registry 配布時の優先実行経路。
- 既存の add-on(youtube-mp4-download 等)は `local-command`(bash スクリプト)+
  `runtimeHints`(`yt-dlp`, `ffmpeg`, `node`, ...)方式。
  **ヒントは宣言だけで、ツールの存在チェックも自動インストールも無い** ← 非エンジニアの最大の障壁。
- capability モデル(`process.spawn`, `network.egress`, `filesystem.read/write`, `env.read`
  + scope + reason)が既にマニフェストに存在。
- add-on は package 単位の `.riela/packages/<pkg>/` に加えて、
  node-addon install 時に `~/.riela/addons/<ns>/<name>/<ver>` へ共有投影される。

### Apple Container(外部事実)

- apple/container 1.0 は 2026-06 に安定版。Apple Silicon 専用、macOS 26 (Tahoe) が
  サポート対象(macOS 15 でも動くが非推奨)。
- インストールは GitHub Releases の署名済み `.pkg`、または Homebrew。
  利用開始には `container system start` が必要。

## 3. 基本方針: 「npm をゼロから作る」は **やらない**

| 選択肢 | コスト | 得られるもの | 判定 |
| --- | --- | --- | --- |
| A. 現行 git レジストリ + 生成インデックス | 小 | clone 不要の検索、install の 1 コマンド化 | **採用(Phase 1)** |
| B. GitHub Releases に `.rielapkg` を添付 | 小〜中 | バージョン固定・イミュータブル配布・部分ダウンロード | **採用(Phase 2)** |
| C. OCI レジストリ (ghcr.io) 配布 | 中 | コンテナイメージと package を同一基盤で配布、認証・dedup が既製 | **コンテナイメージには採用、package payload は任意(Phase 3)** |
| D. 独自 npm 型レジストリサーバ | 大 | 完全な制御 | **不採用**。運用負荷(可用性・認証・abuse 対応)が個人レジストリ規模に見合わない |

理由: npm が提供する価値(名前解決・バージョン解決・整合性・配布)のうち、
名前解決とバージョン解決はマニフェスト+インデックスで、配布とイミュータブル性は
GitHub Releases / OCI で既に満たせる。サーバをゼロから書いて増えるのは運用負荷だけ。
将来マルチテナントな公開レジストリが本当に必要になった時点で、
インデックス形式をそのまま静的ホスティング(CDN 上の JSON)に載せ替えられる設計にしておく。

## 4. 全体アーキテクチャ

```
                    ┌────────────────────────────────────────┐
                    │  riela-packages (GitHub repo)          │
                    │  packages/*/riela-package.json          │
                    │  registry-index.json  ← CI が生成       │
                    │  GitHub Releases: <pkg>-<ver>.rielapkg  │
                    └───────────────┬────────────────────────┘
                                    │            ┌──────────────────────┐
                                    │            │ ghcr.io/tacogips/     │
                                    │            │ riela-addons/<name>   │
                                    │            │ (プリビルドイメージ)   │
                                    │            └──────────┬───────────┘
                        riela package install <id>          │ pull
                                    │                       │
        ┌───────────────────────────▼───────────────────────▼──────────┐
        │ riela CLI                                                     │
        │  ├ registry-index 取得(clone 不要の検索・解決)                │
        │  ├ .rielapkg 取得 + sha256 検証 + 依存解決                     │
        │  ├ addon store: ~/.riela/addons/<ns>/<name>/<ver>(共有)      │
        │  ├ ContainerRuntime 抽象                                       │
        │  │   ├ AppleContainerDriver (`container` CLI)                 │
        │  │   ├ DockerDriver / PodmanDriver                            │
        │  └ riela setup / riela doctor(ランタイム導入・診断)           │
        └───────────────────────────────────────────────────────────────┘
```

## 5. コンテナノード実行(要望 3 の中核)

既にスキーマにある `execution.kind: "container"` を実装する。ゼロからの発明ではなく
「宣言済みの空欄を埋める」作業になる。

### 5.1 addon.json 拡張

```jsonc
{
  "name": "tacogips/youtube-mp4-download",
  "version": "2",
  "execution": {
    "kind": "container",
    "containerfilePath": "Containerfile",          // フォールバック(ローカルビルド)
    "image": "ghcr.io/tacogips/riela-addons/youtube-mp4-download:2",  // 推奨経路
    "imageDigest": "sha256:...",                    // pin 用
    "platforms": ["linux/arm64", "linux/amd64"]
  },
  "capabilities": [
    { "name": "network.egress", "required": true, "reason": "YouTube からのダウンロード" },
    { "name": "filesystem.write", "scope": "runtime.output", "required": true }
  ],
  "inputSchema": { "...": "既存のまま" }
}
```

ポイント:
- **プリビルドイメージ優先**。ユーザ環境で `Containerfile` をビルドさせない
  (ビルドは遅い・失敗要因が多い・非エンジニアに不向き)。riela-packages の CI が
  multi-arch (arm64/amd64) イメージをビルドして ghcr.io に push し、
  `imageDigest` をマニフェストに焼き込む。
- `containerfilePath` は「イメージが取得できない/自作したい」場合のフォールバックと
  再現性の担保(ソース公開)として残す。
- `imageDigest` が未 pin の開発・未公開 add-on では、Riela は `containerfilePath`
  を優先してローカル build fallback を使う。publish 済み image は digest pin 後に
  prebuilt image として実行する。

### 5.2 ContainerRuntime 抽象(riela 本体)

```swift
protocol ContainerRuntime {
    static func detect() async -> ContainerRuntimeStatus  // installed / running / absent
    func pull(image: String, digest: String?) async throws
    func run(_ spec: ContainerRunSpec) async throws -> ContainerRunResult
}
// 実装: AppleContainerDriver(`container` CLI)、DockerDriver、PodmanDriver
```

- 検出優先順位(macOS): `container`(Apple Silicon + macOS 26)→ `docker` → `podman`。
  `riela config set container.runtime docker` で固定も可能。
- `ContainerRunSpec` への写像:
  - `inputs` → env / argv(既存の argvTemplate 方式を踏襲)
  - `RIELA_ARTIFACT_DIR` → ボリュームマウント(書込み先はこのマウントのみ)
  - capability → ランタイムフラグ:
    `network.egress` 無し → ネットワーク無効、
    `filesystem.read` の `addon.input` は `pdfPath` などの入力 payload から
    必要な親ディレクトリだけを read-only mount、
    `filesystem.write` の `runtime.output` は `RIELA_ARTIFACT_DIR` のみ許可、
    `env.read` は envSchema 宣言分のみ渡す。
  - **capability モデルがそのままコンテナのサンドボックス設定になる**。
    local-command では「宣言」だった capability が、container では「強制」になる。
    これがコンテナ化の安全上の最大の利点。

### 5.3 ユーザ体験(YouTube ダウンロードの例)

```
$ riela package install @tacogips/youtube-mp4-download-addon
✔ registry index 取得
✔ 依存解決: (なし)
✔ コンテナランタイム: Apple Container (running)
✔ イメージ取得: ghcr.io/tacogips/riela-addons/youtube-mp4-download@sha256:...
⚠ このノードは次の権限を要求します:
    - network.egress: YouTube からのダウンロード
    - filesystem.write (runtime.output のみ)
  許可しますか? [Y/n]
✔ インストール完了。yt-dlp / ffmpeg のローカルインストールは不要です。
```

以後 workflow から `"addon": {"name": "tacogips/youtube-mp4-download", "version": "2"}` で
参照するだけ。ホストに yt-dlp / ffmpeg は一切入らない。

## 6. Apple Container の導入を riela が面倒みる(要望 4)

### 6.1 `riela doctor`(診断)

- Apple Silicon か、macOS バージョン、コンテナランタイム有無・起動状態、
  各 CLI backend (`claude` / `codex` / `cursor`)、インストール済み package の
  `environmentVariables` / `runtimeHints` 充足状況を一覧表示。
- インストール済み add-on の要求ツールが欠けていれば具体的な導入コマンドを提示。

### 6.2 `riela setup container`(導入)

非エンジニア向けに、次を対話式で自動化:

1. 前提チェック: Apple Silicon / macOS 26+(未満なら Docker Desktop 案内へフォールバック)
2. apple/container の GitHub Releases から**署名・公証済み `.pkg`** をダウンロード
3. `spctl --assess` / 署名検証後、`open <pkg>` で macOS 標準インストーラを起動
   (admin 権限は OS のダイアログに委ねる。riela が sudo を要求しない)
4. インストール完了を検知して `container system start` を実行
5. `container run hello-world` 相当の疎通確認

設計判断:
- **`.pkg` + 標準インストーラ経路を第一候補**にする。Homebrew は非エンジニアには
  前提が重い(Xcode CLT 等)。brew が既に入っていれば `brew install container` を使う。
- `riela package install` 時に container 必須 add-on を検出したら、
  「Apple Container が必要です。今セットアップしますか?」と 1 ステップで
  `riela setup container` へ誘導する。これが実質の "riela からインストール"。
- 将来 RielaApp(GUI)からは同フローをボタン 1 つで呼べるようにする
  (CLI コマンドとして切っておけば GUI は薄いラッパで済む)。

## 7. node 単位のインストールと再利用(要望 2)

### 7.1 共有 addon store

現状: add-on は package のコピーとして `.riela/packages/<pkg>/addons/...` に入り、
プロジェクトごとに重複する。

提案: content-addressed な共有ストアを導入。

```
~/.riela/addons/
  tacogips/youtube-mp4-download/2/     ← 実体(contentDigest で検証済み)
.riela/packages/<pkg>/addons/...       ← 実体 or 共有ストアへの参照(lockfile 記録)
```

- 同じ add-on を使う複数プロジェクトでダウンロード・イメージ pull が 1 回で済む。
- コンテナイメージは元々ランタイム側でホスト共有されるので、この構造と整合する。

### 7.2 `riela node` サブコマンド(package の糖衣)

```
riela node search youtube            # kind=node-addon に絞った検索
riela node install tacogips/youtube-mp4-download   # 単一 add-on を含む package を解決して導入
riela node list                      # 利用可能な add-on 一覧(scope 横断)
riela node run tacogips/youtube-mp4-download --variables '{"url":"https://..."}'   # workflow なしの単発実行
```

- 内部は既存の package install を再利用(add-on は必ず package に属する、を維持)。
- `riela node run` は「workflow を書かずに node を試す」導線で、
  非エンジニアにも開発者のデバッグにも効く。現在は `--variables <json|@file>`
  で入力し、将来 inputSchema から対話的に入力を聞ける。

### 7.3 workflow / instance の再利用

- workflow は既に package で再利用可能。足りないのは **lockfile**:
  `riela-lock.json`(package id → version / digest / registry / image digest)を
  プロジェクトに保存し、`riela package install`(引数なし)で lockfile 通りに復元
  = npm の `package.json` + `npm ci` 相当。チームへの配布・CI 再現がこれで完成する。
- instance(実行済みセッション・成果物)の共有は別問題として切り離す。
  まずは `riela session export` の成果物を package の `examples/` に置ける、程度に留める。

## 8. レジストリの段階的進化(要望 1・5)

### Phase 1: インデックス生成と install の 1 コマンド化(小、すぐ)

- riela-packages の CI(既存 Taskfile `check` の延長)で `registry-index.json` を生成:
  全 package の name / version / kind / tags / description / backends /
  requiredEnvironment / addon 一覧 / digest を 1 ファイルに集約。
- riela CLI は raw.githubusercontent.com からインデックスだけ取得して検索・解決。
  **clone 不要・`--local-path` 不要**になり、`riela package search youtube` が即動く。
- 検索対象に description を含める(現状 name/tags のみ)。
- 依存自動解決(ソース実装済み)を Homebrew リリースに乗せる。

### Phase 2: Releases 配布と lockfile(中)

- CI がタグ push 時に package ごとの `.rielapkg` を GitHub Releases に添付し、
  インデックスに `archiveUrl` + `sha256` を記録。
- install は「インデックス → 該当 archive のみダウンロード → 検証」になり、
  git 履歴も他 package も落とさない。イミュータブルなバージョン参照が可能に。
- `riela-lock.json` 導入(§7.3)。
- checksum の正を MD5 から sha256 (integrity.digest) に一本化。MD5 は後方互換のみ。

### Phase 3: コンテナイメージ配布 + (任意) OCI package 配布

- riela-packages CI で container add-on のイメージを multi-arch ビルド → ghcr.io へ。
  digest をマニフェストへ焼き込み(§5.1)。
  build job は `container-image-digest-<package-id>` artifact を出力し、
  `update-container-image-digests.ts --digest-file` で manifest へ pin する。
- 任意: `.rielapkg` 自体も ORAS で ghcr.io に置けるようにする(イメージと package の
  配布基盤統一)。ただし Phase 2 で困っていなければやらない。

### サードパーティレジストリ

現行の「registry = GitHub repo」モデルはそのまま活きる。第三者は自分の
riela-packages 形式 repo を作り CI テンプレート(インデックス生成 + digest 更新 +
イメージビルド)を流用、利用者は `riela package registry add` で追加。
**分散型のまま npm 的な UX に到達する**のがこの設計の要点。

## 9. セキュリティ

- 整合性: sha256 digest を全経路(archive / addon content / image)で必須化。
  インデックス経由の解決は常に digest pin。
- 署名: Phase 2 以降で minisign または sigstore/cosign によるレジストリ署名を検討
  (イメージは cosign が自然)。個人レジストリのうちは digest pin で十分。
- 権限: install 時に capability を明示提示して同意を取る(§5.3)。同意結果は
  既存スキーマの `capabilityGrant` に記録。container 実行では capability を強制、
  local-command では警告表示(コンテナ化への移行インセンティブにもなる)。
- 非コンテナ add-on の `runtimeHints` は宣言止まりにせず、install/doctor 時に
  存在チェック + 導入コマンド提示まで行う(自動インストールはしない。
  ホスト環境を書き換えるのはコンテナ経路に限定する)。

## 10. 実装ロードマップ(riela 本体 / riela-packages の分担)

| # | 項目 | どこ | 規模 |
| --- | --- | --- | --- |
| 1 | registry-index.json 生成 CI + CLI の index 検索 | packages / riela | 小 |
| 2 | 依存自動解決を含む 0.1.18 リリース | riela | 小(実装済みの出荷) |
| 3 | `riela doctor`(runtimeHints / env / runtime 検査) | riela | 小〜中 |
| 4 | ContainerRuntime 抽象 + AppleContainerDriver + DockerDriver | riela | 中 |
| 5 | `execution.kind: container` 実行系(capability→sandbox 写像) | riela | 中 |
| 6 | youtube-mp4-download 等を container add-on 化 + イメージ CI | packages | 小〜中 |
| 7 | `riela setup container`(.pkg 導入フロー) | riela | 中 |
| 8 | `.rielapkg` Releases 配布 + lockfile | riela / packages | 中 |
| 9 | 共有 addon store + `riela node` サブコマンド | riela | 中 |
| 10 | 署名 (cosign/minisign)、ORAS 配布 | 両方 | 後日判断 |

推奨着手順: 1→2→3 で「今日の痛み」(clone 必須・依存手動・環境不備が実行時まで
分からない)を先に消し、4→5→6→7 で本命のコンテナノード体験を作る。
8 以降は利用者が増えてから。

## 11. 未決事項

- Apple Container のボリュームマウント/ネットワーク制御の粒度が Docker と揃うか
  (ドライバ実装時に差分吸収レイヤの厚みを実測で決める)
- Linux ホスト(riela を Linux で使う場合)のランタイム優先順位(podman/docker)
- `riela node run` の入力対話 UI をどこまで作り込むか(非エンジニア向け導線の要)
- macOS 26 未満ユーザへの案内(Docker Desktop 誘導 or 非対応と明示)
