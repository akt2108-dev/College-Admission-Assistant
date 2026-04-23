import csv
import os
import re
import statistics
from pathlib import Path


DATA_ROOT = Path(__file__).resolve().parent.parent

YEAR_TO_FILE = {
    "2024-25": "hbtu_placement_statistics_2024_25.csv",
    "2025-26": "hbtu_placement_statistics_2025_26.csv",
}


def _candidate_data_roots() -> list[Path]:
    roots: list[Path] = []

    env_root = os.getenv("PLACEMENT_DATA_DIR", "").strip()
    if env_root:
        roots.append(Path(env_root))

    module_backend_dir = Path(__file__).resolve().parent
    module_project_root = module_backend_dir.parent
    cwd = Path.cwd()

    roots.extend([
        DATA_ROOT,
        module_backend_dir,
        module_project_root,
        cwd,
        cwd.parent,
    ])

    deduped: list[Path] = []
    seen = set()
    for root in roots:
        try:
            key = str(root.resolve())
        except Exception:
            key = str(root)
        if key in seen:
            continue
        seen.add(key)
        deduped.append(root)
    return deduped


def _resolve_csv_path(filename: str) -> tuple[Path, list[str]]:
    checked_paths: list[str] = []
    for root in _candidate_data_roots():
        candidate = root / filename
        checked_paths.append(str(candidate))
        if candidate.exists():
            return candidate, checked_paths

    fallback_root = _candidate_data_roots()[0] if _candidate_data_roots() else Path(".")
    return fallback_root / filename, checked_paths


def _total_loaded_records() -> int:
    return sum(len(PLACEMENT_DATA_BY_YEAR.get(year, {}).get("records", [])) for year in AVAILABLE_YEARS)


def get_placement_files_health() -> dict:
    """
    Verify configured placement CSV files are present and readable.
    Intended for startup/readiness checks in production.
    """
    files = {}
    all_ok = True

    for year_label, filename in YEAR_TO_FILE.items():
        file_path, checked_paths = _resolve_csv_path(filename)
        exists = file_path.exists()
        readable = False
        columns = []
        sample_row_present = False
        error = None

        if exists:
            try:
                with file_path.open("r", encoding="utf-8-sig", newline="") as csvfile:
                    reader = csv.DictReader(csvfile)
                    columns = list(reader.fieldnames or [])
                    if columns:
                        sample_row_present = next(reader, None) is not None
                        readable = True
                    else:
                        error = "CSV header is missing or empty"
            except Exception as exc:
                error = str(exc)
        else:
            error = "File not found"

        ok = exists and readable
        all_ok = all_ok and ok

        files[year_label] = {
            "ok": ok,
            "file": str(file_path),
            "checked_paths": checked_paths,
            "exists": exists,
            "readable": readable,
            "columns": columns,
            "sample_row_present": sample_row_present,
            "error": error,
        }

    return {
        "ok": all_ok,
        "data_root": str(DATA_ROOT),
        "files": files,
    }

META_COLUMNS = {
    "row_id",
    "sno",
    "company_name",
    "companyname",
    "company",
    "process",
    "dateofvisit",
    "date_of_visit",
    "ctc_lpa",
    "package_lpa",
    "offers",
    "total",
}

BRANCH_DISPLAY = {
    "cse": "CSE",
    "it": "IT",
    "ee": "EE",
    "et": "ET",
    "me": "ME",
    "ce": "CE",
    "che": "CHE",
    "pl": "PL",
    "ot": "OT",
    "pt": "PT",
    "lt": "LT",
    "be": "BE",
    "ft": "FT",
    "mca": "MCA",
    "mba": "MBA",
    "mtech": "MTech",
    "msc": "MSc",
    "msc_maths": "MSc Maths",
}

BTECH_BRANCHES = {
    "cse", "it", "ee", "et", "me", "ce", "che", "pl", "ot", "pt", "lt", "be", "ft"
}

COURSE_TO_BRANCHES = {
    "B.Tech": BTECH_BRANCHES,
    "MCA": {"mca"},
    "MBA": {"mba"},
    "MTech": {"mtech"},
    "MSc Maths": {"msc_maths", "msc"},
}

