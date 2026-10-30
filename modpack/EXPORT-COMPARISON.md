# Server mods only と All mods の比較

この文書は#005適用前の調査記録。現在のComposeはAll mods + Embeddium明示除外へ更新済み。最新結果は [server/README.md](server/README.md) を参照。

旧候補は展開済みm_alt（およびそれをそのまま固定ZIP化したstaging/server-pack.zip）。旧ZIP原本は受領していない。
新候補はfor_server.zip。両者を別のstagingで検査し、Mod JARや設定を混在させていない。
Windows元インスタンスは未受領・未照合。**いずれの候補もワールド起動を許可しない**。

## 差分

- Minecraft 1.20.1 / Forge 47.4.10は同じ。
- 旧39参照（必須38・任意1）→新81参照（必須80・任意1）。追加42、削除0、共通39のfileID/required変更0。
- 新旧のmodlist.htmlも同じ42プロジェクトが追加され、削除なし。
- overridesは各3,551ファイル。config 227 / tacz 3,324。
- バイト内容が変わった同名ファイルは0。日本語パス1件のUnicode NFC/NFD表現だけが異なる。NFC正規化後は全ファイル名・内容ハッシュが一致。
- defaultconfigs、独立datapacks、kubejs、scripts、overrides/modsは新旧とも同梱なし。TaCZ内の独自スクリプト等は維持されている。
- 新旧ともJARを含まないCurseForgeの参照型エクスポート。元Modpackのversionは空でリリース名では識別できない。
- 旧manifestにあったrecommendedRam=9088は新manifestにない。RAM設定変更の証拠とは扱わず、Composeの8Gは維持した。

## 指定されたMod

