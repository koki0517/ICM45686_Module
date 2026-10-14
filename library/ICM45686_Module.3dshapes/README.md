# 3Dモデルの出典

モジュールのPCB外形・部品位置は本リポジトリのICM-45686.kicad_pcbから生成しました。ICM-45686パッケージは既存のICM_45686/ICM-45686.stepを使用しています。

コネクタとコンデンサはインストール済みKiCad標準3Dライブラリの以下のデータを使用しています。

- Connector_PinHeader_2.54mm.3dshapes/PinHeader_1x04_P2.54mm_Vertical.step
- Connector_PinSocket_2.54mm.3dshapes/PinSocket_1x04_P2.54mm_Vertical.step
- Capacitor_SMD.3dshapes/C_0402_1005Metric.step

コネクタの作者情報は同梱のKiCad-PinHeader-CREDITS.mdとKiCad-PinSocket-CREDITS.mdに収録しています。コンデンサはKiCad library teamの標準モデルです。

KiCad由来のモデルを含むこの3Dライブラリは、同梱のKiCad-LICENSE.mdに記載されたCC-BY-SA 4.0とKiCadの例外条項の下で提供します。元リポジトリのライセンスはルートのLICENCE.txtを参照してください。

組立・配置・STEP出力はlibrary/scripts/generate_library.pyとKiCad CLIで生成しました。

KiCad表示と機械CADで使用するモデルは `ICM45686_Module.step` の1個です。母基板側ソケット・ICM基板側ヘッダー・部品付きICM基板を含みます。KiCadの書き出し後、scripts/color_step.py（CadQuery）で元部品の材料色と基板レイヤーの色を復元しています。中間モデルは一時フォルダで生成します。
