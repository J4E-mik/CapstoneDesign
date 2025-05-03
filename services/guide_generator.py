def generate_guide_messages(itinerary: dict) -> list[str]:
    messages = []

    for idx, leg in enumerate(itinerary.get("legs", [])):
        mode = leg.get("mode")

        if mode == "WALK":
            steps = leg.get("steps", [])
            section = f"[{idx+1}] [{mode}] 구간"
            
            for step_idx, step in enumerate(steps):
                desc = step.get("description","").strip()
                if desc:
                    step_msg = f"{section} > {step_idx+1}단계: {desc}"
                    messages.append(step_msg)
        
        elif mode == "BUS":
            bus_number = leg.get("route", "알 수 없음")
            start = leg["start"].get("name")
            end = leg["end"].get("name")
            msg = f"{section}\n정류장 '{start}'에서 '{bus_number}'번 버스를 탑승하여 '{end}' 정류장에서 하차합니다."
            messages.append(msg)

        elif mode == "SUBWAY":
            line = leg.get("route", "지하철")
            start = leg["start"].get("name")
            end = leg["end"].get("name")
            msg = f"{section}\n'{start}'역에서 '{line}'을 탑승하여 '{end}'역에서 하차합니다."
            messages.append(msg)

    return messages

def extract_walk_steps(itinerary: dict) -> list[dict]:
    step_list = []

    for leg_idx, leg in enumerate(itinerary.get("legs",[])):
        if leg.get("mode") == "WALK":
            steps = leg.get("steps", [])
            for step_idx, step in enumerate(steps):
                desc = step.get("description","").strip()
                lat = step.get("point",{}).get("lat")
                lon = step.get("point",{}).get("lon")

                if desc and lat and lon:
                    step_list.append({
                        "leg_idx": leg_idx,
                        "step_idx": step_idx,
                        "text":desc,
                        "lat":lat,
                        "lon":lon
                    })
    return step_list