# Modpack調査結果（再エクスポート前の候補）

この文書は#005適用前の調査記録。現在のComposeはAll mods + Embeddium明示除外へ更新済み。最新結果は [server/README.md](server/README.md) を参照。

このレポートは最初の展開済み `m_alt/` に対するもの。ZIP原本は作業開始時に存在せず、ZIP原本のCRC等は未検証。
新しいエクスポートは別の候補として解析し、混在させない。現在の候補は既存環境との照合未完了で、ワールドの読み込みを許可しない。

## 確認結果

- Minecraft 1.20.1 / Forge 47.4.10。Java 17を使用。
- manifestのMod参照は39件、required=trueが38件、falseが1件（Enhanced AI）。
- Modpackのversionとauthorは元manifestでは空。リリース名だけでは固定できないため、入力全体をSHA-256で固定する。
- 元のエクスポートにMod JARは同梱なし。その後、隔離したstaging/preparedに38 JARを取得し、JAR内メタデータを読み取り検査した。実行互換性とワールドの検証は未実施。
- overrides/config: 227ファイル。overrides/tacz: 3,324ファイル。
- defaultconfigs / datapacks / kubejs / scripts は同梱なし。ただしTaCZ配下には独自スクリプト等があるので全体を維持する。
- Mekanism、Mekanism Generators、Curios、GeckoLib、playerAnimator、Artifacts等の参照はmanifestにない。設定にMekanism等の痕跡はあるがJARの代用にはならない。
- 元ワールドの必要Mod一覧は未取得。設定の残存だけで現在導入されていると断定しない。

## 各Modの固定参照と確認できたバージョン

全39プロジェクトについて公開ページのEnvironmentはClient & Server。これは各固定JARが必ず起動できるという保証ではない。
クライアント専用と断定して除外するModは現時点で0件。JEIも表示系という理由だけで削除しない。
一部ファイルページは取得できなかったが、後続の公式APIメタデータと取得済みJARで必須38件のファイル名・内部バージョンを確認した。詳細はresolved-mods.jsonとfile-metadata.json。

