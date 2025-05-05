# domain_checker

ドメインリストからWHOIS情報と主要DNSレコードを自動収集し、CSV形式で出力するPythonスクリプトです。  
レートリミット対策として、クエリ間に待機時間を設けており、WHOIS・DNSサーバーへの過負荷を防ぎます。

---

## 特徴

- ドメインごとにWHOIS情報（登録者、登録日、有効期限、ネームサーバー等）を取得
- A/AAAA/MX/NS/TXT/SOA/CNAME/SRV/PTRなど主要DNSレコードを自動収集
- レートリミット対策としてクエリ間の遅延を設定可能
- 取得結果をCSVファイルで出力
- エラーや取得不可情報も明示的に記録

---

## 必要な環境

- Python 3.7 以上

### 必要なパッケージ

`requirements.txt` を利用してインストールしてください。

```
python-whois
dnspython
```

インストールコマンド例：

```
pip install -r requirements.txt
```

---

## 使い方

### 1. ドメインリストファイルの作成

1行に1ドメインずつ記載したテキストファイル（例: `domains.txt`）を用意します。

例:
```
example.com
google.com
example.jp
```

### 2. スクリプトの実行

```
python domain_checker.py <input.txt> <output.csv> [delay]
```

- `<input.txt>`: ドメインリストファイル
- `<output.csv>`: 結果出力先CSVファイル
- `[delay]`: （オプション）各ドメイン処理間の待機秒数（デフォルト: 5秒）

#### 実行例

```
python domain_checker.py domains.txt report.csv
```

10秒間隔でクエリする場合:

```
python domain_checker.py domains.txt report.csv 10
```

---

## 出力例

| domain      | registrar    | created    | expires    | nameservers           | status    | updated    | A              | MX               | ... |
|-------------|--------------|------------|------------|-----------------------|-----------|------------|----------------|------------------|-----|
| example.com | RESERVED     | 1995-08-13 | 2024-08-14 | a.iana-servers.net    | N/A       | N/A        | 93.184.216.34  | N/A              | ... |
| google.com  | MarkMonitor  | 1997-09-15 | 2028-09-14 | ns1.google.com; ...   | clientTransferProhibited | 2023-09-09 | 142.250.206.46 | 10 smtp.google.com | ... |

---

## 注意事項

- 大量のドメインを処理する場合は、delay値を大きめ（例: 10秒以上）に設定してください。
- WHOIS情報は一部ドメインで非公開や省略される場合があります。
- DNSサーバーやWHOISサーバーの仕様・制限により、すべての情報が取得できない場合があります。
- 本ツールの利用によるサーバーへの過負荷や利用規約違反にご注意ください。

---

## ライセンス

MIT License

---

## 作者

- perplexity-ai（サンプルコード作成）
- ご質問・ご要望はIssueまで
```

情報源
