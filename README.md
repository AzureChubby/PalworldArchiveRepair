# Palworld Archive Repair

![Docker Image Version](https://img.shields.io/docker/v/qian/palworld-archive-repair)
[![Image Size](https://img.shields.io/docker/image-size/qian/palworld-archive-repair/latest)](https://hub.docker.com/r/qian/palworld-archive-repair/tags)

## Instructions

> [!IMPORTANT]
> 
> Not thoroughly tested; please make sure to backup before use.
> 
> 未经过充分测试，请确定使用前已经做过备份。


## TODO

- ✅ 登录服务器需要重新创建账号问题
- ✅ 登录之后光身子没有任何装备或者帕鲁以及无法使用快捷键问题
  - 需要保证首次使用的时候没有此 bug；如果有的话，需要进行手动修复(因 Level.sav 存档文件过大，因此未进行解析后对用户装备槽进行修复。此问题原因是`PalStorageContainerId`字段丢失)；
  - 当前代码原理是将第一次识别到的用户数据进行备份，后续如果有需要，则使用此备份数据进行恢复`PalStorageContainerId`字段数据；
- ⌛️ U tell me


## Docker Compose

```yaml
services:
  palworld:
    image: thijsvanloef/palworld-server-docker:latest
    #...
    volumes:
      - ./data:/palworld/
    environment:    
      - BACKUP_ENABLED=true
      - BACKUP_CRON_EXPRESSION=5 */6 * * *
  
  archive-repair:
    image: qian/palworld-archive-repair:latest
    volumes:
      - ./data/Pal/Saved/SaveGames/0/9B6884AE9C8644F0A07D67CA7475E474:/data/save_games
      - ./data/repair/backups:/data/backups
      - ./data/repair/log:/var/log
    environment:
      - CRON_REPAIR=0 */6 * * *
    restart: unless-stopped
```

## Credits

- [palworld-save-tools](https://github.com/cheahjs/palworld-save-tools)