import re

from modifiers import apply_modifier


def test_format_template_with_modifiers():
    template = "On a {weather:upperCase} day, you {mood:adverb} put on a {clothe:pascalCase}."
    pattern = re.compile(r'\{(\w+)(?:\s*:\s*(\w+))?\}')
    pairs = pattern.findall(template)

    data = {'weather': 'sunny', 'mood': 'happy', 'clothe': 'blue jacket'}
    formatted_data = {}
    for param, mod in pairs:
        val = data.get(param, '')
        if mod:
            val = apply_modifier(mod, val, {'required': [], 'template': template})
        formatted_data[param] = val

    safe_template = pattern.sub(lambda m: '{' + m.group(1) + '}', template)
    result = safe_template.format(**formatted_data)

    assert 'SUNNY' in result
    assert 'BlueJacket' in result or 'Blue Jacket' in result
    assert 'happily' in result or 'happyly' in result
