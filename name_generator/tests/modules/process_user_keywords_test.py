from ...modules.process_user_keywords import process_keyword_list

def test_process_keyword_list():
    # arrange
    # act
    res = process_keyword_list(["", "Test", "$Cake", "unit"])
    # assert
    assert res is not None
    assert res[0].origin == ["keyword_list"]
    assert res[0].keyword == "cake"