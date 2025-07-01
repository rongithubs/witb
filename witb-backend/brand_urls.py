"""
Brand to URL mapping for golf equipment manufacturers.
Maps brand names to their product category URLs for easy linking.
"""

BRAND_URLS = {
    # Major Club Manufacturers
    "TaylorMade": "https://www.taylormadegolf.com/taylormade-clubs/?lang=en_US",
    "Callaway": "https://www.callawaygolf.com/golf-clubs",
    "Titleist": "https://www.titleist.com/explore-golf-clubs/",
    "PING": "https://ping.com/en-us/clubs/",
    "Mizuno": "https://mizunogolf.com/us/",
    "Cobra": "https://www.cobragolf.com",
    "Srixon": "https://us.dunlopsports.com/srixon/clubs",
    "Cleveland": "https://us.dunlopsports.com/cleveland-golf/clubs",
    
    # Putter Specialists
    "Odyssey": "https://odyssey.callawaygolf.com/putters",
    "L.A.B. Golf": "https://labgolf.com/collections/putters",
    "Axis1": "https://axis1golf.com/putters",
    
    # Grip Manufacturers
    "Golf Pride": "https://www.golfpride.com/us/en-us.html",
    "Lamkin": "https://www.lamkingrips.com/",
    "SuperStroke": "https://superstrokeusa.com/",
    "Iomic": "https://www.iomicusa.com/",
    
    # Other Equipment
    "Bridgestone": "https://www.bridgestonegolf.com/en-us/index/",
    "Nike": "https://www.nike.com/w/golf-8k6u7",  # General Nike golf
    
    # Specialty/Boutique Brands
    "Miura": "https://www.miuragolf.com/collections/irons",
    "Maxfli": "https://www.dickssportinggoods.com/f/maxfli",  # Available at Dick's
}

def get_brand_url(brand_name: str) -> str:
    """
    Get the product URL for a given brand name.
    
    Args:
        brand_name: The brand name to look up
        
    Returns:
        The product URL for the brand, or None if not found
    """
    if not brand_name:
        return None
        
    # Try exact match first
    if brand_name in BRAND_URLS:
        return BRAND_URLS[brand_name]
    
    # Try case-insensitive match
    brand_lower = brand_name.lower()
    for brand, url in BRAND_URLS.items():
        if brand.lower() == brand_lower:
            return url
    
    # Try partial match for brands with variations
    for brand, url in BRAND_URLS.items():
        if brand_lower in brand.lower() or brand.lower() in brand_lower:
            return url
    
    return None

def get_all_supported_brands() -> list:
    """Get list of all supported brand names."""
    return list(BRAND_URLS.keys())