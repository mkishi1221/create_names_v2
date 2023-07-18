from ...modules.get_whois import get_whois

def test_domain_not_avail():
    # arrange
    # act
    res = get_whois("google.com")
    # assert
    assert res is not None
    assert res.availability == "not available"

def test_domain_avail():
    # arrange
    # act
    res = get_whois("messaguides.co")
    # assert
    assert res is not None
    assert res.availability == "available"