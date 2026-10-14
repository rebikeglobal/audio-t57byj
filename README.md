# study-audio

個人用的 unlisted podcast feeds，用來在 Apple Podcasts 收聽筆記的語音版。

| 節目 | `--show` | Feed |
| --- | --- | --- |
| LJ 研究 | `research`（預設） | `https://rebikeglobal.github.io/audio-t57byj/research/feed.xml` |
| LJ 個人學習 | `study` | `https://rebikeglobal.github.io/audio-t57byj/study/feed.xml` |

- 舊的根目錄 feed（`/feed.xml`）已於 2026-10-14 移除；若之前訂閱過，請改訂閱上面的 `research/feed.xml`。
- iOS 訂閱方式：Podcasts App →「資料庫」→ 右上角「⋯」→「透過 URL 追蹤節目」，貼上 feed URL。
- 已設定 `<itunes:block>Yes</itunes:block>`、`noindex` 與 `robots.txt`；但 repo 是 public，**任何知道網址的人都能收聽**。

## 新增一集

```bash
python3 add_episode.py [--show research|study] path/to/episode.mp3 "標題" "描述" [--date YYYY-MM-DD 或 YYYY-MM-DDTHH:MM:SS+08:00；預設為現在時間]
git add -A && git commit -m "Add episode" && git push
```

- 需要 `ffprobe`（用來計算 `itunes:duration`）。
- 各節目的檔案位置：每個節目各自有一個資料夾（`research/`、`study/`），裡面放 `feed.xml`、`episodes.json` 與 `episodes/`，以及該節目的封面 `cover-vN.png`。
- 節目名稱、描述與封面設定在 `add_episode.py` 的 `SHOWS`。要換封面時，請使用**新的檔名**，Apple 才會更新。
- 不帶檔案參數執行 `python3 add_episode.py` 會重建所有 feeds。
- 單檔必須小於 100 MB（GitHub 的限制），太長就分成多集。
- Apple Podcasts 會快取 feed 與封面，更新可能要幾分鐘到幾小時才出現。
