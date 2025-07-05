#!/usr/bin/env python3
"""
LPGA Player Data Population Script
Populates the database with top 50 LPGA players and their equipment data
"""

import asyncio
import sys
import os
import uuid

# Add the backend directory to path for database access
backend_path = os.path.join(os.path.dirname(__file__), '..', 'witb-backend')
sys.path.append(backend_path)

# Change to backend directory for database access
os.chdir(backend_path)

from database import engine
from sqlalchemy import text

# Known LPGA top 50 players with sample WITB data
LPGA_PLAYERS_DATA = [
    {
        "rank": 1,
        "name": "Nelly Korda",
        "country": "USA",
        "tour": "LPGA",
        "age": 26,
        "average_points": 10.38,
        "total_points": 384.11,
        "events_played": 37,
        "witb_items": [
            {"category": "Driver", "brand": "Titleist", "model": "TSR3", "loft": "10.5 degrees", "shaft": "Mitsubishi Tensei AV Raw Blue 55 TX"},
            {"category": "3-Wood", "brand": "Titleist", "model": "TSR3", "loft": "16.5 degrees", "shaft": "Mitsubishi Tensei AV Raw Blue 75 TX"},
            {"category": "Iron", "brand": "Titleist", "model": "T100", "loft": "4-PW", "shaft": "True Temper Dynamic Gold Tour Issue X100"},
            {"category": "Wedge", "brand": "Titleist", "model": "Vokey SM9", "loft": "52, 56, 60", "shaft": "True Temper Dynamic Gold Tour Issue X100"},
            {"category": "Putter", "brand": "Titleist", "model": "Scotty Cameron Special Select Newport 2", "loft": "", "shaft": ""},
            {"category": "Ball", "brand": "Titleist", "model": "Pro V1x", "loft": "", "shaft": ""}
        ]
    },
    {
        "rank": 2,
        "name": "Jeeno Thitikul",
        "country": "THA",
        "tour": "LPGA",
        "age": 21,
        "average_points": 8.86,
        "total_points": 363.38,
        "events_played": 41,
        "witb_items": [
            {"category": "Driver", "brand": "TaylorMade", "model": "Stealth Plus", "loft": "9 degrees", "shaft": "Mitsubishi Tensei CK Pro Orange 60 TX"},
            {"category": "3-Wood", "brand": "TaylorMade", "model": "Stealth Plus", "loft": "15 degrees", "shaft": "Mitsubishi Tensei CK Pro Orange 70 TX"},
            {"category": "Iron", "brand": "TaylorMade", "model": "P770", "loft": "4-PW", "shaft": "True Temper Dynamic Gold Tour Issue S400"},
            {"category": "Wedge", "brand": "TaylorMade", "model": "Milled Grind 3", "loft": "50, 54, 58", "shaft": "True Temper Dynamic Gold Tour Issue S400"},
            {"category": "Putter", "brand": "TaylorMade", "model": "Spider Tour X", "loft": "", "shaft": ""},
            {"category": "Ball", "brand": "TaylorMade", "model": "TP5x", "loft": "", "shaft": ""}
        ]
    },
    {
        "rank": 3,
        "name": "Lydia Ko",
        "country": "NZL",
        "tour": "LPGA",
        "age": 27,
        "average_points": 7.45,
        "total_points": 305.45,
        "events_played": 41,
        "witb_items": [
            {"category": "Driver", "brand": "PXG", "model": "0311 Gen5", "loft": "10.5 degrees", "shaft": "Fujikura Ventus Blue 6 S"},
            {"category": "3-Wood", "brand": "PXG", "model": "0311 Gen5", "loft": "15 degrees", "shaft": "Fujikura Ventus Blue 7 S"},
            {"category": "Iron", "brand": "PXG", "model": "0311 P Gen5", "loft": "4-PW", "shaft": "True Temper Dynamic Gold Tour Issue S300"},
            {"category": "Wedge", "brand": "PXG", "model": "Sugar Daddy II", "loft": "50, 54, 58", "shaft": "True Temper Dynamic Gold Tour Issue S300"},
            {"category": "Putter", "brand": "Odyssey", "model": "White Hot OG #7", "loft": "", "shaft": ""},
            {"category": "Ball", "brand": "Titleist", "model": "Pro V1", "loft": "", "shaft": ""}
        ]
    },
    {
        "rank": 4,
        "name": "Ruoning Yin",
        "country": "CHN",
        "tour": "LPGA",
        "age": 22,
        "average_points": 6.89,
        "total_points": 282.65,
        "events_played": 41,
        "witb_items": [
            {"category": "Driver", "brand": "Callaway", "model": "Paradym Triple Diamond", "loft": "9 degrees", "shaft": "Fujikura Ventus TR Blue 6 X"},
            {"category": "3-Wood", "brand": "Callaway", "model": "Paradym", "loft": "15 degrees", "shaft": "Fujikura Ventus TR Blue 7 X"},
            {"category": "Iron", "brand": "Callaway", "model": "Apex Pro 21", "loft": "4-PW", "shaft": "True Temper Dynamic Gold Tour Issue X100"},
            {"category": "Wedge", "brand": "Callaway", "model": "Jaws MD5", "loft": "52, 56, 60", "shaft": "True Temper Dynamic Gold Tour Issue X100"},
            {"category": "Putter", "brand": "Odyssey", "model": "Tri-Hot 5K Double Wide", "loft": "", "shaft": ""},
            {"category": "Ball", "brand": "Callaway", "model": "Chrome Soft X", "loft": "", "shaft": ""}
        ]
    },
    {
        "rank": 5,
        "name": "Haeran Ryu",
        "country": "KOR",
        "tour": "LPGA",
        "age": 23,
        "average_points": 6.12,
        "total_points": 251.02,
        "events_played": 41,
        "witb_items": [
            {"category": "Driver", "brand": "Ping", "model": "G430 LST", "loft": "9 degrees", "shaft": "Mitsubishi Tensei CK Pro Orange 60 X"},
            {"category": "3-Wood", "brand": "Ping", "model": "G430", "loft": "14.5 degrees", "shaft": "Mitsubishi Tensei CK Pro Orange 70 X"},
            {"category": "Iron", "brand": "Ping", "model": "Blueprint T", "loft": "4-PW", "shaft": "True Temper Dynamic Gold Tour Issue S400"},
            {"category": "Wedge", "brand": "Ping", "model": "Glide 4.0", "loft": "50, 54, 58", "shaft": "True Temper Dynamic Gold Tour Issue S400"},
            {"category": "Putter", "brand": "Ping", "model": "Heppler Piper C", "loft": "", "shaft": ""},
            {"category": "Ball", "brand": "Titleist", "model": "Pro V1x", "loft": "", "shaft": ""}
        ]
    },
    {
        "rank": 6,
        "name": "Maja Stark",
        "country": "SWE",
        "tour": "LPGA",
        "age": 25,
        "average_points": 5.85,
        "total_points": 240.05,
        "events_played": 41,
        "witb_items": [
            {"category": "Driver", "brand": "Ping", "model": "G430 MAX", "loft": "10.5 degrees", "shaft": "Fujikura Ventus Blue 6 S"},
            {"category": "3-Wood", "brand": "Ping", "model": "G430", "loft": "15 degrees", "shaft": "Fujikura Ventus Blue 7 S"},
            {"category": "Iron", "brand": "Ping", "model": "i230", "loft": "4-PW", "shaft": "True Temper Dynamic Gold Tour Issue S300"},
            {"category": "Wedge", "brand": "Ping", "model": "Glide 4.0", "loft": "52, 56, 60", "shaft": "True Temper Dynamic Gold Tour Issue S300"},
            {"category": "Putter", "brand": "Ping", "model": "PLD Milled Oslo", "loft": "", "shaft": ""},
            {"category": "Ball", "brand": "Titleist", "model": "Pro V1", "loft": "", "shaft": ""}
        ]
    },
    {
        "rank": 7,
        "name": "Lilia Vu",
        "country": "USA",
        "tour": "LPGA",
        "age": 26,
        "average_points": 5.67,
        "total_points": 232.55,
        "events_played": 41,
        "witb_items": [
            {"category": "Driver", "brand": "Titleist", "model": "TSR2", "loft": "10.5 degrees", "shaft": "Mitsubishi Tensei AV Raw White 55 S"},
            {"category": "3-Wood", "brand": "Titleist", "model": "TSR2", "loft": "15 degrees", "shaft": "Mitsubishi Tensei AV Raw White 65 S"},
            {"category": "Iron", "brand": "Titleist", "model": "T100", "loft": "4-PW", "shaft": "True Temper Dynamic Gold Tour Issue S300"},
            {"category": "Wedge", "brand": "Titleist", "model": "Vokey SM9", "loft": "50, 54, 58", "shaft": "True Temper Dynamic Gold Tour Issue S300"},
            {"category": "Putter", "brand": "Scotty Cameron", "model": "Special Select Newport 2", "loft": "", "shaft": ""},
            {"category": "Ball", "brand": "Titleist", "model": "Pro V1x", "loft": "", "shaft": ""}
        ]
    },
    {
        "rank": 8,
        "name": "Hannah Green",
        "country": "AUS",
        "tour": "LPGA",
        "age": 27,
        "average_points": 5.23,
        "total_points": 214.63,
        "events_played": 41,
        "witb_items": [
            {"category": "Driver", "brand": "Ping", "model": "G430 LST", "loft": "9 degrees", "shaft": "Fujikura Ventus TR Blue 6 S"},
            {"category": "3-Wood", "brand": "Ping", "model": "G430", "loft": "14.5 degrees", "shaft": "Fujikura Ventus TR Blue 7 S"},
            {"category": "Iron", "brand": "Ping", "model": "Blueprint T", "loft": "4-PW", "shaft": "True Temper Dynamic Gold Tour Issue S300"},
            {"category": "Wedge", "brand": "Ping", "model": "Glide 4.0", "loft": "50, 54, 58", "shaft": "True Temper Dynamic Gold Tour Issue S300"},
            {"category": "Putter", "brand": "Ping", "model": "Heppler Tomcat 14", "loft": "", "shaft": ""},
            {"category": "Ball", "brand": "Titleist", "model": "Pro V1", "loft": "", "shaft": ""}
        ]
    },
    {
        "rank": 9,
        "name": "Hyo Joo Kim",
        "country": "KOR",
        "tour": "LPGA",
        "age": 29,
        "average_points": 4.98,
        "total_points": 204.32,
        "events_played": 41,
        "witb_items": [
            {"category": "Driver", "brand": "TaylorMade", "model": "Qi10", "loft": "9 degrees", "shaft": "Mitsubishi Tensei CK Pro Orange 60 S"},
            {"category": "3-Wood", "brand": "TaylorMade", "model": "Qi10", "loft": "15 degrees", "shaft": "Mitsubishi Tensei CK Pro Orange 70 S"},
            {"category": "Iron", "brand": "TaylorMade", "model": "P7MC", "loft": "4-PW", "shaft": "True Temper Dynamic Gold Tour Issue S300"},
            {"category": "Wedge", "brand": "TaylorMade", "model": "Milled Grind 4", "loft": "50, 54, 58", "shaft": "True Temper Dynamic Gold Tour Issue S300"},
            {"category": "Putter", "brand": "TaylorMade", "model": "TP Hydro Blast Bandon 3", "loft": "", "shaft": ""},
            {"category": "Ball", "brand": "TaylorMade", "model": "TP5", "loft": "", "shaft": ""}
        ]
    },
    {
        "rank": 10,
        "name": "Mao Saigo",
        "country": "JPN",
        "tour": "LPGA",
        "age": 23,
        "average_points": 4.78,
        "total_points": 196.12,
        "events_played": 41,
        "witb_items": [
            {"category": "Driver", "brand": "Srixon", "model": "ZX5 Mk II", "loft": "10.5 degrees", "shaft": "Fujikura Ventus Blue 6 S"},
            {"category": "3-Wood", "brand": "Srixon", "model": "ZX", "loft": "15 degrees", "shaft": "Fujikura Ventus Blue 7 S"},
            {"category": "Iron", "brand": "Srixon", "model": "ZX7 Mk II", "loft": "4-PW", "shaft": "True Temper Dynamic Gold Tour Issue S300"},
            {"category": "Wedge", "brand": "Cleveland", "model": "RTX 6 ZipCore", "loft": "50, 54, 58", "shaft": "True Temper Dynamic Gold Tour Issue S300"},
            {"category": "Putter", "brand": "Odyssey", "model": "Tri-Hot 5K Seven", "loft": "", "shaft": ""},
            {"category": "Ball", "brand": "Srixon", "model": "Z-Star XV", "loft": "", "shaft": ""}
        ]
    },
    {
        "rank": 11,
        "name": "Rose Zhang",
        "country": "USA",
        "tour": "LPGA",
        "age": 21,
        "average_points": 4.65,
        "total_points": 190.86,
        "events_played": 41,
        "witb_items": [
            {"category": "Driver", "brand": "Callaway", "model": "Paradym", "loft": "10.5 degrees", "shaft": "Fujikura Ventus Blue 6 S"},
            {"category": "3-Wood", "brand": "Callaway", "model": "Paradym", "loft": "15 degrees", "shaft": "Fujikura Ventus Blue 7 S"},
            {"category": "Iron", "brand": "Callaway", "model": "Apex Pro 21", "loft": "4-PW", "shaft": "True Temper Dynamic Gold Tour Issue S300"},
            {"category": "Wedge", "brand": "Callaway", "model": "Jaws MD5", "loft": "50, 54, 58", "shaft": "True Temper Dynamic Gold Tour Issue S300"},
            {"category": "Putter", "brand": "Odyssey", "model": "White Hot OG #1WS", "loft": "", "shaft": ""},
            {"category": "Ball", "brand": "Callaway", "model": "Chrome Soft X", "loft": "", "shaft": ""}
        ]
    },
    {
        "rank": 12,
        "name": "Lauren Coughlin",
        "country": "USA",
        "tour": "LPGA",
        "age": 31,
        "average_points": 4.52,
        "total_points": 185.41,
        "events_played": 41,
        "witb_items": [
            {"category": "Driver", "brand": "Titleist", "model": "TSR3", "loft": "9 degrees", "shaft": "Fujikura Ventus Black 6 S"},
            {"category": "3-Wood", "brand": "Titleist", "model": "TSR3", "loft": "15 degrees", "shaft": "Fujikura Ventus Black 7 S"},
            {"category": "Iron", "brand": "Titleist", "model": "T100", "loft": "4-PW", "shaft": "True Temper Dynamic Gold Tour Issue S300"},
            {"category": "Wedge", "brand": "Titleist", "model": "Vokey SM9", "loft": "52, 56, 60", "shaft": "True Temper Dynamic Gold Tour Issue S300"},
            {"category": "Putter", "brand": "Scotty Cameron", "model": "Special Select Fastback 1.5", "loft": "", "shaft": ""},
            {"category": "Ball", "brand": "Titleist", "model": "Pro V1", "loft": "", "shaft": ""}
        ]
    },
    {
        "rank": 13,
        "name": "Jin Young Ko",
        "country": "KOR",
        "tour": "LPGA",
        "age": 29,
        "average_points": 4.48,
        "total_points": 183.68,
        "events_played": 41,
        "witb_items": [
            {"category": "Driver", "brand": "TaylorMade", "model": "Stealth 2 Plus", "loft": "9 degrees", "shaft": "Mitsubishi Tensei CK Pro Orange 60 S"},
            {"category": "3-Wood", "brand": "TaylorMade", "model": "Stealth 2", "loft": "15 degrees", "shaft": "Mitsubishi Tensei CK Pro Orange 70 S"},
            {"category": "Iron", "brand": "TaylorMade", "model": "P7MC", "loft": "4-PW", "shaft": "True Temper Dynamic Gold Tour Issue S300"},
            {"category": "Wedge", "brand": "TaylorMade", "model": "Milled Grind 3", "loft": "50, 54, 58", "shaft": "True Temper Dynamic Gold Tour Issue S300"},
            {"category": "Putter", "brand": "TaylorMade", "model": "Spider Tour X", "loft": "", "shaft": ""},
            {"category": "Ball", "brand": "TaylorMade", "model": "TP5", "loft": "", "shaft": ""}
        ]
    },
    {
        "rank": 14,
        "name": "Ayaka Furue",
        "country": "JPN",
        "tour": "LPGA",
        "age": 24,
        "average_points": 4.35,
        "total_points": 178.35,
        "events_played": 41,
        "witb_items": [
            {"category": "Driver", "brand": "Ping", "model": "G430 MAX", "loft": "10.5 degrees", "shaft": "Fujikura Ventus Blue 5 S"},
            {"category": "3-Wood", "brand": "Ping", "model": "G430", "loft": "16 degrees", "shaft": "Fujikura Ventus Blue 6 S"},
            {"category": "Iron", "brand": "Ping", "model": "i230", "loft": "5-PW", "shaft": "True Temper Dynamic Gold Tour Issue S300"},
            {"category": "Wedge", "brand": "Ping", "model": "Glide 4.0", "loft": "52, 56, 60", "shaft": "True Temper Dynamic Gold Tour Issue S300"},
            {"category": "Putter", "brand": "Ping", "model": "PLD Milled Anser", "loft": "", "shaft": ""},
            {"category": "Ball", "brand": "Titleist", "model": "Pro V1", "loft": "", "shaft": ""}
        ]
    },
    {
        "rank": 15,
        "name": "Ally Ewing",
        "country": "USA",
        "tour": "LPGA",
        "age": 32,
        "average_points": 4.22,
        "total_points": 173.02,
        "events_played": 41,
        "witb_items": [
            {"category": "Driver", "brand": "Titleist", "model": "TSR2", "loft": "10.5 degrees", "shaft": "Mitsubishi Tensei AV Raw White 55 S"},
            {"category": "3-Wood", "brand": "Titleist", "model": "TSR2", "loft": "16.5 degrees", "shaft": "Mitsubishi Tensei AV Raw White 65 S"},
            {"category": "Iron", "brand": "Titleist", "model": "T150", "loft": "5-PW", "shaft": "True Temper Dynamic Gold Tour Issue S300"},
            {"category": "Wedge", "brand": "Titleist", "model": "Vokey SM9", "loft": "50, 54, 58", "shaft": "True Temper Dynamic Gold Tour Issue S300"},
            {"category": "Putter", "brand": "Scotty Cameron", "model": "Special Select Newport 2", "loft": "", "shaft": ""},
            {"category": "Ball", "brand": "Titleist", "model": "Pro V1x", "loft": "", "shaft": ""}
        ]
    },
    # Players 16-50 for complete top 50
    {"rank": 16, "name": "Celine Boutier", "country": "FRA", "tour": "LPGA", "age": 30, "average_points": 4.15, "total_points": 170.15, "events_played": 41, "witb_items": []},
    {"rank": 17, "name": "Megan Khang", "country": "USA", "tour": "LPGA", "age": 27, "average_points": 4.08, "total_points": 167.28, "events_played": 41, "witb_items": []},
    {"rank": 18, "name": "Brooke Henderson", "country": "CAN", "tour": "LPGA", "age": 27, "average_points": 3.95, "total_points": 162.95, "events_played": 41, "witb_items": []},
    {"rank": 19, "name": "Patty Tavatanakit", "country": "THA", "tour": "LPGA", "age": 25, "average_points": 3.88, "total_points": 159.08, "events_played": 41, "witb_items": []},
    {"rank": 20, "name": "Atthaya Thitikul", "country": "THA", "tour": "LPGA", "age": 21, "average_points": 3.82, "total_points": 156.62, "events_played": 41, "witb_items": []},
    {"rank": 21, "name": "Lexi Thompson", "country": "USA", "tour": "LPGA", "age": 29, "average_points": 3.75, "total_points": 153.75, "events_played": 41, "witb_items": []},
    {"rank": 22, "name": "Yuka Saso", "country": "JPN", "tour": "LPGA", "age": 23, "average_points": 3.68, "total_points": 150.88, "events_played": 41, "witb_items": []},
    {"rank": 23, "name": "Xiyu Lin", "country": "CHN", "tour": "LPGA", "age": 28, "average_points": 3.62, "total_points": 148.42, "events_played": 41, "witb_items": []},
    {"rank": 24, "name": "Georgia Hall", "country": "ENG", "tour": "LPGA", "age": 28, "average_points": 3.55, "total_points": 145.55, "events_played": 41, "witb_items": []},
    {"rank": 25, "name": "Andrea Lee", "country": "USA", "tour": "LPGA", "age": 25, "average_points": 3.48, "total_points": 142.68, "events_played": 41, "witb_items": []},
    {"rank": 26, "name": "Sei Young Kim", "country": "KOR", "tour": "LPGA", "age": 31, "average_points": 3.42, "total_points": 140.22, "events_played": 41, "witb_items": []},
    {"rank": 27, "name": "Anna Nordqvist", "country": "SWE", "tour": "LPGA", "age": 37, "average_points": 3.35, "total_points": 137.35, "events_played": 41, "witb_items": []},
    {"rank": 28, "name": "Stephanie Kyriacou", "country": "AUS", "tour": "LPGA", "age": 24, "average_points": 3.28, "total_points": 134.48, "events_played": 41, "witb_items": []},
    {"rank": 29, "name": "Miyu Yamashita", "country": "JPN", "tour": "LPGA", "age": 24, "average_points": 3.22, "total_points": 132.02, "events_played": 41, "witb_items": []},
    {"rank": 30, "name": "Nasa Hataoka", "country": "JPN", "tour": "LPGA", "age": 25, "average_points": 3.15, "total_points": 129.15, "events_played": 41, "witb_items": []},
    {"rank": 31, "name": "Esther Henseleit", "country": "GER", "tour": "LPGA", "age": 25, "average_points": 3.08, "total_points": 126.28, "events_played": 41, "witb_items": []},
    {"rank": 32, "name": "Jennifer Kupcho", "country": "USA", "tour": "LPGA", "age": 27, "average_points": 3.02, "total_points": 123.82, "events_played": 41, "witb_items": []},
    {"rank": 33, "name": "Cheyenne Knight", "country": "USA", "tour": "LPGA", "age": 28, "average_points": 2.95, "total_points": 120.95, "events_played": 41, "witb_items": []},
    {"rank": 34, "name": "Minami Katsu", "country": "JPN", "tour": "LPGA", "age": 22, "average_points": 2.88, "total_points": 118.08, "events_played": 41, "witb_items": []},
    {"rank": 35, "name": "Carlota Ciganda", "country": "ESP", "tour": "LPGA", "age": 34, "average_points": 2.82, "total_points": 115.62, "events_played": 41, "witb_items": []},
    {"rank": 36, "name": "Angel Yin", "country": "USA", "tour": "LPGA", "age": 25, "average_points": 2.75, "total_points": 112.75, "events_played": 41, "witb_items": []},
    {"rank": 37, "name": "Charley Hull", "country": "ENG", "tour": "LPGA", "age": 28, "average_points": 2.68, "total_points": 109.88, "events_played": 41, "witb_items": []},
    {"rank": 38, "name": "Ryann O'Toole", "country": "USA", "tour": "LPGA", "age": 37, "average_points": 2.62, "total_points": 107.42, "events_played": 41, "witb_items": []},
    {"rank": 39, "name": "Ariya Jutanugarn", "country": "THA", "tour": "LPGA", "age": 28, "average_points": 2.55, "total_points": 104.55, "events_played": 41, "witb_items": []},
    {"rank": 40, "name": "Moriya Jutanugarn", "country": "THA", "tour": "LPGA", "age": 30, "average_points": 2.48, "total_points": 101.68, "events_played": 41, "witb_items": []},
    {"rank": 41, "name": "Danielle Kang", "country": "USA", "tour": "LPGA", "age": 31, "average_points": 2.42, "total_points": 99.22, "events_played": 41, "witb_items": []},
    {"rank": 42, "name": "Leona Maguire", "country": "IRL", "tour": "LPGA", "age": 29, "average_points": 2.35, "total_points": 96.35, "events_played": 41, "witb_items": []},
    {"rank": 43, "name": "Jeongeun Lee6", "country": "KOR", "tour": "LPGA", "age": 28, "average_points": 2.28, "total_points": 93.48, "events_played": 41, "witb_items": []},
    {"rank": 44, "name": "Ashleigh Buhai", "country": "RSA", "tour": "LPGA", "age": 35, "average_points": 2.22, "total_points": 91.02, "events_played": 41, "witb_items": []},
    {"rank": 45, "name": "Narin An", "country": "KOR", "tour": "LPGA", "age": 28, "average_points": 2.15, "total_points": 88.15, "events_played": 41, "witb_items": []},
    {"rank": 46, "name": "Mel Reid", "country": "ENG", "tour": "LPGA", "age": 36, "average_points": 2.08, "total_points": 85.28, "events_played": 41, "witb_items": []},
    {"rank": 47, "name": "Peiyun Chien", "country": "TWN", "tour": "LPGA", "age": 26, "average_points": 2.02, "total_points": 82.82, "events_played": 41, "witb_items": []},
    {"rank": 48, "name": "Gaby Lopez", "country": "MEX", "tour": "LPGA", "age": 30, "average_points": 1.95, "total_points": 79.95, "events_played": 41, "witb_items": []},
    {"rank": 49, "name": "Amy Yang", "country": "KOR", "tour": "LPGA", "age": 34, "average_points": 1.88, "total_points": 77.08, "events_played": 41, "witb_items": []},
    {"rank": 50, "name": "Albane Valenzuela", "country": "SUI", "tour": "LPGA", "age": 26, "average_points": 1.82, "total_points": 74.62, "events_played": 41, "witb_items": []}
    # Complete top 50 LPGA players
]

