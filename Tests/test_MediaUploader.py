import pytest
from App.MediaUploader import MediaUploader

@pytest.fixture()
def fixture_MediaUploader_find_urls():
    return [
        'https://www.youtube.com/123',
        'https://google.com'
    ]

@pytest.mark.parametrize(
    "text",
    [("fixture_MediaUploader_find_urls")]
)
def test_MediaUploader_find_urls(text, request):
    texts = request.getfixturevalue(text)
    for text in texts:
        print(text)
        print(MediaUploader.find_urls(text=text))
        # assert not(False is not MediaUploader.find_urls(text=text))
