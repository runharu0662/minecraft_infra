# GitHub公開準備（#006）

**構成コードのPush準備：可。Minecraft起動の許可ではない。**
All mods、73 JARの固定情報、指定7件のクライアント除外、既存ワールドの起動ガードを維持した。
この作業ではgit addによる実ステージング、commit、pushは行っていない。

## 公開予定ファイル（33件）

既存追跡3件と未追跡の新規30件。公開するModpack情報は識別子・版数・ハッシュ等の定義と調査結果だけで、JARや実設定の再配布ではない。
旧候補の定義・報告は履歴資料。現在のComposeが参照する定義はmodpack/server。

| パス |
| --- |
| .env.example |
| .gitignore |
| PUBLISHING.md |
| README.md |
| compose.yaml |
| modpack/EXPORT-COMPARISON.md |
| modpack/REPORT.md |
| modpack/all-mods-files.json |
| modpack/all-mods-manifest.json |
| modpack/all-mods-resolved.json |
| modpack/exclude-include.json |
| modpack/file-metadata.json |
| modpack/manifest.json |
| modpack/pack.env |
| modpack/pack.lock.json |
| modpack/resolved-mods.json |
| modpack/server.properties.example |
| modpack/server/DEPENDENCIES.md |
| modpack/server/README.md |
| modpack/server/client-exclusions.json |
| modpack/server/dependency-audit.json |
| modpack/server/installed-mods.json |
| modpack/server/manifest.json |
| modpack/server/pack.env |
| modpack/server/pack.lock.json |
| scripts/Get-ModInventory.ps1 |
| scripts/audit-mods.py |
| scripts/compare-modpacks.py |
| scripts/prepare-modpack.py |
| scripts/prepare-only.sh |
| scripts/require-world.sh |
| tests/test_inventory.py |
| tests/test_safety.py |

## Gitから除外するもの

| パス・種類 | 用途 |
| --- | --- |
| for_server.zip、*.zip、*.jar、m_alt/ | 原本・Mod本体・非公開overrides |
| staging/、downloads/、migration-private/ | 取得物、詳細検査、インベントリ、準備ログ |
| data/、backups/ | ワールド、プレイヤーデータ、バックアップ |
| .env、.env.*（.env.exampleを除く） | APIキー等の実値 |
| secrets/、*.secret、*.key、*.pem、id_rsa*、id_ed25519*、.ssh/、.aws/、.tailscale/ | 鍵・認証情報 |
| *.log、crash-reports/ | 実行ログ・個人情報 |
| chatgpt-handoff.txt | ChatGPTへのローカル引き継ぎ。ファイル自体は保持 |
| __pycache__/、*.pyc、.DS_Store | 生成物 |

未追跡の新規ファイルを含む公開予定全件を確認した。テキスト走査とJSON項目確認で、実キー、秘密鍵、個人パス、メール、プレイヤーデータ、署名付きダウンロードURLは検出されなかった。
実行データ・元overrides・API生キャッシュは公開対象に含めない。既存追跡3件にも機密ファイルは見つかっていない。Git履歴の変更はしていない。

## 最終検証

- Pythonテスト25件成功。
- シェル2ファイルの構文検査成功。PowerShellのWindows実機実行は未検証。
- 通常profileとtoolsのCompose config成功。ローカルは公式Compose単体v5.6.1を使用（通常のdocker composeプラグインは未導入）。
- git diff --check成功。git status / git ls-files / git add --dry-runで公開対象を確認。実ステージングはしない。
- 73 JARの実物が固定SHA-256と一致、除外設定不変、元ZIP不変。
- MODPACK_VERIFIED_SHA256は空。data/・新規ワールドの生成なし。

## 起動ブロッカー

1. ExpandAbility / smartbrainlibの必須依存不足。元ZIPに参照がなく、JAR監査でも不足。
2. 元Windows実JARとの一致・有効状態・正確な版数が未確認。
3. 既存ワールドのバックアップ・コピーのインポート、ホストUUID/NBT、実起動・保存の検証が未実施。
候補は [DEPENDENCIES.md](modpack/server/DEPENDENCIES.md) に根拠付きで記録しただけで未導入。
ExpandAbility 9.0.4（Forge 1.20.1）とSmartBrainLib 1.15（Forge 1.20.1）は要求範囲を満たす候補だが、元環境と同じとは扱わない。

## 次にユーザーが実行するコマンド

この作業では実行しない。公開対象のコードだけを指定し、ステージング後にも確認してから保存する。

```bash
git status --short
git add -- .gitignore .env.example compose.yaml README.md PUBLISHING.md modpack scripts tests
git diff --cached --check
git diff --cached --stat
git diff --cached --name-only
git commit -m "feat: prepare pinned Forge modpack server configuration"
git push origin main
```

ステージング後の一覧にZIP/JAR・ワールド・ログ・鍵・.env実値等が混入していないことを確認する。
git pull/cloneだけでは非公開ZIPと実データは揃わない。VPS上でもZIPを別経路で用意し、元環境照合と起動ブロッカーを解消するまではMinecraftを起動しない。
