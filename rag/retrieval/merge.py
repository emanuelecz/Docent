def merge(*result_lists, k: int = 60):
    fused = {}

    for results in result_lists:
        for rank, candidate in enumerate(results, start=1):
            number = candidate["github_number"]
            if number not in fused:
                fused[number] = {"candidate": candidate, "score": 0.0}
            fused[number]["score"] += 1.0 / (k + rank)

    ranked = sorted(fused.values(), key=lambda item: item["score"], reverse=True)

    return [
        {**item["candidate"], "rrf_score": item["score"]}
        for item in ranked
    ]
