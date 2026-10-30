# minecraft-infra

友人向けMinecraft Java Edition / ForgeサーバーをDocker Composeと国内VPSで運用する。
最大5人程度を想定。**Windows CurseForge + Essentialで現在プレイ中の既存ワールドの維持が最優先**。

予定環境: ConoHa VPS 6 vCPU / RAM 12GB、Java 17、Minecraftヒープ8GB。
接続名はmc.runharu.net、管理はTailscale + SSHを想定。VPS接続・DNS変更は未実施。

## 現状と作業境界

- WSLで従来構成の起動・ログインに成功。既存ワールド移行は未検証。
- 元環境の詳細、ワールドの実物、VPSは未確認。本番移行完了ではない。
- 元ワールドはコピー元専用。削除・初期化・再生成・直接編集をしない。
- 作業前に全体バックアップを作成し、以降の作業・テストはコピーで行う。
- VPSへの転送・起動はユーザーの明示指示後。既存データの上書きも個別の明示指示が必要。
- このリポジトリの更新では、データ転送・起動・上書きを実行しない。

## Modpackの準備（ワールドなしで実施可能）

現在のComposeはAll modsの `for_server.zip` を基にしたサーバー用定義
`modpack/server/` と、非公開 `staging/server-all-mods/` を参照する。
Minecraft **1.20.1 / Forge 47.4.10**、元manifestの参照は81件（必須80・任意1）。
旧候補および除外前のAll modsの調査結果は別に保管し、混在させない。

Embeddium 0.3.31を `modpack/exclude-include.json` で明示除外する。
Essential / Entity Culling / Mouse Tweaks / Better Advancements / BadOptimizations / Neatは
公式helperの固定ファイルのClientタグ判定による自動除外を維持する。
版数・固定ID・除外理由は [modpack/server/client-exclusions.json](modpack/server/client-exclusions.json)。
サーバー用の実取得結果・一覧は [modpack/server/README.md](modpack/server/README.md)。

既存Windowsの実JARとの照合と不足依存の解決は未完了。
**MODPACK_VERIFIED_SHA256を設定せず、ワールドを起動しない。**
不足はExpandAbility（Artifactsが`[9.0.0,)`を要求）とSmartBrainLib（TACZ Turretsが`[1.15,)`を要求）。
取得可能な対応候補と未確認事項は [未解決依存](modpack/server/DEPENDENCIES.md) に記録した。候補は未導入。
構成コードの公開対象・検証結果・commit/push手順は [PUBLISHING.md](PUBLISHING.md) を参照。
新旧エクスポート比較は [modpack/EXPORT-COMPARISON.md](modpack/EXPORT-COMPARISON.md) を参照。

### 導入方式

`AUTO_CURSEFORGE` とローカルZIPを採用する。未公開のカスタムパックに対応し、
manifestのprojectID/fileIDでModを固定し、overridesを反映できる。
JAR直接コピー方式はAPI不要だが、今回の入力にはJARがなく、各JARの入手・版数・依存を別管理する必要がある。
両方式ともModや設定の再配布条件は別途確認が必要。

- 公開するのは識別子のみのmanifest、ハッシュ、スクリプト、ドキュメント。
- ZIP、JAR、元overridesは非公開。`git pull` だけでは揃わず、同じZIPを別経路で準備する。
- Java 17以降の現行イメージにはCurseForgeキーが内包される。固定イメージで利用できない場合は
  自分のキーを非公開.envの `CF_API_KEY='実値'` に設定する。ドル記号を含むキーは単引用符で囲む。
  キーを画面・ログ・Gitへ出さず、共有時のCompose確認には `config --quiet` を使う。
- 自動取得を許可しないModは公式エラーに記載された**同じfileID**をブラウザで取得し、
  非公開の `staging/server-all-mods/downloads/` に置いて再実行する。最新版で代用しない。
