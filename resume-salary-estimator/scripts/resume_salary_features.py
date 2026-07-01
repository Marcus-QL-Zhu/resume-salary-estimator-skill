#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np
import pandas as pd


FUNCTION_KEYWORDS = {
    "technology": ["engineering", "software", "hardware", "architecture", "algorithm", "data", "cloud", "firmware", "研发", "开发", "架构", "算法", "软件", "硬件", "数据", "云", "系统"],
    "product": ["product", "roadmap", "requirement", "user", "产品", "需求", "用户"],
    "project_delivery": ["project", "delivery", "implementation", "milestone", "项目", "交付", "实施", "里程碑"],
    "business_sales": ["sales", "customer", "market", "commercial", "business development", "销售", "客户", "市场", "商务"],
    "operations_supply": ["operations", "supply chain", "procurement", "logistics", "运营", "供应链", "采购", "物流"],
    "manufacturing_quality": ["manufacturing", "process", "equipment", "quality", "yield", "test", "制造", "工艺", "设备", "质量", "良率", "测试"],
    "management": ["manager", "director", "head", "vp", "general manager", "lead", "管理", "总监", "负责人", "经理", "副总", "总经理", "团队"],
    "finance_legal_hr": ["finance", "legal", "hr", "recruiting", "compliance", "财务", "法务", "人力", "招聘", "合规"],
}

OWNERSHIP_WORDS = ["led", "owned", "built", "launched", "delivered", "scaled", "主导", "负责", "牵头", "独立", "搭建", "上线", "落地", "量产"]
COORDINATION_WORDS = ["support", "assist", "coordinate", "communicate", "align", "track", "支持", "协助", "配合", "协调", "沟通", "对接", "跟进"]
RESPONSIBILITY_WORDS = ["responsible", "duty", "managed", "participated", "负责", "职责", "工作内容", "参与", "管理", "处理", "维护"]
RESULT_WORDS = ["increase", "reduce", "improve", "revenue", "cost", "efficiency", "quality", "latency", "uptime", "提升", "降低", "增长", "节省", "营收", "成本", "效率", "质量", "良率"]
TOOL_WORDS = ["python", "java", "sql", "linux", "docker", "kubernetes", "aws", "azure", "git", "jenkins", "react", "vue", "spark", "pytorch", "tensorflow"]

DEGREE_PATTERNS = {
    "phd": ["phd", "doctor", "doctoral", "博士"],
    "mba": ["mba", "emba", "工商管理硕士"],
    "master": ["master", "msc", "m.s.", "硕士", "研究生"],
    "bachelor": ["bachelor", "bsc", "b.s.", "本科", "学士"],
    "associate": ["associate", "college", "大专", "专科"],
}
OVERSEAS_EDUCATION_WORDS = [
    "university of",
    "institute of technology",
    "college",
    "usa",
    "uk",
    "germany",
    "france",
    "canada",
    "australia",
    "singapore",
    "japan",
    "korea",
    "海外",
    "留学",
    "德国",
    "美国",
    "英国",
    "法国",
    "加拿大",
    "澳大利亚",
    "新加坡",
    "日本",
    "韩国",
]
ELITE_EDUCATION_WORDS = [
    "985",
    "211",
    "double first-class",
    "双一流",
    "ivy league",
    "oxford",
    "cambridge",
    "mit",
    "stanford",
    "harvard",
    "tsinghua",
    "peking university",
    "清华",
    "北大",
]
LANGUAGE_WORDS = ["english", "german", "french", "japanese", "korean", "英语", "德语", "法语", "日语", "韩语"]
EDUCATION_FIELD_KEYWORDS = {
    "engineering": ["engineering", "engineer", "机械", "车辆", "电子", "自动化", "控制", "工程"],
    "computer_science": ["computer science", "software", "计算机", "软件", "信息"],
    "business": ["business", "management", "mba", "工商管理", "管理", "市场营销"],
    "finance": ["finance", "accounting", "economics", "金融", "会计", "经济"],
    "law_hr": ["law", "legal", "human resources", "法律", "法学", "人力资源"],
    "science": ["physics", "chemistry", "math", "statistics", "物理", "化学", "数学", "统计"],
}

DATE_RE = re.compile(
    r"(?P<start_y>20\d{2}|19\d{2})[./-](?P<start_m>\d{1,2})\s*[-–—]\s*"
    r"(?:(?P<end_y>20\d{2}|19\d{2})[./-](?P<end_m>\d{1,2})|(?P<present>present|now|current|至今|现在))"
    r"\s*\((?P<duration>[^)]{1,20})\)",
    flags=re.IGNORECASE,
)


@dataclass
class RoleTenure:
    start: str
    end: str
    duration_months: int | None
    is_current: bool
    snippet: str


def count_terms(text: str, terms: list[str]) -> int:
    text = "" if pd.isna(text) else str(text)
    return sum(len(re.findall(re.escape(term), text, flags=re.IGNORECASE)) for term in terms)


