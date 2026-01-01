import asyncio
from vars import EchoInput
from main import echo


def test_echo_without_lang():
    # Construct an EchoInput without 'lang' set to ensure code handles missing lang
    inp = EchoInput(weather='sunny', mood='happy', clothe='t-shirt')
    out = asyncio.run(echo(inp))
    assert hasattr(out, 'text') and isinstance(out.text, str)
    assert out.text != ""  # should return some text (or a failure message), but must not raise
