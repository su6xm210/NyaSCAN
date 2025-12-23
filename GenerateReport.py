from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from datetime import datetime
from html import escape
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

DEFAULT_LOG_DIR = Path(__file__).parent / "log"
RESULT_PATTERN = re.compile(
    r'^\[(?P<ts>[^\]]+)\]\s*'
    r'(?P<url>\S*)\s*'
    r'(?P<status>There is(?: not)? a security vulnerability)\s*'
    r'"(?P<poc>[^"]*)"\s*'
    r'(?P<detail>.*)$'
)

ERROR_PATTERN = re.compile(
    r'^\[(?P<ts>[^\]]+)\]\s*(?P<message>.*)$'
)


@dataclass
class ResultEntry:
    timestamp: str
    url: str
    status: str
    poc: str
    detail: str
    source: str

    @property
    def is_vulnerable(self) -> bool:
        return "There is a security vulnerability" in self.status


@dataclass
class ErrorEntry:
    timestamp: str
    message: str
    source: str


def read_lines_any(path: Path, encodings: Iterable[str]) -> List[str]:
    for enc in encodings:
        try:
            return path.read_text(encoding=enc).splitlines()
        except UnicodeDecodeError:
            continue
    return path.read_text(encoding=encodings[0], errors="ignore").splitlines()


def load_logs(log_dir: Path) -> Tuple[List[ResultEntry], List[ErrorEntry]]:
    """读取日志目录，解析结果日志与错误日志。"""
    results: List[ResultEntry] = []
    errors: List[ErrorEntry] = []

    if not log_dir.exists():
        return results, errors
    preferred_encodings = ("utf-8", "gbk", "gb2312")

    for path in sorted(log_dir.glob("*")):
        if not path.is_file():
            continue
        lines = read_lines_any(path, preferred_encodings)

        for line in lines:
            text = line.strip()
            if not text:
                continue

            m = RESULT_PATTERN.match(text)
            if m:
                results.append(
                    ResultEntry(
                        timestamp=m.group("ts"),
                        url=m.group("url"),
                        status=m.group("status"),
                        poc=m.group("poc"),
                        detail=m.group("detail").strip(),
                        source=path.name,
                    )
                )
                continue

            m = ERROR_PATTERN.match(text)
            if m:
                errors.append(
                    ErrorEntry(
                        timestamp=m.group("ts"),
                        message=m.group("message").strip(),
                        source=path.name,
                    )
                )
    return results, errors


def build_summary(results: List[ResultEntry]) -> dict:
    """生成统计数据"""
    vuln_count = sum(1 for r in results if r.is_vulnerable)
    total = len(results)
    target_set = {r.url for r in results if r.url}
    poc_set = {r.poc for r in results if r.poc}
    return {
        "total": total,
        "vuln": vuln_count,
        "safe": total - vuln_count,
        "targets": len(target_set),
        "pocs": len(poc_set),
    }