- 独自の明示除外はEmbeddiumのみ。イメージ内の汎用リストを根拠なく追加せず、公式helperのClientファイル判定は維持する。
  公式helperのファイル側Client/Server判定は残るため、取得結果と元一覧を必ず照合する。
  JEI等を見た目だけで削除しない。除外が必要なら固定JARの根拠を確認して別リリースで変更する。
- `required=false` のEnhanced AIは公式helperでは導入されない。元manifestは変更していない。
- ZIPのSHA-256を起動前に検査し、Minecraft/Forgeの環境変数とmanifest由来の固定値も照合する。
  AUTO_CURSEFORGEの実際のローダー選択はZIPのmanifestが基準になる。
- 自動同期と強制再インストールはfalse。既存overridesは上書きしない。
  固定fileID、ZIP、イメージdigestを変更しなければ再起動で最新版を選択しない。

### 1. 一つのエクスポートを検査・固定する

Python 3.11以降とDocker Composeが必要。日本語や空白を含むパスは引用符で囲む。
ZIPまたは展開済みフォルダを一つだけ指定する。原本は変更しない。

```bash
python3 scripts/prepare-modpack.py 'for_server.zip' \
  --staging-dir staging/server-all-mods --definition-dir modpack/server
# 次の更新候補は別のstaging-dir / definition-dirで準備し、既存成果物を上書きしない。
```

スクリプトはリポジトリ内の入力だけを読み、パス逸脱・リンク・特殊ファイル・重複パス・
Unicode/大文字小文字の衝突・サイズ上限・manifestの形式を検査する。
ZIPは直接展開せず読み取り検査し、許可したMod設定ディレクトリだけを含む固定ZIPを作る。
world/saves等や未知のトップレベル内容は自動削除せずエラーにする。
同一内容の再実行は可能で、異なる既存成果物への置換は拒否する。

```text
modpack/server/                  # 公開可能なサーバー用定義（JAR/設定の再配布ではない）
  manifest.json、pack.lock.json、pack.env
  client-exclusions.json、installed-mods.json、README.md
# 共通ポリシー: modpack/exclude-include.json
staging/server-all-mods/         # 全て非公開
  server-pack.zip                # Composeが使用する固定ZIP
  inspection.json                # 入力全ファイルのハッシュと検出パス
  downloads/                     # 手動取得ファイル
  prepared/                      # worldなしの導入検証用
```

### 2. Mod取得だけを先に検証する

新しい.envに.env.exampleの内容を設定する（既存.envは上書きしない）。
.env.exampleは確認したイメージdigest、Minecraft/Forgeを指定済み。
イメージのdigestはレジストリで確認した固定値であり、ワールド移行合格の意味ではない。

```bash
docker compose config --quiet
docker compose --profile tools run --rm --no-deps modpack-prepare
python3 scripts/audit-mods.py staging/server-all-mods/prepared/mods > staging/server-all-mods/mod-audit.json
```

modpack-prepareは公式mc-image-helperのinstall-curseforgeだけを実行する。
ワールドのガードを迂回してMinecraftを起動するものではなく、**Minecraftを起動しない**。
書き込み先はstaging/server-all-mods/preparedだけで、dataも元インスタンスもマウントしない。
初回はForgeインストーラも取得される場合がある。手動取得要求や不足があれば解消する。
private ZIPの照合には `modpack/server/pack.lock.json` のarchive_sha256を使う。

監査スクリプトはJARを実行せず、mods.toml、JAR manifest、Jar-in-Jarを読み、
Mod ID・バージョン・SHA-256・必須のサーバー依存IDを出力する。
JARなし・不正JAR・必須ID不足は非ゼロで終了する。バージョン範囲の適合は手動で照合する。
取得結果のMod数や自動除外ログも確認し、元インスタンスと違う項目を解消する。
出力があるだけで監査合格とは扱わない。

### 3. 元インスタンスと照合する

WindowsのCurseForgeで元プロファイルのフォルダを開き、読み取り専用の一覧を作る。
以下はPowerShellの例。出力先は元インスタンスの外に置く。