async def populate_lpga_players():
    """Populate the database with LPGA players and their WITB data"""
    try:
        async with engine.begin() as conn:
            for player_data in LPGA_PLAYERS_DATA:
                print(f"Processing {player_data['name']}...")
                
                # Check if player already exists
                result = await conn.execute(text("""
                    SELECT id FROM players 
                    WHERE LOWER(name) = LOWER(:name) AND tour = 'LPGA'
                """), {"name": player_data["name"]})
                
                existing_player = result.fetchone()
                
                if existing_player:
                    player_id = existing_player[0]
                    print(f"  Player {player_data['name']} already exists, updating...")
                    
                    # Update existing player
                    await conn.execute(text("""
                        UPDATE players 
                        SET ranking = :ranking, country = :country, age = :age,
                            average_points = :average_points, total_points = :total_points,
                            events_played = :events_played
                        WHERE id = :player_id
                    """), {
                        "ranking": player_data["rank"],
                        "country": player_data["country"],
                        "age": player_data.get("age"),
                        "average_points": player_data["average_points"],
                        "total_points": player_data["total_points"],
                        "events_played": player_data["events_played"],
                        "player_id": player_id
                    })
                else:
                    print(f"  Adding new player {player_data['name']}...")
                    
                    # Insert new player with UUID
                    player_id = str(uuid.uuid4())
                    await conn.execute(text("""
                        INSERT INTO players (id, name, country, tour, age, ranking)
                        VALUES (:id, :name, :country, :tour, :age, :ranking)
                    """), {
                        "id": player_id,
                        "name": player_data["name"],
                        "country": player_data["country"],
                        "tour": player_data["tour"],
                        "age": player_data.get("age"),
                        "ranking": player_data["rank"]
                    })
                
                # Add WITB items if provided
                if "witb_items" in player_data:
                    # Delete existing WITB items for this player
                    await conn.execute(text("""
                        DELETE FROM witb_items WHERE player_id = :player_id
                    """), {"player_id": player_id})
                    
                    # Add new WITB items
                    for item in player_data["witb_items"]:
                        await conn.execute(text("""
                            INSERT INTO witb_items (id, player_id, category, brand, model, loft, shaft)
                            VALUES (:id, :player_id, :category, :brand, :model, :loft, :shaft)
                        """), {
                            "id": str(uuid.uuid4()),
                            "player_id": player_id,
                            "category": item["category"],
                            "brand": item["brand"],
                            "model": item["model"],
                            "loft": item.get("loft", ""),
                            "shaft": item.get("shaft", "")
                        })
                    
                    print(f"  Added {len(player_data['witb_items'])} WITB items")
                
                print(f"  ✓ Completed {player_data['name']}")
        
        print(f"\n✅ Successfully populated {len(LPGA_PLAYERS_DATA)} LPGA players!")
        
    except Exception as e:
        print(f"❌ Error populating LPGA data: {e}")
        raise

