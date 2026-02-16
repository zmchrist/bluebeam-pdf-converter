"""
Auto-tuning engine for icon rendering parameters.

Uses coordinate descent optimization to adjust icon_config.py
parameters (colors, offsets, sizes) to maximize visual match
against reference deployment PDFs.
"""

import logging
from typing import Callable

from PIL import Image

from scripts.icon_tuner.icon_comparator import (
    compute_similarity,
    render_icon_to_image,
)

logger = logging.getLogger(__name__)


def extract_dominant_circle_color(
    ref_img: Image.Image,
) -> tuple[float, float, float]:
    """
    Extract the dominant circle color from a reference icon image.

    Crops to the circle region, filters out white/black/gray pixels,
    and returns the median color of remaining pixels.

    Args:
        ref_img: Reference icon image

    Returns:
        RGB color tuple in 0-1 range
    """
    w, h = ref_img.size

    # Crop to circle region (inner 70% width, rows 20-85% height)
    crop_x1 = int(w * 0.15)
    crop_y1 = int(h * 0.20)
    crop_x2 = int(w * 0.85)
    crop_y2 = int(h * 0.85)
    cropped = ref_img.crop((crop_x1, crop_y1, crop_x2, crop_y2)).convert("RGB")

    pixels = list(cropped.getdata())

    # Filter out white, black, and near-gray pixels
    colored = []
    for r, g, b in pixels:
        lum = 0.299 * r + 0.587 * g + 0.114 * b
        if lum > 220 or lum < 30:
            continue
        # Check for near-gray (low saturation)
        max_c = max(r, g, b)
        min_c = min(r, g, b)
        if max_c - min_c < 25:
            continue
        colored.append((r, g, b))

    if not colored:
        # Fallback: use all non-white pixels
        colored = [(r, g, b) for r, g, b in pixels
                   if 0.299 * r + 0.587 * g + 0.114 * b < 220]

    if not colored:
        return (0.5, 0.5, 0.5)

    # Compute median
    colored.sort(key=lambda c: c[0])
    med_r = colored[len(colored) // 2][0]
    colored.sort(key=lambda c: c[1])
    med_g = colored[len(colored) // 2][1]
    colored.sort(key=lambda c: c[2])
    med_b = colored[len(colored) // 2][2]

    return (
        round(med_r / 255.0, 4),
        round(med_g / 255.0, 4),
        round(med_b / 255.0, 4),
    )


def _score_with_override(
    subject: str,
    ref_img: Image.Image,
    base_config: dict,
    override: dict,
    metric_fn: Callable[[dict], float] | None = None,
) -> float:
    """Render icon with overrides and score against reference."""
    merged = {**base_config, **override}
    gen_img = render_icon_to_image(subject, config_override=merged)
    if gen_img is None:
        return 0.0

    scores = compute_similarity(ref_img, gen_img)

    if metric_fn:
        return metric_fn(scores)

    return scores["combined"]


def binary_search_parameter(
    subject: str,
    ref_img: Image.Image,
    base_config: dict,
    param_name: str,
    low: float,
    high: float,
    steps: int = 8,
    metric_fn: Callable[[dict], float] | None = None,
) -> float:
    """
    Binary search for optimal value of a single numeric parameter.

    Tests 3 points per iteration (low, mid, high), narrows around best.

    Args:
        subject: Deployment subject name
        ref_img: Reference icon image
        base_config: Current icon config
        param_name: Parameter name to optimize
        low: Lower bound
        high: Upper bound
        steps: Number of iterations
        metric_fn: Optional function to extract score from similarity dict

    Returns:
        Optimal parameter value
    """
    best_val = (low + high) / 2
    best_score = 0.0

    for _ in range(steps):
        mid = (low + high) / 2
        test_points = [low, mid, high]

        for val in test_points:
            override = {param_name: round(val, 4)}
            score = _score_with_override(subject, ref_img, base_config, override, metric_fn)

            if score > best_score:
                best_score = score
                best_val = val

        # Narrow range around best
        range_size = (high - low) / 3
        low = max(low, best_val - range_size)
        high = min(high, best_val + range_size)

    return round(best_val, 4)


def grid_search_offsets(
    subject: str,
    ref_img: Image.Image,
    base_config: dict,
    x_param: str,
    y_param: str,
    x_range: tuple[float, float],
    y_range: tuple[float, float],
    coarse_step: float = 1.0,
    fine_step: float = 0.2,
    metric_fn: Callable[[dict], float] | None = None,
) -> tuple[float, float]:
    """
    Two-pass grid search for optimal x/y offset parameters.

    Coarse grid first, then fine grid around the best coarse point.

    Args:
        subject: Deployment subject name
        ref_img: Reference icon image
        base_config: Current icon config
        x_param: X offset parameter name
        y_param: Y offset parameter name
        x_range: (min, max) for x offset
        y_range: (min, max) for y offset
        coarse_step: Step size for coarse pass
        fine_step: Step size for fine pass
        metric_fn: Optional scoring function

    Returns:
        (best_x, best_y) offset values
    """
    best_x, best_y = 0.0, 0.0
    best_score = 0.0

    # Coarse pass
    x = x_range[0]
    while x <= x_range[1]:
        y = y_range[0]
        while y <= y_range[1]:
            override = {x_param: round(x, 4), y_param: round(y, 4)}
            score = _score_with_override(subject, ref_img, base_config, override, metric_fn)
            if score > best_score:
                best_score = score
                best_x, best_y = x, y
            y += coarse_step
        x += coarse_step

    # Fine pass around best
    fine_x_min = max(x_range[0], best_x - coarse_step)
    fine_x_max = min(x_range[1], best_x + coarse_step)
    fine_y_min = max(y_range[0], best_y - coarse_step)
    fine_y_max = min(y_range[1], best_y + coarse_step)

    x = fine_x_min
    while x <= fine_x_max:
        y = fine_y_min
        while y <= fine_y_max:
            override = {x_param: round(x, 4), y_param: round(y, 4)}
            score = _score_with_override(subject, ref_img, base_config, override, metric_fn)
            if score > best_score:
                best_score = score
                best_x, best_y = x, y
            y += fine_step
        x += fine_step

    return (round(best_x, 4), round(best_y, 4))


def auto_tune_icon(
    subject: str,
    ref_img: Image.Image,
    current_config: dict,
    max_iterations: int = 20,
    threshold: float = 0.85,
) -> tuple[dict, list[dict]]:
    """
    Auto-tune icon rendering parameters to match reference.

    Optimization phases:
    A. Extract circle color directly
    B. Binary search img_scale_ratio
    C. Grid search img_x/y_offset
    D. Grid search brand/model x/y offsets
    E. Step search font sizes

    Args:
        subject: Deployment subject name
        ref_img: Reference icon image
        current_config: Current icon configuration
        max_iterations: Max optimization iterations (unused, kept for API compat)
        threshold: Target combined score (stop early if reached)

    Returns:
        (proposed_overrides, iteration_history)
    """
    proposed: dict = {}
    history: list[dict] = []

    # Get baseline score
    gen_img = render_icon_to_image(subject)
    if gen_img is None:
        logger.warning(f"Cannot render {subject}, skipping tune")
        return proposed, history

    baseline = compute_similarity(ref_img, gen_img)
    history.append({"phase": "baseline", "score": baseline["combined"], "params": {}})
    logger.info(f"{subject}: baseline combined={baseline['combined']:.3f}")

    if baseline["combined"] >= threshold:
        logger.info(f"{subject}: already above threshold {threshold}")
        return proposed, history

    # Phase A: Extract circle color
    color = extract_dominant_circle_color(ref_img)
    proposed["circle_color"] = color
    logger.info(f"{subject}: extracted color={color}")

    gen_img = render_icon_to_image(subject, config_override=proposed)
    if gen_img:
        score_a = compute_similarity(ref_img, gen_img)
        history.append({"phase": "color", "score": score_a["combined"], "params": {"circle_color": color}})
        logger.info(f"{subject}: after color -> combined={score_a['combined']:.3f}")

        if score_a["combined"] >= threshold:
            return proposed, history

    # Phase B: Binary search img_scale_ratio
    best_scale = binary_search_parameter(
        subject, ref_img, proposed, "img_scale_ratio", 0.3, 2.0, steps=6
    )
    proposed["img_scale_ratio"] = best_scale

    gen_img = render_icon_to_image(subject, config_override=proposed)
    if gen_img:
        score_b = compute_similarity(ref_img, gen_img)
        history.append({"phase": "scale", "score": score_b["combined"], "params": {"img_scale_ratio": best_scale}})
        logger.info(f"{subject}: after scale={best_scale} -> combined={score_b['combined']:.3f}")

        if score_b["combined"] >= threshold:
            return proposed, history

    # Phase C: Grid search img_x/y_offset
    best_ix, best_iy = grid_search_offsets(
        subject, ref_img, proposed,
        "img_x_offset", "img_y_offset",
        (-2.0, 2.0), (-2.0, 2.0),
        coarse_step=1.0, fine_step=0.4,
    )
    if best_ix != 0.0:
        proposed["img_x_offset"] = best_ix
    if best_iy != 0.0:
        proposed["img_y_offset"] = best_iy

    gen_img = render_icon_to_image(subject, config_override=proposed)
    if gen_img:
        score_c = compute_similarity(ref_img, gen_img)
        history.append({
            "phase": "img_offset",
            "score": score_c["combined"],
            "params": {"img_x_offset": best_ix, "img_y_offset": best_iy},
        })
        logger.info(f"{subject}: after img_offset=({best_ix},{best_iy}) -> combined={score_c['combined']:.3f}")

        if score_c["combined"] >= threshold:
            return proposed, history

    # Phase D: Grid search brand/model text offsets
    best_bx, best_by = grid_search_offsets(
        subject, ref_img, proposed,
        "brand_x_offset", "brand_y_offset",
        (-2.0, 2.0), (-5.0, 0.0),
        coarse_step=1.0, fine_step=0.4,
    )
    proposed["brand_x_offset"] = best_bx
    proposed["brand_y_offset"] = best_by

    best_mx, best_my = grid_search_offsets(
        subject, ref_img, proposed,
        "model_x_offset", "model_y_offset",
        (-2.0, 2.0), (0.0, 5.0),
        coarse_step=1.0, fine_step=0.4,
    )
    proposed["model_x_offset"] = best_mx
    proposed["model_y_offset"] = best_my

    gen_img = render_icon_to_image(subject, config_override=proposed)
    if gen_img:
        score_d = compute_similarity(ref_img, gen_img)
        history.append({
            "phase": "text_offsets",
            "score": score_d["combined"],
            "params": {
                "brand_x_offset": best_bx, "brand_y_offset": best_by,
                "model_x_offset": best_mx, "model_y_offset": best_my,
            },
        })
        logger.info(f"{subject}: after text_offsets -> combined={score_d['combined']:.3f}")

        if score_d["combined"] >= threshold:
            return proposed, history

    # Phase E: Step search font sizes
    best_brand_fs = binary_search_parameter(
        subject, ref_img, proposed, "brand_font_size", 0.4, 4.0, steps=6
    )
    proposed["brand_font_size"] = best_brand_fs

    best_model_fs = binary_search_parameter(
        subject, ref_img, proposed, "model_font_size", 0.4, 4.0, steps=6
    )
    proposed["model_font_size"] = best_model_fs

    best_id_fs = binary_search_parameter(
        subject, ref_img, proposed, "id_font_size", 1.0, 4.0, steps=5
    )
    proposed["id_font_size"] = best_id_fs

    gen_img = render_icon_to_image(subject, config_override=proposed)
    if gen_img:
        score_e = compute_similarity(ref_img, gen_img)
        history.append({
            "phase": "font_sizes",
            "score": score_e["combined"],
            "params": {
                "brand_font_size": best_brand_fs,
                "model_font_size": best_model_fs,
                "id_font_size": best_id_fs,
            },
        })
        logger.info(f"{subject}: after font_sizes -> combined={score_e['combined']:.3f}")

        if score_e["combined"] >= threshold:
            return proposed, history

    # Phase F: Structural parameters (id_box, border)
    best_id_box_h = binary_search_parameter(
        subject, ref_img, proposed, "id_box_height", 2.0, 6.0, steps=5
    )
    proposed["id_box_height"] = best_id_box_h

    best_id_box_wr = binary_search_parameter(
        subject, ref_img, proposed, "id_box_width_ratio", 0.4, 0.8, steps=5
    )
    proposed["id_box_width_ratio"] = best_id_box_wr

    best_border_w = binary_search_parameter(
        subject, ref_img, proposed, "circle_border_width", 0.3, 2.5, steps=5
    )
    proposed["circle_border_width"] = best_border_w

    best_id_border_w = binary_search_parameter(
        subject, ref_img, proposed, "id_box_border_width", 0.3, 2.0, steps=5
    )
    proposed["id_box_border_width"] = best_id_border_w

    gen_img = render_icon_to_image(subject, config_override=proposed)
    if gen_img:
        score_f = compute_similarity(ref_img, gen_img)
        history.append({
            "phase": "structural",
            "score": score_f["combined"],
            "params": {
                "id_box_height": best_id_box_h,
                "id_box_width_ratio": best_id_box_wr,
                "circle_border_width": best_border_w,
                "id_box_border_width": best_id_border_w,
            },
        })
        logger.info(f"{subject}: after structural -> combined={score_f['combined']:.3f}")

    return proposed, history


def generate_proposed_config(results: dict[str, tuple[dict, list[dict]]]) -> str:
    """
    Generate Python source code for proposed ICON_OVERRIDES.

    Args:
        results: Dict mapping subject -> (proposed_overrides, history)

    Returns:
        Formatted Python source code string
    """
    lines = [
        '"""',
        "Proposed icon config overrides generated by auto-tuner.",
        "",
        "Review these values and apply to ICON_OVERRIDES in icon_config.py",
        '"""',
        "",
        "PROPOSED_OVERRIDES = {",
    ]

    for subject in sorted(results.keys()):
        proposed, history = results[subject]
        if not proposed:
            continue

        # Get score improvement
        baseline = history[0]["score"] if history else 0
        final = history[-1]["score"] if history else 0

        lines.append(f'    "{subject}": {{')
        lines.append(f"        # Score: {baseline:.3f} -> {final:.3f}")

        for key, value in sorted(proposed.items()):
            if isinstance(value, tuple):
                formatted = f"({value[0]:.4f}, {value[1]:.4f}, {value[2]:.4f})"
                lines.append(f'        "{key}": {formatted},')
            elif isinstance(value, float):
                lines.append(f'        "{key}": {value:.4f},')
            else:
                lines.append(f'        "{key}": {value!r},')

        lines.append("    },")

    lines.append("}")
    lines.append("")

    return "\n".join(lines)
