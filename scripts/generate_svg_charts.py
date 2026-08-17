import json
import os
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(SCRIPT_DIR)
JSON_PATH = os.path.join(REPO_ROOT, "pypi_downloads.json")

colors = {
    "openinference": "#3182bd",  # blue
    "openllmetry": "#e6550d",    # orange
    "opentelemetry": "#31a354",  # green (combined CNCF)
    "python-contrib": "#74c476", # light green
    "python-genai": "#de2d26"     # red
}

def escape_xml(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def format_val(val):
    if val >= 1000000:
        return f"{val/1000000:.2f}M"
    elif val >= 1000:
        return f"{val/1000:.1f}k"
    else:
        return str(val)

def generate_grouped_bar_chart(reports):
    # Groups: target libraries
    libraries = ["google-genai", "openai-agents", "openai", "langchain", "anthropic"]
    sources = ["openinference", "openllmetry", "opentelemetry"]
    
    # Extract downloads
    data = {}
    for lib in libraries:
        data[lib] = {src: 0 for src in sources}
        if lib in reports:
            for pkg in reports[lib]:
                src = pkg["source"]
                if src in ["python-genai", "python-contrib"]:
                    data[lib]["opentelemetry"] += pkg["downloads_last_month"]
                elif src in data[lib]:
                    data[lib][src] += pkg["downloads_last_month"]

    # Chart specs
    width = 800
    height = 500
    padding_left = 80
    padding_right = 150
    padding_top = 60
    padding_bottom = 90
    
    plot_width = width - padding_left - padding_right
    plot_height = height - padding_top - padding_bottom
    
    # Use 7M as max Y scale to leave space for labels above the tallest bar (5.47M)
    max_y = 7000000
    
    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="100%" height="100%" style="background-color: #ffffff; font-family: -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Helvetica, Arial, sans-serif;">'
    ]
    
    svg.append(f'<text x="{width/2}" y="30" text-anchor="middle" font-size="18" font-weight="bold" fill="#333">Downloads Last Month by Target Library &amp; Source</text>')
    
    # Grid lines & Y-axis labels
    for i in range(8):
        y_val = i * 1000000
        y_pos = padding_top + plot_height - (y_val / max_y * plot_height)
        label = f"{y_val/1000000:.0f}M" if y_val > 0 else "0"
        svg.append(f'<line x1="{padding_left}" y1="{y_pos}" x2="{padding_left + plot_width}" y2="{y_pos}" stroke="#e0e0e0" stroke-width="1" />')
        svg.append(f'<text x="{padding_left - 10}" y="{y_pos + 4}" text-anchor="end" font-size="12" fill="#666">{label}</text>')
        
    num_groups = len(libraries)
    group_width = plot_width / num_groups
    bar_gap = 2
    num_bars = len(sources)
    bar_width = (group_width * 0.7) / num_bars
    
    for g_idx, lib in enumerate(libraries):
        group_center = padding_left + (g_idx * group_width) + (group_width / 2)
        group_start = group_center - ((num_bars * bar_width + (num_bars - 1) * bar_gap) / 2)
        
        y_label = padding_top + plot_height + 20
        svg.append(f'<text x="{group_center + 10}" y="{y_label}" transform="rotate(-25 {group_center + 10} {y_label})" text-anchor="end" font-size="11" font-weight="600" fill="#333">{escape_xml(lib)}</text>')
        
        for b_idx, src in enumerate(sources):
            val = data[lib][src]
            bar_height = (val / max_y) * plot_height
            x_pos = group_start + b_idx * (bar_width + bar_gap)
            y_pos = padding_top + plot_height - bar_height
            
            if val > 0:
                svg.append(f'<rect x="{x_pos}" y="{y_pos}" width="{bar_width}" height="{bar_height}" fill="{colors[src]}" rx="2" />')
                # Value label (rotated -45 degrees)
                x_text = x_pos + bar_width / 2
                y_text = y_pos - 4
                svg.append(f'<text x="{x_text}" y="{y_text}" transform="rotate(-45 {x_text} {y_text})" text-anchor="start" font-size="8.5" font-weight="bold" fill="#555">{format_val(val)}</text>')
                svg.append(f'<title>{src}: {val:,}</title>')
                
    # Legend
    legend_x = width - padding_right + 20
    for idx, src in enumerate(sources):
        legend_y = padding_top + idx * 30
        svg.append(f'<rect x="{legend_x}" y="{legend_y}" width="18" height="18" fill="{colors[src]}" rx="3" />')
        svg.append(f'<text x="{legend_x + 25}" y="{legend_y + 14}" font-size="13" fill="#333">{escape_xml(src)}</text>')
        
    svg.append(f'<line x1="{padding_left}" y1="{padding_top}" x2="{padding_left}" y2="{padding_top + plot_height}" stroke="#888" stroke-width="1.5" />')
    svg.append(f'<line x1="{padding_left}" y1="{padding_top + plot_height}" x2="{padding_left + plot_width}" y2="{padding_top + plot_height}" stroke="#888" stroke-width="1.5" />')
    
    svg.append('</svg>')
    return "\n".join(svg)