async def verify_lpga_data():
    """Verify that LPGA data was populated correctly"""
    try:
        async with engine.begin() as conn:
            # Count LPGA players
            result = await conn.execute(text("""
                SELECT COUNT(*) FROM players WHERE tour = 'LPGA'
            """))
            lpga_count = result.scalar()
            
            # Count WITB items for LPGA players
            result = await conn.execute(text("""
                SELECT COUNT(*) FROM witb_items w
                JOIN players p ON w.player_id = p.id
                WHERE p.tour = 'LPGA'
            """))
            witb_count = result.scalar()
            
            # Get top 5 LPGA players
            result = await conn.execute(text("""
                SELECT name, ranking, country, average_points
                FROM players 
                WHERE tour = 'LPGA'
                ORDER BY ranking
                LIMIT 5
            """))
            top_players = result.fetchall()
            
            print(f"\n📊 LPGA Data Verification:")
            print(f"  Total LPGA players: {lpga_count}")
            print(f"  Total WITB items: {witb_count}")
            print(f"  Top 5 players:")
            for player in top_players:
                print(f"    {player[1]:2d}. {player[0]} ({player[2]}) - {player[3]:.2f} avg pts")
                
    except Exception as e:
        print(f"❌ Error verifying data: {e}")

if __name__ == "__main__":
    print("🏌️‍♀️ Starting LPGA Data Population...")
    asyncio.run(populate_lpga_players())
    asyncio.run(verify_lpga_data())
    print("🎯 LPGA data population completed!")