```powershell
$SourceMods = 'C:\実際のインスタンス\mods'
$InventoryFile = Join-Path ([Environment]::GetFolderPath('Desktop')) 'minecraft-mods.csv'
Get-ChildItem -LiteralPath $SourceMods -File -Filter '*.jar' |
  Sort-Object Name |
  ForEach-Object {
    [PSCustomObject]@{
      File = $_.Name
      SHA256 = (Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash
    }
  } | Export-Csv -LiteralPath $InventoryFile -NoTypeInformation -Encoding UTF8
```

新しいエクスポートではServer mods onlyを外し、元の全Modを含める。
ワールドは含めない。ZIP原本とMod一覧を非公開で渡す。
Mekanism本体と実際に使っている関連Mod・依存Modのバージョンを一覧と照合する。
クライアント専用Modを専用サーバーへ残すかは、各固定JARの仕様で判断する。

不足・バージョン範囲・サーバー側の除外理由を全て解消したリリースだけで、
.envの `MODPACK_VERIFIED_SHA256` に**そのリリースの**archive_sha256を記入する。
現在の候補では記入しない。未設定・別ハッシュならワールドがあっても起動を拒否する。

### 新旧エクスポートとWindows実JARの読み取り専用比較

比較スクリプトはJSONを標準出力へ出すだけで、入力やワールドを書き換えない。
詳細にはローカル履歴のパスが含まれ得るので、出力は非公開stagingへ保存する。

```bash
python3 -B scripts/compare-modpacks.py exports m_alt for_server.zip > staging/export-comparison.json
```

Windowsでゲーム・ランチャーを終了し、CurseForgeから**元のプレイ用プロファイル**のフォルダを開く。
Get-ModInventory.ps1はmods直下の.jarと.jar.disabledの名前・サイズ・SHA-256・SHA-1・有効状態だけを読む。
Mod/JAR/ワールドを変更せず、絶対パスやユーザー名を出力しない。出力先は元インスタンス外にする。

```powershell
& .\scripts\Get-ModInventory.ps1 -ModsPath 'C:\実際の元インスタンス\mods' |
  Out-File -LiteralPath "$env:USERPROFILE\Desktop\windows-mods.json" -Encoding utf8
```

windows-mods.jsonを非公開stagingへ渡してから、除外前のAll mods調査で取得した全固定fileIDのメタデータと照合する。
サーバー用にはEmbeddiumを取得しないため、元Windowsの比較にはstaging/all-mods側のメタデータを使う。
任意Mod Enhanced AIはrequired=falseのため通常の準備サービスでは導入しない。
版数照合のためだけにstaging/optional-referenceへ同じfileIDのJARを取得した（サーバーへ追加していない）。

```bash
python3 -B scripts/compare-modpacks.py inventory \
  staging/windows-mods.json for_server.zip \
  staging/all-mods/prepared/.cache/curseforge \
  staging/optional-reference/.cache/curseforge > staging/windows-comparison.json
```

- missing_from_source: エクスポートにあるがWindows実物に対応がない項目。
- extra_in_source: Windows実物にあるがエクスポートに対応がない項目（エクスポート側の不足候補）。
- different_or_duplicate: 同名別ハッシュ、または同じ内容のJAR重複。
- selection_state_differences: requiredの選択状態と.jar.disabled等の状態の違い。解釈を確認し、勝手に変更しない。
- unresolved_metadata: 固定fileIDのメタデータ未取得。これがある間は不足・余分を確定しない。

不一致・未解決ありは終了コード1、入力不正は2。出力があっても終了コードと内容を確認する。
source_matches_exportがtrueでも、サーバー専用構成の採否・依存バージョン・ワールド検証は別で、
world_verifiedは常にfalse。環境変数や起動許可を自動設定しない。
PowerShellスクリプトのWindows実機実行はユーザー側で必要。

### 更新時の保護