def numeric_result_count(text: str) -> int:
    text = "" if pd.isna(text) else str(text)
    patterns = [
        r"\d+(?:\.\d+)?\s*%",
        r"\d+(?:\.\d+)?\s*(?:x|倍)",
        r"\d+(?:\.\d+)?\s*(?:million|billion|k|m|万|亿)",
    ]
    return sum(len(re.findall(pattern, text, flags=re.IGNORECASE)) for pattern in patterns)


def function_hits(text: str, min_hits_per_family: int = 2) -> tuple[int, str]:
    hits = [family for family, terms in FUNCTION_KEYWORDS.items() if count_terms(text, terms) >= min_hits_per_family]
    return len(hits), "|".join(hits)


def education_features(text: str) -> dict:
    text = "" if pd.isna(text) else str(text)
    degree_order = ["associate", "bachelor", "master", "mba", "phd"]
    ranks = {name: i + 1 for i, name in enumerate(degree_order)}
    hits = [name for name in degree_order if count_terms(text, DEGREE_PATTERNS[name]) > 0]
    highest = max(hits, key=lambda name: ranks[name]) if hits else "unknown"
    fields = [name for name, terms in EDUCATION_FIELD_KEYWORDS.items() if count_terms(text, terms) > 0]
    return {
        "highest_degree_group": highest,
        "highest_degree_rank": ranks.get(highest, 0),
        "has_master_or_above": int(ranks.get(highest, 0) >= ranks["master"]),
        "has_phd": int(highest == "phd"),
        "has_mba": int("mba" in hits),
        "overseas_education_signal": int(count_terms(text, OVERSEAS_EDUCATION_WORDS) > 0),
        "elite_education_signal": int(count_terms(text, ELITE_EDUCATION_WORDS) > 0),
        "international_language_signal": int(count_terms(text, LANGUAGE_WORDS) > 0),
        "education_field_count": len(fields),
        "education_field_groups": "|".join(fields),
    }


def normalize_degree_group(value: str) -> str:
    value = "" if pd.isna(value) else str(value).strip().lower()
    if not value:
        return "unknown"
    if any(token in value for token in ["phd", "doctor", "doctoral", "博士", "doctorate"]):
        return "phd"
    if any(token in value for token in ["mba", "emba", "工商管理硕士"]):
        return "mba"
    if any(token in value for token in ["master", "msc", "m.s.", "硕士", "研究生"]):
        return "master"
    if any(token in value for token in ["bachelor", "bsc", "b.s.", "本科", "学士"]):
        return "bachelor"
    if any(token in value for token in ["associate", "college", "大专", "专科", "college_or_below"]):
        return "associate"
    if value in {"doctor", "master", "mba_emba", "bachelor", "college_or_below", "missing", "unknown"}:
        return {"doctor": "phd", "mba_emba": "mba", "college_or_below": "associate", "missing": "unknown"}.get(value, value)
    return value


def education_features_from_structured_degree(value: str) -> dict:
    highest = normalize_degree_group(value)
    ranks = {"unknown": 0, "associate": 1, "bachelor": 2, "master": 3, "mba": 3, "phd": 4}
    return {
        "highest_degree_group": highest,
        "highest_degree_rank": ranks.get(highest, 0),
        "has_master_or_above": int(ranks.get(highest, 0) >= ranks["master"]),
        "has_phd": int(highest == "phd"),
        "has_mba": int(highest == "mba"),
    }


def month_index(value: str) -> int | None:
    if value == "present":
        return None
    match = re.match(r"(\d{4})\.(\d{2})", value)
    if not match:
        return None
    return int(match.group(1)) * 12 + int(match.group(2))


def months_from_duration(text: str) -> int | None:
    total = 0
    found = False
    for pattern, multiplier in [
        (r"(\d+)\s*(?:years?|yrs?|年)", 12),
        (r"(\d+)\s*(?:months?|mos?|个月|月)", 1),
    ]:
        match = re.search(pattern, str(text), flags=re.IGNORECASE)
        if match:
            total += int(match.group(1)) * multiplier
            found = True
    return total if found and total > 0 else None


def is_near_duplicate(candidate: RoleTenure, existing: list[RoleTenure]) -> bool:
    c_start = month_index(candidate.start)
    c_end = month_index(candidate.end)
    for role in existing:
        r_start = month_index(role.start)
        r_end = month_index(role.end)
        if c_start is None or r_start is None:
            continue
        if candidate.is_current and role.is_current and abs(c_start - r_start) <= 1:
            return True
        if c_end is not None and r_end is not None and abs(c_start - r_start) <= 1 and abs(c_end - r_end) <= 2:
            return True
    return False