def render_html(results: List[ResultEntry], errors: List[ErrorEntry], log_dir: Path) -> str:
    """将数据渲染为HTML字符串"""
    summary = build_summary(results)
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    vuln_results = [r for r in results if r.is_vulnerable]
    safe_results = [r for r in results if not r.is_vulnerable]

    def group_by_target(rows: List[ResultEntry]) -> Dict[str, Dict[str, int]]:
        """统计结果"""
        stats: Dict[str, Dict[str, int]] = {}
        for r in rows:
            key = r.url or "-"
            if key not in stats:
                stats[key] = {"poc_total": 0, "vuln": 0, "safe": 0}
            stats[key]["poc_total"] += 1
            if r.is_vulnerable:
                stats[key]["vuln"] += 1
            else:
                stats[key]["safe"] += 1
        return stats

    target_stats = group_by_target(results)

    def row_result(r: ResultEntry) -> str:
        status_class = "vuln" if r.is_vulnerable else "safe"
        return (
            "<tr>"
            f"<td>{escape(r.timestamp)}</td>"
            f"<td>{escape(r.url or '-')}</td>"
            f"<td class='{status_class}'>{escape('存在漏洞' if r.is_vulnerable else '未发现')}</td>"
            f"<td>{escape(r.poc or '-')}</td>"
            f"<td>{escape(r.detail or '-')}</td>"
            f"<td>{escape(r.source)}</td>"
            "</tr>"
        )

    def row_target(addr: str, stat: Dict[str, int]) -> str:
        return (
            "<tr>"
            f"<td>{escape(addr)}</td>"
            f"<td>{stat['poc_total']}</td>"
            f"<td>{stat['vuln']}</td>"
            f"<td>{stat['safe']}</td>"
            "</tr>"
        )

    def row_error(e: ErrorEntry) -> str:
        return (
            "<tr>"
            f"<td>{escape(e.timestamp)}</td>"
            f"<td>{escape(e.message)}</td>"
            f"<td>{escape(e.source)}</td>"
            "</tr>"
        )

    html = f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <title>漏洞检测评估报告</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 24px; color: #222; }}
    h1, h2 {{ margin-bottom: 8px; }}
    .meta {{ color: #555; margin-bottom: 16px; }}
    table {{ border-collapse: collapse; width: 100%; margin-bottom: 24px; }}
    th, td {{ border: 1px solid #ddd; padding: 8px; font-size: 14px; }}
    th {{ background: #f5f5f5; text-align: left; }}
    tr:nth-child(even) {{ background: #fafafa; }}
    .vuln {{ color: #b30000; font-weight: bold; }}
    .safe {{ color: #2e7d32; }}
    .chip {{ display: inline-block; padding: 4px 8px; margin-right: 8px;
            border-radius: 4px; background: #f0f0f0; font-size: 13px; }}
    details summary {{ cursor: pointer; font-weight: 600; margin-bottom: 8px; }}
  </style>
</head>
<body>
  <h1>漏洞检测评估报告</h1>
  <div class="meta">
    <div class="chip">生成时间：{escape(now)}</div>
    <div class="chip">日志目录：{escape(str(log_dir))}</div>
    <div class="chip">总记录：{summary['total']}</div>
    <div class="chip">确认漏洞：{summary['vuln']}</div>
    <div class="chip">未发现漏洞：{summary['safe']}</div>
    <div class="chip">涉及目标：{summary['targets']}</div>
    <div class="chip">涉及 POC：{summary['pocs']}</div>
  </div>

  <h2>测试目标</h2>
  <table>
    <thead>
      <tr>
        <th>目标地址</th>
        <th>测试 POC 数</th>
        <th>存在漏洞</th>
        <th>未发现</th>
      </tr>
    </thead>
    <tbody>
      {''.join(row_target(addr, stat) for addr, stat in target_stats.items()) or '<tr><td colspan="4">无目标数据</td></tr>'}
    </tbody>
  </table>

  <h2>存在漏洞</h2>
  <table>
    <thead>
      <tr>
        <th>时间</th>
        <th>目标 URL</th>
        <th>结论</th>
        <th>POC</th>
        <th>详情</th>
        <th>来源日志</th>
      </tr>
    </thead>
    <tbody>
      {''.join(row_result(r) for r in vuln_results) or '<tr><td colspan="6">未发现漏洞记录</td></tr>'}
    </tbody>
  </table>

  <h2>未发现漏洞</h2>
  <details>
    <summary>展开/折叠 未发现漏洞列表（{len(safe_results)} 条）</summary>
    <table>
      <thead>
        <tr>
          <th>时间</th>
          <th>目标 URL</th>
          <th>结论</th>
          <th>POC</th>
          <th>详情</th>
          <th>来源日志</th>
        </tr>
      </thead>
      <tbody>
        {''.join(row_result(r) for r in safe_results) or '<tr><td colspan="6">无记录</td></tr>'}
      </tbody>
    </table>
  </details>

  <h2>错误与异常</h2>
  <table>
    <thead>
      <tr>
        <th>时间</th>
        <th>信息</th>
        <th>来源日志</th>
      </tr>
    </thead>
    <tbody>
      {''.join(row_error(e) for e in errors) or '<tr><td colspan="3">无错误记录</td></tr>'}
    </tbody>
  </table>
</body>
</html>"""
    return html


def main() -> None:
    parser = argparse.ArgumentParser(
        description="从 log 目录生成 HTML 漏洞检测报告"
    )
    parser.add_argument(
        "--log",
        dest="log_dir",
        default=str(DEFAULT_LOG_DIR),
        help="日志目录路径（默认：项目根目录下的 log）",
    )
    parser.add_argument(
        "--output",
        dest="output",
        default="scan_report.html",
        help="输出 HTML 文件路径（默认：scan_report.html）",
    )
    args = parser.parse_args()

    log_dir = Path(args.log_dir)
    output_path = Path(args.output)

    results, errors = load_logs(log_dir)
    html = render_html(results, errors, log_dir)

    output_path.write_text(html, encoding="utf-8")
    print(f"报告已生成：{output_path.resolve()}")


if __name__ == "__main__":
    main()