Modpack更新は別リリース用ディレクトリで準備し、旧ZIP・固定定義・全data・外部DBを保存する。
現候補の成果物を上書きして進めない。元インスタンスと同じ版数を確認した新しいZIPで検証し、
新しいワールドコピーでテストする。稼働中のdataに新しいMod設定を同期しない。
ロールバックはModだけを戻さず、対応する全dataと設定も同じ時点へ戻す。

### 公開と非公開

| 公開可能 | 非公開 |
| --- | --- |
| compose.yaml、scripts、tests、README、.env.example、識別子/ハッシュのみのmodpack定義 | .env、APIキー、RCONパスワード、SSH鍵、Tailscale認証情報 |
| 再配布条件確認済みの自作定義 | ZIP/JAR/overrides（再配布未確認）、元m_alt、staging、downloads |
| 個人情報を含まない調査結果 | data、プレイヤーデータ、backups、ログ、詳細検査報告 |

.gitignoreは未追跡ファイルに適用される。既に追跡された秘密ファイルが見つかった場合は
内容を表示せず、追跡解除と必要な秘密の失効・再発行を検討する。既存Git履歴は改変しない。

## 移行前の調査票

未確認項目を埋めてから移行する。個人情報を含む記録はGit対象外の `migration-private/` へ。

| 項目 | 記録する内容 |
| --- | --- |
| 保存場所 | OS、ランチャー、インスタンスとワールドの絶対パス、容量 |
| 元環境 | シングルプレイ / Essential / 専用サーバー |
| バージョン | Minecraft、Forgeの完全な番号、Modpack名・正確なリリース、Java |
| Mod | jar一覧、バージョン、SHA-256、依存関係、クライアント専用Mod |
| プレイヤー | 名前、UUID、ホストか、所持品・装備・エンダーチェスト・経験値・位置 |
| 認証 | 元のonline-mode、移行先の認証方式、UUIDの一致 |
| ワールド外 | config、defaultconfigs、kubejs、scripts、Mod独自フォルダ、外部DB |
| VPS | OS、CPU/RAM/ディスク、配置先、Docker Compose、実行UID/GID、接続制限 |

ランチャーの「フォルダを開く」等で実際のゲームディレクトリを確認する。
シングルプレイ/Essentialは通常その配下の `saves/<保存名>`、専用サーバーは
server.propertiesのlevel-nameを手掛かりにする。標準パスの推測だけで決めない。

## 1. 停止状態で全体バックアップ

1. 全員退出後、ゲームを保存して終了、または専用サーバーを正常停止する。
2. ワールド全体とゲーム/サーバーインスタンス全体を、元ディレクトリ外へアーカイブする。
   Mod、設定、スクリプト、manifest等を含める。外部DB等も同じ停止時点でバックアップする。
3. アーカイブの一覧とSHA-256を記録し、空ディレクトリへの復元・内容照合を確認する。
4. 別媒体にもコピーする。元データと保管バックアップを作業先に指定しない。

WSL/Linuxでの例。パスは実値に置換する。照合完了まで元環境を起動しない。

```bash
SOURCE_INSTANCE='/absolute/path/to/source-instance'
SOURCE_WORLD='/absolute/path/to/source-world'
BACKUP_ROOT='/absolute/path/to/backup-storage'
BACKUP_DIR="$BACKUP_ROOT/migration-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$BACKUP_ROOT"
mkdir "$BACKUP_DIR"
tar -cpf "$BACKUP_DIR/instance.tar" -C "$SOURCE_INSTANCE" .
tar -cpf "$BACKUP_DIR/world.tar" -C "$SOURCE_WORLD" .
tar -tf "$BACKUP_DIR/world.tar"
sha256sum "$BACKUP_DIR/instance.tar" "$BACKUP_DIR/world.tar"
mkdir "$BACKUP_DIR/restore-check"
tar -xpf "$BACKUP_DIR/world.tar" -C "$BACKUP_DIR/restore-check"
diff -qr "$SOURCE_WORLD" "$BACKUP_DIR/restore-check"
```

instance.tarも別の空ディレクトリに復元して同様に照合する。
エラー・差分があれば先に解消する。macOSでは `shasum -a 256` を使える。

