import os
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

class ReportGenerator:
    @staticmethod
    def generate_json_report(stats: Dict[str, Any], songs_detail: List[Dict[str, Any]], export_path: str):
        """Generates a structured JSON report of scan statistics and detailed statuses."""
        report = {
            "generated_at": datetime.now().isoformat(),
            "statistics": stats,
            "details": songs_detail
        }
        os.makedirs(os.path.dirname(os.path.abspath(export_path)), exist_ok=True)
        with open(export_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=4, ensure_ascii=False)

    @staticmethod
    def generate_txt_report(stats: Dict[str, Any], songs_detail: List[Dict[str, Any]], export_path: str):
        """Generates a plain-text report summarizing matching results and failures."""
        lines = []
        lines.append("=" * 60)
        lines.append("LYRICFORGE RUN REPORT")
        lines.append(f"Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("=" * 60)
        lines.append("\nSUMMARY STATISTICS:")
        for k, v in stats.items():
            lines.append(f"  {k.replace('_', ' ').title()}: {v}")
        
        lines.append("\n" + "=" * 60)
        
        embedded = [s for s in songs_detail if s.get('status') == 'Embedded']
        matched = [s for s in songs_detail if s.get('status') == 'Matched']
        failed = [s for s in songs_detail if s.get('status') == 'Failed']
        unmatched = [s for s in songs_detail if s.get('status') == 'Unmatched']

        if embedded:
            lines.append("\nEMBEDDED SONGS:")
            for s in embedded:
                lines.append(f"  - {Path(s['file_path']).name}")
                lines.append(f"    Song Path: {s['file_path']}")
                lines.append(f"    Lyrics: {s.get('lyric_path', 'N/A')}")
                if s.get('spectral_cutoff'):
                    legit_val = s.get('legit')
                    legit_str = "Yes (Verified Lossless)" if (legit_val == 1 or legit_val is True) else "No (Fake Upscale / Transcode)"
                    lines.append(f"    Legit Lossless: {legit_str}")
                    lines.append(f"    Verification Details: {s.get('legit_reason', 'N/A')}")
        
        if failed:
            lines.append("\nFAILED EMBEDDINGS:")
            for s in failed:
                lines.append(f"  - {Path(s['file_path']).name}")
                lines.append(f"    Path: {s['file_path']}")
                lines.append(f"    Error: {s.get('error', 'Unknown Error')}")

        if unmatched:
            lines.append("\nUNMATCHED SONGS:")
            for s in unmatched:
                lines.append(f"  - {Path(s['file_path']).name} (Artist: {s.get('artist') or 'N/A'}, Title: {s.get('title') or 'N/A'})")

        os.makedirs(os.path.dirname(os.path.abspath(export_path)), exist_ok=True)
        with open(export_path, 'w', encoding='utf-8') as f:
            f.write("\n".join(lines))

    @staticmethod
    def generate_html_report(stats: Dict[str, Any], songs_detail: List[Dict[str, Any]], export_path: str):
        """Generates a responsive, visually stunning HTML report with premium design components."""
        embedded = [s for s in songs_detail if s.get('status') == 'Embedded']
        matched = [s for s in songs_detail if s.get('status') == 'Matched']
        failed = [s for s in songs_detail if s.get('status') == 'Failed']
        unmatched = [s for s in songs_detail if s.get('status') == 'Unmatched']

        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>LyricForge Report</title>
    <style>
        body {{
            font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, sans-serif;
            background-color: #0f172a;
            color: #f8fafc;
            margin: 0;
            padding: 2rem;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        h1 {{
            background: linear-gradient(to right, #6366f1, #a855f7);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 2.5rem;
            margin-bottom: 0.5rem;
        }}
        .meta {{
            color: #94a3b8;
            margin-bottom: 2rem;
        }}
        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 1.5rem;
            margin-bottom: 3rem;
        }}
        .card {{
            background: #1e293b;
            padding: 1.5rem;
            border-radius: 12px;
            border: 1px solid #334155;
            text-align: center;
        }}
        .card .value {{
            font-size: 2rem;
            font-weight: bold;
            color: #38bdf8;
            margin-bottom: 0.5rem;
        }}
        .card .label {{
            color: #94a3b8;
            font-size: 0.9rem;
            text-transform: uppercase;
        }}
        .section {{
            margin-bottom: 3rem;
            background: #1e293b;
            border: 1px solid #334155;
            border-radius: 16px;
            padding: 1.5rem;
        }}
        h2 {{
            margin-top: 0;
            color: #e2e8f0;
            border-bottom: 1px solid #334155;
            padding-bottom: 0.5rem;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 1rem;
            text-align: left;
        }}
        th, td {{
            padding: 0.75rem 1rem;
            border-bottom: 1px solid #334155;
        }}
        th {{
            color: #94a3b8;
            font-weight: 600;
        }}
        tr:hover {{
            background-color: #1e293b55;
        }}
        .badge {{
            display: inline-block;
            padding: 0.25rem 0.5rem;
            border-radius: 9999px;
            font-size: 0.75rem;
            font-weight: 600;
        }}
        .badge-success {{ background-color: #065f46; color: #34d399; }}
        .badge-pending {{ background-color: #78350f; color: #fbbf24; }}
        .badge-failed {{ background-color: #7f1d1d; color: #f87171; }}
        .badge-unmatched {{ background-color: #374151; color: #d1d5db; }}
        .badge-legit {{ background-color: #065f46; color: #34d399; }}
        .badge-fake {{ background-color: #7c2d12; color: #fdba74; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>LyricForge Summary Report</h1>
        <div class="meta">Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</div>
        
        <div class="grid">
            <div class="card"><div class="value">{stats.get('total_songs', 0)}</div><div class="label">Total Songs</div></div>
            <div class="card"><div class="value">{stats.get('total_lyrics', 0)}</div><div class="label">Total Lyrics</div></div>
            <div class="card"><div class="value" style="color: #34d399">{stats.get('embedded', 0)}</div><div class="label">Embedded</div></div>
            <div class="card"><div class="value" style="color: #fbbf24">{stats.get('matched', 0)}</div><div class="label">Matched (Pending)</div></div>
            <div class="card"><div class="value" style="color: #f87171">{stats.get('failed', 0)}</div><div class="label">Failed</div></div>
            <div class="card"><div class="value" style="color: #94a3b8">{stats.get('unmatched', 0)}</div><div class="label">Unmatched</div></div>
        </div>
"""

        if embedded:
            html += """
        <div class="section">
            <h2>Successfully Embedded Songs</h2>
            <table>
                <thead>
                    <tr>
                        <th>Song Title</th>
                        <th>Artist</th>
                        <th>Lyrics File</th>
                        <th>Legitimacy Check</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody>"""
            for s in embedded:
                legit_badge = ""
                if s.get('spectral_cutoff'):
                    if s.get('legit') == 1 or s.get('legit') is True:
                        legit_badge = '<span class="badge badge-legit">Verified Lossless</span>'
                    else:
                        legit_badge = f'<span class="badge badge-fake" title="{s.get("legit_reason", "")}">Upscaled / Fake ⚠️</span>'
                else:
                    legit_badge = '<span class="badge badge-unmatched">Not Checked</span>'

                html += f"""
                    <tr>
                        <td><b>{s.get('title', 'Unknown')}</b></td>
                        <td>{s.get('artist', 'Unknown')}</td>
                        <td>{Path(s.get('lyric_path', '')).name if s.get('lyric_path') else ''}</td>
                        <td>{legit_badge}</td>
                        <td><span class="badge badge-success">Embedded</span></td>
                    </tr>"""
            html += """
                </tbody>
            </table>
        </div>"""

        if failed:
            html += """
        <div class="section">
            <h2>Failed Embedding Attempts</h2>
            <table>
                <thead>
                    <tr>
                        <th>Song Title</th>
                        <th>Artist</th>
                        <th>Error Detail</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody>"""
            for s in failed:
                html += f"""
                    <tr>
                        <td><b>{s.get('title', 'Unknown')}</b></td>
                        <td>{s.get('artist', 'Unknown')}</td>
                        <td style="color: #f87171">{s.get('error', 'Unknown Error')}</td>
                        <td><span class="badge badge-failed">Failed</span></td>
                    </tr>"""
            html += """
                </tbody>
            </table>
        </div>"""

        if unmatched:
            html += """
        <div class="section">
            <h2>Unmatched Songs</h2>
            <table>
                <thead>
                    <tr>
                        <th>File Name</th>
                        <th>Path</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody>"""
            for s in unmatched:
                html += f"""
                    <tr>
                        <td><b>{Path(s['file_path']).name}</b></td>
                        <td>{s['file_path']}</td>
                        <td><span class="badge badge-unmatched">Unmatched</span></td>
                    </tr>"""
            html += """
                </tbody>
            </table>
        </div>"""

        html += """
    </div>
</body>
</html>"""
        os.makedirs(os.path.dirname(os.path.abspath(export_path)), exist_ok=True)
        with open(export_path, 'w', encoding='utf-8') as f:
            f.write(html)