def generate_contrib_vs_genai_chart(reports):
    libraries = ["openai-agents", "openai"]
    sources = ["python-contrib", "python-genai"]
    
    # Extract downloads
    data = {}
    for lib in libraries:
        data[lib] = {src: 0 for src in sources}
        if lib in reports:
            for pkg in reports[lib]:
                src = pkg["source"]
                if src in data[lib]:
                    data[lib][src] += pkg["downloads_last_month"]

    # Chart specs
    width = 800
    height = 420
    padding_left = 80
    padding_right = 150
    padding_top = 50
    padding_bottom = 60
    
    plot_width = width - padding_left - padding_right
    plot_height = height - padding_top - padding_bottom
    
    # Max value is openai-agents contrib (2.85M). Let's use 3.5M as max Y scale to leave space for labels.
    max_y = 3500000
    
    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="100%" height="100%" style="background-color: #ffffff; font-family: -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Helvetica, Arial, sans-serif;">'
    ]
    
    svg.append(f'<text x="{width/2}" y="30" text-anchor="middle" font-size="18" font-weight="bold" fill="#333">OTel Contrib vs GenAI</text>')
    
    # Grid lines & Y-axis labels
    for i in range(5):
        y_val = i * 1000000
        y_pos = padding_top + plot_height - (y_val / max_y * plot_height)
        label = f"{y_val/1000000:.1f}M" if y_val > 0 else "0"
        svg.append(f'<line x1="{padding_left}" y1="{y_pos}" x2="{padding_left + plot_width}" y2="{y_pos}" stroke="#e0e0e0" stroke-width="1" />')
        svg.append(f'<text x="{padding_left - 10}" y="{y_pos + 4}" text-anchor="end" font-size="12" fill="#666">{label}</text>')
        
    num_groups = len(libraries)
    group_width = plot_width / num_groups
    bar_gap = 4
    num_bars = len(sources)
    bar_width = (group_width * 0.5) / num_bars
    
    for g_idx, lib in enumerate(libraries):
        group_center = padding_left + (g_idx * group_width) + (group_width / 2)
        group_start = group_center - ((num_bars * bar_width + (num_bars - 1) * bar_gap) / 2)
        
        svg.append(f'<text x="{group_center}" y="{padding_top + plot_height + 25}" text-anchor="middle" font-size="13" font-weight="600" fill="#333">{escape_xml(lib)}</text>')
        
        for b_idx, src in enumerate(sources):
            val = data[lib][src]
            bar_height = (val / max_y) * plot_height
            x_pos = group_start + b_idx * (bar_width + bar_gap)
            y_pos = padding_top + plot_height - bar_height
            
            if val > 0:
                svg.append(f'<rect x="{x_pos}" y="{y_pos}" width="{bar_width}" height="{bar_height}" fill="{colors[src]}" rx="2" />')
                # Value label (horizontal, centered on top of bar)
                x_text = x_pos + bar_width / 2
                y_text = y_pos - 6
                svg.append(f'<text x="{x_text}" y="{y_text}" text-anchor="middle" font-size="11" font-weight="bold" fill="#444">{format_val(val)}</text>')
                svg.append(f'<title>{src}: {val:,}</title>')
                
    # Legend
    legend_x = width - padding_right + 20
    for idx, src in enumerate(sources):
        legend_y = padding_top + idx * 30
        svg.append(f'<rect x="{legend_x}" y="{legend_y}" width="18" height="18" fill="{colors[src]}" rx="3" />')
        svg.append(f'<text x="{legend_x + 25}" y="{legend_y + 14}" font-size="13" fill="#333">{escape_xml(src)}</text>')
        
    svg.append(f'<line x1="{padding_left}" y1="{padding_top}" x2="{padding_left}" y2="{padding_top + plot_height}" stroke="#888" stroke-width="1.5" />')
    svg.append(f'<line x1="{padding_left}" y1="{padding_top + plot_height}" x2="{padding_left + plot_width}" y2="{padding_top + plot_height}" stroke="#888" stroke-width="1.5" />')
    
    svg.append('</svg>')
    return "\n".join(svg)

