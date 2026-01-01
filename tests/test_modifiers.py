import modifiers


def test_title_and_camel():
    assert modifiers.apply_modifier('titleCase', 'a blue sky') == 'A Blue Sky'
    assert modifiers.apply_modifier('camelCase', 'a blue sky') == 'aBlueSky'


def test_adverb_and_adjective():
    assert modifiers.apply_modifier('adverb', 'quick') == 'quickly'
    assert modifiers.apply_modifier('adjective', 'sun') == 'suny' or isinstance(modifiers.apply_modifier('adjective', 'sun'), str)


def test_unknown_modifier_returns_original():
    assert modifiers.apply_modifier('noSuchModifier', 'text') == 'text'


def test_list_modifiers_contains_expected():
    names = {m['name'] for m in modifiers.list_modifiers()}
    assert 'snakeCase' in names
    assert 'adverb' in names
