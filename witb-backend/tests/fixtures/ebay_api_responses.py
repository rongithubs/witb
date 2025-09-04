"""Mock eBay API response fixtures for testing."""


class EBayAPIFixtures:
    """Mock data for eBay API responses."""

    @staticmethod
    def valid_search_response():
        """Valid eBay Browse API search response for golf equipment."""
        return {
            "href": "https://api.ebay.com/buy/browse/v1/item_summary/search?q=TaylorMade+Stealth&category_ids=1617&limit=20",
            "total": 125,
            "next": "https://api.ebay.com/buy/browse/v1/item_summary/search?q=TaylorMade+Stealth&category_ids=1617&limit=20&offset=20",
            "limit": 20,
            "offset": 0,
            "itemSummaries": [
                {
                    "itemId": "334567890123",
                    "title": "TaylorMade Stealth Driver 10.5° Right Hand Regular Flex",
                    "price": {"value": "399.99", "currency": "USD"},
                    "itemWebUrl": "https://www.ebay.com/itm/334567890123",
                    "categoryId": "1617",
                    "categoryPath": "Sporting Goods|Golf|Golf Clubs & Equipment|Golf Clubs",
                    "condition": "New",
                    "image": {
                        "imageUrl": "https://i.ebayimg.com/images/g/abc123/s-l1600.jpg"
                    },
                    "seller": {
                        "username": "golf_pro_shop",
                        "feedbackPercentage": 99.5,
                        "feedbackScore": 15420,
                    },
                    "itemLocation": {"country": "US"},
                    "buyingOptions": ["FixedPrice"],
                    "shippingOptions": [
                        {
                            "shippingCost": {"value": "19.99", "currency": "USD"},
                            "shippingCostType": "FIXED",
                        }
                    ],
                },
                {
                    "itemId": "335123456789",
                    "title": "TaylorMade Stealth Irons 5-PW Steel Shafts Right Hand",
                    "price": {"value": "849.99", "currency": "USD"},
                    "itemWebUrl": "https://www.ebay.com/itm/335123456789",
                    "categoryId": "1617",
                    "categoryPath": "Sporting Goods|Golf|Golf Clubs & Equipment|Golf Clubs",
                    "condition": "New",
                    "image": {
                        "imageUrl": "https://i.ebayimg.com/images/g/def456/s-l1600.jpg"
                    },
                    "seller": {
                        "username": "premium_golf_outlet",
                        "feedbackPercentage": 98.9,
                        "feedbackScore": 8532,
                    },
                    "itemLocation": {"country": "US"},
                    "buyingOptions": ["FixedPrice"],
                    "shippingOptions": [
                        {
                            "shippingCost": {"value": "0.00", "currency": "USD"},
                            "shippingCostType": "FREE",
                        }
                    ],
                },
            ],
        }

    @staticmethod
    def empty_search_response():
        """Empty eBay search response with no results."""
        return {
            "href": "https://api.ebay.com/buy/browse/v1/item_summary/search?q=NonExistentBrand&category_ids=1617&limit=20",
            "total": 0,
            "limit": 20,
            "offset": 0,
            "itemSummaries": [],
        }

    @staticmethod
    def valid_product_details_response():
        """Valid eBay product details response."""
        return {
            "itemId": "334567890123",
            "title": "TaylorMade Stealth Driver 10.5° Right Hand Regular Flex",
            "price": {"value": "399.99", "currency": "USD"},
            "itemWebUrl": "https://www.ebay.com/itm/334567890123",
            "categoryId": "1617",
            "categoryPath": "Sporting Goods|Golf|Golf Clubs & Equipment|Golf Clubs",
            "condition": "New",
            "conditionId": "1000",
            "image": {"imageUrl": "https://i.ebayimg.com/images/g/abc123/s-l1600.jpg"},
            "seller": {
                "username": "golf_pro_shop",
                "feedbackPercentage": 99.5,
                "feedbackScore": 15420,
                "sellerAccountType": "BUSINESS",
            },
            "itemLocation": {"country": "US", "postalCode": "90210"},
            "buyingOptions": ["FixedPrice"],
            "shippingOptions": [
                {
                    "shippingCost": {"value": "19.99", "currency": "USD"},
                    "shippingCostType": "FIXED",
                    "minEstimatedDeliveryDate": "2025-01-15T00:00:00.000Z",
                    "maxEstimatedDeliveryDate": "2025-01-20T00:00:00.000Z",
                }
            ],
            "description": "Brand new TaylorMade Stealth Driver with 10.5° loft. Right hand orientation with regular flex shaft. Includes headcover and adjustment tool.",
            "aspects": {
                "Brand": ["TaylorMade"],
                "Model": ["Stealth"],
                "Club Type": ["Driver"],
                "Loft": ["10.5°"],
                "Dexterity": ["Right Hand"],
                "Flex": ["Regular"],
            },
        }

    @staticmethod
    def oauth_token_response():
        """Valid OAuth token response."""
        return {
            "access_token": "v^1.1#i^1#p^3#I^3#r^0#f^0#t^H4sIAAAAAAAAAOVZ...",
            "expires_in": 7200,
            "token_type": "Application Access Token",
        }

    @staticmethod
    def search_error_response():
        """eBay API error response for testing error handling."""
        return {
            "errors": [
                {
                    "errorId": 1001,
                    "domain": "API_BROWSE",
                    "subdomain": "Browsing",
                    "category": "REQUEST",
                    "message": "Invalid request parameter 'category_ids'",
                    "longMessage": "The specified category ID is not valid for the marketplace.",
                    "parameters": [
                        {"name": "category_ids", "value": "invalid_category"}
                    ],
                }
            ]
        }

    @staticmethod
    def product_not_found_response():
        """eBay API 404 response for product not found."""
        return {
            "errors": [
                {
                    "errorId": 1102,
                    "domain": "API_BROWSE",
                    "subdomain": "Browsing",
                    "category": "REQUEST",
                    "message": "The item ID provided was not found.",
                    "longMessage": "The item ID provided in the request was not found or is not active.",
                }
            ]
        }

    @staticmethod
    def malformed_item_response():
        """Malformed eBay item for testing error handling."""
        return {
            "itemId": "123456789",
            "title": "Test Item",
            # Missing required price field
            "itemWebUrl": "https://www.ebay.com/itm/123456789",
        }

    @staticmethod
    def search_response_with_mixed_items():
        """Search response with mix of valid and invalid items."""
        return {
            "total": 2,
            "limit": 20,
            "offset": 0,
            "itemSummaries": [
                # Valid item
                {
                    "itemId": "334567890123",
                    "title": "Titleist Pro V1 Golf Balls Dozen",
                    "price": {"value": "54.99", "currency": "USD"},
                    "itemWebUrl": "https://www.ebay.com/itm/334567890123",
                    "condition": "New",
                    "seller": {"username": "golf_store", "feedbackPercentage": 99.0},
                    "buyingOptions": ["FixedPrice"],
                },
                # Invalid item (missing price)
                {
                    "itemId": "123456789",
                    "title": "Broken Item",
                    "itemWebUrl": "https://www.ebay.com/itm/123456789",
                },
            ],
        }
