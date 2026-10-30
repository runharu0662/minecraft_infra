# 未解決依存と候補（#006・未導入）

73 JARの固定構成とクライアントMod除外を維持する。候補を追加・ダウンロード・更新していない。
Windows元インスタンスとの一致は未確認で、既存ワールドの起動は禁止したまま。

| 不足Mod | 実JARが要求する条件 | 取得可能な対応候補（採用決定ではない） |
| --- | --- | --- |
| ExpandAbility (`expandability`) | Artifacts 9.5.19: `[9.0.0,)` | [Forge 1.20–1.20.1 / 9.0.4](https://www.curseforge.com/minecraft/mc-mods/expandability/files/5301414)、`expandability-9.0.4.jar`、465066:5301414 |
| SmartBrainLib (`smartbrainlib`) | TACZ Turrets 3.0.1: `[1.15,)` | [Forge 1.20.1 / 1.15](https://www.curseforge.com/minecraft/mc-mods/smartbrainlib/files/5654964)、`SmartBrainLib-forge-1.20.1-1.15.jar`、661293:5654964 |

候補は配布元の固定ファイルページにMinecraft/Forge対応と版数が掲載され、要求範囲を数値上満たす。
全Modとの実行互換性・候補JARの実物・元Windowsと同じ版数かは未検証。
Fabric/NeoForge用ファイルや別Minecraft版で代用せず、最新版だからという理由で採用しない。

## 確認済みの不足理由

- All mods原本のmanifestに両projectIDはない。ZIP内のoverridesにもJARはない。
- 公式helperはmanifestの固定参照を処理し、欠落依存の元環境と同じ版数を推測して補完しない。
- 今回の明示除外はEmbeddiumだけ。両依存Modは除外リストに入っていない。
- 73 JARとJar-in-Jarから得たMod IDにも両IDがなく、依存監査は終了コード1になる。
- 実JAR由来の根拠は [dependency-audit.json](dependency-audit.json) のmissing_ids。

なぜ元エクスポートに含まれなかったかは未確定。
元Windowsで未導入なのか、手動JARがエクスポートから漏れたのか、別プロファイル・選択状態なのかは、
読み取り専用の実JAR一覧で確認する。元ワールドが破損したとは判断していない。

## 次の確認

元Windowsのプレイ用プロファイルで `scripts/Get-ModInventory.ps1` を実行し、
`windows-mods.json` を非公開で渡す。両Modの有無・有効状態・正確な版数を照合する。
実物に存在すれば同じ版数を新候補として固定し、存在しなければ理由を調べてから追加方針を決める。
この確認まで `MODPACK_VERIFIED_SHA256` を空のまま維持する。
