from statistics import median
from typing import TypedDict


class AlignedSegment(TypedDict):
    start_ms: int
    end_ms: int
    confidence: float
    method: str


def align_syllable_segments(
    *,
    syllable_count: int,
    samples: list[float],
    sample_rate: int,
    duration_ms: int,
    pitch_track: list[dict[str, float | int]],
) -> list[AlignedSegment]:
    if syllable_count <= 0:
        return []
    if duration_ms <= 0:
        duration_ms = max(1, syllable_count * 240)

    energy_track = _energy_track(samples=samples, sample_rate=sample_rate)
    active_start, active_end = _active_region(
        duration_ms=duration_ms,
        energy_track=energy_track,
        pitch_track=pitch_track,
    )
    if active_end <= active_start:
        active_start = 0
        active_end = duration_ms

    if syllable_count == 1:
        return [
            {
                "start_ms": active_start,
                "end_ms": active_end,
                "confidence": _single_segment_confidence(energy_track),
                "method": "energy-vad-single",
            }
        ]

    span = active_end - active_start
    min_segment_ms = max(90, min(240, round(span / syllable_count * 0.45)))
    boundaries = [active_start]
    boundary_confidences: list[float] = []
    for boundary_index in range(1, syllable_count):
        expected_ms = active_start + round(span * boundary_index / syllable_count)
        search_radius = max(80, min(260, round(span / syllable_count * 0.42)))
        lower = max(active_start + min_segment_ms * boundary_index, expected_ms - search_radius)
        upper = min(active_end - min_segment_ms * (syllable_count - boundary_index), expected_ms + search_radius)
        if lower >= upper:
            boundary_ms = expected_ms
            confidence = 0.0
        else:
            boundary_ms, confidence = _find_energy_valley(
                energy_track=energy_track,
                lower_ms=lower,
                upper_ms=upper,
                expected_ms=expected_ms,
            )
        boundary_ms = max(boundaries[-1] + min_segment_ms, min(boundary_ms, active_end - min_segment_ms))
        boundaries.append(boundary_ms)
        boundary_confidences.append(confidence)
    boundaries.append(active_end)

    segments: list[AlignedSegment] = []
    for index in range(syllable_count):
        left_confidence = boundary_confidences[index - 1] if index > 0 else _edge_confidence(energy_track, active_start)
        right_confidence = boundary_confidences[index] if index < len(boundary_confidences) else _edge_confidence(
            energy_track,
            active_end,
        )
        confidence = round(max(0.0, min(1.0, (left_confidence + right_confidence) / 2)), 3)
        segments.append(
            {
                "start_ms": boundaries[index],
                "end_ms": boundaries[index + 1],
                "confidence": confidence,
                "method": "energy-valley-v1",
            }
        )
    return segments


def _energy_track(*, samples: list[float], sample_rate: int, frame_ms: int = 30, hop_ms: int = 15) -> list[dict[str, float | int]]:
    if not samples or sample_rate <= 0:
        return []
    frame_size = max(1, round(sample_rate * frame_ms / 1000))
    hop_size = max(1, round(sample_rate * hop_ms / 1000))
    track: list[dict[str, float | int]] = []
    for start in range(0, max(1, len(samples) - frame_size + 1), hop_size):
        frame = samples[start : start + frame_size]
        if not frame:
            continue
        energy = sum(sample * sample for sample in frame) / len(frame)
        track.append(
            {
                "time_ms": round((start + len(frame) / 2) / sample_rate * 1000),
                "energy": energy,
            }
        )
    return _smooth_energy_track(track)


def _smooth_energy_track(track: list[dict[str, float | int]]) -> list[dict[str, float | int]]:
    if len(track) < 3:
        return track
    smoothed: list[dict[str, float | int]] = []
    for index, item in enumerate(track):
        window = track[max(0, index - 2) : min(len(track), index + 3)]
        smoothed.append(
            {
                "time_ms": item["time_ms"],
                "energy": sum(float(frame["energy"]) for frame in window) / len(window),
            }
        )
    return smoothed


def _active_region(
    *,
    duration_ms: int,
    energy_track: list[dict[str, float | int]],
    pitch_track: list[dict[str, float | int]],
) -> tuple[int, int]:
    if not energy_track and not pitch_track:
        return 0, duration_ms

    energies = [float(item["energy"]) for item in energy_track]
    threshold = _energy_threshold(energies)
    active_times = [int(item["time_ms"]) for item in energy_track if float(item["energy"]) >= threshold]
    active_times.extend(int(item["time_ms"]) for item in pitch_track if float(item["f0_hz"]) > 0)
    if not active_times:
        return 0, duration_ms
    return max(0, min(active_times) - 45), min(duration_ms, max(active_times) + 45)


def _find_energy_valley(
    *,
    energy_track: list[dict[str, float | int]],
    lower_ms: int,
    upper_ms: int,
    expected_ms: int,
) -> tuple[int, float]:
    candidates = [item for item in energy_track if lower_ms <= int(item["time_ms"]) <= upper_ms]
    if not candidates:
        return expected_ms, 0.0

    window_energies = [float(item["energy"]) for item in candidates]
    reference = median(window_energies) if window_energies else 0.0
    time_span = max(1, upper_ms - lower_ms)

    def candidate_cost(item: dict[str, float | int]) -> float:
        energy = float(item["energy"])
        distance_penalty = abs(int(item["time_ms"]) - expected_ms) / time_span * max(reference, 1e-9) * 0.35
        return energy + distance_penalty

    best = min(candidates, key=candidate_cost)
    best_energy = float(best["energy"])
    confidence = 0.0 if reference <= 1e-9 else (reference - best_energy) / reference
    return int(best["time_ms"]), round(max(0.0, min(1.0, confidence)), 3)


def _energy_threshold(energies: list[float]) -> float:
    if not energies:
        return 0.0
    sorted_energies = sorted(energies)
    low = sorted_energies[max(0, round(len(sorted_energies) * 0.2) - 1)]
    high = sorted_energies[min(len(sorted_energies) - 1, round(len(sorted_energies) * 0.8) - 1)]
    return max(low * 1.8, (low + high) * 0.28)


def _edge_confidence(energy_track: list[dict[str, float | int]], edge_ms: int) -> float:
    if not energy_track:
        return 0.0
    energies = [float(item["energy"]) for item in energy_track]
    reference = median(energies) if energies else 0.0
    nearby = [
        float(item["energy"])
        for item in energy_track
        if abs(int(item["time_ms"]) - edge_ms) <= 75
    ]
    if not nearby or reference <= 1e-9:
        return 0.0
    edge_energy = min(nearby)
    return round(max(0.0, min(1.0, (reference - edge_energy) / reference)), 3)


def _single_segment_confidence(energy_track: list[dict[str, float | int]]) -> float:
    if not energy_track:
        return 0.0
    energies = [float(item["energy"]) for item in energy_track]
    threshold = _energy_threshold(energies)
    active = [energy for energy in energies if energy >= threshold]
    return round(len(active) / len(energies), 3) if energies else 0.0
