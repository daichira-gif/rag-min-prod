from src.rag.pii import scrub

def test_scrub_email():
    text = "My email is test.user@example.com, please contact me."
    expected = "My email is [EMAIL], please contact me."
    assert scrub(text) == expected

def test_scrub_phone():
    text = "Call me at +1 (123) 456-7890."
    expected = "Call me at [PHONE]."
    assert scrub(text) == expected

def test_scrub_credit_card():
    text = "My card number is 4111-1111-1111-1111."
    expected = "My card number is [CARD]."
    assert scrub(text) == expected

def test_scrub_no_pii():
    text = "This is a normal sentence with no sensitive data."
    assert scrub(text) == text

def test_scrub_multiple_pii():
    text = "Contact test@example.com or 555-123-4567."
    expected = "Contact [EMAIL] or [PHONE]."
    assert scrub(text) == expected
