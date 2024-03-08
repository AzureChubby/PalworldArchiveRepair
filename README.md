# Palworld Archive Repair

![Docker Image Version](https://img.shields.io/docker/v/qian/palworld-archive-repair)
[![Image Size](https://img.shields.io/docker/image-size/qian/palworld-archive-repair/latest)](https://hub.docker.com/r/qian/palworld-archive-repair/tags)


## 帕鲁存档修复工具

- ✅ 登录服务器重新创建账号问题
- ⌛️ 登录之后光身子无法使用快捷键


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
      - ./data/Pal/Saved/SaveGames/0/9B6884AE9C8644F0A07D67CA7475E474/Players:/data/Players
      - ./data/log:/var/log
    environment:
      - CRON_REPAIR=0 */6 * * *
    restart: unless-stopped
```