"""Mock ESPN API response fixtures for testing."""

from datetime import datetime


class ESPNAPIFixtures:
    """Mock data for ESPN Golf API responses."""
    
    @staticmethod
    def valid_scoreboard_response():
        """Valid ESPN scoreboard API response with Justin Rose winning."""
        return {
            "events": [{
                "id": "401580326",
                "name": "FedEx St. Jude Championship",
                "shortName": "St. Jude Championship",
                "date": "2025-08-07T00:00:00Z",
                "competitions": [{
                    "id": "401580326",
                    "status": {
                        "clock": 0.0,
                        "displayClock": "0.0",
                        "period": 4,
                        "type": {
                            "id": "3",
                            "name": "STATUS_FINAL",
                            "state": "post",
                            "completed": True,
                            "description": "Final",
                            "detail": "Final",
                            "shortDetail": "Final"
                        }
                    },
                    "competitors": [
                        {
                            "id": "2184",
                            "athlete": {
                                "id": "2184",
                                "displayName": "Justin Rose",
                                "shortName": "J. Rose",
                                "flag": {
                                    "href": "https://a.espncdn.com/i/teamlogos/countries/500/eng.png"
                                }
                            },
                            "score": "-16",
                            "position": "1"
                        },
                        {
                            "id": "9478",
                            "athlete": {
                                "id": "9478", 
                                "displayName": "J.J. Spaun",
                                "shortName": "J. Spaun",
                                "flag": {
                                    "href": "https://a.espncdn.com/i/teamlogos/countries/500/usa.png"
                                }
                            },
                            "score": "-16",
                            "position": "T2"  # Tied for second after playoff
                        },
                        {
                            "id": "10046",
                            "athlete": {
                                "id": "10046",
                                "displayName": "Scottie Scheffler", 
                                "shortName": "S. Scheffler",
                                "flag": {
                                    "href": "https://a.espncdn.com/i/teamlogos/countries/500/usa.png"
                                }
                            },
                            "score": "-15",
                            "position": "T3"
                        },
                        {
                            "id": "5470",
                            "athlete": {
                                "id": "5470",
                                "displayName": "Tommy Fleetwood",
                                "shortName": "T. Fleetwood",
                                "flag": {
                                    "href": "https://a.espncdn.com/i/teamlogos/countries/500/eng.png"
                                }
                            },
                            "score": "-15", 
                            "position": "T3"
                        }
                    ]
                }]
            }]
        }
    
    @staticmethod
    def tournament_in_progress_response():
        """ESPN response for tournament still in progress."""
        return {
            "events": [{
                "id": "401580327",
                "name": "BMW Championship",
                "shortName": "BMW Championship", 
                "date": "2025-08-14T00:00:00Z",
                "competitions": [{
                    "id": "401580327",
                    "status": {
                        "type": {
                            "id": "2", 
                            "name": "STATUS_IN_PROGRESS",
                            "state": "in",
                            "completed": False,
                            "description": "In Progress",
                            "detail": "Round 3",
                            "shortDetail": "R3"
                        }
                    },
                    "competitors": [
                        {
                            "athlete": {"displayName": "Scottie Scheffler"},
                            "score": "-10",
                            "position": "1"
                        },
                        {
                            "athlete": {"displayName": "Xander Schauffele"}, 
                            "score": "-9",
                            "position": "2"
                        }
                    ]
                }]
            }]
        }
    
    @staticmethod
    def empty_scoreboard_response():
        """Empty ESPN scoreboard response."""
        return {
            "events": []
        }
    
    @staticmethod
    def malformed_scoreboard_response():
        """Malformed ESPN scoreboard response."""
        return {
            "events": [{
                "name": "Test Tournament",
                "competitions": [{
                    "status": {"type": {"name": "STATUS_FINAL"}},
                    "competitors": [
                        {
                            # Missing athlete data
                            "score": "-15"
                        },
                        {
                            "athlete": {"displayName": "Valid Player"},
                            # Missing score data
                        }
                    ]
                }]
            }]
        }
    
    @staticmethod
    def valid_events_response():
        """Valid ESPN events API response."""
        return {
            "items": [
                {
                    "id": "401580326",
                    "name": "FedEx St. Jude Championship",
                    "date": "2025-08-07T00:00:00Z",
                    "status": {
                        "type": {
                            "id": "3",
                            "name": "STATUS_FINAL",
                            "completed": True
                        }
                    },
                    "competitions": [{
                        "competitors": [
                            {
                                "athlete": {"displayName": "Justin Rose"},
                                "statistics": [{"value": 1}]  # Position 1
                            },
                            {
                                "athlete": {"displayName": "J.J. Spaun"}, 
                                "statistics": [{"value": 2}]  # Position 2
                            }
                        ]
                    }]
                }
            ]
        }
    
    @staticmethod
    def score_edge_cases():
        """Various score format edge cases."""
        return {
            "events": [{
                "name": "Edge Case Tournament",
                "date": "2025-08-07T00:00:00Z", 
                "competitions": [{
                    "status": {"type": {"name": "STATUS_FINAL"}},
                    "competitors": [
                        {"athlete": {"displayName": "Even Par Player"}, "score": "0"},
                        {"athlete": {"displayName": "Plus Player"}, "score": "+5"},
                        {"athlete": {"displayName": "Big Minus"}, "score": "-25"},
                        {"athlete": {"displayName": "Withdrawal"}, "score": "WD"},
                        {"athlete": {"displayName": "Cut Player"}, "score": "CUT"},
                        {"athlete": {"displayName": "Empty Score"}, "score": ""},
                        {"athlete": {"displayName": "Missing Score"}},  # No score field
                    ]
                }]
            }]
        }
    
    @staticmethod
    def database_witb_response():
        """Mock database response for WITB data."""
        return [
            ('player-id-1', 'Justin Rose', 'Driver', 'TaylorMade', 'GT2', None, 'Project X HZRDUS Smoke Green'),
            ('player-id-1', 'Justin Rose', '3-wood', 'TaylorMade', 'M6', '15°', 'Project X HZRDUS Smoke Green'),
            ('player-id-1', 'Justin Rose', '7-wood', 'TaylorMade', 'M6', '21°', 'Project X HZRDUS Smoke Green'),
            ('player-id-1', 'Justin Rose', 'Iron', 'Mizuno', 'JPX923 Tour', '4-PW', 'KBS Tour 120'),
            ('player-id-1', 'Justin Rose', 'Wedge', 'Titleist', 'Vokey SM9', '52°', 'KBS Hi-Rev'),
            ('player-id-1', 'Justin Rose', 'Wedge', 'Titleist', 'Vokey SM9', '56°', 'KBS Hi-Rev'),
            ('player-id-1', 'Justin Rose', 'Wedge', 'Titleist', 'Vokey SM9', '60°', 'KBS Hi-Rev'),
            ('player-id-1', 'Justin Rose', 'Putter', 'Odyssey', 'Toulon Design Garage SC', None, None),
            ('player-id-1', 'Justin Rose', 'Ball', 'Titleist', 'Pro V1 Left Dot', None, None),
            ('player-id-1', 'Justin Rose', 'Grip', 'Lamkin', 'JR REL', None, None),
        ]
    
    @staticmethod
    def http_error_responses():
        """Various HTTP error response scenarios."""
        return {
            404: {"error": "Tournament not found"},
            500: {"error": "Internal server error"},
            429: {"error": "Too many requests"},
            503: {"error": "Service unavailable"}
        }