## 2. 作業コピーの配置

検証済みバックアップから新しい作業ディレクトリへ復元する。
既存dataには展開しない。WSLの既存テスト環境も保管し、移行用には別ディレクトリへcloneする。
Composeのホスト `./data` がコンテナの `/data` に対応する。
例の移行先名は `imported-world`。フォルダ名の変更はコピー側だけで行う。

```text
新しい作業ディレクトリ/
├── compose.yaml、.env、scripts/、modpack/、staging/
└── data/
    ├── server.properties       # level-name=imported-world
    ├── mods/                   # 同じリリースのサーバー用Mod
    ├── config/
    ├── defaultconfigs/         # 存在する場合
    ├── kubejs/、scripts/        # 存在する場合
    ├── <その他Mod固有の外部データ>
    └── imported-world/         # 保存フォルダの中身を丸ごと復元
        ├── level.dat、level.dat_old
        ├── playerdata/、advancements/、stats/
        ├── serverconfig/、datapacks/、data/
        ├── region/、entities/、poi/
        ├── DIM-1/、DIM1/
        ├── dimensions/
        └── <その他すべての保存データ>
```

一覧は例。存在するファイルを選別してコピーせず、全体を維持する。
level.dat、playerdata、serverconfigは移行前後の存在・内容を必ず確認する。
元にない項目は理由を調べる。`world/world/level.dat` の二重配置を避ける。
ネザー・エンド・追加ディメンションやMod独自の保存先を削除・再生成しない。
チーム・クエスト・所有権・ネットワーク情報も保存先を決め打ちせず調査する。
外部DBがあればテスト専用に複製し、元DBへの接続を防ぐ。

専用サーバーならserver.propertiesもコピーする。シングルプレイ等で存在しなければ
作業コピーに作成する。元の難易度・ゲームモード等も確認する。

```properties
level-name=imported-world
online-mode=true
```

level-nameは.envのWORLD_NAMEと一致させ、重複行なし・LF改行で記載する。
online-modeの切替はUUID不一致を招くため、元が異なる場合は自動変更せず調査する。
この構成ではserver.propertiesの自動生成・自動上書きを無効にしている。

## 3. ホストの所持品とUUID

シングルプレイ/Essentialのホストは、最新状態がlevel.datの `Data.Player` にあり、
`playerdata/<UUID>.dat` と一致しない可能性がある。ホストとゲストを別々に確認する。

1. 元環境で所持品等の画面を記録する。NBT閲覧ツールで**コピー**のData.Playerと
   UUIDファイルを比較し、同じJavaアカウントのUUID・認証方式を確認する。
2. 最新状態がData.Playerだけにある場合、作業コピーをさらにバックアップする。
   NBTツールでPlayer compoundを対応する `playerdata/<UUID>.dat` のルートcompoundへ
   移す方法を検討する。装備・経験値・位置・Mod追加NBTも維持し、形式とUUIDの整合性を確認する。
   既存ファイルの置換は個別の明示指示後。元データは変更しない。
3. advancements、stats、Modのプレイヤー・チーム情報も同じUUIDとの対応を確認する。
   単純なファイル名変更で全ModのUUID移行が完了すると扱わない。
4. ホスト・ゲスト双方のログイン後の所持品等を照合するまで移行完了にしない。

実データ未確認のため変換は未実施。Essential等のクライアント専用Modは
同じModpackリリースのサーバーパックと照合する。ゲーム内容に関わるModを
削除・更新して起動エラーを回避しない。全差分と理由を記録する。

## 4. バージョン固定・起動前確認

.env.exampleから新しい.envを作り、確認した実値を設定する。

- MINECRAFT_VERSION: 元と同じ完全な番号。当初想定は1.20.1だが実物を優先する。
- FORGE_VERSION: 元と同じ完全なForge番号。latest/recommendedは使わない。
- MINECRAFT_IMAGE: 検証するJava 17イメージのdigest付き参照。
  `itzg/minecraft-server:java17@sha256:<確認したdigest>`。仮の値を入れない。
