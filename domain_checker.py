import csv
import sys
import time
import dns.resolver
import whois
from pathlib import Path
from typing import Dict, List

DEFAULT_RECORD_TYPES = ['A', 'AAAA', 'MX', 'NS', 'TXT', 'SOA', 'CNAME', 'SRV', 'PTR']
DEFAULT_DELAY = 5  # デフォルトの遅延時間（秒）

def get_whois_data(domain: str) -> Dict[str, str]:
    """WHOIS情報を取得"""
    try:
        w = whois.whois(domain)
        return {
            'domain': domain,
            'registrar': w.registrar if w.registrar else 'N/A',
            'created': w.creation_date[0].strftime('%Y-%m-%d') if w.creation_date else 'N/A',
            'expires': w.expiration_date[0].strftime('%Y-%m-%d') if w.expiration_date else 'N/A',
            'nameservers': '; '.join(w.name_servers) if w.name_servers else 'N/A',
            'status': '; '.join(w.status) if w.status else 'N/A',
            'updated': w.updated_date[0].strftime('%Y-%m-%d') if w.updated_date else 'N/A'
        }
    except Exception as e:
        return {'domain': domain, 'error': f"WHOIS Error: {str(e)}"}

def get_dns_records(domain: str) -> Dict[str, str]:
    """DNS全レコードを取得"""
    records = {}
    resolver = dns.resolver.Resolver()
    resolver.timeout = 5
    resolver.lifetime = 5

    try:
        # ANYレコードの取得を試みる
        try:
            answer = resolver.resolve(domain, 'ANY')
            for rdata in answer:
                rt = dns.rdatatype.to_text(rdata.rdtype)
                records.setdefault(rt, []).append(rdata.to_text())
        except dns.resolver.NoAnswer:
            pass
        except dns.resolver.NoNameservers:
            records['error'] = 'DNS Server Error'

        # 主要レコードタイプを個別にチェック
        for rt in DEFAULT_RECORD_TYPES:
            try:
                answer = resolver.resolve(domain, rt)
                records[rt] = [rdata.to_text() for rdata in answer]
            except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN):
                continue
            except Exception:
                pass

    except dns.resolver.NXDOMAIN:
        records['error'] = 'NXDOMAIN'
    except Exception as e:
        records['error'] = f"DNS Error: {str(e)}"

    return {k: '; '.join(v) if isinstance(v, list) else v for k, v in records.items()}

def main(input_file: str, output_file: str, delay: int):
    if not Path(input_file).exists():
        print(f"Error: {input_file} not found")
        sys.exit(1)

    with open(input_file, 'r') as f:
        domains = [line.strip() for line in f if line.strip()]

    # 全フィールドを動的に収集
    all_fields = set()
    sample_data = []

    for i, domain in enumerate(domains, 1):
        print(f"Processing ({i}/{len(domains)}): {domain}")
        
        # WHOIS情報取得
        whois_data = get_whois_data(domain)
        
        # DNS情報取得
        dns_data = get_dns_records(domain)
        
        combined = {**whois_data, **dns_data}
        all_fields.update(combined.keys())
        sample_data.append(combined)
        
        # レートリミット対策の遅延
        if i < len(domains):
            print(f"Waiting {delay} seconds...")
            time.sleep(delay)

    # フィールド順序を最適化
    base_fields = [
        'domain', 'registrar', 'created', 'expires',
        'nameservers', 'status', 'updated', 'error'
    ]
    dns_fields = sorted([f for f in all_fields if f not in base_fields])
    fieldnames = base_fields + dns_fields

    # CSV出力
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(sample_data)

    print(f"Done: Results saved to {output_file}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python domain_checker.py <input.txt> <output.csv> [delay]")
        print("Example: python domain_checker.py domains.txt report.csv 5")
        sys.exit(1)
    
    delay = int(sys.argv[3]) if len(sys.argv) > 3 else DEFAULT_DELAY
    main(sys.argv[1], sys.argv[2], delay)