def extract_roles(text: str) -> list[RoleTenure]:
    text = "" if pd.isna(text) else str(text)
    lower = text.lower()
    end_candidates = [idx for marker in ["project", "education", "skills", "项目经历", "教育经历", "技能"] if (idx := lower.find(marker.lower())) > 0]
    section = text[: min(end_candidates)] if end_candidates else text
    roles: list[RoleTenure] = []
    for match in DATE_RE.finditer(section):
        present = bool(match.group("present"))
        start = f"{match.group('start_y')}.{int(match.group('start_m')):02d}"
        end = "present" if present else f"{match.group('end_y')}.{int(match.group('end_m')):02d}"
        role = RoleTenure(
            start=start,
            end=end,
            duration_months=months_from_duration(match.group("duration")),
            is_current=present,
            snippet=re.sub(r"\s+", " ", section[max(0, match.start() - 80) : min(len(section), match.end() + 140)]).strip(),
        )
        if not is_near_duplicate(role, roles):
            roles.append(role)
    return roles


def add_features(df: pd.DataFrame, resume_col: str, degree_col: str | None = None) -> pd.DataFrame:
    out = df.copy()
    text = out[resume_col].fillna("").astype(str)
    out["ownership_count"] = text.map(lambda s: count_terms(s, OWNERSHIP_WORDS))
    out["coordination_count"] = text.map(lambda s: count_terms(s, COORDINATION_WORDS))
    out["responsibility_count"] = text.map(lambda s: count_terms(s, RESPONSIBILITY_WORDS))
    out["result_word_count"] = text.map(lambda s: count_terms(s, RESULT_WORDS))
    out["numeric_result_count"] = text.map(numeric_result_count)
    out["tool_count"] = text.map(lambda s: count_terms(s, TOOL_WORDS))
    out["function_family_count"], out["function_families"] = zip(*text.map(function_hits))
    education = pd.DataFrame([education_features(s) for s in text], index=out.index)
    if degree_col and degree_col in out.columns:
        structured = pd.DataFrame([education_features_from_structured_degree(v) for v in out[degree_col]], index=out.index)
        for col in structured.columns:
            education[col] = structured[col]
        education["education_source"] = "structured_degree_column"
    else:
        education["education_source"] = "resume_text"
    out = pd.concat([out, education], axis=1)
    out["education_signal_score"] = (
        out["highest_degree_rank"]
        + out["overseas_education_signal"]
        + out["elite_education_signal"]
        + out["international_language_signal"]
    )

    roles = text.map(extract_roles)
    out["parsed_roles_json"] = roles.map(lambda rs: json.dumps([asdict(r) for r in rs], ensure_ascii=False))
    out["completed_role_count"] = roles.map(lambda rs: sum(1 for r in rs if not r.is_current and r.duration_months is not None))
    out["recent3_completed_short_count"] = roles.map(
        lambda rs: sum(
            1
            for r in [r for r in rs if not r.is_current and r.duration_months is not None][:3]
            if r.duration_months <= 18
        )
    )
    out["recent2_completed_avg_months"] = roles.map(
        lambda rs: np.mean([r.duration_months for r in [r for r in rs if not r.is_current and r.duration_months is not None][:2]])
        if len([r for r in rs if not r.is_current and r.duration_months is not None]) >= 2
        else np.nan
    )

    out["end_to_end_ownership"] = (
        (out["ownership_count"] >= 5) & (out["result_word_count"] >= 2) & (out["numeric_result_count"] >= 1)
    ).astype(int)
    out["career_scatter_risk"] = (out["function_family_count"] >= 5).astype(int)
    out["career_scatter_without_ownership"] = (
        (out["career_scatter_risk"] == 1) & (out["end_to_end_ownership"] == 0)
    ).astype(int)
    out["responsibility_without_results"] = (
        (out["responsibility_count"] >= 8) & (out["result_word_count"] <= 3) & (out["numeric_result_count"] == 0)
    ).astype(int)
    out["weak_ownership_signal"] = (
        (out["coordination_count"] >= 6) & (out["ownership_count"] <= 3) & (out["numeric_result_count"] == 0)
    ).astype(int)
    out["tool_stack_without_result"] = (
        (out["tool_count"] >= 8) & (out["numeric_result_count"] == 0) & (out["result_word_count"] <= 3)
    ).astype(int)
    out["recent_short_tenure_risk"] = (
        (out["recent3_completed_short_count"] >= 2) & (out["recent2_completed_avg_months"] <= 24)
    ).astype(int)
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description="Create generic resume-derived salary estimator features.")
    parser.add_argument("--input", required=True, help="Input CSV path.")
    parser.add_argument("--output", required=True, help="Output CSV path.")
    parser.add_argument("--resume-col", default="resume_text", help="Column containing resume text.")
    parser.add_argument("--degree-col", default=None, help="Optional structured highest-degree/degree-group column. Preferred over resume-text education parsing when present.")
    parser.add_argument("--salary-col", default=None, help="Optional salary column. Kept unchanged; useful for profiling.")
    args = parser.parse_args()

    df = pd.read_csv(args.input)
    if args.resume_col not in df.columns:
        raise SystemExit(f"Missing resume column: {args.resume_col}")
    out = add_features(df, args.resume_col, args.degree_col)
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(args.output, index=False)


if __name__ == "__main__":
    main()