- WORLD_NAME: `imported-world` 等。英数字・`_`・`-`のみ。level-nameと一致させる。
- MC_UID/MC_GID: 移行先の実行UID/GID（初期値1000）。

Minecraft・Forge・Modpack・個別Modを元と一致させ、設定・スクリプト・データパックも移行する。
jarのSHA-256を照合する。移行とアップデートを同時にしない。
初回起動前にも作業コピー全体をバックアップする。

```bash
docker compose config --quiet
```

未設定値があるとCompose展開が失敗する。起動ガードはlevel.datの欠落・空ファイル、
level-nameの不一致をMinecraft起動前に検出する。NBT完全性・Mod互換性は保証しない。
ガード解除やダミーlevel.datで回避しない。

転送・復元後に `ls -ln` / `stat` で所有者と権限を確認する。
実行UID/GIDがディレクトリを検索・書き込みでき、ファイルを読み書きできる必要がある。
必要なchown/chmodは対象パスを確認して作業コピーdata配下だけに適用する。
元ワールドやバックアップには適用せず、`chmod -R 777` は使わない。

## 5. コピーでWSL検証

既存テストサーバーを正常停止してポート競合を避け、新しい作業コピーで実施する。
接続者と外部サービスを検証用に限定する。

```bash
docker compose up -d
docker compose logs -f minecraft
```

レジストリ欠落・Mod不一致・ディメンション読込失敗・NBTエラー等があれば正常停止し、
ログを保管して原因を調査する。欠落無視や再生成で続行しない。
停止に2分以上必要な環境ではstop_grace_periodを伸ばし、強制終了を避ける。

以下を全て確認し、日時・参加者・座標・画面・ログを記録する。

- [ ] 元の建築物・主要拠点が存在する
- [ ] 全参加者の所持品・装備・エンダーチェスト・経験値が維持される
- [ ] AE2のネットワーク・ストレージ・所有権が維持される
- [ ] Mekanism等の機械・配管・内容物・設定が維持される
- [ ] Modの進行状況・クエスト・チームが維持される
- [ ] ネザー・エンド・既存の追加ディメンションと拠点が維持される
- [ ] 正常停止・再起動・再ログイン後も上記が維持される

再起動は `docker compose stop minecraft` の正常停止完了後に
`docker compose up -d` で行う。起動成功だけでは合格にしない。

## 6. VPS移行（明示的な転送・起動指示後）

1. WSL検証合格後、移行先パス・対象データ・停止時間・復旧先を確認する。
2. 元環境を正常停止し、最終バックアップとSHA-256を新規作成する。
   テスト後も元で遊んだ場合は最新コピーで同じ変換・検証をやり直す。
3. VPSに既存環境がある場合は正常停止し、data・Compose・.env・image digest・
   外部DBを含めて復元可能なバックアップを作成する。
4. 転送指示後、**新しいリリース用ディレクトリ**にアーカイブ・設定を転送する。
   双方のSHA-256を照合し、空のstagingへ展開して新しいdataを準備する。
   既存dataには展開しない。`rsync --delete` は使わない。
5. level.dat・playerdata・serverconfig・全ディメンション・外部データ・UUID・
   バージョン・level-name・所有者/権限を照合し、起動前バックアップを保存する。
6. 新リリースでComposeのconfigを確認し、旧コンテナ停止と新dataのマウント先を確認する。
7. 起動指示後に新リリースを起動し、検証参加者のみ接続する。
8. VPSでもセクション5の全項目と再起動を確認してから本番開放する。
   元環境は停止したコピー元として保存し、二つのワールドを並行運用しない。

## 7. ロールバック

異常時は新VPSサーバーを正常停止し、失敗したdataとログを調査用に保管する。
稼働中データを上書きせず、保管バックアップや元ワールドを直接起動しない。

- 旧VPSがある場合: 切替前のdata・Compose・.env・固定イメージ・外部DBを
  バックアップから**別の復元先**へコピーし、マウント先・権限を確認する。
