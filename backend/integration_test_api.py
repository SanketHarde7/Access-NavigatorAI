"""
Access Navigator AI — Backend Test Suite
==========================================
Comprehensive test cases covering all API endpoints:
  1. Health check
  2. Stadium listing
  3. Zone fetching (all stadiums)
  4. Coordinate fetching
  5. Graph fetching
  6. Route calculation
  7. Same-origin route (edge case)
  8. Invalid stadium (404)
  9. Demo scenarios
  10. Caption processing
  11. Chat endpoint
  12. Predictions
  13. Analytics
  14. Batch zone update
  15. Announcements
"""
import requests
import json
import sys
import time

BASE = "http://localhost:8000"
PASS = 0
FAIL = 0
TOTAL = 0


def test(name, fn):
    """Run a single test and track pass/fail."""
    global PASS, FAIL, TOTAL
    TOTAL += 1
    try:
        result = fn()
        if result:
            PASS += 1
            print(f"  ✅ {name}")
        else:
            FAIL += 1
            print(f"  ❌ {name} — returned falsy")
    except Exception as e:
        FAIL += 1
        print(f"  ❌ {name} — {e}")


def run_all():
    global PASS, FAIL, TOTAL

    print("\n" + "=" * 60)
    print("  ACCESS NAVIGATOR AI — TEST SUITE")
    print("=" * 60)

    # --- 1. Health Check ---
    print("\n📡 Health Check")
    def t_health():
        r = requests.get(f"{BASE}/api/health", timeout=5)
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "ok"
        assert data["version"] == "2.0.0"
        assert "features" in data
        assert data["stadiums_loaded"] >= 3
        return True
    test("GET /api/health", t_health)

    # --- 2. Stadium Listing ---
    print("\n🏟️  Stadiums")
    def t_stadiums():
        r = requests.get(f"{BASE}/api/stadiums", timeout=5)
        assert r.status_code == 200
        data = r.json()
        ids = [s["stadium_id"] for s in data["stadiums"]]
        assert "metlife" in ids
        assert "sofi" in ids
        assert "azteca" in ids
        return True
    test("GET /api/stadiums", t_stadiums)

    def t_stadium_detail():
        r = requests.get(f"{BASE}/api/stadiums/metlife", timeout=5)
        assert r.status_code == 200
        data = r.json()
        assert data["name"] == "MetLife Stadium"
        assert data["zone_count"] > 0
        return True
    test("GET /api/stadiums/metlife", t_stadium_detail)

    # --- 3. Zones (all stadiums) ---
    print("\n📍 Zones")
    for sid in ["metlife", "sofi", "azteca"]:
        def t_zones(stadium_id=sid):
            r = requests.get(f"{BASE}/api/zones?stadium_id={stadium_id}", timeout=5)
            assert r.status_code == 200
            data = r.json()
            assert isinstance(data, list)
            assert len(data) > 0
            # Check zone structure
            z = data[0]
            assert "zone_id" in z
            assert "status" in z
            assert "crowd_density_pct" in z
            assert "type" in z
            return True
        test(f"GET /api/zones?stadium_id={sid}", t_zones)

    # --- 4. Invalid Stadium ---
    print("\n🚫 Error Handling")
    def t_invalid_stadium():
        r = requests.get(f"{BASE}/api/zones?stadium_id=invalid_xyz", timeout=5)
        assert r.status_code == 404
        return True
    test("GET /api/zones?stadium_id=invalid → 404", t_invalid_stadium)

    # --- 5. Coordinates ---
    print("\n📐 Coordinates & Graph")
    def t_coords():
        r = requests.get(f"{BASE}/api/coordinates?stadium_id=metlife", timeout=5)
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data, dict)
        assert len(data) > 0
        # Check coordinate structure
        first_key = list(data.keys())[0]
        assert "x" in data[first_key]
        assert "y" in data[first_key]
        return True
    test("GET /api/coordinates", t_coords)

    # --- 6. Graph ---
    def t_graph():
        r = requests.get(f"{BASE}/api/graph?stadium_id=metlife", timeout=5)
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data, dict)
        assert len(data) > 0
        return True
    test("GET /api/graph", t_graph)

    # --- 7. Route Calculation ---
    print("\n🗺️  Route Calculation")
    def t_route():
        zones = requests.get(f"{BASE}/api/zones?stadium_id=metlife", timeout=5).json()
        start = zones[0]["zone_id"]
        end = zones[-1]["zone_id"]
        r = requests.post(f"{BASE}/api/route", json={
            "user_id": "test_user",
            "stadium_id": "metlife",
            "accessibility_need": "wheelchair",
            "current_location": start,
            "destination": end,
        }, timeout=30)
        assert r.status_code == 200
        data = r.json()
        assert "recommended_path" in data
        assert "eta_minutes" in data
        assert "reasoning" in data
        assert "confidence" in data
        return True
    test("POST /api/route (wheelchair)", t_route)

    # --- 8. Same-origin Route (edge case) ---
    def t_same_route():
        r = requests.post(f"{BASE}/api/route", json={
            "user_id": "test_user",
            "stadium_id": "metlife",
            "accessibility_need": "wheelchair",
            "current_location": "pepsi_gate",
            "destination": "pepsi_gate",
        }, timeout=10)
        assert r.status_code == 200
        data = r.json()
        assert data["eta_minutes"] == 0
        assert "already at" in data["reasoning"].lower()
        return True
    test("POST /api/route (same start=end)", t_same_route)

    # --- 9. Demo Scenarios ---
    print("\n🎮 Demo Scenarios")
    for scenario in ["normal", "blocked", "halftime", "evacuation"]:
        def t_scenario(s=scenario):
            r = requests.post(f"{BASE}/api/demo/scenario", json={
                "scenario_type": s,
                "stadium_id": "metlife",
            }, timeout=10)
            assert r.status_code == 200
            data = r.json()
            assert data["scenario"] == s
            assert data["zones_affected"] >= 0
            assert len(data["description"]) > 0
            return True
        test(f"POST /api/demo/scenario ({scenario})", t_scenario)

    # --- 10. Caption Processing ---
    print("\n📝 Caption Processing")
    def t_caption():
        r = requests.post(f"{BASE}/api/caption", json={
            "raw_text": "Gate 5 is now closed for maintenance. Please use Gate 3.",
        }, timeout=15)
        assert r.status_code == 200
        data = r.json()
        assert "display_text" in data
        assert "urgency" in data
        assert "confidence" in data
        return True
    test("POST /api/caption", t_caption)

    def t_empty_caption():
        r = requests.post(f"{BASE}/api/caption", json={"raw_text": "  "}, timeout=5)
        assert r.status_code == 200
        data = r.json()
        assert data["confidence"] == 0
        return True
    test("POST /api/caption (empty text)", t_empty_caption)

    # --- 11. Chat ---
    print("\n💬 Conversational AI")
    def t_chat():
        r = requests.post(f"{BASE}/api/chat", json={
            "user_id": "test_user",
            "stadium_id": "metlife",
            "accessibility_need": "wheelchair",
            "message": "Where is the nearest elevator?",
        }, timeout=30)
        assert r.status_code == 200
        data = r.json()
        assert "response" in data
        assert len(data["response"]) > 0
        return True
    test("POST /api/chat", t_chat)

    # --- 12. Predictions ---
    print("\n🔮 Predictions")
    def t_predictions():
        r = requests.get(f"{BASE}/api/predictions/metlife?horizon_minutes=30", timeout=15)
        assert r.status_code == 200
        data = r.json()
        assert "predictions" in data
        assert "overall_risk" in data
        assert "summary" in data
        return True
    test("GET /api/predictions/metlife", t_predictions)

    # --- 13. Analytics ---
    print("\n📊 Analytics")
    def t_analytics():
        r = requests.get(f"{BASE}/api/analytics/metlife", timeout=15)
        assert r.status_code == 200
        data = r.json()
        assert "total_fans_estimated" in data
        assert "zone_analytics" in data
        assert "ai_insights" in data
        assert "recommendations" in data
        return True
    test("GET /api/analytics/metlife", t_analytics)

    # --- 14. Batch Zone Update ---
    print("\n🔄 Batch Operations")
    def t_batch():
        r = requests.post(f"{BASE}/api/zones/batch-update", json={
            "stadium_id": "metlife",
            "updates": [
                {"zone_id": "pepsi_gate", "crowd_density_pct": 42},
            ],
        }, timeout=10)
        assert r.status_code == 200
        data = r.json()
        assert data["updated"] == 1
        return True
    test("POST /api/zones/batch-update", t_batch)

    # --- 15. Announcements ---
    print("\n📢 Announcements")
    def t_announcements():
        r = requests.get(f"{BASE}/api/announcements", timeout=5)
        assert r.status_code == 200
        data = r.json()
        assert "announcements" in data
        return True
    test("GET /api/announcements", t_announcements)

    # --- SUMMARY ---
    print("\n" + "=" * 60)
    print(f"  RESULTS: {PASS}/{TOTAL} passed, {FAIL} failed")
    print("=" * 60 + "\n")

    return FAIL == 0


if __name__ == "__main__":
    # Wait for server to be ready
    print("Waiting for backend...")
    for i in range(10):
        try:
            requests.get(f"{BASE}/api/health", timeout=2)
            break
        except Exception:
            time.sleep(1)

    success = run_all()
    sys.exit(0 if success else 1)