BRANCH_QUERY_ALIASES = {
    "cse": ["cse", "computer science", "computer science and engineering"],
    "it": ["it", "information technology"],
    "ee": ["ee", "electrical", "electrical engineering"],
    "et": ["et", "ece", "electronics", "electronics engineering"],
    "me": ["me", "mechanical", "mechanical engineering"],
    "ce": ["ce", "civil", "civil engineering"],
    "che": ["che", "chemical", "chemical engineering"],
    "pl": ["pl", "plastic", "plastic technology"],
    "ot": ["ot", "oil", "oil technology"],
    "pt": ["pt", "paint", "paint technology"],
    "lt": ["lt", "leather", "leather technology"],
    "be": ["be", "biochemical", "bio chemical", "biochemical engineering"],
    "ft": ["ft", "food", "food technology"],
    "mca": ["mca"],
    "mba": ["mba"],
    "mtech": ["mtech", "m tech", "m.tech"],
    "msc_maths": ["msc maths", "msc maths", "m sc maths", "m.sc maths", "msc"],
}


def _normalize_key(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", (name or "").strip().lower()).strip("_")


def _normalize_text(message: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9]+", " ", message.lower())).strip()


def _normalize_branch_column(column_name: str) -> str:
    norm = _normalize_key(column_name)
    if norm in {"msc", "mscmaths", "msc_maths", "msc_mathematics"}:
        return "msc_maths"
    return norm


def _parse_float(value: str):
    if value is None:
        return None
    text = str(value).strip().replace(",", "")
    if not text:
        return None
    try:
        return float(text)
    except ValueError:
        return None


def _parse_int(value: str) -> int:
    parsed = _parse_float(value)
    if parsed is None:
        return 0
    return int(parsed)


def _first_present_value(row: dict, keys: list[str]) -> str:
    normalized = {_normalize_key(k): v for k, v in row.items()}
    for key in keys:
        value = normalized.get(key, "")
        if str(value).strip():
            return str(value).strip()
    return ""


def _load_year_data(year_label: str, filename: str) -> dict:
    file_path, checked_paths = _resolve_csv_path(filename)
    if not file_path.exists():
        return {
            "year": year_label,
            "file": str(file_path),
            "checked_paths": checked_paths,
            "load_error": "File not found",
            "records": [],
            "raw_rows": [],
            "branch_columns": [],
        }

    records = []
    raw_rows = []
    branch_columns_set = set()

    with file_path.open("r", encoding="utf-8-sig", newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if not row:
                continue
            if not any(str(v).strip() for v in row.values()):
                continue

            raw_rows.append(row)

            company_name = _first_present_value(row, ["company_name", "companyname", "company"])
            package_lpa = _parse_float(_first_present_value(row, ["ctc_lpa", "package_lpa"]))
            total_offers = _parse_int(_first_present_value(row, ["offers", "total"]))

            branch_offers = {}
            for column_name, value in row.items():
                norm_col = _normalize_key(column_name)
                if not norm_col or norm_col in META_COLUMNS:
                    continue

                offers_in_col = _parse_int(value)
                if offers_in_col <= 0:
                    continue

                branch_code = _normalize_branch_column(column_name)
                branch_columns_set.add(branch_code)
                branch_offers[branch_code] = branch_offers.get(branch_code, 0) + offers_in_col

            if total_offers <= 0 and branch_offers:
                total_offers = sum(branch_offers.values())

            if not company_name and package_lpa is None and total_offers <= 0 and not branch_offers:
                continue

            records.append(
                {
                    "company": company_name or "Unknown",
                    "package_lpa": package_lpa,
                    "offers": total_offers,
                    "branches": branch_offers,
                    "raw": row,
                }
            )

    return {
        "year": year_label,
        "file": str(file_path),
        "checked_paths": checked_paths,
        "load_error": None,
        "records": records,
        "raw_rows": raw_rows,
        "branch_columns": sorted(branch_columns_set),
    }


def _load_all_data() -> dict:
    data = {}
    for year_label, filename in YEAR_TO_FILE.items():
        data[year_label] = _load_year_data(year_label, filename)
    return data


PLACEMENT_DATA_BY_YEAR = _load_all_data()
AVAILABLE_YEARS = sorted(PLACEMENT_DATA_BY_YEAR.keys())


def _format_lpa(value) -> str:
    if value is None:
        return "-"
    return f"{value:.2f}".rstrip("0").rstrip(".") + " LPA"


def _weighted_packages(records: list[dict], weight_getter) -> list[float]:
    values = []
    for record in records:
        package = record.get("package_lpa")
        if package is None:
            continue
        weight = int(weight_getter(record))
        if weight <= 0:
            continue
        values.extend([package] * weight)
    return values


def _year_summary(year_label: str) -> dict:
    year_data = PLACEMENT_DATA_BY_YEAR.get(year_label, {})
    records = year_data.get("records", [])

    companies_visited = len({r["company"] for r in records if r.get("company")})
    total_offers = sum(int(r.get("offers", 0)) for r in records)

    weighted_packages = _weighted_packages(records, lambda r: r.get("offers", 0))
    average_package = (sum(weighted_packages) / len(weighted_packages)) if weighted_packages else None
    median_package = statistics.median(weighted_packages) if weighted_packages else None

    package_values = [r["package_lpa"] for r in records if r.get("package_lpa") is not None]
    highest_package = max(package_values) if package_values else None

    highest_companies = []
    if highest_package is not None:
        highest_companies = sorted(
            {
                r["company"]
                for r in records
                if r.get("package_lpa") == highest_package and r.get("company")
            }
        )

    return {
        "year": year_label,
        "companies_visited": companies_visited,
        "total_offers": total_offers,
        "average_package": average_package,
        "median_package": median_package,
        "highest_package": highest_package,
        "highest_companies": highest_companies,
    }


def _branch_stats_for_year(year_label: str, branch_code: str) -> dict:
    records = PLACEMENT_DATA_BY_YEAR.get(year_label, {}).get("records", [])

    relevant = [r for r in records if r.get("branches", {}).get(branch_code, 0) > 0]
    offers = sum(r["branches"][branch_code] for r in relevant)
    companies = len({r["company"] for r in relevant if r.get("company")})

    weighted_packages = _weighted_packages(relevant, lambda r: r["branches"].get(branch_code, 0))
    avg_package = (sum(weighted_packages) / len(weighted_packages)) if weighted_packages else None
    median_package = statistics.median(weighted_packages) if weighted_packages else None

    highest_package = None
    highest_companies = []
    package_values = [r["package_lpa"] for r in relevant if r.get("package_lpa") is not None]
    if package_values:
        highest_package = max(package_values)
        highest_companies = sorted(
            {r["company"] for r in relevant if r.get("package_lpa") == highest_package and r.get("company")}
        )

    return {
        "year": year_label,
        "branch": branch_code,
        "offers": offers,
        "companies": companies,
        "average_package": avg_package,
        "median_package": median_package,
        "highest_package": highest_package,
        "highest_companies": highest_companies,
    }


def _course_stats_for_year(year_label: str, course_name: str) -> dict:
    target_branches = COURSE_TO_BRANCHES.get(course_name, set())
    records = PLACEMENT_DATA_BY_YEAR.get(year_label, {}).get("records", [])

    relevant = []
    for record in records:
        offers_in_course = sum(record.get("branches", {}).get(branch, 0) for branch in target_branches)
        if offers_in_course > 0:
            relevant.append((record, offers_in_course))

    offers = sum(offers_in_course for _, offers_in_course in relevant)
    companies = len({record["company"] for record, _ in relevant if record.get("company")})

    weighted_packages = []
    for record, offers_in_course in relevant:
        package = record.get("package_lpa")
        if package is not None:
            weighted_packages.extend([package] * offers_in_course)

    avg_package = (sum(weighted_packages) / len(weighted_packages)) if weighted_packages else None
    median_package = statistics.median(weighted_packages) if weighted_packages else None

    highest_package = None
    highest_companies = []
    package_values = [record["package_lpa"] for record, _ in relevant if record.get("package_lpa") is not None]
    if package_values:
        highest_package = max(package_values)
        highest_companies = sorted(
            {
                record["company"]
                for record, _ in relevant
                if record.get("package_lpa") == highest_package and record.get("company")
            }
        )

    return {
        "year": year_label,
        "course": course_name,
        "offers": offers,
        "companies": companies,
        "average_package": avg_package,
        "median_package": median_package,
        "highest_package": highest_package,
        "highest_companies": highest_companies,
    }


def _extract_year_label(message: str):
    yr_match = re.search(r"\b(20\d{2})\s*[-/]\s*(\d{2})\b", message)
    if yr_match:
        return f"{yr_match.group(1)}-{yr_match.group(2)}"

    for full_year in re.findall(r"\b20\d{2}\b", message):
        year_int = int(full_year)
        candidate = f"{year_int}-{str((year_int + 1) % 100).zfill(2)}"
        if candidate in AVAILABLE_YEARS:
            return candidate

    return None


def _extract_branch_code(message: str):
    norm_msg = _normalize_text(message)
    padded = f" {norm_msg} "

    for branch_code, aliases in BRANCH_QUERY_ALIASES.items():
        for alias in aliases:
            norm_alias = _normalize_text(alias)
            if not norm_alias:
                continue
            if f" {norm_alias} " in padded:
                return branch_code

    return None


def _extract_course_name(message: str, branch_code: str | None):
    message_lc = message.lower()

    if "b.tech" in message_lc or "btech" in message_lc:
        return "B.Tech"
    if "mca" in message_lc:
        return "MCA"
    if "mba" in message_lc:
        return "MBA"
    if "mtech" in message_lc or "m tech" in message_lc or "m.tech" in message_lc:
        return "MTech"
    if any(k in message_lc for k in ["msc", "m.sc", "m sc", "maths"]):
        return "MSc Maths"

    if branch_code in BTECH_BRANCHES:
        return "B.Tech"
    if branch_code == "mca":
        return "MCA"
    if branch_code == "mba":
        return "MBA"
    if branch_code == "mtech":
        return "MTech"
    if branch_code in {"msc", "msc_maths"}:
        return "MSc Maths"

    return None


def detect_placement_intent(user_message: str) -> dict:
    message = user_message.lower()

    placement_cues = [
        "placement", "placements", "package", "ctc", "companies visited", "offers"
    ]
    is_placement = any(cue in message for cue in placement_cues)

    year_label = _extract_year_label(message)
    branch_code = _extract_branch_code(message)
    course_name = _extract_course_name(message, branch_code)

    subintent = "overview"
    if any(k in message for k in ["highest package giving compan", "highest package company", "highest paying company"]):
        subintent = "highest_companies_year_wise"
    elif "companies visited" in message or "visited companies" in message:
        subintent = "companies_visited_year_wise"
    elif "median package" in message:
        subintent = "median_package_year_wise"
    elif any(k in message for k in ["average package", "avg package", "mean package"]):
        subintent = "average_package_year_wise"
    elif any(k in message for k in ["highest package", "max package", "maximum package"]):
        subintent = "highest_package_year_wise"
    elif "course wise" in message or "course-wise" in message:
        subintent = "course_wise"
    elif "branch wise" in message or "branch-wise" in message:
        subintent = "branch_wise"
    elif branch_code is not None and is_placement:
        subintent = "branch_wise"
    elif course_name is not None and is_placement:
        subintent = "course_wise"

    if "placement statistics" in message or "placement stats" in message:
        is_placement = True

    return {
        "is_placement": is_placement,
        "subintent": subintent,
        "year": year_label,
        "branch": branch_code,
        "course": course_name,
    }


def _build_overview_message() -> str:
    summaries = [_year_summary(year) for year in AVAILABLE_YEARS]

    lines = [
        "## HBTU Placement Statistics - Year-wise Overview",
        "",
        "| Year | Companies Visited | Total Offers | Average Package | Median Package | Highest Package |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for s in summaries:
        lines.append(
            f"| {s['year']} | {s['companies_visited']} | {s['total_offers']} | "
            f"{_format_lpa(s['average_package'])} | {_format_lpa(s['median_package'])} | {_format_lpa(s['highest_package'])} |"
        )

    lines.append("")
    lines.append("### Highest Package Giving Companies")
    for s in summaries:
        companies = ", ".join(s["highest_companies"]) if s["highest_companies"] else "-"
        lines.append(f"- {s['year']}: {companies} ({_format_lpa(s['highest_package'])})")

    return "\n".join(lines)


def _build_branch_message(year: str | None, branch_code: str | None) -> str:
    target_years = [year] if year in AVAILABLE_YEARS else AVAILABLE_YEARS

    if branch_code:
        branch_name = BRANCH_DISPLAY.get(branch_code, branch_code.upper())
        lines = [
            f"## Placement Statistics for {branch_name} - Year-wise",
            "",
            "| Year | Offers | Companies | Average Package | Median Package | Highest Package |",
            "|---|---:|---:|---:|---:|---:|",
        ]
        year_stats = []
        for yr in target_years:
            stats = _branch_stats_for_year(yr, branch_code)
            year_stats.append(stats)
            lines.append(
                f"| {yr} | {stats['offers']} | {stats['companies']} | {_format_lpa(stats['average_package'])} | "
                f"{_format_lpa(stats['median_package'])} | {_format_lpa(stats['highest_package'])} |"
            )

        lines.append("")
        lines.append("### Highest Package Giving Companies")
        for stats in year_stats:
            companies = ", ".join(stats["highest_companies"]) if stats["highest_companies"] else "-"
            lines.append(f"- {stats['year']}: {companies} ({_format_lpa(stats['highest_package'])})")
        return "\n".join(lines)

    lines = ["## Branch-wise Placement Statistics"]
    for yr in target_years:
        lines.extend([
            "",
            f"### {yr}",
            "| Branch | Offers | Companies | Average Package | Highest Package |",
            "|---|---:|---:|---:|---:|",
        ])

        branch_stats = []
        for branch in sorted(PLACEMENT_DATA_BY_YEAR.get(yr, {}).get("branch_columns", [])):
            stats = _branch_stats_for_year(yr, branch)
            if stats["offers"] > 0:
                branch_stats.append(stats)

        branch_stats.sort(key=lambda x: x["offers"], reverse=True)

        for stats in branch_stats:
            branch_name = BRANCH_DISPLAY.get(stats["branch"], stats["branch"].upper())
            lines.append(
                f"| {branch_name} | {stats['offers']} | {stats['companies']} | "
                f"{_format_lpa(stats['average_package'])} | {_format_lpa(stats['highest_package'])} |"
            )

    return "\n".join(lines)


def _build_course_message(year: str | None, course_name: str | None) -> str:
    target_years = [year] if year in AVAILABLE_YEARS else AVAILABLE_YEARS

    if course_name in COURSE_TO_BRANCHES:
        lines = [
            f"## Placement Statistics for {course_name} - Year-wise",
            "",
            "| Year | Offers | Companies | Average Package | Median Package | Highest Package |",
            "|---|---:|---:|---:|---:|---:|",
        ]
        summaries = []
        for yr in target_years:
            stats = _course_stats_for_year(yr, course_name)
            summaries.append(stats)
            lines.append(
                f"| {yr} | {stats['offers']} | {stats['companies']} | {_format_lpa(stats['average_package'])} | "
                f"{_format_lpa(stats['median_package'])} | {_format_lpa(stats['highest_package'])} |"
            )

        lines.append("")
        lines.append("### Highest Package Giving Companies")
        for stats in summaries:
            companies = ", ".join(stats["highest_companies"]) if stats["highest_companies"] else "-"
            lines.append(f"- {stats['year']}: {companies} ({_format_lpa(stats['highest_package'])})")
        return "\n".join(lines)

    lines = [
        "## Course-wise Placement Statistics - Year-wise",
        "",
        "| Year | Course | Offers | Companies | Average Package | Median Package | Highest Package |",
        "|---|---|---:|---:|---:|---:|---:|",
    ]

    for yr in target_years:
        for course in COURSE_TO_BRANCHES:
            stats = _course_stats_for_year(yr, course)
            lines.append(
                f"| {yr} | {course} | {stats['offers']} | {stats['companies']} | "
                f"{_format_lpa(stats['average_package'])} | {_format_lpa(stats['median_package'])} | "
                f"{_format_lpa(stats['highest_package'])} |"
            )

    return "\n".join(lines)


def _build_metric_year_wise_message(metric: str) -> str:
    summaries = [_year_summary(year) for year in AVAILABLE_YEARS]

    if metric == "companies_visited_year_wise":
        lines = [
            "## Companies Visited - Year-wise",
            "",
            "| Year | Companies Visited |",
            "|---|---:|",
        ]
        for s in summaries:
            lines.append(f"| {s['year']} | {s['companies_visited']} |")
        return "\n".join(lines)

    if metric == "average_package_year_wise":
        lines = [
            "## Average Package - Year-wise",
            "",
            "| Year | Average Package |",
            "|---|---:|",
        ]
        for s in summaries:
            lines.append(f"| {s['year']} | {_format_lpa(s['average_package'])} |")
        return "\n".join(lines)

    if metric == "median_package_year_wise":
        lines = [
            "## Median Package - Year-wise",
            "",
            "| Year | Median Package |",
            "|---|---:|",
        ]
        for s in summaries:
            lines.append(f"| {s['year']} | {_format_lpa(s['median_package'])} |")
        return "\n".join(lines)

    if metric == "highest_package_year_wise":
        lines = [
            "## Highest Package - Year-wise",
            "",
            "| Year | Highest Package |",
            "|---|---:|",
        ]
        for s in summaries:
            lines.append(f"| {s['year']} | {_format_lpa(s['highest_package'])} |")
        return "\n".join(lines)

    if metric == "highest_companies_year_wise":
        lines = [
            "## Highest Package Giving Companies - Year-wise",
            "",
            "| Year | Highest Package | Companies |",
            "|---|---:|---|",
        ]
        for s in summaries:
            companies = ", ".join(s["highest_companies"]) if s["highest_companies"] else "-"
            lines.append(f"| {s['year']} | {_format_lpa(s['highest_package'])} | {companies} |")
        return "\n".join(lines)

    return _build_overview_message()


def get_placement_response(user_message: str) -> dict:
    if not AVAILABLE_YEARS:
        return {
            "message": "Placement data is currently unavailable.",
            "data": {"subtopic": "placement"},
            "actions": [],
            "suggestions": [],
        }

    if _total_loaded_records() == 0:
        health = get_placement_files_health()
        return {
            "message": (
                "Placement data files are not loaded on the server right now, so accurate statistics "
                "cannot be shown.\n\n"
                "Please verify deployment includes both placement CSV files or set PLACEMENT_DATA_DIR "
                "to the folder containing them.\n\n"
                "Check startup health endpoint: /health/startup\n\n"
                "Source: https://hbtu.ac.in/training-placements/#PlacementStatistics"
            ),
            "data": {
                "subtopic": "placement_data_unavailable",
                "available_years": AVAILABLE_YEARS,
                "file_health": health,
            },
            "actions": [
                {"label": "Placement Overview", "value": "Show placement statistics year-wise"},
                {"label": "Companies Visited", "value": "Show companies visited year-wise"},
                {"label": "Highest Package", "value": "Show highest package year-wise"},
            ],
        }

    detected = detect_placement_intent(user_message)
    subintent = detected["subintent"]

    if subintent == "branch_wise":
        message = _build_branch_message(detected.get("year"), detected.get("branch"))
    elif subintent == "course_wise":
        message = _build_course_message(detected.get("year"), detected.get("course"))
    elif subintent in {
        "companies_visited_year_wise",
        "average_package_year_wise",
        "median_package_year_wise",
        "highest_package_year_wise",
        "highest_companies_year_wise",
    }:
        message = _build_metric_year_wise_message(subintent)
    else:
        message = _build_overview_message()

    message += "\n\nSource: https://hbtu.ac.in/training-placements/#PlacementStatistics"

    return {
        "message": message,
        "data": {
            "subtopic": subintent,
            "year": detected.get("year"),
            "branch": detected.get("branch"),
            "course": detected.get("course"),
            "available_years": AVAILABLE_YEARS,
        },
        "actions": [
            {"label": "Placement Overview", "value": "Show placement statistics year-wise"},
            {"label": "Branch-wise Stats", "value": "Show placement statistics branch-wise"},
            {"label": "Course-wise Stats", "value": "Show placement statistics course-wise"},
            {"label": "Median Package", "value": "Show median package year-wise"},
            {"label": "Highest Package Companies", "value": "Show highest package giving companies year-wise"},
        ],
        # "suggestions": [
        #     "Show placement statistics for 2025-26",
        #     "Show CSE placement statistics year-wise",
        #     "Show placement statistics course-wise",
        #     "Show companies visited year-wise",
        #     "Show average package year-wise",
        # ],
    }