- 初回VPS移行の場合: 最終バックアップを新しいローカルインスタンスへ復元する。
  元と同じMinecraft・Forge・Mod・設定を使う。シングルプレイ/Essentialでは
  変換前のホストデータを使う。

復旧先と失われる可能性のある移行後の進捗を説明する。
VPSの転送・起動、既存データの置換は明示指示を受けてから実施する。
復旧後も建築物・所持品・Mod進行・ディメンションを確認する。
失敗したワールドとの差分を自動合成しない。

## 参照

- [Forge設定](https://docker-minecraft-server.readthedocs.io/en/latest/types-and-platforms/server-types/forge/)
- [server.propertiesとLEVEL](https://docker-minecraft-server.readthedocs.io/en/latest/configuration/server-properties/)
- [UID/GID・停止猶予](https://docker-minecraft-server.readthedocs.io/en/latest/configuration/misc-options/)
- [NBTExplorer](https://github.com/jaquadro/NBTExplorer)

## Windowsの既存ワールドを後で渡す手順

1. 上記のMod一覧と全Modエクスポートを先に照合し、依存関係を解決する。
2. 全参加者退出後、Windowsのゲームを「保存して終了」し、ランチャーも終了する。
3. 元インスタンス全体と実際のsaves配下の対象ワールド全体を、元パス外へそれぞれコピーする。
   ファイル選別はせず、level.dat、playerdata、serverconfig、Modデータ、追加ディメンションも丸ごと保存する。
4. コピーからZIPを作成し、PowerShellのGet-FileHashでSHA-256を記録する。
   元インスタンスのバックアップは別媒体にも保管する。公開GitHubへ送らない。
5. WSLのstagingに別名で転送し、同じSHA-256であることを確認する。
   空の作業先に安全に復元し、セクション1〜4の照合とホストNBT確認を行う。
   prepare-modpack.pyはワールド用インポータではないので、ワールドZIPには使わない。
6. 明示的にインポート作業を依頼した後、復元したコピーを新しいdata/imported-worldに配置する。
   data/server.propertiesを確認し、ホワイトリストへ実際の参加者のUUIDを登録する。
   template使用時は既存ワールドの難易度等も引き継ぐ。既存dataには展開しない。
7. まずWSLでセクション5の全項目を検証する。VPSへの転送・起動は別の明示指示後。

## ConoHaでの公開前提（設定作業は未実施）

- VPSの12GB RAMに対してJavaヒープ8GB。残りはOS・Docker・Javaのヒープ外領域等に使う。
  manifestのrecommendedRamは9088MBなので、指定の8GBで足りるかは実測する。
- server.propertiesのmax-players=5、online-mode=true、ホワイトリストを確認する。
- mc.runharu.netのA/AAAAはVPSの実際に使うIPへ向ける。通常のCloudflareプロキシは
  MinecraftのTCP 25565を中継しないのでDNS onlyを使う。IPv6を使わない場合は不用意にAAAAを作らない。
- ConoHa側とOS側のTCP 25565を必要な範囲へ公開する。SSHはTailscale経由で管理する。
  Docker公開ポートはOSのファイアウォールとの相互作用も含めて実機で確認する。
- RCONパスワードやSSH鍵、Tailscale認証情報はGit管理しない。

## Modpack方式の参照

- [AUTO_CURSEFORGE公式説明](https://docker-minecraft-server.readthedocs.io/en/latest/types-and-platforms/mod-platforms/auto-curseforge/)
- [起動処理の公式実装](https://github.com/itzg/docker-minecraft-server/blob/master/scripts/start-deployAutoCF)
- [公式helperのrequired/Client判定・固定ファイル処理](https://github.com/itzg/mc-image-helper/blob/main/src/main/java/me/itzg/helpers/curseforge/CurseForgeInstaller.java)
- [Cloudflareのプロキシ対象ポート](https://developers.cloudflare.com/fundamentals/reference/network-ports/)
