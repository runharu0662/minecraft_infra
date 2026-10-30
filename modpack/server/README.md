# All modsからのサーバー用導入結果（#005）

All mods原本のWindows側構成を変更せず、サーバー用結果だけを別ディレクトリで作成した。
Composeの入力は `modpack/server/` と非公開 `staging/server-all-mods/`。旧候補と除外前のAll mods調査結果はそのまま保存。
**Mod取得の確認まで。必須依存が未解決のためワールド起動禁止。Windows実JARとの一致も未確認。**

## 除外ポリシー

明示除外は共通の `modpack/exclude-include.json` のglobalExcludesにembeddiumを指定する。
このファイルは準備用helperと通常のAUTO_CURSEFORGEの両方が同じものを参照する。
globalForceIncludesは空。公式helperの固定ファイルのClient/Server判定を変更していない。
ゲーム内容・依存Modを推測で除外せず、manifestの81参照とrequired値も維持する。

| Mod / 固定バージョン | projectID:fileID | 除外方法・理由 |
| --- | --- | --- |
| [Neat-1.20.1-41-FORGE.jar](https://www.curseforge.com/minecraft/mc-mods/neat/files/5838485) / 41 | 238372:5838485 | 公式helperの自動除外。固定ファイルのClientタグがありServerタグがない。 |
| [entityculling-forge-1.11.3-mc1.20.1.jar](https://www.curseforge.com/minecraft/mc-mods/entityculling/files/9100267) / 1.11.3 | 448233:9100267 | 公式helperの自動除外。固定ファイルのClientタグがありServerタグがない。 |
| [BadOptimizations-2.4.1-1.20.1.jar](https://www.curseforge.com/minecraft/mc-mods/badoptimizations/files/7338200) / 2.4.1 | 949555:7338200 | 公式helperの自動除外。固定ファイルのClientタグがありServerタグがない。 |
| [Essential_1-5-1_forge_1-20-1.jar](https://www.curseforge.com/minecraft/mc-mods/essential-mod/files/9189705) / 1.5.1 | 546670:9189705 | 公式helperの自動除外。固定ファイルのClientタグがありServerタグがない。 |
| [BetterAdvancements-Forge-1.20.1-0.6.0.73.jar](https://www.curseforge.com/minecraft/mc-mods/better-advancements/files/8569648) / 0.6.0.73 | 272515:8569648 | 公式helperの自動除外。固定ファイルのClientタグがありServerタグがない。 |
| [MouseTweaks-forge-mc1.20.1-2.25.1.jar](https://www.curseforge.com/minecraft/mc-mods/mouse-tweaks/files/5338457) / 2.25.1 | 60089:5338457 | 公式helperの自動除外。固定ファイルのClientタグがありServerタグがない。 |
| [embeddium-0.3.31+mc1.20.1.jar](https://www.curseforge.com/minecraft/mc-mods/embeddium/files/5681725) / 0.3.31+mc1.20.1 | 908741:5681725 | 明示除外。作者がクライアント用描画最適化Modと説明。#005の指定。 |

実行ログにEmbeddiumのconfigurationによる除外を確認した。上の7ファイルはサーバー用modsに存在しない。
Enhanced AI 3.3.7.5はクライアント専用として除外したのではなく、元manifestのrequired=falseに従い導入されない。
81参照 − 任意1 − 自動除外6 − 明示除外1 = **73トップレベルJAR**。
Jar-in-Jarの内包ライブラリはこのJAR数とは別に依存監査する。

## 未解決の必須依存

| 依存元 | 不足するMod ID | JARが要求するバージョン範囲 |
| --- | --- | --- |
| Artifacts | expandability | [9.0.0,) |
| TACZ Turrets | smartbrainlib | [1.15,) |

不足を最新版で自動補完せず、元Windowsの実JAR・有効状態・正確な版数との照合を待つ。
Mekanism Toolsも元All modsに参照がなく、実物の有無を確認するまで追加しない。
監査はJAR内部の必須依存IDの存在検査であり、全バージョン範囲・実行互換性・ワールド整合性の保証ではない。

## 導入された73 JARの全一覧

ファイル名・表示版・固定ID・SHA-256・内部Mod ID/版数は [installed-mods.json](installed-mods.json)。
Jar-in-Jarを含む監査結果は [dependency-audit.json](dependency-audit.json)。

| projectID:fileID | JARファイル名 | 内部Mod ID / バージョン |
| --- | --- | --- |
| 313970:6461960 | Apotheosis-1.20.1-7.4.8.jar | apotheosis / 7.4.8 |
| 898963:5634071 | ApothicAttributes-1.20.1-1.3.7.jar | attributeslib / 1.3.7 |
| 574300:7244744 | Applied-Mekanistics-1.4.3.jar | appmek / 1.4.3 |
| 463826:5254550 | Atlas Lib-1.20.1-1.1.12.jar | atlaslib / 1.1.12 |
| 280510:7612291 | AttributeFix-Forge-1.20.1-21.0.5.jar | attributefix / 21.0.5 |
| 231382:5422013 | BrandonsCore-1.20.1-3.2.1.302-universal.jar | brandonscore / 3.2.1.302 |
| 256717:5278538 | Clumps-forge-1.20.1-12.0.0.4.jar | clumps / 12.0.0.4 |
| 242818:8491810 | CodeChickenLib-1.20.1-4.4.0.528-universal.jar | codechickenlib / 4.4.0.528 |
| 442508:4983862 | DungeonsArise-1.20.x-2.1.58-release.jar | dungeons_arise / 2.1.58-1.20.x |
| 953637:4981380 | DungeonsAriseSevenSeas-1.20.x-1.0.2-forge.jar | dungeons_arise_seven_seas / 1.0.2 |
| 1471165:8292038 | EndingLibrary-1.20.1-2.1.19fix-all.jar | ending_library / 2.1.19fix |
| 336184:5600004 | EnigmaticLegacy-2.30.1.jar | enigmaticlegacy / 2.30.1 |
| 229449:6028079 | EpicSiegeMod-14.171.jar | epicsiegemod / 14.171 |
| 398521:8765179 | FarmersDelight-1.20.1-1.3.4.jar | farmersdelight / 1.20.1-1.3.4 |
| 299540:5181098 | FastFurnace-1.20.1-8.0.2.jar | fastfurnace / 8.0.2 |
| 475117:7527943 | FastSuite-1.20.1-5.1.2.jar | fastsuite / 5.1.2 |
| 288885:5101229 | FastWorkbench-1.20.1-8.0.4.jar | fastbench / 8.0.4 |
| 324717:8479276 | Jade-1.20.1-Forge-11.13.3.jar | jade / 11.13.3+forge |
| 268560:6552911 | Mekanism-1.20.1-10.4.16.80.jar | mekanism / 10.4.16 |
| 268566:6552914 | MekanismGenerators-1.20.1-10.4.16.80.jar | mekanismgenerators / 10.4.16 |
| 916747:6274623 | OctoLib-FORGE-0.5.0.1+1.20.1.jar | octolib / 0.5.0.1 |
| 850298:8483796 | PassiveSkillTree-1.20.1-BETA-0.7.6e-all.jar | skilltree / 0.7.6e |
| 306770:7731017 | Patchouli-1.20.1-85-FORGE.jar | patchouli / 1.20.1-85-FORGE |
| 283644:6274231 | Placebo-1.20.1-8.6.3.jar | placebo / 8.6.3 |
| 485779:8843034 | The-Hordes-1.20.1-1.6.3i-all.jar | hordes / 1.6.3g |
| 379849:5182632 | The_Undergarden-1.20.1-0.8.14.jar | undergarden / 0.8.14 |
| 251730:5179872 | Voidscape-1.20.1-1.5.389.jar | voidscape / 1.20.1-1.5.389 |
| 64760:8336490 | [1.20.1] SecurityCraft v1.10.2.1.jar | securitycraft / 1.10.2.1 |
| 255308:6134920 | aether-1.20.1-1.5.2-neoforge.jar | aether / 1.20.1-1.5.2-neoforge |
| 1091339:9188826 | alltheleaks-1.1.4+1.20.1-forge.jar | alltheleaks / 1.1.4+1.20.1-forge |
| 248787:4770828 | appleskin-forge-mc1.20.1-2.5.1.jar | appleskin / 2.5.1+mc1.20.1 |
| 223794:8991271 | appliedenergistics2-forge-15.4.11.jar | ae2 / 15.4.11 |
| 419699:5137938 | architectury-9.2.14-forge.jar | architectury / 9.2.14 |
| 312353:7903806 | artifacts-forge-9.5.19.jar | artifacts / 9.5.19 |
| 531320:4601241 | awesomedungeon-forge-1.20.1-3.2.0.jar | awesomedungeon / 3.2.0 |
| 575406:4601238 | awesomedungeonend-forge-1.20.1-3.1.1.jar | awesomedungeonend / 3.1.1 |
| 566649:4601246 | awesomedungeonnether-forge-1.20.1-3.1.1.jar | awesomedungeonnether / 3.1.1 |
| 556490:4601248 | awesomedungeonocean-forge-1.20.1-3.3.0.jar | awesomedungeonocean / 3.3.0 |
| 312918:5010316 | blue_skies-1.20.1-1.3.31.jar | blue_skies / 1.3.31 |
| 308989:5281700 | caelus-forge-3.2.0+1.20.1.jar | caelus / 3.2.0+1.20.1 |
| 348521:5729105 | cloth-config-11.1.136-forge.jar | cloth_config / 11.1.136 |
| 309927:6418456 | curios-forge-5.14.1+1.20.1.jar | curios / 5.14.1+1.20.1 |
| 659011:5906086 | deeperdarker-forge-1.20.1-1.3.3.jar | deeperdarker / 1.3.3 |
| 404183:5598990 | endrem_forge-5.3.3-R-1.20.1.jar | endrem / 5.3.3-R-1.20.1 |
| 901420:8384482 | exdeorum-1.53.jar | exdeorum / 1.53 |
| 1420337:7642083 | fantasy_ending-1.20.1-2.7.20-all.jar | fantasy_ending / 2.7.20 |
| 429235:4810975 | ferritecore-6.0.1-forge.jar | ferritecore / 6.0.1 |
| 388172:8285794 | geckolib-forge-1.20.1-4.8.4.jar | geckolib / 4.8.4 |
| 1173950:8204776 | guideme-20.1.15.jar | guideme / 20.1.15 |
| 465109:8306331 | insanelib-1.23.4.6.jar | insanelib / 1.23.4.6 |
| 1492763:9328058 | irons_lib-1.20.1-2.3.0.jar | irons_lib / 1.20.1-2.3.0 |
| 855414:8680180 | irons_spellbooks-1.20.1-3.16.3.jar | irons_spellbooks / 1.20.1-3.16.3 |
| 238222:9298209 | jei-1.20.1-forge-15.74.0.229.jar | jei / 15.74.0.229 |
| 351264:7291067 | kotlinforforge-4.12.0-all.jar | Mod IDなし（言語プロバイダー等。ファイル版は固定IDとファイル名で記録） |
| 532727:4601234 | libraryferret-forge-1.20.1-4.0.0.jar | libraryferret / 4.0.0 |
| 437409:5302100 | majrusz-library-forge-1.20.1-7.0.8.jar | majruszlibrary / 7.0.8 |
| 430642:5293465 | majruszs-difficulty-forge-1.20.1-1.9.10.jar | majruszsdifficulty / 1.9.10 |
| 1689768:9318716 | mezz_config-1.20.1-forge-0.6.9.jar | mezz_config / 0.6.9 |
| 790626:9309378 | modernfix-forge-5.27.91+mc1.20.1.jar | modernfix / 5.27.91+mc1.20.1 |
| 872516:8145294 | nether_remastered-2.6-forge-1.20.1.jar | nether_remastered / 2.6 |
| 967560:5063173 | nophantoms-0.1.jar | nophantoms / 0.1 |
| 689467:7872374 | packetfixer-3.3.2-1.18-1.20.4-merged.jar | packetfixer / 3.3.2 |
| 658587:4587214 | player-animation-lib-forge-1.0.2-rc1+1.20.jar | playeranimator / 1.0.2-rc1+1.20 |
| 388800:8854504 | polymorph-forge-0.49.11+1.20.1.jar | polymorph / 0.49.11+1.20.1 |
| 1100379:7106942 | rarcompat-1.20.1-0.5.jar | rarcompat / 0.5 |
| 445274:7708970 | relics-1.20.1-0.8.0.13.jar | relics / 0.8.0.13 |
| 277616:4888575 | solcarrot-1.20.1-1.15.1.jar | solcarrot / 1.15.1 |
| 422301:9323244 | sophisticatedbackpacks-1.20.1-3.26.15.2228.jar | sophisticatedbackpacks / 3.26.15.2228 |
| 618298:9323153 | sophisticatedcore-1.20.1-1.5.16.2433.jar | sophisticatedcore / 1.5.16.2433 |
| 361579:4738952 | spark-1.10.53-forge.jar | spark / 1.10.53 |
| 378802:5278429 | structure_gel-1.20.1-2.16.2.jar | structure_gel / 2.16.2 |
| 1028108:9037989 | tacz-1.20.1-1.1.8-hotfix2.jar | tacz / 1.1.8-hotfix2 |
| 1376660:9316839 | tacz_turrets-forge-3.0.1-1.20.1.jar | tacz_turrets / 3.0.1 |

準備サービス（Mod取得とForgeインストーラ）は終了コード0で完了。Minecraft本体の起動は未実施。

## 再現手順と保護

```bash
python3 -B scripts/prepare-modpack.py for_server.zip \
  --staging-dir staging/server-all-mods --definition-dir modpack/server
docker compose --profile tools run --rm --no-deps modpack-prepare
python3 -B scripts/audit-mods.py staging/server-all-mods/prepared/mods > staging/server-all-mods/mod-audit.json
```

監査コマンドは不足依存があるため終了コード1になるのが現在の正しい結果。
通常のMinecraftサービスは起動していない。MODPACK_VERIFIED_SHA256は空のまま。
ワールド欠落・level-name不一致等の既存ガードも維持し、data/の自動作成は禁止したまま。
除外設定を変更した場合は既存helperの導入キャッシュを信用せず、新しい準備先で結果を照合する。
稼働データへの変更やCF_FORCE_SYNCHRONIZEの常時有効化で調整しない。
Windows元構成との比較は除外前のAll modsメタデータを使い、サーバーの73件だけを元構成とみなさない。

元ZIP・JAR・インスタンス・ワールドは変更していない。VPS接続、ワールド起動、commit/pushは行っていない。

公式根拠: [AUTO_CURSEFORGEの除外機能](https://docker-minecraft-server.readthedocs.io/en/latest/types-and-platforms/mod-platforms/auto-curseforge/)、[Embeddium作者説明](https://www.curseforge.com/minecraft/mc-mods/embeddium)。