| projectID | fileID | required | 確認できた表示名・バージョン（出典） |
| --- | --- | --- | --- |
| 689467 | 7872374 | true | [Packet Fixer - Packet Fixer 3.3.2](https://www.curseforge.com/minecraft/mc-mods/packet-fixer/files/7872374) |
| 404183 | 5598990 | true | [End Remastered [NeoForge/Fabric] - End Remastered 1.20.X R5.3.3 [Forge]](https://www.curseforge.com/minecraft/mc-mods/endremastered/files/5598990) |
| 855414 | 8680180 | true | [Iron's Spells 'n Spellbooks - 1.20.1-3.16.3](https://www.curseforge.com/minecraft/mc-mods/irons-spells-n-spellbooks/files/8680180) |
| 872516 | 8145294 | true | [Nether Remastered - nether_remastered-2.6-forge-1.20.1](https://www.curseforge.com/minecraft/mc-mods/nether-remastered/files/8145294) |
| 916747 | 6274623 | true | [ShatterLib \| OctoLib - OctoLib-FORGE-0.5.0.1+1.20.1.jar](https://www.curseforge.com/minecraft/mc-mods/shatterbyte-lib/files/6274623) |
| 1689768 | 9318716 | true | [mezzconfig：当初ファイルページ未確認（後続のfile-metadata.jsonで確認済み）](https://www.curseforge.com/minecraft/mc-mods/mezzconfig/files/9318716) |
| 238222 | 9298209 | true | [jei：当初ファイルページ未確認（後続のfile-metadata.jsonで確認済み）](https://www.curseforge.com/minecraft/mc-mods/jei/files/9298209) |
| 351264 | 7291067 | true | [Kotlin for Forge - Kotlin for Forge 4.12.0](https://www.curseforge.com/minecraft/mc-mods/kotlin-for-forge/files/7291067) |
| 1420337 | 7642083 | true | [Fantasy Ending - fantasy_ending-1.20.1-2.7.20-all.jar](https://www.curseforge.com/minecraft/mc-mods/fantasy-ending/files/7642083) |
| 324717 | 8479276 | true | [Jade 🔍 - [Forge 1.20.1] 11.13.3](https://www.curseforge.com/minecraft/mc-mods/jade/files/8479276) |
| 306770 | 7731017 | true | [Patchouli - Patchouli-1.20.1-85-FORGE.jar](https://www.curseforge.com/minecraft/mc-mods/patchouli/files/7731017) |
| 463826 | 5254550 | true | [Atlas Lib - Atlas Lib-1.20.1-1.1.12.jar](https://www.curseforge.com/minecraft/mc-mods/atlas-lib/files/5254550) |
| 379849 | 5182632 | true | [The Undergarden - The Undergarden 0.8.14](https://www.curseforge.com/minecraft/mc-mods/the-undergarden/files/5182632) |
| 1091339 | 9188826 | true | [AllTheLeaks (Memory Leak Fix) - alltheleaks-1.1.4+1.20.1-forge.jar](https://www.curseforge.com/minecraft/mc-mods/alltheleaks/files/9188826) |
| 223794 | 8991271 | true | [Applied Energistics 2 - 15.4.11 [FORGE]](https://www.curseforge.com/minecraft/mc-mods/applied-energistics-2/files/8991271) |
| 485779 | 8843034 | true | [The Hordes - The-Hordes-1.20.1-1.6.3i.jar](https://www.curseforge.com/minecraft/mc-mods/the-hordes/files/8843034) |
| 1028108 | 9037989 | true | [[TaCZ] Timeless and Classics Zero Guns - tacz-1.20.1-1.1.8-hotfix2.jar](https://www.curseforge.com/minecraft/mc-mods/timeless-and-classics-zero/files/9037989) |
| 378802 | 5278429 | true | [Structure Gel API - Structure Gel 1.20.1-v2.16.2](https://www.curseforge.com/minecraft/mc-mods/structure-gel-api/files/5278429) |
| 64760 | 8336490 | true | [Security Craft - [1.20.1] SecurityCraft v1.10.2.1.jar](https://www.curseforge.com/minecraft/mc-mods/security-craft/files/8336490) |
| 445274 | 7708970 | true | [Relics - relics-1.20.1-0.8.0.13.jar](https://www.curseforge.com/minecraft/mc-mods/relics-mod/files/7708970) |
| 515276 | 8946003 | false | [Enhanced AI - 3.3.7.5](https://www.curseforge.com/minecraft/mc-mods/enhanced-ai/files/8946003) |
| 1100379 | 7106942 | true | [Reliquified Artifacts - rarcompat-1.20.1-0.5.jar](https://www.curseforge.com/minecraft/mc-mods/reliquified-artifacts/files/7106942) |
| 280510 | 7612291 | true | [AttributeFix - AttributeFix-Forge-1.20.1-21.0.5.jar](https://www.curseforge.com/minecraft/mc-mods/attributefix/files/7612291) |
| 242818 | 8491810 | true | [CodeChicken Lib 1.8.+ - CodeChicken Lib 1.20.1-4.4.0.528](https://www.curseforge.com/minecraft/mc-mods/codechicken-lib-1-8/files/8491810) |
| 422301 | 9323244 | true | [Sophisticated Backpacks - 1.20.1-3.26.15.2228](https://www.curseforge.com/minecraft/mc-mods/sophisticated-backpacks/files/9323244) |
| 790626 | 9309378 | true | [modernfix：当初ファイルページ未確認（後続のfile-metadata.jsonで確認済み）](https://www.curseforge.com/minecraft/mc-mods/modernfix/files/9309378) |
| 229449 | 6028079 | true | [Epic Siege Mod - EpicSiegeMod-14.171.jar](https://www.curseforge.com/minecraft/mc-mods/epic-siege-mod/files/6028079) |
| 850298 | 8483796 | true | [Passive Skill Trees - PassiveSkillTree-1.20.1-BETA-0.7.6e-all.jar](https://www.curseforge.com/minecraft/mc-mods/passive-skill-tree/files/8483796) |
| 430642 | 5293465 | true | [Majrusz's Progressive Difficulty - Majrusz's Progressive Difficulty 1.9.10 (Forge)](https://www.curseforge.com/minecraft/mc-mods/majruszs-progressive-difficulty/files/5293465) |
| 437409 | 5302100 | true | [Majrusz Library - Majrusz Library 7.0.8 (Forge)](https://www.curseforge.com/minecraft/mc-mods/majrusz-library/files/5302100) |
| 1471165 | 8292038 | true | [endinglibrary：当初ファイルページ未確認（後続のfile-metadata.jsonで確認済み）](https://www.curseforge.com/minecraft/mc-mods/endinglibrary/files/8292038) |
| 429235 | 4810975 | true | [FerriteCore ((Neo)Forge) - ferritecore-6.0.1-forge.jar](https://www.curseforge.com/minecraft/mc-mods/ferritecore/files/4810975) |
| 1492763 | 9328058 | true | [Iron's Lib - irons_lib-1.20.1-2.3.0](https://www.curseforge.com/minecraft/mc-mods/irons-lib/files/9328058) |
| 312918 | 5010316 | true | [Blue Skies - Blue Skies: Population 1.20.1-v1.3.31](https://www.curseforge.com/minecraft/mc-mods/blue-skies/files/5010316) |
| 618298 | 9323153 | true | [Sophisticated Core - sophisticatedcore-1.20.1-1.5.16.2433.jar](https://www.curseforge.com/minecraft/mc-mods/sophisticated-core/files/9323153) |
| 388800 | 8854504 | true | [Polymorph - polymorph-forge-0.49.11+1.20.1.jar](https://www.curseforge.com/minecraft/mc-mods/polymorph/files/8854504) |
| 398521 | 8765179 | true | [Farmer's Delight - Farmer's Delight 1.3.4 - 1.20.1](https://www.curseforge.com/minecraft/mc-mods/farmers-delight/files/8765179) |
| 277616 | 4888575 | true | [Spice of Life: Carrot Edition - solcarrot-1.20.1-1.15.1.jar](https://www.curseforge.com/minecraft/mc-mods/spice-of-life-carrot-edition/files/4888575) |
| 1376660 | 9316839 | true | [TACZ Turrets - tacz_turrets-forge-3.0.1-1.20.1.jar](https://www.curseforge.com/minecraft/mc-mods/tacz-turrets/files/9316839) |

## 依存関係と未解決事項

以下はCurseForgeのプロジェクト単位の依存表示から得た調査対象。特定fileIDの必要条件は取得したJARのmods.tomlで確認する。
既存インスタンスと同じバージョンが不明なため、最新版や推測による補完はしていない。

| Mod | 公開ページにある依存関係と候補の状態 |
| --- | --- |
| [Iron's Spells](https://www.curseforge.com/minecraft/mc-mods/irons-spells-n-spellbooks/relations/dependencies) | Iron's Libは参照あり。Curios / GeckoLib / playerAnimatorは参照なし |
| [Iron's Lib](https://www.curseforge.com/minecraft/mc-mods/irons-lib/relations/dependencies) | GeckoLibの参照なし |
| [Relics](https://www.curseforge.com/minecraft/mc-mods/relics-mod/relations/dependencies) | OctoLibは参照あり。Curiosは参照なし |
| [Reliquified Artifacts](https://www.curseforge.com/minecraft/mc-mods/reliquified-artifacts/relations/dependencies) | Relicsは参照あり。Artifactsは参照なし |
| [Passive Skill Trees](https://www.curseforge.com/minecraft/mc-mods/passive-skill-tree/relations/dependencies) | AttributeFixは参照あり |

公式mc-image-helperのinstall-curseforgeはmanifestのrequired参照を処理し、未記載の依存Modを元環境と同じバージョンで自動補完するものではない。
Enhanced AIはrequired=falseなので導入対象外になる。ファイル参照は残し、勝手にtrueへ変更しない。
取得後に scripts/audit-mods.py でトップレベルとJar-in-JarのMod ID、バージョン、SHA-256、必須依存IDを出力する。
このスクリプトは依存IDの存在検査であり、Mavenのバージョン範囲判定や実行互換性の保証は行わない。

## 個人情報・秘密情報

入力のテキストを鍵・トークン・秘密設定・ユーザーパス等のパターンで走査した範囲では一致なし。全ての秘密情報がないとの保証ではない。
一方、config内にはJEIのローカル履歴・ブックマーク、sparkのactivity、マシン情報らしきfingerprintがある。
これらを含むoverrides、元フォルダ、ZIP、詳細な検査報告は公開しない。非公開の詳細報告はstaging/inspection.json。
Git追跡済みの3ファイル（Compose、README、gitignore）に秘密情報は検出されていない。履歴改変はしていない。

## 導入方式

| 方式 | 評価 |
| --- | --- |
| A: AUTO_CURSEFORGE + ローカルZIP | 採用。非公開パック対応、projectID/fileIDで固定、overridesも適用。手動取得ファイルは非公開downloadsへ。起動前にZIPのハッシュを検証する |
| B: JARと設定を直接コピー | API不要で完全な実物を固定しやすいが、今回の入力にJARがなく、入手・版数・ライセンス・依存管理を別途すべて維持する必要がある |

公開GitHubのgit pullだけでは非公開ZIP等は揃わない。同じハッシュのZIPと必要な手動取得ファイルを別経路で用意する。
Java 17以降の現行イメージはAPIキーを内包するが、固定イメージでの実動作は別途確認が必要。必要なら自分のキーを非公開.envに設定する。

## 検証の限界

ZIP構築・入力検査・ガード・Compose等の静的な検証は可能。Mod取得・実JAR照合・Forge起動・ワールド移行は別工程。
現在の候補に対してMODPACK_VERIFIED_SHA256を設定してはならない。まず再エクスポートと元インスタンスの一覧を照合する。

## 後続の実ファイル検査と再エクスポート比較

旧候補の38 JARに対する必須依存ID検査は失敗し、architectury / artifacts / curios / geckolib / guideme / smartbrainlibが不足した。
Forgeインストーラの完了は確認したが、Minecraftサーバーは起動していない。

新しいAll modsの比較結果は[EXPORT-COMPARISON.md](EXPORT-COMPARISON.md)を参照。
新候補にはMekanism等が復帰したが、expandabilityとsmartbrainlibが不足しており未検証。
旧候補と新候補を混在させず、Composeの稼働用参照は切り替えていない。
