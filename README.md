# JPEGフィルターのプロトタイプ、pyopengl版
単純にJPEGを受け取り、フィルターをかけ、JPEGを送信する。

## 環境構築
poetryをインストールしておく

```
poetry install
```

## 環境変数

`pyproject.toml`と同じ階層に`.env`を置く

```
# filter.pyで待ち受けるアドレス
FILTER_MY_IP="127.0.0.1"
FILTER_MY_PORT="5005"
# filter.pyからの送信先アドレス
FILTER_YOUR_IP="127.0.0.1"
FILTER_YOUR_PORT="5006"
# filter.pyで使うJPEGの品質
FILTER_JPEG_QUALITY="80"

# sender.pyでファイルから読み込むか？
SENDER_FROM_FILE="1"
# sender.pyの画像幅
SENDER_IMAGE_WIDTH="480"
# sender.pyのFPS
SENDER_FPS="30"

# receiver.pyでファイルへ書き込むか？
RECEIVER_TO_FILE="1"

```

## 実行

最後から順番に実行する。

```
poetry run python ./jpeg_filter_prototype/receiver.py
```

fooの場合
```
poetry run python ./jpeg_filter_prototype/filter_foo.py
```

```
poetry run python ./jpeg_filter_prototype/sender.py
```