| Mod | 旧 | 新の固定参照・確認結果 |
| --- | --- | --- |
| [Mekanism](https://www.curseforge.com/minecraft/mc-mods/mekanism/files/6552911) | なし | 268560:6552911 / Mekanism-1.20.1-10.4.16.80.jar |
| [Mekanism Generators](https://www.curseforge.com/minecraft/mc-mods/mekanism-generators/files/6552914) | なし | 268566:6552914 / MekanismGenerators-1.20.1-10.4.16.80.jar |
| [Mekanism Tools](https://www.curseforge.com/minecraft/mc-mods/mekanism-tools) | なし | なし。バージョンを推測せず、元Windowsの実物確認待ち |
| [AE2](https://www.curseforge.com/minecraft/mc-mods/applied-energistics-2/files/8991271) | 15.4.11 | 同じ223794:8991271 / appliedenergistics2-forge-15.4.11.jar |
| [Ex Deorum](https://www.curseforge.com/minecraft/mc-mods/ex-deorum/files/8384482) | なし | 901420:8384482 / exdeorum-1.53.jar |

Mekanism/Generatorsのファイル版は10.4.16.80、mods.toml内のmod版は10.4.16。両方を区別して記録する。
AE2の内部版は15.4.11、Ex Deorumは1.53。固定fileIDの公式APIメタデータと実際に取得したJARで確認した。
全81件のファイル名・固定ID・版名・公式ハッシュ・依存参照は[all-mods-files.json](all-mods-files.json)。
取得したJARの内部版・SHA-256・必須依存は[all-mods-resolved.json](all-mods-resolved.json)。

## 追加された42プロジェクト

aether, apotheosis, apothic-attributes, appleskin, applied-mekanistics, architectury-api, artifacts, awesome-dungeon-edition-ocean-forge, awesome-dungeon-forge, awesome-dungeon-nether-forge, awesome-dungeon-the-end-forge, badoptimizations, better-advancements, brandons-core, caelus, cloth-config, clumps, curios, deeperdarker, embeddium, enigmatic-legacy, entityculling, essential-mod, ex-deorum, fastfurnace, fastsuite, fastworkbench, geckolib, guideme, insanelib, library-ferret-forge, mekanism, mekanism-generators, mouse-tweaks, neat, no-phantoms, placebo, playeranimator, spark, voidscape, when-dungeons-arise, when-dungeons-arise-seven-seas

## 取得・依存検査の結果

- 旧候補: 38 JAR。必須依存IDが6種類不足（architectury / artifacts / curios / geckolib / guideme / smartbrainlib）。
- 新候補: 74 JAR。共通38 JARはすべて旧候補とSHA-256一致。
- 新候補にもexpandability >= 9.0.0（Artifacts）とsmartbrainlib >= 1.15（TACZ Turrets）が不足。
- 公式helperはrequired=falseのEnhanced AIを導入しない。元manifestのフラグは変更していない。
- Enhanced AI 515276:8946003（enhancedai-3.3.7.5.jar）は版数照合のためだけに別のstaging/optional-referenceへ取得し、稼働用Modには追加していない。
- 6件は固定ファイルのgameVersionsがClientのみを示し、公式helperにより取得対象外になった（手動削除ではない）:
  BadOptimizations 2.4.1 / Better Advancements 0.6.0.73 / Essential 1.5.1 / Entity Culling 1.11.3 / Mouse Tweaks 2.25.1 / Neat 41。
- Embeddium 0.3.31は上記Clientフラグで除外されず取得された。しかし作者の説明はクライアント用最適化Modなので、専用サーバー採否の確認対象。今回は勝手に除外していない。
- Forgeインストーラは新旧とも終了コード0。Minecraftサーバーを起動したわけではなく、data/もワールドも作成していない。
- 不足Modの自動追加・バージョン変更・稼働用manifestの切替はしていない。現在のComposeは旧固定ZIPの参照を保持し、MODPACK_VERIFIED_SHA256未設定で起動を拒否する。

## 考えられる原因（推測と確認済みを区別）

確認済み: エクスポート方式を変えた新候補ではMekanism等42件が復帰し、共通版数も設定も変わっていない。
推測: Server mods onlyフィルターが環境タグ未設定等のModを落とした可能性が高い。
Mekanism/Generatorsの公開ページではEnvironmentがNot Setであり、この推測と整合する。ただしCurseForgeアプリ内部の判定実装までは未確認。
All modsでも不足するModがある理由は未確定。元に未導入、手動追加JARの参照漏れ、異なるプロファイル、無効化状態、エクスポート選択等を実物で確認する。
既存ワールドが壊れた事実は確認されていない。元環境とワールドには一切操作していない。

## 次の操作

1. 元Windowsのプレイ用プロファイルでGet-ModInventory.ps1を実行し、windows-mods.jsonを非公開で渡す。
2. compare-modpacks.py inventoryでAll modsの81参照・公式ハッシュと照合する。スクリプトは入力の読み取りのみ。
3. Mekanism Tools / ExpandAbility / SmartBrainLibの実物・有効状態・正確な版数を確認し、過不足とクライアント用差分を説明できる状態にする。
4. 不足を最新版で補わず、元の実物と同じ版で新リリース候補を定義する。元ワールドのバックアップ・コピーでの検証はその後。
5. ユーザーの指示なしにVPS転送・起動、既存データ上書き、commit/pushをしない。

## 実施済みの検証

- ZIP/展開フォルダのパス・リンク・重複・サイズ・manifest検査。新ZIPは読み取り時のCRC検証も通過。
- 元m_alt全ファイルと新ZIP原本のハッシュ不変。
- 公式Compose単体v5.6.1によるconfig検証（通常profileとtools）。
- Pythonの安全性・ガード・在庫比較テスト22件。シェル構文、git diff --check。
- 固定イメージの実コンテナでワールド欠落時の起動拒否とファイル未生成を確認。
- 元Windows照合、PowerShellのWindows実行、サーバー互換性、実ワールド移行は未検証。

参照: [Embeddium作者説明](https://www.curseforge.com/minecraft/mc-mods/embeddium)、[公式helper実装](https://github.com/itzg/mc-image-helper/blob/main/src/main/java/me/itzg/helpers/curseforge/CurseForgeInstaller.java)。
