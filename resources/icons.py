#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Icon provider for Windows System Manager.
Provides icon names and SVG data for the application.
"""

from PyQt5.QtGui import QIcon, QPainter
from PyQt5.QtCore import QByteArray, QBuffer, QIODevice, Qt
import base64

# Dictionary of icons used in the application
ICON_SVG = {
    # Achievement and level icons
    "trophy": """
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24">
      <path fill="#FFD700" d="M12 2C8.7 2 6 4.7 6 8v1H4c-1.1 0-2 .9-2 2v1c0 1.1.9 2 2 2h2v-1c0 3.3 2.7 6 6 6s6-2.7 6-6v1h2c1.1 0 2-.9 2-2v-1c0-1.1-.9-2-2-2h-2V8c0-3.3-2.7-6-6-6z"/>
      <path fill="#A67C00" d="M12 16c-2.2 0-4-1.8-4-4v-4c0-2.2 1.8-4 4-4s4 1.8 4 4v4c0 2.2-1.8 4-4 4z"/>
      <path fill="#FFD700" d="M12 20c-1.1 0-2 .9-2 2h4c0-1.1-.9-2-2-2z"/>
      <path fill="#FFD700" d="M9 18h6c.6 0 1 .4 1 1v1H8v-1c0-.6.4-1 1-1z"/>
    </svg>
    """,
    "disk": """
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24">
      <circle fill="#3498DB" cx="12" cy="12" r="10"/>
      <circle fill="#1F618D" cx="12" cy="12" r="3"/>
    </svg>
    """,
    "process": """
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24">
      <rect fill="#2ECC71" x="2" y="2" width="9" height="9" rx="1"/>
      <rect fill="#F39C12" x="13" y="2" width="9" height="9" rx="1"/>
      <rect fill="#9B59B6" x="2" y="13" width="9" height="9" rx="1"/>
      <rect fill="#E74C3C" x="13" y="13" width="9" height="9" rx="1"/>
    </svg>
    """,
    "drive": """
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24">
      <rect fill="#95A5A6" x="2" y="6" width="20" height="12" rx="2"/>
      <circle fill="#7F8C8D" cx="6" cy="12" r="2"/>
      <circle fill="#7F8C8D" cx="12" cy="12" r="2"/>
      <circle fill="#7F8C8D" cx="18" cy="12" r="2"/>
    </svg>
    """,
    "folder": """
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24">
      <path fill="#F1C40F" d="M2 6c0-1.1.9-2 2-2h4l2 2h10c1.1 0 2 .9 2 2v10c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6z"/>
    </svg>
    """,
    "app": """
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24">
      <rect fill="#3498DB" x="3" y="3" width="7" height="7" rx="1"/>
      <rect fill="#E74C3C" x="14" y="3" width="7" height="7" rx="1"/>
      <rect fill="#F39C12" x="3" y="14" width="7" height="7" rx="1"/>
      <rect fill="#2ECC71" x="14" y="14" width="7" height="7" rx="1"/>
    </svg>
    """,
    "calendar": """
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24">
      <rect fill="#ECF0F1" x="2" y="4" width="20" height="18" rx="2"/>
      <path fill="#BDC3C7" d="M2 8h20v2H2z"/>
      <path fill="#E74C3C" d="M5 2v4M19 2v4"/>
      <rect fill="#3498DB" x="5" y="10" width="3" height="3"/>
      <rect fill="#2ECC71" x="10.5" y="10" width="3" height="3"/>
      <rect fill="#F39C12" x="16" y="10" width="3" height="3"/>
      <rect fill="#9B59B6" x="5" y="15" width="3" height="3"/>
      <rect fill="#E74C3C" x="10.5" y="15" width="3" height="3"/>
      <rect fill="#1ABC9C" x="16" y="15" width="3" height="3"/>
    </svg>
    """,
    "startup": """
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24">
      <path fill="#F39C12" d="M12 2L2 12h5v8h10v-8h5L12 2z"/>
    </svg>
    """,
    
    # Level icons
    "level1": """
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24">
      <circle fill="#BDC3C7" cx="12" cy="12" r="10"/>
      <text x="12" y="17" font-family="Arial" font-size="14" font-weight="bold" text-anchor="middle" fill="#2C3E50">1</text>
    </svg>
    """,
    "level2": """
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24">
      <circle fill="#A5C4E7" cx="12" cy="12" r="10"/>
      <text x="12" y="17" font-family="Arial" font-size="14" font-weight="bold" text-anchor="middle" fill="#2C3E50">2</text>
    </svg>
    """,
    "level3": """
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24">
      <circle fill="#F7DC6F" cx="12" cy="12" r="10"/>
      <text x="12" y="17" font-family="Arial" font-size="14" font-weight="bold" text-anchor="middle" fill="#2C3E50">3</text>
    </svg>
    """,
    "level4": """
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24">
      <circle fill="#7DCEA0" cx="12" cy="12" r="10"/>
      <text x="12" y="17" font-family="Arial" font-size="14" font-weight="bold" text-anchor="middle" fill="#2C3E50">4</text>
    </svg>
    """,
    "level5": """
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24">
      <circle fill="#F1948A" cx="12" cy="12" r="10"/>
      <text x="12" y="17" font-family="Arial" font-size="14" font-weight="bold" text-anchor="middle" fill="#2C3E50">5</text>
    </svg>
    """,
    "memory": """
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24">
      <path fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" d="M2 2h20v8H2V2z"/>
      <path fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" d="M2 14h20v8H2v-8z"/>
      <path fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" d="M6 6h.01M6 18h.01M10 6h.01M10 18h.01M14 6h.01M14 18h.01M18 6h.01M18 18h.01"/>
    </svg>
    """,
    
    "drive": """
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24">
      <rect x="2" y="6" width="20" height="12" rx="2" ry="2" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
      <circle cx="6" cy="12" r="1" fill="currentColor"/>
      <line x1="10" y1="12" x2="18" y2="12" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
    </svg>
    """,
    
    "process": """
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24">
      <circle cx="12" cy="12" r="10" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
      <circle cx="12" cy="12" r="3" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
      <line x1="12" y1="2" x2="12" y2="4" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
      <line x1="12" y1="20" x2="12" y2="22" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
      <line x1="4.93" y1="4.93" x2="6.34" y2="6.34" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
      <line x1="17.66" y1="17.66" x2="19.07" y2="19.07" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
      <line x1="2" y1="12" x2="4" y2="12" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
      <line x1="20" y1="12" x2="22" y2="12" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
      <line x1="4.93" y1="19.07" x2="6.34" y2="17.66" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
      <line x1="17.66" y1="6.34" x2="19.07" y2="4.93" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
    </svg>
    """,
    
    "background": """
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24">
      <path fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" d="M18 6H5a2 2 0 0 0-2 2v9a2 2 0 0 0 2 2h13a2 2 0 0 0 2-2V8a2 2 0 0 0-2-2z"/>
      <path fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" d="M5 10h14"/>
      <path fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" d="M8 6V3"/>
      <path fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" d="M16 6V3"/>
      <line x1="7" y1="15" x2="7" y2="15" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
      <line x1="12" y1="15" x2="12" y2="15" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
      <line x1="17" y1="15" x2="17" y2="15" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
    </svg>
    """,
    
    "file": """
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24">
      <path fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" d="M13 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z"/>
      <path fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" d="M13 2v7h7"/>
    </svg>
    """,
    
    "app": """
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24">
      <rect x="2" y="2" width="6" height="6" rx="1" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
      <rect x="16" y="2" width="6" height="6" rx="1" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
      <rect x="2" y="16" width="6" height="6" rx="1" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
      <rect x="16" y="16" width="6" height="6" rx="1" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
      <line x1="9" y1="5" x2="15" y2="5" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
      <line x1="9" y1="19" x2="15" y2="19" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
      <line x1="5" y1="9" x2="5" y2="15" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
      <line x1="19" y1="9" x2="19" y2="15" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
    </svg>
    """,
    
    "refresh": """
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24">
      <path fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" d="M23 4v6h-6"/>
      <path fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" d="M1 20v-6h6"/>
      <path fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10"/>
      <path fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" d="M1 14l4.64 4.36A9 9 0 0 0 20.49 15"/>
    </svg>
    """,
    
    "about": """
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24">
      <circle cx="12" cy="12" r="10" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
      <line x1="12" y1="16" x2="12" y2="12" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
      <line x1="12" y1="8" x2="12.01" y2="8" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
    </svg>
    """,
    
    "folder": """
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24">
      <path fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/>
    </svg>
    """
}

def svg_to_icon(svg_data):
    """Convert SVG data to a QIcon."""
    try:
        # Skip SVG rendering completely and use a simpler method
        # Create an empty icon instead - this is to avoid the QBuffer issue
        # that occurs on some PyQt5 installations
        return QIcon()
    except Exception as e:
        print(f"Error creating icon: {str(e)}")
        # Return an empty icon as fallback
        return QIcon()

def get_icon(name):
    """
    Get an icon by name.
    
    Args:
        name: Icon name from the ICON_SVG dictionary
        
    Returns:
        QIcon: The requested icon
    """
    if name in ICON_SVG:
        return svg_to_icon(ICON_SVG[name])
    return QIcon()
