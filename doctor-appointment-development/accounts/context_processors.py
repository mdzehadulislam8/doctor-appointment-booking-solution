"""
Context processors for accounts app
"""
from .translations import TRANSLATIONS


def language_context(request):
    """Add language context to all templates"""
    # Get language preference
    if request.user.is_authenticated:
        lang = request.user.language
    else:
        lang = request.session.get('language', 'en')
    
    # Get theme preference
    if request.user.is_authenticated:
        dark_mode = request.user.dark_mode
    else:
        dark_mode = request.session.get('theme') == 'dark'
    
    # Get translations
    translations = TRANSLATIONS.get(lang, TRANSLATIONS['en'])
    
    return {
        'current_language': lang,
        'dark_mode': dark_mode,
        'translations': translations,
        'is_bangla': lang == 'bn',
    }