def generate_stacked_area_chart(json_data):
    sources = ["openllmetry", "opentelemetry", "openinference"]
    
    # Calculate downloads for each snapshot
    data_by_date = []
    max_total = 0
    
    for entry in json_data:
        date_collected = entry.get("date_collected", "")
        reports = entry.get("reports", {})
        downloads = {src: 0 for src in sources}
        for lib, pkgs in reports.items():
            if lib == "util":
                continue
            for pkg in pkgs:
                src = pkg["source"]
                val = pkg["downloads_last_month"]
                if src in ["python-genai", "python-contrib"]:
                    downloads["opentelemetry"] += val
                elif src in downloads:
                    downloads[src] += val
        total = sum(downloads.values())
        if total > max_total:
            max_total = total
        data_by_date.append({
            "date": date_collected,
            "downloads": downloads,
            "total": total
        })
        
    width = 800
    height = 450
    padding_left = 80
    padding_right = 200
    padding_top = 60
    padding_bottom = 60
    
    plot_width = width - padding_left - padding_right
    plot_height = height - padding_top - padding_bottom
    
    # Round max_total up to next 5M
    max_y = max(40000000, ((max_total // 5000000) + 1) * 5000000)
    
    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="100%" height="100%" style="background-color: #ffffff; font-family: -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Helvetica, Arial, sans-serif;">'
    ]
    
    svg.append(f'<text x="{width/2}" y="30" text-anchor="middle" font-size="18" font-weight="bold" fill="#333">Adoption Growth Over Time</text>')
    
    # Grid lines & Y-axis labels
    num_grid_lines = 6
    for i in range(num_grid_lines):
        y_val = i * (max_y / (num_grid_lines - 1))
        y_pos = padding_top + plot_height - (y_val / max_y * plot_height)
        label = f"{y_val/1000000:.0f}M" if y_val > 0 else "0"
        svg.append(f'<line x1="{padding_left}" y1="{y_pos}" x2="{padding_left + plot_width}" y2="{y_pos}" stroke="#e0e0e0" stroke-width="1" />')
        svg.append(f'<text x="{padding_left - 10}" y="{y_pos + 4}" text-anchor="end" font-size="12" fill="#666">{label}</text>')
        
    num_points = len(data_by_date)
    y_base = padding_top + plot_height
    
    if num_points == 1:
        # Single point vertical column layout
        pt = data_by_date[0]
        x_pos = padding_left + plot_width / 2
        bar_width = 50
        x_start = x_pos - bar_width / 2
        
        h_llmetry = (pt["downloads"]["openllmetry"] / max_y) * plot_height
        y_llmetry = y_base - h_llmetry
        svg.append(f'<rect x="{x_start}" y="{y_llmetry}" width="{bar_width}" height="{h_llmetry}" fill="{colors["openllmetry"]}" rx="2" />')
        
        h_otel = (pt["downloads"]["opentelemetry"] / max_y) * plot_height
        y_otel = y_llmetry - h_otel
        svg.append(f'<rect x="{x_start}" y="{y_otel}" width="{bar_width}" height="{h_otel}" fill="{colors["opentelemetry"]}" rx="2" />')
        
        h_inf = (pt["downloads"]["openinference"] / max_y) * plot_height
        y_inf = y_otel - h_inf
        svg.append(f'<rect x="{x_start}" y="{y_inf}" width="{bar_width}" height="{h_inf}" fill="{colors["openinference"]}" rx="2" />')
        
        label_x = x_pos + bar_width / 2 + 12
        for src, y_seg, h_seg in [
            ("openinference", y_inf, h_inf),
            ("opentelemetry", y_otel, h_otel),
            ("openllmetry", y_llmetry, h_llmetry)
        ]:
            y_mid = y_seg + h_seg / 2
            pct = (pt["downloads"][src] / pt["total"] * 100) if pt["total"] > 0 else 0
            svg.append(f'<line x1="{x_pos + bar_width/2}" y1="{y_mid}" x2="{label_x - 3}" y2="{y_mid}" stroke="#777" stroke-dasharray="2,2" stroke-width="1" />')
            svg.append(f'<text x="{label_x}" y="{y_mid + 4}" font-size="11" font-weight="bold" fill="#333">{src}: {format_val(pt["downloads"][src])} ({pct:.1f}%)</text>')
            
        try:
            date_label = datetime.strptime(pt["date"], "%Y-%m-%d").strftime("%b %d, %Y")
        except Exception:
            date_label = pt["date"]
        svg.append(f'<line x1="{x_pos}" y1="{y_base}" x2="{x_pos}" y2="{y_base + 6}" stroke="#888" stroke-width="1.5" />')
        svg.append(f'<text x="{x_pos}" y="{y_base + 22}" text-anchor="middle" font-size="11" font-weight="bold" fill="#333">{date_label}</text>')
    else:
        # Multi-point stacked area
        x_coords = [padding_left + i * (plot_width / (num_points - 1)) for i in range(num_points)]
        stacked_baselines = [[0]*num_points for _ in range(len(sources) + 1)]
        for p_idx, pt in enumerate(data_by_date):
            current_sum = 0
            for s_idx, src in enumerate(sources):
                current_sum += pt["downloads"][src]
                stacked_baselines[s_idx + 1][p_idx] = current_sum
                
        for s_idx in range(len(sources)):
            src = sources[s_idx]
            points = []
            for p_idx in range(num_points):
                x = x_coords[p_idx]
                y = y_base - (stacked_baselines[s_idx + 1][p_idx] / max_y * plot_height)
                points.append(f"{x},{y}")
            for p_idx in range(num_points - 1, -1, -1):
                x = x_coords[p_idx]
                y = y_base - (stacked_baselines[s_idx][p_idx] / max_y * plot_height)
                points.append(f"{x},{y}")
            points_str = " ".join(points)
            svg.append(f'<polygon points="{points_str}" fill="{colors[src]}" opacity="0.85" />')
            
        for p_idx, pt in enumerate(data_by_date):
            x = x_coords[p_idx]
            svg.append(f'<line x1="{x}" y1="{y_base}" x2="{x}" y2="{y_base + 6}" stroke="#888" stroke-width="1.5" />')
            try:
                date_label = datetime.strptime(pt["date"], "%Y-%m-%d").strftime("%b %d")
            except Exception:
                date_label = pt["date"]
            svg.append(f'<text x="{x}" y="{y_base + 22}" text-anchor="middle" font-size="11" font-weight="bold" fill="#333">{date_label}</text>')
            
        # Legend for multi-point
        latest_pt = data_by_date[-1]
        legend_x = width - padding_right + 20
        for idx, src in enumerate(reversed(sources)):
            legend_y = padding_top + idx * 35
            latest_val = latest_pt["downloads"][src]
            latest_pct = (latest_val / latest_pt["total"] * 100) if latest_pt["total"] > 0 else 0
            svg.append(f'<rect x="{legend_x}" y="{legend_y}" width="18" height="18" fill="{colors[src]}" rx="3" />')
            svg.append(f'<text x="{legend_x + 25}" y="{legend_y + 14}" font-size="12" fill="#333">{escape_xml(src)}</text>')
            svg.append(f'<text x="{legend_x + 25}" y="{legend_y + 28}" font-size="10.5" fill="#666">{latest_pct:.1f}% ({format_val(latest_val)})</text>')

    svg.append(f'<line x1="{padding_left}" y1="{padding_top}" x2="{padding_left}" y2="{y_base}" stroke="#888" stroke-width="1.5" />')
    svg.append(f'<line x1="{padding_left}" y1="{y_base}" x2="{padding_left + plot_width}" y2="{y_base}" stroke="#888" stroke-width="1.5" />')
    svg.append('</svg>')
    return "\n".join(svg)

def main():
    # Load JSON data
    with open(JSON_PATH, "r") as f:
        json_data = json.load(f)
        
    latest_entry = json_data[-1]
    latest_report = latest_entry["reports"]
    date_collected = latest_entry["date_collected"]
    
    # Generate SVGs
    grouped_bar_svg = generate_grouped_bar_chart(latest_report)
    contrib_vs_genai_svg = generate_contrib_vs_genai_chart(latest_report)
    stacked_area_svg = generate_stacked_area_chart(json_data)
    
    # Save SVGs to workspace directory
    compare_adoption_path = os.path.join(REPO_ROOT, "compare_adoption_across_sources.svg")
    contrib_vs_genai_path = os.path.join(REPO_ROOT, "otel_contrib_vs_genai.svg")
    growth_path = os.path.join(REPO_ROOT, "adoption_growth_over_time.svg")
    
    with open(compare_adoption_path, "w") as f:
        f.write(grouped_bar_svg)
        
    with open(contrib_vs_genai_path, "w") as f:
        f.write(contrib_vs_genai_svg)
        
    with open(growth_path, "w") as f:
        f.write(stacked_area_svg)
        
    # Write adoption_charts.md artifact
    md_content = f"""# OpenTelemetry GenAI Instrumentation Adoption Dashboard

This dashboard visualizes the PyPI download statistics for the Generative AI instrumentation packages across different repository sources:
- `opentelemetry` (Official CNCF packages, combining `python-genai` and `python-contrib`)
- `openinference` (OpenInference packages)
- `openllmetry` (Traceloop / OpenLLMetry packages)

---

## 1. Adoption Growth Over Time

This chart shows the total aggregate monthly downloads for each package source.
> [!NOTE]
> Currently displays a single vertical stacked line representing the actual compiled data point for {datetime.strptime(date_collected, "%Y-%m-%d").strftime("%B %Y")}.

![Adoption Growth Over Time](./adoption_growth_over_time.svg)

---

## 2. Compare Adoption Across Sources

This chart compares the downloads last month for each target library across all available instrumentation package sources.

![Compare Adoption Across Sources](./compare_adoption_across_sources.svg)

---

## 3. OTel Contrib vs GenAI

This chart compares the downloads last month for the legacy `python-contrib` packages against the new `python-genai` packages.
> [!NOTE]
> This highlights the shift in adoption from legacy packages (e.g., in `python-contrib`) to the new, GenAI-specific packages in this repository (`python-genai`).

![OTel Contrib vs GenAI](./otel_contrib_vs_genai.svg)

---

*Charts generated on: {datetime.now().strftime("%Y-%m-%d")}*
"""
    
    md_path = os.path.join(REPO_ROOT, "adoption_charts.md")
    with open(md_path, "w") as f:
        f.write(md_content)
        
    print("Success: Generated SVGs and Markdown artifact")

if __name__ == "__main__":
    main()
