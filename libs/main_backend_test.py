from main_backend import short, get_save_path

def test_short():
    assert short('directory\\name') == 'name'

def test_get_save_path():
    assert get_save_path('hbarchart', 'directory_path') == 'directory_path\\hbarchart_1.png'